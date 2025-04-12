# backend_app/message_publisher.py
from celery import Celery

# same broker config used by the worker
celery = Celery('producer', broker='redis://localhost:6379/0',backend='redis://localhost:6379/0')