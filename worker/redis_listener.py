import redis
import json
import time

# create a redis connection
redis_conn = redis.Redis(host='127.0.0.1', port=6379, db=0)

# function to listen to the redis queue
def listen_to_queue():
    """Listens to the redis queue for new tasks."""
    print("Listening to the redis queue...")
    
    while True:
        try:
            queue_data = redis_conn.brpop("task_queue")
            print(f"Task received from the queue: {queue_data}")
            
            # later you can process the task here
            # for now, just print the task
        except Exception as e:
            print(f"Error receiving task from the queue: {e}")
        time.sleep(1)  # Prevents excessive CPU usage
