import time
from collections import defaultdict
from state_manager import state_db

# Constants
RATE_LIMIT_PER_MINUTE = 60
JAIL_TIME_SECONDS = 1800 # 30 mins

# In-Memory Rate Limiter (Since we are single process/single worker in this simple demo, or acceptable for per-worker limiting)
# For multi-worker, this needs shared memory or just DB sync (slower).
# "Zero Budget" choice: Per-worker RAM limiting is fine.
request_counts = defaultdict(list)

async def is_banned(ip: str) -> bool:
    """Checks if the IP is currently in the jail (SQLite)."""
    # Optimization: Cache bans in memory for 10s? For now, DB read (sqlite is fast on local SSD)
    # To be extremely fast, we could keep a local set and update it periodically.
    # But let's check DB for robustness.
    # We also check TTL.
    
    # Check DB
    # Note: This is synchronous sqlite call wrapped in async function signature for compatibility
    # If high load, move to threadpool or use aiosqlite. 
    # For now, quick check.
    
    rows = state_db.get_banned_ips()
    current_time = time.time()
    
    for ban_ip, reason, timestamp, ttl in rows:
        if ban_ip == ip:
            if current_time - timestamp < ttl:
                return True
            else:
                # Expired
                state_db.unban_ip(ip)
                return False
    return False

async def jail_ip(ip: str, reason: str = "Rate Limit Exceeded"):
    """Bans an IP for 30 minutes."""
    state_db.ban_ip(ip, reason, time.time(), JAIL_TIME_SECONDS)

async def check_rate_limit(ip: str) -> bool:
    """
    Implements a Sliding Window Rate Limiter (In-Memory).
    """
    current_time = time.time()
    timestamps = request_counts[ip]
    
    # Remove old timestamps
    request_counts[ip] = [t for t in timestamps if current_time - t < 60]
    
    # Add new
    request_counts[ip].append(current_time)
    
    if len(request_counts[ip]) > RATE_LIMIT_PER_MINUTE:
        await jail_ip(ip)
        return False
        
    return True

async def log_waf_event(ip: str, method: str, path: str, rule: str, agent: str):
    state_db.log_waf_event(ip, method, path, rule, agent, time.time())

async def log_request(ip: str, method: str, path: str, status_code: int, start_time: float):
    duration = (time.time() - start_time) * 1000
    state_db.log_request(ip, method, path, status_code, duration, time.time())
