# import asyncio
# import json

# from asgiref.sync import async_to_sync
# from celery import Celery, shared_task, states
# from celery.exceptions import Ignore
# from channels.layers import get_channel_layer

# from .models import Notification


# @shared_task(bind=True)
# def boardcast_notification(self, data):
#     print(data)
#     # try:
#     notification = Notification.objects.get(id=int(data))
#     print(notification)
#     if len(notification) > 0:
#         notification.first()
#         channel_layer = get_channel_layer()

#         # print("--------------------------------")
#         # loop = asyncio.new_event_loop()
#         # print("--------------------------------")
#         # asyncio.set_event_loop(loop)
#         # print(notification.message)
#         # loop.run_until_complete(
#         #     channel_layer.group_send(
#         #         "notification_group",
#         #         {
#         #             "type": "send_notification_message",
#         #             "message": json.dumps(notification.message),
#         #         },
#         #     )
#         # )
#         # Sending notification asynchronously
#         async def send_notification():
#             await channel_layer.group_send(
#                 "notification_group",
#                 {
#                     "type": "send_notification_message",
#                     "message": json.dumps(notification.message),
#                 },
#             )
#             # Run the asynchronous function using async_to_sync

#         async_to_sync(send_notification)()

#         print("hello")
#         notification.sent = True
#         notification.save()
#         return "Done"
#     else:
#         self.update_state(
#             state="Fail",
#             meta={
#                 "exe": "Not Found",
#             },
#         )
#         raise Ignore()
#     # except:
#     #     self.update_state(
#     #         state="Fail",
#     #         meta={
#     #             "exe": "Not Found",
#     #         },
#     #     )
#     #     raise Ignore()

import json

from asgiref.sync import async_to_sync
from celery import shared_task
from celery.exceptions import Ignore
from channels.layers import get_channel_layer
from django.shortcuts import get_object_or_404

from .models import Notification


@shared_task(bind=True)
def boardcast_notification(self, data):
    print(data)
    try:
        notification = get_object_or_404(Notification, id=int(data))
        channel_layer = get_channel_layer()
        print(notification.message)

        # Sending notification asynchronously
        async def send_notification():
            await channel_layer.group_send(
                "notification_group",
                {
                    "type": "send_notification_message",
                    "message": json.dumps(notification.message),
                },
            )

        async_to_sync(send_notification)()

        print("hello")
        notification.sent = True
        notification.save()
        return "Done"
    except Notification.DoesNotExist:
        self.update_state(
            state="Fail",
            meta={
                "exe": "Not Found",
            },
        )
        raise Ignore()
