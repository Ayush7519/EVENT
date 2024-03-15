import csv
import os
from datetime import datetime, timedelta

from django.db import models
from rest_framework import serializers

from account.models import Artist
from ems.validations import isalphanumericalvalidator, isalphavalidator


def category_image_dir_path(instance, filename):
    event_name = instance.name
    img = instance.photo  # name of the image.
    ext = img.name.split(".")[-1]  # extracting the image extensions
    # filename = str(event_name) + "." + str(ext)

    # Validate image extension
    valid_extensions = ["png", "jpg", "jpeg"]
    if ext.lower() not in valid_extensions:
        raise serializers.ValidationError(
            "Extension does not match. It should be of png, jpg, jpeg"
        )

    # Define the directory path for event photos
    event_photos_directory = "Sponser Photos"

    # Construct the file path within the event photos directory
    filename = f"{event_name}.{ext}"
    return os.path.join(event_photos_directory, filename)


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
        blank=False,
        null=False,
    )

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
    GENRES_TYPE = (
        ("Pop", "Pop"),
        ("Rock", "Rock"),
        ("Melody", "Medoly"),
        ("Hiphop/Rap", "Hiphop/Rap"),
        ("Electronic/Dance", "Electronic/Dance"),
        ("Intie/Alternative", "Intie/Alternative"),
        ("R&B/Soul", "R&B/Soul"),
        ("Country", "Country"),
        ("Jazz", "Jazz"),
        ("Classical", "Classical"),
        ("Old/Ethic", "Old/Ethic"),
    )
    STATUS_TYPE = (
        ("Accept", "Accept"),
        ("Request", "Request"),
    )
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
    genres = models.CharField(
        max_length=1000,
        blank=True,
        null=True,
        choices=GENRES_TYPE,
    )
    status = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        choices=STATUS_TYPE,
    )

    # here we are over writing the save model for the notification model.
    def save(self, *args, **kwargs):
        # aafu vanda tala ko model bata import gare function vitrai garna parxa
        from emsadmin.models import create_event_csv
        from notification.models import Notification

        # here we are checking if notification is present in the model or not.
        notification_instance = Notification.objects.filter(event=self).first()
        super(Event, self).save(*args, **kwargs)

        if notification_instance:
            print("yes")
            # Update fields of the existing Notification
            notification_instance.event = self
            # ... update other fields as needed
            notification_instance.save()
        else:
            # here we make the message to send through the channle
            message = (
                "Here we go new event alert!!!"
                + " "
                + self.event_name
                + " "
                + "on"
                + " "
                + str(self.date)
                + " "
                + "at"
                + " "
                + str(self.time)
                + "."
            )
            current_date_time = datetime.now()
            updated_date = current_date_time + timedelta(minutes=1)
            notificaton_data = Notification(
                event=self,
                message=message,
                send_on=updated_date,
            )
            notificaton_data.save()
            create_event_csv()

    def __str__(self):
        return self.event_name


def create_event_csv():
    # defining the path to save the csv file.
    csv_file_path = "/Users/aayush/working file/EVENT/mycsv.csv"
    # fetching the required data for the re.
    events = Event.objects.filter(event_completed=False)
    # defining the header for the csv.
    header = ["id", "event_name", "genres", "artist", "location", "event_completed"]
    with open(csv_file_path, "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(header)
        for event in events:
            # Write event data to CSV file
            writer.writerow(
                [
                    event.id,
                    event.event_name,
                    event.genres,
                    event.artist,
                    event.location,
                    event.event_completed,
                ]
            )
