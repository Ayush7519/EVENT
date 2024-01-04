from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from account.renders import UserRenderer
from ems.pagination import MyPageNumberPagination

from .models import Content_Management, Heading
from .serializer import (
    Content_ManagementListSerializer,
    Content_ManagementSerializer,
    HeadingSerializer,
)


# heading
# heading created.
class HeadingCreateApiView(generics.CreateAPIView):
    renderer_classes = [UserRenderer]
    queryset = Heading.objects.all()
    serializer_class = HeadingSerializer


# heading list.
class HeadingListApiView(generics.ListAPIView):
    renderer_classes = [UserRenderer]
    queryset = Heading.objects.all()
    serializer_class = HeadingSerializer


# content_management
# content_management creating.
class Content_ManagementCreateApiView(APIView):
    permission_classes = [permissions.IsAdminUser]
    renderer_classes = [UserRenderer]

    def post(self, request, *args, **kwargs):
        serializer = Content_ManagementSerializer(data=request.data)
        if serializer.is_valid():
            # to update the model fields data after the serializer this methods is used.
            serializer.validated_data["updated_by"] = request.user.name
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# content-management list with search.
class Content_ManagementSearchApiView(generics.ListAPIView):
    queryset = Content_Management.objects.all()
    serializer_class = Content_ManagementSerializer
    filter_backends = [SearchFilter]
    search_fields = ["heading"]
    pagination_class = MyPageNumberPagination
    permission_classes = [permissions.IsAdminUser]


# content-management draft list only.
class Content_ManagementStatusListApiView(APIView, PageNumberPagination):
    permission_classes = [permissions.IsAdminUser]
    page_size = 10

    def get(self, request, status, format=None, *args, **kwargs):
        if status == "Draft" or status == "Publish":
            queryset = Content_Management.objects.filter(status=status)
            results = self.paginate_queryset(queryset, request, view=self)
            serializer = Content_ManagementSerializer(results, many=True)
            return self.get_paginated_response(serializer.data)

        elif status == "All":
            queryset = Content_Management.objects.all()
            results = self.paginate_queryset(queryset, request, view=self)
            serializer = Content_ManagementSerializer(results, many=True)
            return self.get_paginated_response(serializer.data)

        else:
            return Response(
                {"msg": "Check your status.That doesn't match our status"}
            )


# content-management update.
class Content_managementUpdateApiView(generics.UpdateAPIView):
    queryset = Content_Management.objects.all()
    serializer_class = Content_ManagementSerializer
    permission_classes = [permissions.IsAdminUser]
    renderer_classes = [UserRenderer]


# content-management delete.
class Content_ManagementDeleteApiView(generics.DestroyAPIView):
    queryset = Content_Management.objects.all()
    serializer_class = Content_ManagementSerializer
    permission_classes = [permissions.IsAdminUser]
    renderer_classes = [UserRenderer]


# this for making the dynamic webpage.
# content-management for the front end user.
class Contetn_Manageent_ButtonListApiView(APIView):
    renderer_classes = [UserRenderer]

    def get(self, request, pk, *args, **kwargs):
        print(pk)
        try:
            heading_info = Heading.objects.get(id=pk)
            print(heading_info)
        except Heading.DoesNotExist:
            return Response(
                {"msg": "Searched Heading is not available"},
                status=status.HTTP_404_NOT_FOUND,
            )
        cms_info = Content_Management.objects.filter(heading=heading_info)
        print(cms_info)
        serializer = Content_ManagementListSerializer(cms_info, many=True)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
