import redis

class RedisCacheDB:
    def __init__(self, host='localhost', port=6379, db=0):
        self.client = redis.StrictRedis(host=host, port=port, db=db, decode_responses=True)
    
    def initialize_hash(self, file_id: str):
        file_id = file_id
        key = f"file_status:{file_id}"
        self.client.hset(key, mapping={
            "file_id": file_id,
            "uploaded": "False",
            "processed_by_llm": "False",
            "script_executed": "False",
            "ready": "False",
        })
    
    def update_status(self, file_id: str, field: str, value: bool):
        key = f"file_status:{file_id}"
        self.client.hset(key, field, str(value))
    
    def get_status(self, file_id: str):
        key = f"file_status:{file_id}"
        status_info = self.client.hgetall(key)
        for k, v in status_info.items():
            if v == "True":
                status_info[k] = True
            elif v == "False":
                status_info[k] = False
        return status_info

    def delete_status(self, file_id: str):
        key = f"file_status:{file_id}"
        deleted = self.client.delete(key)
        return deleted > 0

cache_db = RedisCacheDB(host='cachedb', port=6379, db=0)