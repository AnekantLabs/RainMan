# filepath: /home/daksh/RainMan/worker/utils/redis_client.py
import json
import logging
import redis

# Redis configuration
REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = None  # Set to None if no password is required

# Initialize Redis client
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True  # Auto-decode response bytes to strings
)

# Set up logging (add this near the top of your file)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def save_order_to_redis(self, order_id, order_data):
    """
    Saves order details to Redis for tracking.
    """
    try:
        redis_key = f"order:{order_id}"
        redis_client.set(redis_key, json.dumps(order_data))
        redis_client.expire(redis_key, 86400)  # Set expiration to 24 hours
        logger.info(f"✅ Order {order_id} saved to Redis.")
    except Exception as e:
        logger.error(f"❌ Failed to save order {order_id} to Redis: {e}")