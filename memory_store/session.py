class SessionMemory:
    def __init__(self, store):
        self.store = store
    
    def get_history(self, session_id):
        return self.store.client.lrange(f"session:{session_id}", 0, -1)
        
    def add_message(self, session_id, message):
        self.store.client.rpush(f"session:{session_id}", message)
