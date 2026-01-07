import os

# Configuration
# Default to Localhost for dev, but Render will use the actual domain manually if needed.
# For a proxy, we forward to... itself? Or a mock backend?
# In this "IronWall" logic, it seems to act as a WAF in front of a backend.
# If no backend is defined, we'll just echo/mock for now to ensure it runs.
BACKEND_URL = os.getenv("BACKEND_URL", "http://example.com") 

SECRET_KEY = os.getenv("IRONWALL_SECRET", "dev-secret-key")
