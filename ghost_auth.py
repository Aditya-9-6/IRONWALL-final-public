import json

def verify_biometrics(bio_data_str: str) -> bool:
    """
    Verifies behavioral biometric data.
    Returns True if human, False if bot.
    """
    if not bio_data_str:
        return True # Fail open if no data? Or strict? Let's be lenient for demo.
        
    try:
        data = json.loads(bio_data_str)
        variance = data.get('variance', 0)
        backspace_count = data.get('backspace_count', 0)
        
        # Logic: If flight_time variance is 0, it's a bot (perfect typing)
        if variance == 0:
            return False
            
        # Logic: If backspace used, likely human
        if backspace_count > 0:
            return True
            
        # Default fallback
        return True
        
    except:
        return False
