import orjson
import time
from state_manager import state_db

class SchemaLearner:
    def __init__(self):
        pass

    def _get_type_name(self, value):
        """Returns a string representation of the basic type."""
        if isinstance(value, int): return "int"
        if isinstance(value, float): return "float"
        if isinstance(value, str): return "str"
        if isinstance(value, bool): return "bool"
        if isinstance(value, list): return "list"
        if isinstance(value, dict): return "dict"
        return "unknown"

    def _flatten_payload(self, payload, prefix=""):
        """Recursively yields (key_path, type) tuples."""
        if isinstance(payload, dict):
            for k, v in payload.items():
                new_key = f"{prefix}.{k}" if prefix else k
                yield from self._flatten_payload(v, new_key)
        elif isinstance(payload, list):
            # For lists, we just want to know it contains items of a certain type
            # We treat the list content generically for now to avoid massive schema explosion
            if payload:
                # Sample the first item for type inference
                yield from self._flatten_payload(payload[0], f"{prefix}[]")
        else:
            yield (prefix, self._get_type_name(payload))

    async def learn_request(self, host, path, method, payload_bytes):
        """
        Passively learns the schema of valid requests.
        Async fire-and-forget.
        """
        try:
            payload = orjson.loads(payload_bytes)
        except:
            return # Ignore non-JSON or malformed

        timestamp = time.time()
        for key_path, type_name in self._flatten_payload(payload):
             # Save to DB
             state_db.add_schema_entry(host, method, path, key_path, type_name, timestamp)

    async def validate_request(self, host, path, method, payload_bytes):
        """
        Validates a request against the learned schema.
        Returns a Risk Score (0-100).
        """
        try:
            payload = orjson.loads(payload_bytes)
        except:
            # If we expect JSON (based on headers) but get garbage, that's suspicious.
            # But here we just won't validate schema.
            return 0 

        risk_score = 0
        
        # We iterate over the incoming payload
        for key_path, type_name in self._flatten_payload(payload):
            
            # Check if we have seen this key before
            known_types = state_db.get_schema_types(host, method, path, key_path)
            
            if not known_types:
                # New field we've never seen? 
                # Low risk, APIs evolve.
                continue 
                
            if type_name not in known_types:
                # ANOMALY DETECTED!
                # e.g. We saw 'int' for 'age' 1000 times, now we see 'str' ("1 OR 1=1")
                # High probability of Injection Attack or Fuzzing
                risk_score += 50
                
        # Cap score
        return min(risk_score, 100)

    async def get_learned_schema_stats(self):
        """Debug function to see what we've learned."""
        entries = state_db.get_all_schemas()
        # Return summary similar to original
        return entries
