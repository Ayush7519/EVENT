from rest_framework import serializers

from .models import Artist, Event, Sponser


# Sponser
# creating serializer for the sponser.
class Sponser_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Sponser
        fields = "__all__"


# Event
# creating serializer for the event.
class Event_Serializer(serializers.ModelSerializer):
    # this done for accepting the multiple value in the model relation field form the front end user.
    artist = serializers.PrimaryKeyRelatedField(
        queryset=Artist.objects.all(), many=True
    )
    sponser = serializers.PrimaryKeyRelatedField(
        queryset=Sponser.objects.all(), many=True
    )

    class Meta:
        model = Event
        fields = "__all__"


# creating serializer for the event list/detail view...
class EventList_Serializer(serializers.ModelSerializer):
    # this done for converting the pimary key into string.
    artist = serializers.StringRelatedField(many=True)
    sponser = serializers.StringRelatedField(many=True)

    class Meta:
        model = Event
        fields = "__all__"
