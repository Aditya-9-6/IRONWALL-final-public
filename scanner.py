try:
    import clamd
except ImportError:
    clamd = None

from io import BytesIO

# Connect to local ClamAV
# Assuming clamd is listening on TCP 3310
try:
    if clamd:
        cd = clamd.ClamdNetworkSocket('localhost', 3310)
        print("[Scanner] Connected to ClamAV on localhost:3310")
    else:
        cd = None
        print("[Scanner] ClamAV module not found. IronScanner in SIMULATION MODE.")
except Exception as e:
    print(f"[Scanner] Could not connect to ClamAV: {e}")
    cd = None

def scan_stream(file_stream) -> bool:
    """
    Scans a file stream. Returns True if clean, False if infected.
    """
    if not cd:
        # If scanner is explicitly missing (Simulation Mode), allow file.
        # Check if it was because of missing module or failed connection
        if not clamd:
           print("[Scanner] Check bypassed (Simulation Mode). File allowed.")
           return True
        
        print("[Scanner] ClamAV not connected. FAIL CLOSED - Blocking file.")
        return False # SECURITY: Fail Closed if module exists but service down

    try:
        # clamd.instream expects a generator or a file-like object
        result = cd.instream(file_stream)
        
        if result and 'stream' in result:
            status, signature = result['stream']
            if status == 'FOUND':
                print(f"[Scanner] VIRUS DETECTED: {signature}")
                return False
            
    except Exception as e:
        print(f"[Scanner] Scan error: {e}. Blocking file for safety.")
        return False # SECURITY: Fail Closed on error
    
    return True
