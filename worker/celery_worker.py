# worker/celery_worker.py
from celery import Celery

celery_app = Celery(
    "rainman",
    broker="redis://127.0.0.1:6379/0",
    backend="redis://127.0.0.1:6379/0",
    include=["tasks.websocket_alert", "tasks.process_alert"]
)

celery_app.conf.task_routes = {
    "tasks.process_alert": {"queue": "alerts"},
    "tasks.connect_websocket": {"queue": "websocket_queue"}, 
    "tasks.connect_websocket_startup": {"queue": "websocket_queue"}
}
