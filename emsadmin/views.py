from datetime import datetime, timedelta

from rest_framework import generics, permissions, status
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from account.renders import UserRenderer
from ems.pagination import MyPageNumberPagination
from ems.permission import IsArtistUser

from .models import Artist, Event, Sponser
from .serializer import Event_Serializer, EventList_Serializer, Sponser_Serializer


# Sopnser
# Sponser Creating.
class SponserCreateApiView(generics.CreateAPIView):
    queryset = Sponser.objects.all()
    serializer_class = Sponser_Serializer
    renderer_classes = [UserRenderer]


# Sponser Listing.
class SponserListApiView(generics.ListAPIView):
    queryset = Sponser.objects.all()
    serializer_class = Sponser_Serializer
    pagination_class = MyPageNumberPagination


# Sponser search.
class SponserSearchApiView(generics.ListAPIView):
    queryset = Sponser.objects.all()
    serializer_class = Sponser_Serializer
    filter_backends = [SearchFilter]
    search_fields = [
        "name",
        "sponser_type",
    ]
    pagination_class = MyPageNumberPagination


# Sponser update.
class SponserUpdateApiView(generics.UpdateAPIView):
    queryset = Sponser.objects.all()
    serializer_class = Sponser_Serializer
    renderer_classes = [UserRenderer]


# Sponser delete.
class SponserDeleteApiView(generics.DestroyAPIView):
    queryset = Sponser.objects.all()
    serializer_class = Sponser_Serializer
    renderer_classes = [UserRenderer]


# Event
# Event Create.
class EventCreateApiView(generics.CreateAPIView):
    renderer_classes = [UserRenderer]

    def post(self, request, *args, **kwargs):
        serializer = Event_Serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            artist_value = serializer.validated_data["artist"]
            capacity = serializer.validated_data["capacity"]
            serializer.validated_data["remaining_capacity"] = capacity
            print(artist_value)
            for art_data in artist_value:
                print(art_data)
                try:
                    data = Artist.objects.get(user_id=art_data.user_id)
                    data.is_available = False
                    data.save()
                except Event.DoesNotExist:
                    return Response(
                        {
                            "msg": "The Artist you have selected is not prestnt in our database"
                        },
                        status=status.HTTP_404_NOT_FOUND,
                    )
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )


