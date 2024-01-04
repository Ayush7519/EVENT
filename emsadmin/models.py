import os

from django.db import models
from rest_framework import serializers

from account.models import Artist
from ems.validations import isalphanumericalvalidator, isalphavalidator


def category_image_dir_path(instance, filename):
    event_name = instance.name
    img = instance.photo  # name of the image.
    ext = img.name.split(".")[-1]  # extracting the image extensions
    filename = str(event_name) + "." + str(ext)
    # print(filename)
    # validating the image extension.
    if (
        str(ext).lower() == "png"
        or str(ext).lower() == "jpg"
        or str(ext).lower() == "jpeg"
    ):
        return filename
    else:
        raise serializers.ValidationError(
            "Extension Doesnot match.It should be of png,jpg,jpeg"
        )


# SPONSER MODEL
class Sponser(models.Model):
    SPONSER_TYPE = (
        ("Title Sponser", "title sponser"),
        ("Platinum", "platinum"),
        ("Gold", "gold"),
        ("Silver", "silver"),
        ("Bronze", "bronze"),
    )
    sponser_type = models.CharField(
        choices=SPONSER_TYPE,
        max_length=100,
        null=False,
        blank=False,
    )
    name = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        validators=[isalphavalidator],
    )
    amount = models.BigIntegerField(null=False, blank=False)
    photo = models.ImageField(
        upload_to=category_image_dir_path,
        blank=True,
    )

    def dymanic_amount_value(self):
        value = self.sponser_type
        print(value)
        if value == "title sponser":
            return 10000

    def get_dynamic_amount(self):
        return self.dymanic_amount_value

    def __str__(self):
        return self.name


# this is for validating the image.
def category_image_dir_path(instance, filename):
    event_name = instance.event_name
    img = instance.photo
    ext = img.name.split(".")[-1]

    # Validate image extension
    valid_extensions = ["png", "jpg", "jpeg"]
    if ext.lower() not in valid_extensions:
        raise serializers.ValidationError(
            "Extension does not match. It should be of png, jpg, jpeg"
        )

    # Define the directory path for event photos
    event_photos_directory = "Event Photos"

    # Construct the file path within the event photos directory
    filename = f"{event_name}.{ext}"
    return os.path.join(event_photos_directory, filename)


# EVENT MODEL
class Event(models.Model):
    photo = models.ImageField(
        upload_to=category_image_dir_path,
        blank=False,
        null=False,
    )
    event_name = models.CharField(
        max_length=500,
        validators=[isalphanumericalvalidator],
        null=False,
        blank=False,
    )
    date = models.DateField(null=False, blank=False)
    time = models.TimeField(null=False, blank=False)
    # this is the place to change in the host api.
    artist = models.ManyToManyField(
        Artist,
    )
    location = models.CharField(max_length=100, null=False, blank=False)
    capacity = models.BigIntegerField(null=False, blank=False)
    entry_fee = models.BigIntegerField(null=False, blank=False)
    sponser = models.ManyToManyField(Sponser, null=True, blank=True)
    event_completed = models.BooleanField(default=False)
    remaining_capacity = models.PositiveBigIntegerField(null=True, blank=True)
    no_of_participant = models.PositiveBigIntegerField(
        default=0,
        null=False,
        blank=False,
    )

    def __str__(self):
        return self.event_name
