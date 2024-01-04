from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    # USER ACCOUNT MANAGEMENT PATH.
    path(
        "register/",
        views.UserRegistrationView.as_view(),
        name="user registration path",
    ),
    path(
        "login/",
        views.UserLoginView.as_view(),
        name="user login path",
    ),
    path(
        "user-profile/",
        views.UserProfileView.as_view(),
        name="login user profile details view path",
    ),
    path(
        "login-user-profile-update/<str:name>/",
        views.UserLoginProfileFullUpdateView.as_view(),
        name="login user full detail update view.",
    ),
    path(
        "password-change/",
        views.UserPasswordChangeView.as_view(),
        name="user password change path",
    ),
    path(
        "send-reset-password-email/",
        views.SendPassowrdEmailView.as_view(),
        name="password change email path",
    ),
    path(
        "reset-password/<uid>/<token>/",
        views.UserPasswordResetView.as_view(),
        name="user e-password change path",
    ),
    # USERS DATA FROM THE DATABASE FOR THE ADMIN.
    path(
        "all-user-data/",
        views.AllUserListApiView.as_view(),
        name="all user data from the database",
    ),
    path(
        "all-user-data-search/",
        views.AllUserSearchApiView.as_view(),
        name="path searching the user from the database",
    ),
    path(
        "all-user-data-update/<int:pk>/",
        views.AllUserUpdateApiView.as_view(),
        name="path for updating the data of the user from the admin pannel.",
    ),
    path(
        "all-user-data-delete/<int:pk>/",
        views.AllUserDeleteApiView.as_view(),
        name="path deleting the data of the user from the admin pannel",
    ),
    # ARTIST PATHS.
    path(
        "artist/create/",
        views.ArtistCreateApiView.as_view(),
        name="artist create path",
    ),
    path(
        "artist/list/",
        views.ArtistListApiView.as_view(),
        name="artist list path",
    ),
    path(
        "artist/search/",
        views.ArtistSearchApiViews.as_view(),
        name="artist search path",
    ),
    path(
        "artist/update/<int:pk>/",
        views.ArtistUpdateView.as_view(),
        name="artist update path",
    ),
    path(
        "artist/delete/<int:pk>/",
        views.ArtistDeleteView.as_view(),
        name="artist delete path",
    ),
    # NORMAL USER PATHS.
    path(
        "normal-user/create/",
        views.NormalUserCreateApiView().as_view(),
        name="normal user create path",
    ),
    path(
        "normal-user/list/",
        views.NormalUserListApiView.as_view(),
        name="normal user list path",
    ),
    path(
        "normal-user/search/",
        views.NormalUserSearchApiViews.as_view(),
        name="normal user search path",
    ),
    path(
        "normal-user/update/<int:pk>/",
        views.NormalUserUpdateApiView.as_view(),
        name="normal user update path",
    ),
    path(
        "normal-user/delete/<int:pk>/",
        views.NormalUserDeleteApiView.as_view(),
        name="normal user delete path",
    ),
    # MANAGER PATHS.
    path(
        "manager/create/",
        views.ManagerCreateApiViews.as_view(),
        name="manager create path",
    ),
    path(
        "manager/list/",
        views.ManagerListApiViews.as_view(),
        name="manager list path",
    ),
    path(
        "manager/search/",
        views.ManagerSearchApiViews.as_view(),
        name="manager search path",
    ),
    path(
        "manager/update/<int:pk>/",
        views.ManagerUpdateApiViews.as_view(),
        name="manager update path",
    ),
    path(
        "manager/delete/<int:pk>/",
        views.ManagerDeleteApiViews.as_view(),
        name="manager delete path",
    ),
    # route to send the mail to the indivisual artist.
    path(
        "send-email/<int:pk>/",
        views.EmailButton_View.as_view(),
        name="path to send the email to the user",
    ),
]
