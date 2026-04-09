import os
from celery import Celery
from celery.signals import task_failure
import logging

logger = logging.getLogger('celery.errors')

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

app = Celery('eduflow')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


@task_failure.connect
def on_task_failure(sender, task_id, exception, args, kwargs, traceback, **kw):
    """
    Global handler for task failures. Logs the error with full context
    so it can be picked up by monitoring/alerting systems.
    """
    logger.error(
        f"Task {sender.name}[{task_id}] failed: {exception}",
        exc_info=True,
        extra={
            'task_name': sender.name,
            'task_id': task_id,
            'task_args': args,
            'task_kwargs': kwargs,
        }
    )
