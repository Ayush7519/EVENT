import json

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_celery_beat.models import CrontabSchedule, PeriodicTask

from emsadmin.models import Event


# notification model
class Notification(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    send_on = models.DateTimeField()
    sent = models.BooleanField(default=False)


@receiver(post_save, sender=Notification)
def notification_handler(sender, instance, created, **kwargs):
    if created:
        schedule, created = CrontabSchedule.objects.get_or_create(
            hour=instance.send_on.hour,
            minute=instance.send_on.minute,
            day_of_month=instance.send_on.day,
            month_of_year=instance.send_on.month,
        )
        task = PeriodicTask.objects.create(
            crontab=schedule,
            name="boardcast-notification-" + str(instance.id),
            task="notification.tasks.boardcast_notification",
            args=json.dumps((instance.id,)),
        )
