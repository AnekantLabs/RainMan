
# create a redis task queue
import redis
import json
from worker.celery_app import app
# crate a redis connection
redis_conn = redis.Redis(host='127.0.0.1', port=6379, db=0)

# function to add a task to the queue
def add_task_to_queue(task: dict):
    """Adds a task to the redis queue."""
    try:
        # redis_conn.lpush("alerts", json.dumps(task))
        
        app.send_task("tasks.process_alert", args=[task], queue="alerts")
        print(f"Task added to the queue: {task}")
        
        # print all tasks in the queue
        print(redis_conn.lrange("alerts", 0, -1))
        
        return {"message": "Task added to the queue!"}
    except Exception as e:
        print(f"Error adding task to the queue: {e}")
        return {"message": "Error adding task to the queue!"}