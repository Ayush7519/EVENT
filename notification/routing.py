from django.urls import path

from . import consumer

websocket_urlpatterns = [
    path(
        "ws/notification/",
        consumer.NotificationConsumer.as_asgi(),
        name="path to call the web socket",
    ),
]
