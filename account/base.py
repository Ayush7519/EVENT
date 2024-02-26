import os

from django.db import models
from rest_framework import serializers

from ems.validations import iscontactvalidator


def category_image_dir_path(instance, filename):
    nm = instance.user.name
    img = instance.photo
    ext = img.name.split(".")[-1]

    # Validate image extension
    valid_extensions = ["png", "jpg", "jpeg"]
    if ext.lower() not in valid_extensions:
        raise serializers.ValidationError(
            "Extension does not match. It should be of png, jpg, jpeg"
        )

    # Define the directory path for event photos
    event_photos_directory = "User Photos"

    # Construct the file path within the event photos directory
    filename = f"{nm}.{ext}"
    return os.path.join(event_photos_directory, filename)


class BaseModel(models.Model):
    GENDER_TYPE = (("Male", "male"), ("Female", "female"), ("Other", "other"))

    photo = models.ImageField(
        upload_to=category_image_dir_path,
        blank=False,
        null=False,
    )
    # yaha change garna parxa haii.
    contact = models.BigIntegerField(
        validators=[iscontactvalidator],
        blank=True,
        null=True,
    )
    gender = models.CharField(choices=GENDER_TYPE, max_length=20, blank=False)
    province = models.CharField(max_length=100, blank=False)
    district = models.CharField(max_length=100, blank=False)
    municipality = models.CharField(max_length=100, blank=False)
    ward = models.PositiveIntegerField(blank=False)

    class Meta:
        abstract = True
