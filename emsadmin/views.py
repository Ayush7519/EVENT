import logging
from collections import Counter
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from account.models import Artist, User
from account.renders import UserRenderer
from account.utils import Util
from booking.models import Ticket
from ems.pagination import MyPageNumberPagination
from ems.permission import IsArtistUser
from notification.models import Notification

from .models import Artist, Event, Sponser
from .serializer import (
    Event_Serializer,
    EventList1_Serializer,
    EventList_Serializer,
    EventListT_Serializer,
    EventRequest_Serializer,
    RecommendedEvent_Serializer,
    Sponser_Serializer,
)


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
            user = request.user
            artist_value = serializer.validated_data["artist"]
            capacity = serializer.validated_data["capacity"]
            serializer.validated_data["remaining_capacity"] = capacity
            for art_data in artist_value:
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

                if user.is_admin == True:
                    serializer.validated_data["status"] = "Accept"
                    serializer.save()
                else:
                    serializer.validated_data["status"] = "Request"
                    # taking out the emails of the admins.
                    user_amin = User.objects.filter(is_admin=True)
                    for users in user_amin:
                        to_email = users.email
                        data = {
                            "subject": "New Event Request!!!",
                            "body": "New Event request is send the the artist. Please check it to accept the request",
                            "to_email": to_email,
                        }
                        Util.send_email(data)
                    serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )


# # Event Complete.
# class EventCompleteApiView(APIView):
#     renderer_classes = [UserRenderer]
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request, event_id, *args, **kwargs):
#         print(event_id)
#         try:
#             event_info = Event.objects.get(id=event_id)
#             print(event_info)
#             artists_ids = [artist.id for artist in event_info.artist.all()]

#         except Event.DoesNotExist:
#             return Response(
#                 {"msg": "Event Doesnot Exists"},
#                 status=status.HTTP_404_NOT_FOUND,
#             )

#         for art_id in artists_ids:
#             # print(art_id)
#             try:
#                 artist_info = Artist.objects.get(id=art_id)
#                 current_date = datetime.now()
#                 artist_data = Event.objects.filter(
#                     artist=artist_info,
#                     date__gt=current_date,
#                 ).exists()
#                 if artist_data:
#                     artist_info.is_available = False
#                 else:
#                     artist_info.is_available = True
#                 artist_info.save()

#             except Artist.DoesNotExist:
#                 return Response(
#                     {"msg": "Artist Not Found"},
#                     status=status.HTTP_404_NOT_FOUND,
#                 )

#         event_info.event_completed = True
#         event_info.save()

#         return Response(
#             {"msg": "Operation Sucessfully Completed."},
#             status=status.HTTP_200_OK,
#         )


# Event List.(for the admin site.)
class EventListApiView(generics.ListAPIView):
    queryset = Event.objects.all().order_by("-date", "-time")
    serializer_class = EventList_Serializer
    pagination_class = MyPageNumberPagination
    renderer_classes = [UserRenderer]


# Event list for the user to show.
class EventListUserApiView(generics.ListAPIView):
    serializer_class = EventListT_Serializer
    renderer_classes = [UserRenderer]
    pagination_class = MyPageNumberPagination

    def get_queryset(self):
        return Event.objects.filter(event_completed=False, status="Accept")


# Event detail view for the frontend.
class EventDetailApiiView(generics.ListAPIView):
    serializer_class = EventList1_Serializer
    renderer_classes = [UserRenderer]

    def get_queryset(self):
        event_id = self.kwargs["pk"]
        try:
            event_data = Event.objects.get(id=event_id)
            print(event_data)
            return Event.objects.filter(id=event_id)
        except Event.DoesNotExist:
            return Event.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if queryset.exists():
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"msg": f"Event with id {self.kwargs['pk']} is not available!"},
                status=status.HTTP_404_NOT_FOUND,
            )


