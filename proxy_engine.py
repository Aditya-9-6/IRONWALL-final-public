from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import httpx
import os
import config

app = FastAPI()

# Mount Static
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ----- Frontend Routes -----
@app.get("/")
async def serve_portal():
    return HTMLResponse(content=open("portal.html", "r", encoding="utf-8").read())

@app.get("/logo.png")
async def serve_logo():
    if os.path.exists("logo.png"):
        return FileResponse("logo.png")
    return Response(status_code=404) # Should handle missing logo gracefully

# ----- Auth Routes (Stub for MVP) -----
# ----- Auth Routes (OTP Implementation) -----
otp_storage = {}  # In-memory OTP storage {email: otp}

@app.post("/send-otp")
async def send_otp(request: Request):
    data = await request.json()
    email = data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email required")
    
    # Generate 6-digit OTP
    import random
    otp = f"{random.randint(100000, 999999)}"
    otp_storage[email] = otp
    
    # Log to Console (for Render Logs)
    print(f" [OTP-DISPATCH] Code for {email}: {otp} (Master Key: 888888)")
    
    return {"message": "OTP sent"}

@app.post("/verify-otp")
async def verify_otp(request: Request):
    data = await request.json()
    email = data.get("email")
    code = data.get("otp")
    
    # Master Key for Demo or Real OTP
    if code == "888888" or otp_storage.get(email) == code:
        # Clear used OTP
        if email in otp_storage:
             del otp_storage[email]
             
        return {
            "access_token": "iron_otp_token_" + os.urandom(4).hex(), 
            "token_type": "bearer",
            "user_email": email
        }
    
    raise HTTPException(status_code=401, detail="Invalid Access Code")

# ----- Proxy Logic -----
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def proxy_all(path: str, request: Request):
    # 1. Build Upstream URL
    url = f"{config.BACKEND_URL}/{path}"
    
    # 2. Forward Headers (Clean Host)
    headers = dict(request.headers)
    headers.pop("host", None)
    headers.pop("content-length", None) # Let httpx recalc

    # 3. Stream Body
    body = await request.body()

    # 4. Forward Request
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.request(
                method=request.method,
                url=url,
                content=body,
                headers=headers,
                params=request.query_params
            )
            
            # 5. Return Response
            # FIX: Strip Content-Length to prevent h11 protocol errors if we were modifying body
            # (We aren't modifying body here, but good practice in this specific environment)
            resp_headers = dict(resp.headers)
            resp_headers.pop("content-length", None) 
            
            return Response(
                content=resp.content,
                status_code=resp.status_code,
                headers=resp_headers
            )
    except Exception as e:
        # If no backend, just echo for demo purposes
        return {
            "status": "IronWall Proxy Active", 
            "message": f"Forwarding to {url} failed (No Backend Configured)",
            "error": str(e)
        }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
