import base64
import os
import time

# Global storage
server_kem = None

class MockKyber:
    """Simulates Kyber-1024 for non-liboqs environments (Demo Mode)"""
    def __init__(self):
        self.name = "Kyber1024-SIMULATION"
        
    def generate_keypair(self):
        # Return random bytes to simulate public key
        return os.urandom(1184) # Size of Kyber1024 key
        
    def encapsulate(self, client_pk):
        # Generate random ciphertext and shared secret
        ciphertext = os.urandom(1568)
        shared_secret = os.urandom(32)
        return ciphertext, shared_secret

def init_quantum_keys():
    """Generates simulated keys if real library is missing."""
    global server_kem
    
    try:
        import oqs
        server_kem = oqs.KeyEncapsulation("Kyber1024")
        print("[Quantum] REAL Kyber-1024 Active (liboqs loaded).")
    except ImportError:
        server_kem = MockKyber()
        print("[Quantum] SIMULATION MODE: Kyber-1024 (liboqs not found)")

    # Simulate generating server keys
    public_key = server_kem.generate_keypair()
    # We don't save to DB in simulation to avoid complexity
    
def perform_handshake(client_public_key_b64: str):
    try:
        if not server_kem:
            init_quantum_keys()
            
        client_pk = base64.b64decode(client_public_key_b64)
        
        # Encapsulate
        ciphertext, shared_secret = server_kem.encapsulate(client_pk)
        
        return {
            "status": "success",
            "ciphertext": base64.b64encode(ciphertext).decode('utf-8'),
            "shared_secret_snippet": base64.b64encode(shared_secret[:8]).decode('utf-8')
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Init on load
init_quantum_keys()
