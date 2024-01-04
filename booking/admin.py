from django.contrib import admin

from .models import Ticket

# registring the ticket model in the admin pannel.
# Ticket


class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "ticket_id",
        "ticket_num",
        "booked_by",
        "event",
        "quantity",
        "total_price",
    )


admin.site.register(Ticket, TicketAdmin)
