import statistics
import time
from collections import deque

# Config
WINDOW_SIZE = 100
SIGMA_THRESHOLD = 3.0 # Z-Score threshold for anomaly
MIN_SAMPLES = 20 # Minimum samples before enforcement

class NeuralShield:
    def __init__(self):
        # We track request body sizes for this demo
        self.request_sizes = deque(maxlen=WINDOW_SIZE)
        
    def learn(self, request_size: int):
        self.request_sizes.append(request_size)
    
    def is_anomaly(self, request_size: int) -> bool:
        if len(self.request_sizes) < MIN_SAMPLES:
            return False # Not enough data
            
        mean = statistics.mean(self.request_sizes)
        stdev = statistics.stdev(self.request_sizes)
        
        if stdev == 0:
            return False
            
        z_score = abs(request_size - mean) / stdev
        
        if z_score > SIGMA_THRESHOLD:
            return True
            
        return False

# Singleton
shield = NeuralShield()
