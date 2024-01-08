from __future__ import absolute_import, unicode_literals

import os
from datetime import timedelta

from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ems.settings")

app = Celery("ems")
app.conf.broker_connection_retry_on_startup = True
app.conf.enable_utc = False

app.conf.update(timezone="Asia/Kathmandu")

app.config_from_object(settings, namespace="CELERY")


# celery beat setting. this is done to tell when to do the job.
app.conf.beat_schedule = {
    # defining the name of the task.
    "checking-the-event-date-time-every-hour": {
        "task": "emsadmin.tasks.test_function",
        "schedule": timedelta(days=2),
    }
}


app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
