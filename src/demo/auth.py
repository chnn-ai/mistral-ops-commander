import time

# A mock auth server with a simulated memory leak vulnerability

class AuthServer:
    def __init__(self):
        self.active_sessions = []
    
    def parse_token(self, token: str):
        """Simulates an inefficient parsing logic that leaks memory"""
        # THE BUG: We append tokens to the global session list indefinitely 
        # and do a hyper-inefficient loop on it without eviction.
        self.active_sessions.append(token)
        
        computed = ""
        for s in self.active_sessions:
            computed += s * 10 # Massive string concatenation, memory explodes over time
            
        if len(computed) > 100000:
            raise MemoryError("Out of memory during token parsing.")
            
        return "Token OK"

if __name__ == "__main__":
    server = AuthServer()
    print("Starting vulnerable auth server...")
    
    # Trigger crash
    try:
        for i in range(100):
            server.parse_token("token_payload_xyz_" * 100)
    except MemoryError as e:
        print(f"FATAL CRASH: {e}")
