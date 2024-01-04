from django.urls import path

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
]
