import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from notification.models import Notification


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = "notification"
        self.room_group_name = "notification_group"
        # adding the channel in the static group.
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )
        await self.accept()

        # Fetch and send recent notifications to the client when they connect
        await self.send_recent_notifications()

    async def receive(self, text_data):
        print("Message from the client:", text_data)

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )

    # sending the message to the websocket.
    async def send_notification_message(self, event):
        message = event["message"]

        try:
            recent_notifications = await self.get_recent_notifications()
            serialized_notifications = [
                {
                    "message": notification.message,
                    "event_id": notification.event.id,
                }
                async for notification in self.async_get_recent_notifications(
                    recent_notifications
                )
            ]
            # Send message to WebSocket
            await self.send(
                text_data=json.dumps(
                    {
                        "message": message,
                        "recent_notifications": serialized_notifications,
                    }
                )
            )
        except Exception as e:
            print("Error sending notification message:", e)

    @sync_to_async
    def get_recent_notifications(self):
        return list(Notification.objects.order_by("-created_at")[:20])

    async def async_get_recent_notifications(self, notifications):
        for notification in notifications:
            notification.event = await sync_to_async(lambda: notification.event)()
            yield notification

    async def send_recent_notifications(self):
        try:
            recent_notifications = await self.get_recent_notifications()
            serialized_notifications = [
                {
                    "message": notification.message,
                    "event_id": notification.event.id,
                }
                async for notification in self.async_get_recent_notifications(
                    recent_notifications
                )
            ]
            # Send recent notifications to the client
            await self.send(
                text_data=json.dumps(
                    {
                        "recent_notifications": serialized_notifications,
                    }
                )
            )
        except Exception as e:
            print("Error sending recent notifications:", e)
