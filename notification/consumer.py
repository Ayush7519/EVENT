# import json

# from asgiref.sync import async_to_sync
# from channels.generic.websocket import AsyncWebsocketConsumer

# from notification.models import Notification


# class NotificationConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_name = "notification"
#         self.room_group_name = "notification_group"
#         # adding the channel in the static group.
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name,
#         )
#         await self.accept()

#     async def receive(self, text_data):
#         print("messsage form the clint...", text_data)

#     async def disconnect(self, close_code):
#         # Leave room group
#         self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name,
#         )

#     # sending the message to the websocket.
#     async def send_notification_message(self, event):
#         message = event["message"]
#         print(message)

#         # Send message to WebSocket
#         await self.send(
#             text_data=json.dumps(
#                 {
#                     "message": message,
#                 }
#             )
#         )


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
        print(message)

        try:
            # Fetch the most recent 20 notifications asynchronously
            recent_notifications = await self.get_recent_notifications()
            serialized_notifications = [
                {
                    "message": notification.message,
                }
                for notification in recent_notifications
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
