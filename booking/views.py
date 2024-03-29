import json
from collections import defaultdict
from datetime import datetime, timedelta

import requests
from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from account.models import User
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
        print(user.username)
        query = Ticket.objects.filter(booked_by=user.username).order_by(
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


# trying the khalti for the payment.
@permission_classes([permissions.IsAuthenticated])
@api_view(["POST"])
def initiate_payment(request):
    # taking out the input of the users.
    url = "https://a.khalti.com/api/v2/epayment/initiate/"
    quantity = int(request.data.get("quantity"))
    return_url = request.data.get("return_url")
    purchase_order_id = request.data.get("purchase_order_id")
    amount = request.data.get("amount")
    user = request.user

    # Retrieve event details
    try:
        event = Event.objects.get(id=purchase_order_id)
    except Event.DoesNotExist:
        return JsonResponse({"error": "Event not found"}, status=404)

    # Check if requested quantity exceeds available quantity
    if event.remaining_capacity < quantity:
        return JsonResponse({"error": "Requested quantity not available"}, status=400)

    modified_return_url = f"{return_url}{user.id}"
    print(modified_return_url)
    # khalti process.
    payload = json.dumps(
        {
            "return_url": modified_return_url,
            "website_url": "http://localhost:3000/page/1",
            "amount": amount,
            "purchase_order_id": purchase_order_id,
            "purchase_order_name": "test",
            # "user_id": request.user,
            # this my be dynamic when the front end is conected.
            "customer_info": {
                "name": "Ayush Kandel",
                "email": "ayushkandel7519@gmail.com",
                "phone": "9800000001",
            },
        }
    )
    headers = {
        "Authorization": "key 094f7156a6c24974b2cb573181689b33",
        # "Authorization": "key 2466a7e05cc84037ad881dfcd3ac6ba6",
        "Content-Type": "application/json",
    }
    print(headers)
    response = requests.request("POST", url, headers=headers, data=payload)
    # return Response(response)
    print("it is response ", response.text)
    new_response = json.loads(response.text)
    print("this is the response converted into the python form", new_response)

    if response.status_code == 200:
        new_response = json.loads(response.text)
        payment_url = new_response.get("payment_url")
        if payment_url:
            print(payment_url)
            # hello = "hello"
            # payment_url_with_data = f"{payment_url}?additional_data={hello}"
            # print(payment_url_with_data)
            return JsonResponse({"payment_url": payment_url, "quantity": quantity})
        else:
            return JsonResponse({"error": "Payment URL not found in response"})
    else:
        return JsonResponse(
            {"error": "Failed to initiate payment", "details": response.text},
            status=response.status_code,
        )


# now validating the khalti payment.
@permission_classes([permissions.IsAuthenticated])
@api_view(["GET"])
def VerifyPayment(request, user_id):
    # taking out the required data.
    url = "https://a.khalti.com/api/v2/epayment/lookup/"
    pidx = request.GET.get("pidx")
    event_id = request.GET.get("purchase_order_id")
    event_data = Event.objects.get(id=event_id)
    event_price = event_data.entry_fee
    event_remaining_capacity = event_data.remaining_capacity
    total_price = int(request.GET.get("amount"))
    price = total_price // 100
    quantity = int(total_price / 100) // event_price

    # defining the header.
    headers = {
        "Authorization": "key 094f7156a6c24974b2cb573181689b33",
        "Content-Type": "application/json",
    }

    # defining the payload.
    payload = json.dumps(
        {
            "pidx": pidx,
        }
    )
    response = requests.request("POST", url, headers=headers, data=payload)
    new_response = json.loads(response.text)

    # checking the status to work further.
    if new_response["status"] == "Completed":
        print("payment sufessful")
        user = User.objects.get(id=user_id)
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
        serializer = TicketCreateSerializer(
            data={
                "event": event_data.id,
                "quantity": quantity,
                "total_price": price,
            }
        )

        if serializer.is_valid(raise_exception=True):
            serializer.validated_data["booked_by"] = user.username
            serializer.validated_data["ticket_num"] = ticket_number
            qtn = serializer.validated_data["quantity"]

            # calculating and updating the remaining capacity.
            rm_ticket = event_remaining_capacity - qtn
            event_data.remaining_capacity = rm_ticket

            # updating the no of participant.
            event_data.no_of_participant = event_data.no_of_participant + qtn
            event_data.save()
            serializer.save()

            # now sending the ticket in the mail to the user.
            fdata = serializer.data
            merged_data = {
                "ticket": fdata,
                "event": event_data,
                "user": user.name,
            }
            # rendering the template in the api.
            # yo chai eswea ma connect garey si sucess response aayasi ballaw garna parxa.
            email_content = render_to_string("ticket.html", {"ticket": merged_data})
            data = {
                "subject": "Ticket Booking Confirmation",
                "body": "Your ticket booking has been successfully processed. Please find the ticket details attached.",
                "to_email": user.email,
                "html_message": email_content,
            }
            Util.send_email1(data)
            link = "http://localhost:3000/event"
            return redirect(link)
    else:
        return Response(
            "sorry your payment is not completed try again later",
            status=status.HTTP_400_BAD_REQUEST,
        )
