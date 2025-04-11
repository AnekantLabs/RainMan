from celery import Celery

# Initialize Celery
app = Celery(
    "rainman",
    broker="redis://127.0.0.1:6379/0",  # Redis as the message broker
    backend="redis://127.0.0.1:6379/0",  # Redis as the result backend
)

# Celery configuration
app.conf.task_routes = {
    "tasks.process_alert": {"queue": "alerts"},
}