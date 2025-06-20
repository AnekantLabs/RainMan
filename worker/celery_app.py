from celery import Celery
from celery.signals import worker_ready
from logging_event import get_logger

import logging

# Initialize logging first
# logger = logging.getLogger(__name__)
logger = get_logger()

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

@worker_ready.connect
def at_worker_ready(sender, **kwargs):
    logger.info("🎯 Worker ready. Sending startup websocket task.")
    sender.app.send_task("tasks.connect_websocket_startup")
