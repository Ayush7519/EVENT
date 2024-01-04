from django.db import models

from ems.validations import isalphavalidator


class Heading(models.Model):
    heading = models.CharField(max_length=100)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.heading


class Content_Management(models.Model):
    STATUS_CHOICES = (
        ("Draft", "draft"),
        ("Publish", "publish"),
    )
    heading = models.ForeignKey(
        Heading,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
    )
    content = models.TextField(null=False, blank=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=10)
    status = models.CharField(choices=STATUS_CHOICES, max_length=100)

    def __str__(self):
        return self.heading.heading
