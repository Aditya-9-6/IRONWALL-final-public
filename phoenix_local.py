try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False

import time
import os
import subprocess
from threading import Thread

# Configuration
IMAGE_NAME = "ironwall-proxy:latest" 
BASE_PORT = 8000
NGINX_CONF_PATH = "nginx.conf" 
DOCKER_SOCK = "unix://var/run/docker.sock"

class PhoenixManager:
    def __init__(self):
        if DOCKER_AVAILABLE:
            try:
                self.client = docker.from_env()
            except Exception as e:
                print(f"[Phoenix] Docker available but connection failed: {e}")
                self.client = None
        else:
            self.client = None
            
        self.current_port = BASE_PORT
        self.current_container = None
        
    def start_proxy(self, port):
        if not self.client: return None
        print(f"[Phoenix] Spawning new proxy on port {port}...")
        try:
            container = self.client.containers.run(
                IMAGE_NAME,
                detach=True,
                ports={'8000/tcp': port}, 
                environment=["PROXY_PORT=8000"],
                name=f"ironwall-proxy-{port}"
            )
            return container
        except Exception as e:
            print(f"[Phoenix] Failed to start container: {e}")
            return None

    def update_nginx(self, active_port):
        if not self.client: return
        print(f"[Phoenix] Updating Nginx upstream to port {active_port}...")
        
        new_conf = f"""events {{}}

http {{
    upstream backend {{
        server ironwall-proxy:{active_port}; 
        server host.docker.internal:{active_port}; 
    }}

    server {{
        listen 80;

        location / {{
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }}
    }}
}}
"""
        try:
            with open(NGINX_CONF_PATH, 'w') as f:
                f.write(new_conf)

            # Reload Nginx
            nginx_container = self.client.containers.get("ironwall_nginx_lb") 
            nginx_container.exec_run("nginx -s reload")
        except Exception as e:
            print(f"[Phoenix] Nginx update failed: {e}")

    def kill_old_container(self, container):
        if container and self.client:
            print(f"[Phoenix] Destroying old container {container.name}...")
            try:
                container.stop()
                container.remove()
            except Exception as e:
                print(f"[Phoenix] Error destroying container: {e}")

    def phoenix_loop(self):
        if not self.client:
            print("[Phoenix] Docker not available. Self-healing disabled.")
            return

        # Initial wait
        time.sleep(10) 
        
        while True:
            time.sleep(600) # 10 minutes
            
            new_port = self.current_port + 1
            if new_port > 8100: new_port = 8000 # Cycle
            
            new_container = self.start_proxy(new_port)
            if new_container:
                # Wait for boot
                time.sleep(5)
                
                # Switch traffic
                self.update_nginx(new_port)
                
                # Kill old
                self.kill_old_container(self.current_container)
                
                self.current_container = new_container
                self.current_port = new_port
                print(f"[Phoenix] Rebirth complete. Active on port {new_port}")

def start_phoenix():
    pm = PhoenixManager()
    t = Thread(target=pm.phoenix_loop, daemon=True)
    t.start()
    print("[Phoenix] Manager started.")
