import requests
import time
import json
import re
import sys

# Target Configuration
PROXY_URL = "http://localhost:8000"
VERIFY_SSL = False 

def test_waf_sqli():
    print("[1] Testing WAF (SQL Injection)...")
    try:
        payload = {"q": "UNION SELECT 1, user, password FROM users"}
        # Note: requests.get encodes params. 
        # To force raw malicious payload into query string if needed, we might need manual construction.
        # But 'requests' usually does okay.
        resp = requests.get(f"{PROXY_URL}/search", params=payload, verify=VERIFY_SSL, timeout=5)
        if resp.status_code == 403:
            print("   [+] BLOCKED (403 Forbidden) - WAF is Active.")
        else:
            print(f"   [-] PASSED ({resp.status_code}) - WAF Failed!")
    except Exception as e:
        print(f"   [!] Error: {e}")

def test_cortex_ai():
    print("\n[2] Testing Cortex AI (ML Detection)...")
    # This payload might bypass simple Regex but catch ML
    # "admin' --" is common, but let's try something that looks structure-wise bad
    # or just relying on the trained model.
    try:
        # "DROP TABLE" is in the training set
        payload = {"q": "DROP TABLE users"} 
        resp = requests.post(f"{PROXY_URL}/api/cortex_test", data=payload, verify=VERIFY_SSL)
        if resp.status_code == 403:
             print("   [+] BLOCKED (403) - Cortex AI identified malice.")
        else:
             print(f"   [-] PASSED ({resp.status_code}) - Cortex AI missed it.")
    except Exception as e:
        print(f"   [!] Error: {e}")

def test_rate_limit():
    print("\n[3] Testing Rate Limiter (DDoS Simulation)...")
    print("    Firing 50 requests in burst...")
    blocked = False
    for i in range(50):
        try:
            resp = requests.get(f"{PROXY_URL}/", verify=VERIFY_SSL, timeout=1)
            if resp.status_code == 429:
                print(f"   [+] BLOCKED (429) at request #{i+1}")
                blocked = True
                break
        except Exception:
            pass
            
    if not blocked:
        print("   [-] FAILED - Rate Limiter did not trigger.")

def test_honeytoken():
    print("\n[4] Testing Deception (Honeytoken)...")
    session = requests.Session()
    session.verify = VERIFY_SSL
    
    print("    Scraping Page for Token...")
    try:
        resp = session.get(f"{PROXY_URL}/login")
        # Look for the hidden input we added in IronMorph
        # <input type="text" name="b_birthday_honey" ...>
        if "b_birthday_honey" in resp.text:
            print("    [+] Found Honeytoken Field: 'b_birthday_honey'")
            
            # Trigger it
            print("    Submitting Honeytoken...")
            data = {"username": "attacker", "password": "123", "b_birthday_honey": "1990-01-01"}
            post_resp = session.post(f"{PROXY_URL}/login", data=data)
            
            if post_resp.status_code == 403:
                print("    [+] INSTANT BAN (403) - Deception Successful.")
            else:
                print(f"    [-] FAILED ({post_resp.status_code}) - Not Banned.")
        else:
            print("    [-] Honeytoken field NOT found in HTML.")
    except Exception as e:
        print(f"    [!] Error: {e}")

def run_attack_simulation():
    print("="*50)
    print("      IRONWALL RED TEAM: ATTACK SIMULATION")
    print("="*50)
    print(f"Target: {PROXY_URL}")
    
    # Wait a moment for server to be ready if called immediately
    time.sleep(2)
    
    test_waf_sqli()
    test_cortex_ai()
    test_honeytoken() # This might ban us, so do it last or handle IP ban
    test_rate_limit() # This definitely bans/limits us
    
    print("\n[=] Simulation Complete.")

if __name__ == "__main__":
    run_attack_simulation()
