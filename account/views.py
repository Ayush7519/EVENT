from django.contrib.auth import authenticate
from django.shortcuts import render
from django.utils.encoding import DjangoUnicodeDecodeError, force_bytes, smart_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import generics, permissions, status
from rest_framework.filters import SearchFilter

# from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from account.renders import UserRenderer
from ems.pagination import MyPageNumberPagination

from .models import Artist, Managers, NormalUser, User
from .serializer import Artist_Serializer  # UserDetail_Serializer,
from .serializer import (
    Alluserdelete_Serializer,
    AllUserList_Serializer,
    Artist_Serializer_Full_Details,
    ArtistLoginProfileFull_Serializer,
    Managers_Serializer,
    Managers_Serializer_Full_Detals,
    NormalUser_Serializer,
    NormalUser_Serializer_Full_Detals,
    NormalUserLoginProfileFull_Serializer,
    SendPasswordEmail_Serializer,
    UserLogin_Serializer,
    UserLoginProfileFull_Serializer,
    UserPasswordChange_Serializer,
    UserPasswordReset_Serializer,
    UserProfile_Serializer,
    UserProfileUpdate_Serializer,
    UserRegistration_Serializer,
)
from .utils import Util


# generating the token for the user.
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


# user registration view.
class UserRegistrationView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserRegistration_Serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            # extracting the id of the registred user.
            uid = user.id
            # email sending after the user is registred and saved.
            data = {
                "subject": "Django Email",
                "body": user.name
                + " "
                + "You have been successfully registred in our Site !!!",
                "to_email": user.email,
            }
            Util.send_email(data)
            token = get_tokens_for_user(user)  # for the token...
            return Response(
                {
                    "token": token,
                    "msg": "Registration Successful",
                    "uid": uid,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# user login view.
class UserLoginView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserLogin_Serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.data.get("email")
            password = serializer.data.get("password")
            user = authenticate(email=email, password=password)
            print(user)
            if user is not None:
                user_type = user.is_admin
                user_artist = user.is_artist
                user_nrmuser = user.is_user
                token = get_tokens_for_user(user)
                return Response(
                    {
                        "token": token,
                        "user_is_admin": user_type,
                        "artist": user_artist,
                        "nrmuser": user_nrmuser,
                        "msg": "Login Successfully",
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"msg": "Email or Password is not valide"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# login user profile view.
class UserProfileView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        serializer = UserProfile_Serializer(request.user)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


# login user full profile update view.
class UserLoginProfileFullUpdateView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, name, *args, **kwargs):
        if name == "artist":
            user = self.request.user
            user_id = user.id
            user_artist_id = user.artist.id
            try:
                user_info = User.objects.get(id=user_id)
                user_artist_info = Artist.objects.get(id=user_artist_id)
            except (User.DoesNotExist, Artist.DoesNotExist):
                return Response(
                    {"msg": "Login User Data Not Found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # now serialixing and valaditing the data for the both models.
            user_serializer_class = UserLoginProfileFull_Serializer(
                user_info,
                data=request.data,
                partial=True,
            )
            artist_serializer_class = ArtistLoginProfileFull_Serializer(
                user_artist_info,
                data=request.data,
                partial=True,
            )
            if user_serializer_class.is_valid(
                raise_exception=True
            ) and artist_serializer_class.is_valid(raise_exception=True):
                user_serializer_class.save()
                artist_serializer_class.save()
                return Response(
                    {"msg": "Data Has Been Sucessfully Updated."},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"msg": "Validation error."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        elif name == "user":
            user = self.request.user
            user_id = user.id
            user_nrmuser_id = user.normaluser.id
            try:
                user_info = User.objects.get(id=user_id)
                user_nrmuser_info = NormalUser.objects.get(id=user_nrmuser_id)
            except (User.DoesNotExist, NormalUser.DoesNotExist):
                return Response(
                    {"msg": "Login User Data Not Found."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            # now serialixing and valaditing the data for the both models.
            user_serializer_class = UserLoginProfileFull_Serializer(
                user_info,
                data=request.data,
                partial=True,
            )
            normaluser_serializer_class = NormalUserLoginProfileFull_Serializer(
                user_nrmuser_info,
                data=request.data,
                partial=True,
            )
            if user_serializer_class.is_valid(
                raise_exception=True
            ) and normaluser_serializer_class.is_valid(raise_exception=True):
                user_serializer_class.save()
                normaluser_serializer_class.save()
                return Response(
                    {"msg": "Data Has Been Sucessfully Updated."},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"msg": "Validation error."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"msg": "Invalid user type!!!"},
                status=status.HTTP_404_NOT_FOUND,
            )


# user password change view.
class UserPasswordChangeView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        serializer = UserPasswordChange_Serializer(
            data=request.data, context={"user": request.user}
        )
        if serializer.is_valid(raise_exception=True):
            return Response(
                {"msg": "Password changed Sucessfully"},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# sending the email to the user to change the password.
class SendPassowrdEmailView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = SendPasswordEmail_Serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response(
                {"msg": "Passwoed Reset link send. Please check your Email"},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# user password change view through the mail.
class UserPasswordResetView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, uid, token, format=None):
        serializer = UserPasswordReset_Serializer(
            data=request.data, context={"uid": uid, "token": token}
        )
        if serializer.is_valid(raise_exception=True):
            return Response({"msg": "Password Reset Sucessfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# email button.
class EmailButton_View(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, pk, fromat=None):
        try:
            artist_info = Artist.objects.get(id=pk)
            em = artist_info.user.email
            uid = urlsafe_base64_encode(force_bytes(pk))
            print(em)
            link = "http://127.0.0.1:3000/event/request/" + uid
            body = "mail form the AB Event..." + link
            data = {
                "subject": "Mail from the AB Events",
                "body": body,
                "to_email": em,
            }
            Util.send_email(data)
        except Artist.DoesNotExist:
            return Response(
                {"msg": "The Artist is not present."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {"msg": "E-mail has been sucessfully send."},
            status=status.HTTP_200_OK,
        )


# USERS
# all user data from the database.
class AllUserListApiView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = AllUserList_Serializer
    pagination_class = MyPageNumberPagination
    permission_classes = [permissions.IsAdminUser]


# searching the user from the database.
class AllUserSearchApiView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = AllUserList_Serializer
    filter_backends = [SearchFilter]
    search_fields = [
        "name",
        "username",
        # can add the user id in the search field if necessary.
        # "id",
        # "email",
    ]
    pagination_class = MyPageNumberPagination
    # renderer_classes = [UserRenderer]


# updating the data of the user from the admin pannel.
class AllUserUpdateApiView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = Alluserdelete_Serializer
    permission_classes = [permissions.IsAdminUser]
    renderer_classes = [UserRenderer]


# deleting the data of the user from the admin pannel.
class AllUserDeleteApiView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = Alluserdelete_Serializer
    permission_classes = [permissions.IsAdminUser]
    renderer_classes = [UserRenderer]


# Artist
# artist creating.
class ArtistCreateApiView(generics.CreateAPIView):
    renderer_classes = [UserRenderer]

    def post(self, request, *args, **kwargs):
        serializer = Artist_Serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            ward_data = serializer.validated_data["ward"]
            if ward_data <= 0:
                return Response(
                    {"msg": "ward value cannot be 0 or less than 0"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )


# artist list.
class ArtistListApiView(generics.ListAPIView):
    queryset = Artist.objects.all()
    serializer_class = Artist_Serializer_Full_Details
    pagination_class = MyPageNumberPagination
    permission_classes = [permissions.IsAuthenticated]


# artist search.
class ArtistSearchApiViews(generics.ListAPIView):
    queryset = Artist.objects.all()
    serializer_class = Artist_Serializer_Full_Details
    filter_backends = [SearchFilter]
    search_fields = [
        "user__name",
        "user__username",
    ]  # relation ma aako field lai search field ma hanlna lai chai yestari garna parxa.
    pagination_class = MyPageNumberPagination
    permission_classes = [permissions.IsAuthenticated]


# artist update.
class ArtistUpdateView(generics.UpdateAPIView):
    queryset = Artist.objects.all()
    serializer_class = Artist_Serializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [UserRenderer]


# artist delete.
class ArtistDeleteView(generics.DestroyAPIView):
    queryset = Artist.objects.all()
    serializer_class = Artist_Serializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [UserRenderer]


# NORMAL USER
# normal user create.
class NormalUserCreateApiView(generics.CreateAPIView):
    renderer_classes = [UserRenderer]

    def post(self, request, *args, **kwargs):
        serializer = NormalUser_Serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            ward_data = serializer.validated_data["ward"]
            if ward_data <= 0:
                return Response(
                    {"msg": "ward value cannot be 0 or less than 0"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )


# normal user list.
class NormalUserListApiView(generics.ListAPIView):
    queryset = NormalUser.objects.all()
    serializer_class = NormalUser_Serializer_Full_Detals
    pagination_class = MyPageNumberPagination
    permission_classes = [permissions.IsAuthenticated]


# normal user search.
class NormalUserSearchApiViews(generics.ListAPIView):
    queryset = NormalUser.objects.all()
    serializer_class = NormalUser_Serializer_Full_Detals
    filter_backends = [SearchFilter]
    search_fields = [
        "user__name",
        "user__username",
    ]
    pagination_class = MyPageNumberPagination
    permission_classes = [permissions.IsAuthenticated]


# normal user update.
class NormalUserUpdateApiView(generics.UpdateAPIView):
    queryset = NormalUser.objects.all()
    serializer_class = NormalUser_Serializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [UserRenderer]


# normal user delete.
class NormalUserDeleteApiView(generics.DestroyAPIView):
    queryset = NormalUser.objects.all()
    serializer_class = NormalUser_Serializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [UserRenderer]


# MANAGER
# manager create.
class ManagerCreateApiViews(generics.CreateAPIView):
    queryset = Managers.objects.all()
    serializer_class = Managers_Serializer
    renderer_classes = [UserRenderer]


# managers list.
class ManagerListApiViews(generics.ListAPIView):
    queryset = Managers.objects.all()
    serializer_class = Managers_Serializer_Full_Detals
    pagination_class = MyPageNumberPagination
    permission_classes = [permissions.IsAuthenticated]


# manager search.
class ManagerSearchApiViews(generics.ListAPIView):
    queryset = Managers.objects.all()
    serializer_class = Managers_Serializer_Full_Detals
    filter_backends = [SearchFilter]
    search_fields = [
        "name",
        "artist__user__name",
        "artist__user__username",
    ]
    pagination_class = MyPageNumberPagination
    permission_classes = [permissions.IsAuthenticated]


# manager update.
class ManagerUpdateApiViews(generics.UpdateAPIView):
    queryset = Managers.objects.all()
    serializer_class = Managers_Serializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [UserRenderer]


# manager delete.
class ManagerDeleteApiViews(generics.DestroyAPIView):
    queryset = Managers.objects.all()
    serializer_class = Managers_Serializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [UserRenderer]
