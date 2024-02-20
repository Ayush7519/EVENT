import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer


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

    async def receive(self, text_data):
        print("messsage form the clint...", text_data)

    async def disconnect(self, close_code):
        # Leave room group
        self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )

    # sending the message to the websocket.
    async def send_notification_message(self, event):
        message = event["message"]
        print(message)

        # Send message to WebSocket
        await self.send(
            text_data=json.dumps(
                {
                    "message": message,
                }
            )
        )
