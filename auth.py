from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional
import jwt
from datetime import datetime, timedelta
import bcrypt
import os
import base64
import time

# Internal modules
from state_manager import state_db
import config

router = APIRouter()

# --- Configuration ---
# Generate a secret key if not in config (In prod, load from env)
SECRET_KEY = os.getenv("IRONWALL_SECRET", "ironwall_quantum_secret_key_x99")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- Pydantic Models ---
class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    username: str # email
    password: str
    biometric_evidence_base64: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    msg: str = "Success"

# --- Utils ---
def get_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def save_biometric_evidence(email: str, b64_data: str):
    try:
        if not b64_data:
            return
            
        # 1. Parse Domain (Company ID)
        domain = email.split('@')[-1] if '@' in email else 'unknown'
        
        # 2. Define Path
        today = datetime.now().strftime("%Y-%m-%d")
        base_dir = f"./storage_vault/{domain}/{today}"
        os.makedirs(base_dir, exist_ok=True)
        
        # 3. Decode Image
        # Remove header if present (data:image/jpeg;base64,...)
        if "base64," in b64_data:
            b64_data = b64_data.split("base64,")[1]
            
        image_data = base64.b64decode(b64_data)
        
        # 4. Save
        timestamp_slug = int(time.time())
        filename = f"{base_dir}/evidence_{email}_{timestamp_slug}.jpg"
        
        with open(filename, "wb") as f:
            f.write(image_data)
            
    except Exception as e:
        print(f"[!] Evidence Storage Failed: {e}")

# --- Routes ---

@router.post("/register", response_model=Token)
async def register(user: UserCreate):
    # Check if user exists
    existing = state_db.get_user_by_email(user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create User
    hashed_pw = get_password_hash(user.password)
    # is_active=True, is_verified=False by default in DB
    success = state_db.create_user(user.email, hashed_pw)
    
    if not success:
        raise HTTPException(status_code=500, detail="Database Error")
    
    # Generate Token Immediately
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer", "msg": "Success"}

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    # 1. Verify Credentials
    user = state_db.get_user_by_email(user_data.username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    if not verify_password(user_data.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # 2. Evidence Storage (IronEye)
    if user_data.biometric_evidence_base64:
        save_biometric_evidence(user_data.username, user_data.biometric_evidence_base64)
    
    # 3. Generate Token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user['email']}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer", "msg": "Login Successful"}