# Event Complete.
class EventCompleteApiView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, event_id, *args, **kwargs):
        print(event_id)
        try:
            event_info = Event.objects.get(id=event_id)
            print(event_info)
            artists_ids = [artist.id for artist in event_info.artist.all()]

        except Event.DoesNotExist:
            return Response(
                {"msg": "Event Doesnot Exists"},
                status=status.HTTP_404_NOT_FOUND,
            )

        for art_id in artists_ids:
            # print(art_id)
            try:
                artist_info = Artist.objects.get(id=art_id)
                current_date = datetime.now()
                artist_data = Event.objects.filter(
                    artist=artist_info,
                    date__gt=current_date,
                ).exists()
                if artist_data:
                    artist_info.is_available = False
                else:
                    artist_info.is_available = True
                artist_info.save()

            except Artist.DoesNotExist:
                return Response(
                    {"msg": "Artist Not Found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

        event_info.event_completed = True
        event_info.save()

        return Response(
            {"msg": "Operation Sucessfully Completed."},
            status=status.HTTP_200_OK,
        )


# Event List.(for the admin site.)
class EventListApiView(generics.ListAPIView):
    queryset = Event.objects.all().order_by("-date", "-time")
    serializer_class = EventList_Serializer
    pagination_class = MyPageNumberPagination
    renderer_classes = [UserRenderer]


# Event list for the user to show.
class EventListUserApiView(generics.ListAPIView):
    serializer_class = EventList_Serializer
    renderer_classes = [UserRenderer]

    def get_queryset(self):
        return Event.objects.filter(event_completed=False)


# Event Search.
# this is for the front end user so they can search the event based on their desire.
class EventSearchApiView(generics.ListAPIView):
    queryset = Event.objects.all().order_by("-date", "-time")
    serializer_class = EventList_Serializer
    filter_backends = [SearchFilter]
    search_fields = [
        "event_name",
        "date",
        "time",
        "artist__user__name",
        "artist__user__username",
        "location",
    ]
    pagination_class = MyPageNumberPagination


# Event Delete.
class EventDeleteApiView(APIView):
    renderer_classes = [UserRenderer]

    def delete(self, request, pk, *args, **kwargs):
        try:
            event_info = Event.objects.get(id=pk)
            artists_ids = [artist.id for artist in event_info.artist.all()]

        except Event.DoesNotExist:
            return Response(
                {"msg": "Event data is not available in the database"},
                status=status.HTTP_404_NOT_FOUND,
            )

        for art_id in artists_ids:
            print(art_id)
            try:
                artist_info = Artist.objects.get(id=art_id)
                artist_info.is_available = True
                artist_info.save()

            except Artist.DoesNotExist:
                return Response(
                    {"msg": "Artist is not available."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        event_info.delete()
        return Response(
            {"msg": "Data has been sucessfully deleted."},
            status=status.HTTP_204_NO_CONTENT,
        )


# event update view.
class EventUpdateApiView(generics.UpdateAPIView):
    queryset = Event.objects.all()
    serializer_class = Event_Serializer
    renderer_classes = [UserRenderer]


# event data based on today ad upcomming.
class EventOptionApiView(APIView, PageNumberPagination):
    renderer_classes = [UserRenderer]
    page_size = 20

    def get(self, request, choice, *args, **kwargs):
        current_date = datetime.now()
        next_day_current_date = current_date + timedelta(days=1)
        if choice == "today":
            event_info = Event.objects.filter(date=current_date)
            print(event_info)
            if event_info.exists():
                page_result = self.paginate_queryset(
                    event_info,
                    request,
                    view=self,
                )
                serializer = EventList_Serializer(page_result, many=True)
                return self.get_paginated_response(serializer.data)

            else:
                return Response(
                    {"msg": "Oops we doesnot have any events today!!!!"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        elif choice == "upcome":
            event_nxt_day = Event.objects.filter(date__gt=current_date)
            print(event_nxt_day)
            if event_nxt_day.exists():
                page_result = self.paginate_queryset(
                    event_nxt_day,
                    request,
                    view=self,
                )
                nxt_serializer = EventList_Serializer(page_result, many=True)
                return self.get_paginated_response(nxt_serializer.data)
            else:
                return Response(
                    {"msg": "Oops we doesnot have any events in upcomming days !!!!"},
                    status=status.HTTP_404_NOT_FOUND,
                )

        else:
            return Response("oops you entered the wrong data")


# login user(artist) event details view for the dashboard.
class LoginArtistEventDetailsApiView(generics.ListAPIView):
    serializer_class = EventList_Serializer
    permission_classes = [IsArtistUser]

    def get_queryset(self):
        name = self.kwargs["name"]
        user = self.request.user
        user_artist = user.artist.id
        current_date = datetime.now()
        next_day_current_date = current_date + timedelta(days=1)
        print(user_artist)
        if name == "All":
            return Event.objects.filter(artist=user_artist)
        elif name == "Complete":
            return Event.objects.filter(
                artist=user_artist,
                event_completed=True,
            )
        elif name == "Pending":
            return Event.objects.filter(
                artist=user_artist,
                event_completed=False,
            )
        elif name == "Today":
            return Event.objects.filter(
                artist=user_artist,
                date=current_date,
            )
        elif name == "Tomorrow":
            return Event.objects.filter(
                artist=user_artist,
                date=next_day_current_date,
            )
        elif name == "Upcome":
            return Event.objects.filter(
                artist=user_artist,
                date__gt=next_day_current_date,
            ).order_by("date")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset.exists():
            serializer = self.get_serializer(queryset, many=True)
            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"msg": "Oops! Now Data Found.!!!"},
                status=status.HTTP_404_NOT_FOUND,
            )


from django.http import HttpResponse

from .tasks import test_function

# def test(request):
#     test_function.delay()
#     return HttpResponse("Done")
