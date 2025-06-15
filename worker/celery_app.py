from celery import Celery


# Initialize Celery
celery_app = Celery(
    "rainman",
    broker="redis://127.0.0.1:6379/0",  # Redis as the message broker
    backend="redis://127.0.0.1:6379/0",  # Redis as the result backend
    include=["tasks.process_alert", "tasks.websocket_alert"]  # Load your task module
)


# Celery configuration
celery_app.conf.task_routes = {
    "tasks.process_alert": {"queue": "alerts"},
    "tasks.connect_websocket": {"queue": "websocket_queue"}, 
}