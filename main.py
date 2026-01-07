import uvicorn
import threading
import time
import sys
import phoenix_local
from config import BACKEND_URL

BANNER = """
██╗██████╗  ██████╗ ███╗   ██╗██╗    ██╗ █████╗ ██╗     ██╗     
██║██╔══██╗██╔═══██╗████╗  ██║██║    ██║██╔══██╗██║     ██║     
██║██████╔╝██║   ██║██╔██╗ ██║██║ █╗ ██║███████║██║     ██║     
██║██╔══██╗██║   ██║██║╚██╗██║██║███╗██║██╔══██║██║     ██║     
██║██║  ██║╚██████╔╝██║ ╚████║╚███╔███╔╝██║  ██║███████╗███████╗
╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚══════╝╚══════╝
      Community Edition v3.1 (God Tier + DLC)
"""

def print_status():
    print(BANNER)
    print("="*60)
    print(f"[*] Proxy Target: {BACKEND_URL}")
    print("[*] Modules Active: Quantum, Morph, Ghost, Scanner, Shield")
    print("[*] DLC Loaded: Minefield, Neural Shield, Zero-DB Dashboard")
    print("="*60)
    print("[+] Starting IronWall Proxy Engine on port 8000...")
    print("[+] Dashboard available via: 'streamlit run dashboard.py'")

def start_phoenix_wrapper():
    # Only start Phoenix if we are in a Docker environment ensuring we don't kill our own process
    # if we were running inside the container being killed. 
    # But for a "runner" script, maybe we just want to run the proxy application.
    # Phoenix logic is specific to the "Manager" role. 
    # We will skip auto-start of Phoenix here to avoid accidental self-destruction loops on local dev.
    pass

if __name__ == "__main__":
    if "--attack" in sys.argv:
        print_status()
        import red_team
        print("\n[+] Launching Red Team Simulation...")
        try:
            red_team.run_attack_simulation()
        except:
            print("[!] Attack Simulation Failed (Is the proxy running?)")
    else:
        print_status()
        
        # Run Uvicorn
        # This blocks, so it's the main process
        try:
            uvicorn.run("proxy_engine:app", host="0.0.0.0", port=8000, reload=False)
        except KeyboardInterrupt:
            print("\n[!] IronWall Shutting Down.")
