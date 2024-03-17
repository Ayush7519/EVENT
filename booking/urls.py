from django.urls import path

from . import views

urlpatterns = [
    path(
        "ticket/booking/<int:event_id>/",
        views.TicketCreateApiView.as_view(),
        name="ticket booking path",
    ),
    path(
        "user/booked/ticket/",
        views.UserBookedTicketApiView.as_view(),
        name="path to get the list of ticket booked by the normal user in their profile.",
    ),
    path(
        "grpah/",
        views.GraphAPI.as_view(),
        name="path to see the graph of the login user",
    ),
    path(
        "payments/",
        views.initiate_payment,
        name="payment",
    ),
]
