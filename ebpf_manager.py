import ipaddress
import logging
import ctypes
import redis.asyncio as redis
from config import REDIS_URL, JAIL_TIME_SECONDS

# Try to import BCC for eBPF support
try:
    from bcc import BPF
    BCC_AVAILABLE = True
except ImportError:
    BCC_AVAILABLE = False
    logging.warning("eBPF: BCC not installed. Falling back to Software Blocking (Redis).")

class BlockManager:
    def __init__(self):
        self.pool = redis.ConnectionPool.from_url(REDIS_URL, decode_responses=True)
        self.r = redis.Redis(connection_pool=self.pool)
        self.mode = "SOFTWARE"
        self.bpf = None
        self.blocked_ips_map = None
        
        # Unsafe but necessary: We need to load eBPF synchronously during init 
        # or have an async setup method. For simplicity, we just check availability here.
        if BCC_AVAILABLE:
            self.load_ebpf()

    def load_ebpf(self):
        """Compiles and loads the XDP Keynel Module."""
        try:
            logging.info("eBPF: Compiling C-Code...")
            self.bpf = BPF(src_file="ebpf_core.c")
            
            # Load function
            fn = self.bpf.load_func("xdp_firewall", BPF.XDP)
            
            # Attach to Interface (Hardcoded 'lo' for local testing)
            # In production, this would be 'eth0' or passed via config.
            interface = "lo" 
            logging.info(f"eBPF: Attaching XDP program to {interface}...")
            self.bpf.attach_xdp(interface, fn, 0)
            
            # Get reference to the map
            self.blocked_ips_map = self.bpf.get_table("blocked_ips")
            self.mode = "KERNEL"
            logging.info("eBPF: System Active! High-Performance Dropping Enabled.")
            
        except Exception as e:
            logging.error(f"eBPF: Failed to load. Error: {e}")
            self.mode = "SOFTWARE"

    async def block_ip(self, ip: str, reason="Active Defense"):
        """
        Blocks an IP address using both Redis (Persistent) and eBPF (Fast).
        """
        # 1. Redis (Software / Logs)
        await self.r.setex(f"jail:{ip}", JAIL_TIME_SECONDS, f"banned:{reason}")
        
        # 2. Kernel (Hardware / XDP)
        if self.mode == "KERNEL" and self.blocked_ips_map:
            try:
                # Convert IP string to int (network byte order is handled by BPF usually, 
                # but ipaddress.packed gives bytes we can cast)
                ip_int = int(ipaddress.IPv4Address(ip))
                # ctypes c_uint32 is needed for BCC keys
                c_ip = ctypes.c_uint32(ip_int)
                c_val = ctypes.c_uint32(1)
                self.blocked_ips_map[c_ip] = c_val
                logging.info(f"eBPF: Added {ip} to Kernel Block Map")
            except Exception as e:
                logging.error(f"eBPF: Failed to add IP {ip}. Error: {e}")

    async def is_blocked(self, ip: str) -> bool:
        """
        Checks if an IP is blocked.
        Redis is the source of truth for the Application Layer.
        (eBPF drops packets before they even reach here, so if we see it, 
         blocking might have failed or it's a new request).
        """
        return await self.r.exists(f"jail:{ip}")
