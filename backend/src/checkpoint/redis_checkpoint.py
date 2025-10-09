import os
from dotenv import load_dotenv

load_dotenv()

class RedisCheckpointer:
    """
    Simplified Redis checkpointer that uses connection string directly.
    Avoids complex SSL handling by using the library's built-in parser.
    """
    
    _instance = None
    _checkpointer = None
    
    def __new__(cls):
        """Singleton pattern to reuse Redis connection"""
        if cls._instance is None:
            cls._instance = super(RedisCheckpointer, cls).__new__(cls)
        return cls._instance
    
    def get_checkpointer(self):
        """
        Returns a Redis checkpointer instance using the simplest possible approach.
        
        Returns:
            RedisSaver or MemorySaver: Redis-based checkpointer or in-memory fallback
        """
        if self._checkpointer is None:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            
            try:
                print(f"🔄 Connecting to Redis...")
                print(f"   URL: {self._mask_url(redis_url)}")
                
                # Import RedisSaver
                from langgraph.checkpoint.redis import RedisSaver
                from redis import Redis
                
                # For your case, non-SSL works, so ensure URL starts with redis://
                if redis_url.startswith("rediss://"):
                    # Your Redis Cloud doesn't need SSL
                    redis_url = redis_url.replace("rediss://", "redis://", 1)
                    print(f"   Changed to non-SSL (redis://)")
                
                # Test connection first
                redis_conn = Redis.from_url(
                    redis_url,
                    decode_responses=False,
                    socket_connect_timeout=10,
                    socket_timeout=10
                )
                redis_conn.ping()
                print(f"   ✅ Redis connection test successful")
                redis_conn.close()
                
                # Create checkpointer - pass URL string, not connection object!
                self._checkpointer = RedisSaver.from_conn_string(redis_url)
                print(f"   ✅ RedisSaver created")
                
                # Get info
                info = redis_conn.info()
                print(f"✅ Redis checkpointer ready!")
                print(f"   Version: {info.get('redis_version', 'unknown')}")
                print(f"   Memory: {info.get('used_memory_human', 'unknown')}")
                
                return self._checkpointer
                
            except ImportError as ie:
                print(f"❌ Import Error: {ie}")
                print(f"   Run: pip install langgraph-checkpoint-redis")
                print("   Falling back to in-memory checkpointer...")
                
                from langgraph.checkpoint.memory import MemorySaver
                self._checkpointer = MemorySaver()
                
            except Exception as e:
                print(f"❌ Redis connection failed: {e}")
                print(f"   Error type: {type(e).__name__}")
                
                # Show detailed traceback for debugging
                import traceback
                print("\n📋 Full traceback:")
                traceback.print_exc()
                
                print("\n   Falling back to in-memory checkpointer...")
                
                from langgraph.checkpoint.memory import MemorySaver
                self._checkpointer = MemorySaver()
        
        return self._checkpointer
    
    def _mask_url(self, url: str) -> str:
        """Mask password in URL"""
        if "@" in url and "://" in url:
            parts = url.split("://", 1)
            if "@" in parts[1]:
                auth, host = parts[1].split("@", 1)
                if ":" in auth:
                    user, pwd = auth.split(":", 1)
                    return f"{parts[0]}://{user}:****@{host}"
        return url[:30] + "..."
    
    def close(self):
        """Close Redis connection"""
        if self._checkpointer is not None:
            try:
                if hasattr(self._checkpointer, 'conn'):
                    self._checkpointer.conn.close()
                print("✅ Redis connection closed")
            except Exception as e:
                print(f"⚠️ Error closing: {e}")
            finally:
                self._checkpointer = None