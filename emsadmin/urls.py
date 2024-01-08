from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from emsadmin import views

urlpatterns = [
    path(
        "sponser/create/",
        views.SponserCreateApiView.as_view(),
        name="sponser create path",
    ),
    path(
        "sponser/list/",
        views.SponserListApiView.as_view(),
        name="sponser details list path",
    ),
    path(
        "sponser/search/",
        views.SponserSearchApiView.as_view(),
        name="sponser search path",
    ),
    path(
        "sponser/update/<int:pk>/",
        views.SponserUpdateApiView.as_view(),
        name="sponser update path",
    ),
    path(
        "sponser/delete/<int:pk>/",
        views.SponserDeleteApiView.as_view(),
        name="sponser delete path",
    ),
    # EVENT.
    path(
        "event/create/",
        views.EventCreateApiView.as_view(),
        name="event creating path",
    ),
    path(
        "event/complete/<int:event_id>/",
        views.EventCompleteApiView.as_view(),
        name="event complete path to change the event data automatically",
    ),
    path(
        "event/list/",
        views.EventListApiView.as_view(),
        name="event details list path",
    ),
    path(
        "event/update/<int:pk>/",
        views.EventUpdateApiView.as_view(),
        name="event update path,",
    ),
    path(
        "event/delete/<int:pk>/",
        views.EventDeleteApiView.as_view(),
        name="event delete path",
    ),
    path(
        "event/search/",
        views.EventSearchApiView.as_view(),
        name="event search path",
    ),
    path(
        "event/choice/<str:choice>/",
        views.EventOptionApiView.as_view(),
        name="yesma chai aaja ko rw aaja paxi ko event ko list matrw aauxa",
    ),
    path(
        "login/artist/event/detail/<str:name>/",
        views.LoginArtistEventDetailsApiView.as_view(),
        name="login artist event detail view path",
    ),
    path("test/", views.test, name="testing"),
]
