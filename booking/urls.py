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
        # name="path to get the list of ticket booked by the normal user in their profile.",
        name="user_booked_ticket",
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
    path(
        "payment/verification/<int:user_id>/",
        views.VerifyPayment,
        name="payment verification",
    ),
    # path("tests/", views.session_data, name="session_data"),
    # path("session/", views.sessio),
]
