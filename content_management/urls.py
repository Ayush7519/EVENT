from django.urls import path
from django.views.generic import RedirectView

from content_management import views

urlpatterns = [
    # heading path
    path(
        "dynamic-heading/list/",
        views.HeadingListApiView.as_view(),
        name="path to get the heading for the dynamic home page",
    ),
    # content-management path
    path(
        "content-management/create/",
        views.Content_ManagementCreateApiView.as_view(),
        name="content-management create path",
    ),
    path(
        "content-management/search/",
        views.Content_ManagementSearchApiView.as_view(),
        name="content-management list path",
    ),
    path(
        "content-management/list/<str:status>/",
        views.Content_ManagementStatusListApiView.as_view(),
        name="content-management based on draft path",
    ),
    path(
        "content-management/update/<int:pk>/",
        views.Content_managementUpdateApiView.as_view(),
        name="content-management update path",
    ),
    path(
        "content-management/delete/<int:pk>/",
        views.Content_ManagementDeleteApiView.as_view(),
        name="content-management delete path",
    ),
    path(
        "event-management/<int:pk>/",
        views.Contetn_Manageent_ButtonListApiView.as_view(),
        name="path to search the content for the frontend",
    ),
    path(
        "iamge/upload/path/",
        views.ImageUploadApiView.as_view(),
        name="path",
    ),
    path(
        "blog/image/upload/",
        views.BlogImageUploadApiView.as_view(),
        name="path to upload the image in the blog tinymc",
    ),
    path(
        "blog/create/",
        views.BlogCreateApiView.as_view(),
        name="path to create the blog",
    ),
    path(
        "blog/list/",
        views.BlogListApiView.as_view(),
        name="path to see all the blogs",
    ),
    path(
        "blog/search/",
        views.BlogSearchApiView.as_view(),
        name="path to search the blog in the frontens and in the admin pannel",
    ),
    path(
        "blog/update/<int:pk>/",
        views.BlogUpdateApiView.as_view(),
        name="path to update the blog content",
    ),
    path(
        "blog/delete/<int:pk>/",
        views.BlogDeleteApiView.as_view(),
        name="path to delete the blog content",
    ),
]
