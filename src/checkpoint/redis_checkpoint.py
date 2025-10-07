import os
from langgraph.checkpoint.redis import RedisSaver
from redis import Redis
from dotenv import load_dotenv

load_dotenv()

class RedisCheckpointer:
    """
    Manages Redis-based checkpointing for LangGraph with proper connection handling.
    """
    
    _instance = None
    _checkpointer = None
    _redis_conn = None
    
    def __new__(cls):
        """Singleton pattern to reuse Redis connection"""
        if cls._instance is None:
            cls._instance = super(RedisCheckpointer, cls).__new__(cls)
        return cls._instance
    
    def get_checkpointer(self):
        """
        Returns a Redis checkpointer instance with proper connection.
        Creates a new instance only if one doesn't exist.
        
        Returns:
            RedisSaver: Redis-based checkpointer for LangGraph
        """
        if self._checkpointer is None:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            
            try:
                # Parse Redis URL
                # Format: redis://[[username:]password@]host[:port][/database]
                if redis_url.startswith("redis://"):
                    redis_url = redis_url[8:]  # Remove redis://
                
                # Split into components
                parts = redis_url.split('@')
                if len(parts) == 2:
                    # Has auth
                    auth_part = parts[0]
                    host_part = parts[1]
                    if ':' in auth_part:
                        username, password = auth_part.split(':', 1)
                    else:
                        username = None
                        password = auth_part
                else:
                    # No auth
                    username = None
                    password = None
                    host_part = parts[0]
                
                # Parse host and port
                if ':' in host_part:
                    host, port = host_part.split(':', 1)
                    port = int(port.split('/')[0])  # Remove database if present
                else:
                    host = host_part.split('/')[0]
                    port = 6379
                
                # Create Redis connection
                self._redis_conn = Redis(
                    host=host,
                    port=port,
                    password=password,
                    decode_responses=False,  # Important for binary data
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
                
                # Test connection
                self._redis_conn.ping()
                
                # Create RedisSaver with the connection
                self._checkpointer = RedisSaver(self._redis_conn)
                
                print(f"✅ Redis checkpointer initialized: redis://{host}:{port}")
                
            except Exception as e:
                print(f"❌ Error connecting to Redis: {e}")
                print("Falling back to in-memory checkpointer...")
                from langgraph.checkpoint.memory import MemorySaver
                self._checkpointer = MemorySaver()
        
        return self._checkpointer
    
    def close(self):
        """Close Redis connection when done"""
        if self._redis_conn is not None:
            try:
                self._redis_conn.close()
                print("✅ Redis connection closed")
            except Exception as e:
                print(f"Error closing Redis connection: {e}")
            finally:
                self._checkpointer = None
                self._redis_conn = None