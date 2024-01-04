from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

from ems.validations import (
    isalphanumericalvalidator,
    isalphavalidator,
    iscontactvalidator,
)

from .base import BaseModel


# CUSTOME USER MANAGER:
class UserManager(BaseUserManager):
    def create_user(
        self,
        email,
        name,
        username,
        is_artist,
        is_user,
        password=None,
        password2=None,
        # **extra_fields,
    ):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            username=username,
            is_artist=is_artist,
            is_user=is_user,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        email,
        username,
        password,
        name,
        **extra_fields,
    ):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            username=username,
            name=name,
            # is_active=True,
            is_artist=False,
            is_user=False,
        )
        user.is_admin = True
        user.is_active = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


# USER MODEL
class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name="E-mail",
        max_length=255,
        unique=True,
    )
    name = models.CharField(max_length=50, validators=[isalphavalidator])
    username = models.CharField(
        max_length=50, validators=[isalphanumericalvalidator], unique=True
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    is_artist = models.BooleanField(default=False, blank=False, null=False)
    is_user = models.BooleanField(default=False, blank=False, null=False)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "name"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    def __str__(self):
        return self.name


# artist model
class Artist(BaseModel):
    PERFORMER_TYPE = (
        ("Single", "single"),
        ("Group", "group"),
        ("Both", "both"),
    )
    user = models.OneToOneField("User", on_delete=models.CASCADE, related_name="artist")
    type_of_the_performer = models.CharField(max_length=100, blank=False, null=False)
    performed_in = models.CharField(
        choices=PERFORMER_TYPE, blank=False, null=False, max_length=20
    )
    description = models.TextField(null=True, blank=True)
    is_available = models.BooleanField(default=True)
    manager = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


# normal user model.
class NormalUser(BaseModel):
    user = models.OneToOneField(
        "User", on_delete=models.CASCADE, related_name="normaluser"
    )

    def __str__(self):
        return self.user.username


# manager model.
class Managers(models.Model):
    artist = models.OneToOneField("Artist", on_delete=models.CASCADE)
    name = models.CharField(
        max_length=50, blank=False, null=False, validators=[isalphavalidator]
    )
    email = models.EmailField(max_length=255, unique=True, blank=False, null=False)
    contact = models.BigIntegerField(
        validators=[iscontactvalidator], blank=False, null=False
    )

    def __str__(self):
        return self.name
