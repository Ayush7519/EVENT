from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import HttpResponse
from django.shortcuts import render


# creating the view for the testing the web socket.
def test(request):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "notification_group",
        {
            "type": "send_notification_message",
            "message": "NOTIFICATION",
        },
    )
    return HttpResponse("DONE")
