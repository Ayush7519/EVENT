from django.contrib import admin

from .models import Event, Sponser


# Sponser model register in the admin.
class SponserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "sponser_type",
        "name",
        "photo",
        "amount",
    )


admin.site.register(Sponser, SponserAdmin)


# Event model register in the admin.
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "photo",
        "event_name",
        "genres",
        "date",
        "time",
        # "artist",
        "location",
        "capacity",
        "remaining_capacity",
        "entry_fee",
        # "sponser",
        "event_completed",
        "no_of_participant",
    )


admin.site.register(Event, EventAdmin)
