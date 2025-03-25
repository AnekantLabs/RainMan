
# create a redis task queue
import redis
import json

# crate a redis connection
redis_conn = redis.Redis(host='127.0.0.1', port=6379, db=0)

# function to add a task to the queue
def add_task_to_queue(task: dict):
    """Adds a task to the redis queue."""
    try:
        redis_conn.lpush("task_queue", json.dumps(task))
        
        print(f"Task added to the queue: {task}")
        
        # print all tasks in the queue
        print(redis_conn.lrange("task_queue", 0, -1))
        
        return {"message": "Task added to the queue!"}
    except Exception as e:
        print(f"Error adding task to the queue: {e}")
        return {"message": "Error adding task to the queue!"}