# Event Search.
# this is for the front end user so they can search the event based on their desire.
class EventSearchApiView(generics.ListAPIView):
    queryset = Event.objects.all().order_by("-id")
    serializer_class = EventList_Serializer
    filter_backends = [SearchFilter]
    search_fields = [
        "event_name",
        # "date",
        # "time",
        "artist__user__name",
        "artist__user__username",
        # "location",
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
        if name == "all":
            return Event.objects.filter(artist=user_artist).order_by("-date")
        elif name == "complete":
            return Event.objects.filter(
                artist=user_artist,
                event_completed=True,
            )
        elif name == "pending":
            return Event.objects.filter(
                artist=user_artist,
                event_completed=False,
            ).order_by("-date")
        elif name == "today":
            return Event.objects.filter(
                artist=user_artist,
                date=current_date,
            ).order_by("-date")
        elif name == "tomorrow":
            return Event.objects.filter(
                artist=user_artist,
                date=next_day_current_date,
            ).order_by("-date")
        elif name == "upcome":
            return Event.objects.filter(
                artist=user_artist,
                date__gt=next_day_current_date,
            ).order_by("-date")

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


# event request for the admin.
class EventRequestApiView(generics.ListAPIView):
    renderer_classes = [UserRenderer]
    permission_classes = [permissions.IsAdminUser]
    serializer_class = EventRequest_Serializer

    def get_queryset(self):
        return Event.objects.filter(status="Request")

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
                {"msg": "No evetns at the request"},
                status=status.HTTP_404_NOT_FOUND,
            )


# accept and decline view.
class EventAcceptAndDeclineApiView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, id, request_type, *args, **kwargs):
        try:
            event_data = Event.objects.get(id=id)
        except Event.DoesNotExist:
            return Response(
                {"msg": f"The event with the id {id} doesnt exists"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request_type == "accept":
            event_data.status = "Accept"
            for artist in event_data.artist.all():
                data = {
                    "subject": "Event Request Accepted",
                    "body": "Congratulations! Your event has been accepted on our website. We look forward to your continued engagement with our platform.",
                    "to_email": artist.user.email,
                }
                Util.send_email(data)
                event_data.save()
        elif request_type == "decline":
            for artist in event_data.artist.all():
                data = {
                    "subject": "Event Request Rejected",
                    "body": "We regret to inform you that your event request has been rejected on our website. We encourage you to review our guidelines and consider reapplying in the future.",
                    "to_email": artist.user.email,
                }
                Util.send_email(data)
                event_data.delete()

        return Response(
            {"msg": "Operation is sucessfully done"},
            status=status.HTTP_200_OK,
        )


# event recommendation system view.
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def recommendation(request):
    print("from the notification")

    # helper function for the recommendation system.
    def get_title_from_id(index):
        return df[df.index == index]["id"].iloc[0]

    def get_id_from_genres(genres):
        # for genre in genres:
        return df[df.genres == genres]["id"].index[0]

    # read the csv file.
    df = pd.read_csv("mycsv.csv")

    # defining the feature for the RE.(like the colums.)
    features = ["genres", "event_name"]

    # this will remove the nan value and put blank value in that place.
    for feature in features:
        df[feature] = df[feature].fillna(" ")

    # now we have to combine the features.
    def combine_feature(row):
        try:
            return row["genres"]
        except:
            print("error", row)

    # this method help to apply the above mtheod in all the data.
    df["combined_feature"] = df.apply(combine_feature, axis=1)

    # making the count matrix form the data.
    cv = CountVectorizer()
    count_matrix = cv.fit_transform(df["combined_feature"])

    # computing the cosine similarities from the count matrix.
    cosine_sim = cosine_similarity(count_matrix)

    # getting the data of the login user in the site.
    most_common_value = None
    user_genre_list = []
    user = request.user
    user_ticket_data = Ticket.objects.filter(booked_by=user)
    for details in user_ticket_data:
        event_info = details.event
        if event_info.genres is not None:
            user_genre_list.append(event_info.genres)
            counter = Counter(user_genre_list)
            most_common_value = counter.most_common(1)[0][0]
    # checking if there is recommendation event or not.
    if most_common_value is None:
        return Response(
            {"message": "user hasnot booked any event so no recommend event!!!"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # user_booked_ticket_genres=['Melody']
    user_booked_ticket_genres = most_common_value

    # getting the index of the movie from the title.
    movie_index = get_id_from_genres(user_booked_ticket_genres)
    similar_event = list(enumerate(cosine_sim[movie_index]))

    # now sorting the data in descending order.lambda show the second value for the list of the data.
    sorted_event_list = sorted(similar_event, key=lambda x: x[0], reverse=True)
    # print(sorted_event_list)

    # serializating the data.
    i = 1
    serializer_data = []
    for event in sorted_event_list:
        event_id = get_title_from_id(event[0])
        event_data = Event.objects.get(id=event_id)
        serializer = RecommendedEvent_Serializer(event_data)
        serializer_data.append(serializer.data)
        print(serializer_data)
        i = i + 1
        if i > 4:
            break
    return Response(
        serializer_data,
        status=status.HTTP_200_OK,
    )
