from collections import defaultdict
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from account.renders import UserRenderer
from account.utils import Util
from booking.serializer import TicketCreateSerializer, UserBookedTicket_Serializer
from ems.permission import IsArtistUser
from emsadmin.models import Artist

from .models import Event, Ticket

# Create your views here.


# creating the view for the ticket api.
class TicketCreateApiView(generics.CreateAPIView):
    renderer_classes = [UserRenderer]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, event_id, *args, **kwargs):
        try:
            event_data = Event.objects.get(id=event_id)

            rcp = event_data.remaining_capacity
        except Event.DoesNotExist:
            return Response(
                {"msg": f"Oops we dont have any event with this id: {event_id}"},
                status=status.HTTP_404_NOT_FOUND,
            )
        current_date_time = datetime.now()
        # converting the datetime into str.
        timestamp_str = current_date_time.strftime("%Y-%m-%d %H:%M:%S.%f")
        # removing the - : from the data.
        formatted_timestamp = (
            timestamp_str.replace("-", "")
            .replace(":", "")
            .replace(".", "")
            .replace(" ", "")
        )
        # making the ticket number.
        ticket_number = "TKT" + str(formatted_timestamp)
        serializer = TicketCreateSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.validated_data["booked_by"] = request.user
            serializer.validated_data["ticket_num"] = ticket_number
            qtn = serializer.validated_data["quantity"]
            # calculating the remaining capacity.
            if qtn > rcp:
                return Response(
                    {"msg": f"Sorry {qtn} tickets are not available...!!!"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            else:
                rm_ticket = rcp - qtn
                print(rm_ticket)
                event_data.remaining_capacity = rm_ticket
                event_data.save()
            # FROM THIS WE HAVE TO ADD THE ESEWA PAYMENT.

            serializer.save()
            # this should be done after the payment is sucessfully done.
            event_data.no_of_participant = event_data.no_of_participant + qtn
            event_data.save()
            user = request.user
            # data for the front-end
            fdata = serializer.data
            user_name = request.user
            merged_data = {
                "ticket": fdata,
                "event": event_data,
                "user": user_name,
            }

            # rendering the template in the api.
            # yo chai eswea ma connect garey si sucess response aayasi ballaw garna parxa.
            email_content = render_to_string("ticket.html", {"ticket": merged_data})
            data = {
                "subject": "Your Ticket Booking Have Been Sucesfully Booked",
                "body": "Please find the ticket as an attachment.",
                "to_email": user.email,
                "html_message": email_content,
            }
            Util.send_email1(data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )


# login (normal)user profile part for the history of the ticket booking.
class UserBookedTicketApiView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserBookedTicket_Serializer

    def get_queryset(self):
        user = self.request.user
        query = Ticket.objects.filter(booked_by=user).order_by(
            "-ticket_id"
        )  # here time and date is needed.
        return query

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
                {"msg": "Oops! You Have Not Booked Any Event...!!!"},
                status=status.HTTP_404_NOT_FOUND,
            )


# Graph creating for the login artist.
class GraphAPI(APIView):
    permission_classes = [IsArtistUser]

    def get(self, request):
        us = self.request.user.id
        try:
            artuser = Artist.objects.get(user_id=us)
        except Artist.DoesNotExist:
            return Response(
                {"msg": f"Oops no artist is available in our database with id {us}"},
                status=status.HTTP_404_NOT_FOUND,
            )

        today = datetime.now().date()
        monthly_participants = defaultdict(
            int
        )  # Dictionary to store aggregated data for all months

        for i in range(12):
            end_day = today - relativedelta(months=i)
            onemonth = end_day - timedelta(days=30)

            artist_one_month_data = Event.objects.filter(
                artist=artuser,
                date__gt=onemonth,
                date__lte=end_day,
            )

            for event in artist_one_month_data:
                month_year = event.date.strftime("%B %Y")
                monthly_participants[month_year] += event.no_of_participant

        # Extract labels and values from the aggregated data
        labels = list(monthly_participants.keys())
        values = list(monthly_participants.values())

        # Sort labels and values based on date
        sorted_indices = sorted(
            range(len(labels)),
            key=lambda i: datetime.strptime(labels[i], "%B %Y"),
        )
        sorted_labels = [labels[i] for i in sorted_indices]
        sorted_values = [values[i] for i in sorted_indices]

        data_list = [{"labels": sorted_labels, "values": sorted_values}]

        return Response(data_list)


import json

# trying the khalti for the payment.
import requests
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework.decorators import api_view, permission_classes


@api_view(["POST"])
def initiate_payment(request):
    url = "https://a.khalti.com/api/v2/epayment/initiate/"
    return_url = request.data.get("return_url")
    print(return_url)
    purchase_order_id = request.data.get("purchase_order_id")
    print(purchase_order_id)
    amount = request.data.get("amount")
    print(amount)
    payload = json.dumps(
        {
            "return_url": return_url,
            "website_url": "http://localhost:3000/page/1",
            "amount": amount,
            "purchase_order_id": purchase_order_id,
            "purchase_order_name": "test",
            # this my be dynamic when the front end is conected.
            "customer_info": {
                "name": "Ayush Kandel",
                "email": "ayushkandel7519@gmail.com",
                "phone": "9800000001",
            },
        }
    )
    headers = {
        "Authorization": "key 77e1305ba1704cd49000f502eb653960",
        "Content-Type": "application/json",
    }
    print(headers)
    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
    new_response = json.loads(response.text)
    print("this is the response converted into the python form", new_response)
    # return Response(response.text)

    # if response.status_code == 200:
    #     new_response = json.loads(response.text)
    #     payment_url = new_response.get("payment_url")
    #     if payment_url:
    #         print(payment_url)
    #         return HttpResponseRedirect(redirect_to=payment_url)
    #     else:
    #         return JsonResponse({"error": "Payment URL not found in response"})
    # else:
    #     return JsonResponse(
    #         {"error": "Failed to initiate payment", "details": response.text},
    #         status=response.status_code,
    #     )
    if response.status_code == 200:
        new_response = json.loads(response.text)
        payment_url = new_response.get("payment_url")
        if payment_url:
            print(payment_url)
            return JsonResponse({"payment_url": payment_url})
        else:
            return JsonResponse({"error": "Payment URL not found in response"})
    else:
        return JsonResponse(
            {"error": "Failed to initiate payment", "details": response.text},
            status=response.status_code,
        )
