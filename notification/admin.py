from django.contrib import admin

from .models import Notification

# Register your models here.


class Notification_Admin(admin.ModelAdmin):
    list_display = ["id", "event", "message", "created_at", "send_on", "sent"]


admin.site.register(Notification, Notification_Admin)
