from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import DjangoUnicodeDecodeError, force_bytes, smart_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import serializers

from .models import Artist, Managers, NormalUser, User
from .utils import Util


# user registrtion serializer.
class UserRegistration_Serializer(serializers.ModelSerializer):
    # here we validate the password of the user to register him or her
    password2 = serializers.CharField(
        style={"input_type": "password", "write_only": True}
    )

    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, attrs):
        password = attrs.get("password")
        password2 = attrs.get("password2")
        if password != password2:
            raise serializers.ValidationError(
                "Password and conform password doesnot match "
            )
        return super().validate(attrs)

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


# userlogin serializer.
class UserLogin_Serializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        model = User
        fields = ["email", "password"]


# user password change serializer.
class UserPasswordChange_Serializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=255, style={"input_type": "password"}, write_only=True
    )
    password2 = serializers.CharField(
        max_length=255, style={"input_type": "password"}, write_only=True
    )

    class Meta:
        model = User
        fields = ["password", "password2"]

    def validate(self, attrs):
        password = attrs.get("password")
        password2 = attrs.get("password2")
        user = self.context.get("user")
        if password != password2:
            raise serializers.ValidationError(
                {"msg": "Password and Confirm password doesnot matches..."}
            )
        user.set_password(password)
        user.save()
        # email send after the password is changed.
        data = {
            "subject": "Django Mail",
            "body": "Hii"
            + " "
            + user.name
            + " "
            + "Your Password Has Been Changed !!!",
            "to_email": user.email,
        }
        Util.send_email(data)
        return attrs


# sending the reset email to the user.
class SendPasswordEmail_Serializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ["email"]

    def validate(self, attrs):
        email = attrs.get("email")
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            print(uid)
            token = PasswordResetTokenGenerator().make_token(user)
            print("the token is:", token)
            link = "http://127.0.0.1:3000/user/reset/" + uid + "/" + token
            print(link)
            # sending the mail to the user to change the password
            body = "Click the following link to change the password" + link
            data = {
                "subject": "Rest Your Password",
                "body": body,
                "to_email": user.email,
            }
            Util.send_email(data)
            return attrs
        else:
            raise serializers.ValidationError("Your Email not found")


# user password change serializer through the mail.
class UserPasswordReset_Serializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=255, style={"input_type": "password"}, write_only=True
    )
    password2 = serializers.CharField(
        max_length=255, style={"input_type": "password"}, write_only=True
    )

    class Meta:
        model = User
        fields = ["password", "password2"]

    def validate(self, attrs):
        try:
            password = attrs.get("password")
            password2 = attrs.get("password2")
            uid = self.context.get("uid")
            token = self.context.get("token")
            if password != password2:
                raise serializers.ValidationError(
                    "Password and Conform Password doesnot matches"
                )
            id = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError("Token is not valid or Expired")
            user.set_password(password)
            user.save()
            return attrs
        except DjangoUnicodeDecodeError as identifier:
            PasswordResetTokenGenerator().check_token(user, token)
            raise serializers.ValidationError("Token is not valid or Expired")


# ARTIST
# create serializer for the artist.
class Artist_Serializer(serializers.ModelSerializer):
    photo = serializers.ImageField(max_length=None, use_url=True)

    class Meta:
        model = Artist
        # fields = "__all__"
        fields = (
            "user",
            "type_of_the_performer",
            "performed_in",
            "description",
            "is_available",
            "manager",
            "photo",
            "gender",
            "province",
            "district",
            "municipality",
            "ward",
        )


class Artist_Serializer_Full_Details(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = "__all__"
        depth = 1


# NORMAL USER
# creating serializer for the normal user.
class NormalUser_Serializer(serializers.ModelSerializer):
    class Meta:
        model = NormalUser
        fields = "__all__"


# listing all the data form the relations.
class NormalUser_Serializer_Full_Detals(serializers.ModelSerializer):
    class Meta:
        model = NormalUser
        fields = "__all__"
        depth = 1


# MANAGER SERIALIZER.
# creating the serializer for the manager.
class Managers_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Managers
        fields = "__all__"


# listing all the data form the relations.
class Managers_Serializer_Full_Detals(serializers.ModelSerializer):
    class Meta:
        model = Managers
        fields = "__all__"
        depth = 2


# USER Profile
# login user profile serializer.
class UserProfile_Serializer(serializers.ModelSerializer):
    artist = Artist_Serializer_Full_Details()
    normaluser = NormalUser_Serializer_Full_Detals()

    class Meta:
        model = User
        fields = "__all__"


# login user profile update serializer.
class UserProfileUpdate_Serializer(serializers.ModelSerializer):
    artist = Artist_Serializer_Full_Details()
    normaluser = NormalUser_Serializer_Full_Detals()

    class Meta:
        model = User
        fields = "__all__"


# all user data from the database serializer.
class AllUserList_Serializer(serializers.ModelSerializer):
    artist = serializers.StringRelatedField()
    normaluser = serializers.StringRelatedField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "name",
            "username",
            "date_created",
            "date_updated",
            "is_artist",
            "is_user",
            "is_active",
            "is_admin",
            "artist",
            "normaluser",
        ]


# user delete path serializer.
class Alluserdelete_Serializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


# user full profile update serializer.
class UserLoginProfileFull_Serializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "name", "username", "is_artist", "is_user"]


class ArtistLoginProfileFull_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = [
            "type_of_the_performer",
            "performed_in",
            "description",
            "is_available",
            "manager",
            "contact",
            "photo",
            "gender",
            "ward",
            "municipality",
            "district",
            "province",
        ]


class NormalUserLoginProfileFull_Serializer(serializers.ModelSerializer):
    class Meta:
        model = NormalUser
        fields = "__all__"


# user serializer for the event details.
class UserDetail_Serializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "name",
        ]
