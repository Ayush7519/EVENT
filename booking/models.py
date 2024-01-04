from django.db import models

from emsadmin.models import Event, Sponser

# model for the ticke.


class Ticket(models.Model):
    ticket_id = models.BigAutoField(
        blank=False,
        null=False,
        primary_key=True,
    )
    ticket_num = models.CharField(max_length=10000, blank=True)
    booked_by = models.CharField(
        max_length=1000,
        blank=True,
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
    )
    quantity = models.PositiveBigIntegerField(
        default=1,
    )
    total_price = models.PositiveBigIntegerField()

    def __str__(self):
        return self.event.event_name
