from django.urls import path

from . import consumer, views

urlpatterns = [
    path("test/", views.test),
]
