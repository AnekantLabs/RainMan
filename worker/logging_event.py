# logging_config.py
import logging
import redis
import json
from datetime import datetime,timedelta, timezone

class RedisLogHandler(logging.Handler):
    def __init__(self, redis_url="redis://localhost:6379", key="worker_logs"):
        super().__init__()
        self.redis = redis.Redis.from_url(redis_url)
        self.key = key

    def emit(self, record):
        log_entry = self.format(record)
        log_object = {
            "level": record.levelname,
            "message": log_entry,
            "timestamp": datetime.now(timezone(timedelta(hours=2))).isoformat()
        }
        try:
            self.redis.lpush(self.key, json.dumps(log_object))
            self.redis.ltrim(self.key, 0, 499)  # Keep last 500 logs
        except Exception:
            # fallback to stderr if Redis is down
            print("Redis log error:", log_entry)

def get_logger(name="rainman"):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = RedisLogHandler()
        formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
    return logger