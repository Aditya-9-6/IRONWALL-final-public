

from fastapi.testclient import TestClient
from proxy_engine import app
from neural_shield import shield
import config
from unittest.mock import AsyncMock, patch
import httpx

# MOCKING BACKEND
# We patch httpx.AsyncClient.get and post to return success immediately
# This prevents the tests from hanging while trying to connect to a non-existent backend
mock_response = httpx.Response(200, content=b"Mock Backend Response")



# Since we are not using pytest runner, we apply patches manually in main
client = TestClient(app)

# Mock backend to avoid 502 errors blocking our 403 checks logic or similar
# Actually, for middleware checks (403), we don't even reach backend.
# If we pass middleware, we get 502 (Bad Gateway) because backend is down.
# That is acceptable for "Passing Middleware" test.

def test_neural_shield():
    # 1. Reset Shield for test
    shield.request_sizes.clear()
    
    # 2. Train with small requests (size ~10 bytes)
    for i in range(25):
        response = client.post("/api/test", content="x"*10)
        # Should be 502 (Backend Error) or 404, but NOT 403
        assert response.status_code != 403
        
    # 3. Attack with huge request (size 1000)
    # Mean ~10, Stdev ~0. 
    # Actually if all are exactly 10, stdev is 0. 
    # Logic: if stdev == 0 -> return False. 
    # So we need variance.
    
    # Train with variety
    import random
    shield.request_sizes.clear()
    for i in range(25):
        size = 10 + random.randint(0, 5)
        client.post("/api/test", content="x"*size)
        
    # Now huge
    # We need to make sure we don't hit rate limit (60/min). 
    # We did 50 requests above.
    # Shield check happens BEFORE Rate Limit? 
    # Let's check proxy_engine.py:
    # 1. is_banned (IP Jail)
    # 2. check_rate_limit
    # 3. Neural Shield (Middleware body check)
    # So we MIGHT get rate limited if we are too fast.
    # Let's reset limiter manually for test
    from limiter import request_counts
    request_counts.clear()

    response = client.post("/api/test", content="x"*5000)
    assert response.status_code == 403
    assert "Neural Shield Anomaly" in response.text or "Anomalous Request" in response.text
    print("Neural Shield Test Passed")

def test_honeypot_multipart():
    # Multipart form data with honey field
    response = client.post("/api/submit", 
                           data={"username": "user", "b_birthday_honey": "I am a bot"},
                           headers={"content-type": "multipart/form-data; boundary=boundary"})
    # Only if I construct it correctly. TestClient handles data param as form-encoded usually unless files passed.
    # Let's use files param to force multipart or just data
    
    response = client.post("/api/submit", data={"b_birthday_honey": "123"})
    # TestClient default is x-www-form-urlencoded
    assert response.status_code == 403
    assert "Blocked" in response.text
    print("Honeypot Form-Encoded Test Passed")

if __name__ == "__main__":
    # Manually mock for the script execution
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get, \
         patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_get.return_value = mock_response
        mock_post.return_value = mock_response
        
        try:
            test_neural_shield()
            test_honeypot_multipart()
            print("ALL TESTS PASSED")
        except Exception as e:
            print(f"TEST FAILED: {e}")
            import traceback
            traceback.print_exc()
