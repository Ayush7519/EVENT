from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from notification import routing as notification_routing

# integrating the web socket.
# Import the WebSocket URL patterns
websocket_urlpatterns = notification_routing.websocket_urlpatterns

# for the swagger documentation.
schema_view = get_schema_view(
    openapi.Info(
        title="EMS DOCUMENTATIONS",
        default_version="v1",
        description="DOCS",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("account.urls")),
    path("", include("content_management.urls")),
    path("", include("emsadmin.urls")),
    path("", include("booking.urls")),
    path("", include("notification.urls")),
    # path for the web socket.
    path("", include(websocket_urlpatterns)),
    # for the swagger documentations.
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
