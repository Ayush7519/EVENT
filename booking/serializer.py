from rest_framework import serializers

from emsadmin.serializer import EventList_Serializer

from .models import Ticket


# creting the serializer for the ticket.
class TicketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = "__all__"

    def validate(self, attrs):
        quantity = attrs.get("quantity")
        event = attrs.get("event")
        event_price = event.entry_fee
        event_total_price = quantity * event_price
        event_total_price_frontend = attrs.get("total_price")
        if event_total_price == event_total_price_frontend:
            return attrs
        else:
            raise serializers.ValidationError(
                "Something Went Wrong In Calculation..!!!"
            )


# creating the serializer for the list for the booked ticket from the user.
class UserBookedTicket_Serializer(serializers.ModelSerializer):
    event = EventList_Serializer()

    class Meta:
        model = Ticket
        fields = "__all__"
        # depth = 1
