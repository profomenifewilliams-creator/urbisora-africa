from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.http import JsonResponse
from django.urls import path, include, re_path
from django.views.static import serve


def healthz(request):
    return JsonResponse({"status": "ok", "service": "urbisora-africa"})


urlpatterns = [
    path("healthz/", healthz, name="healthz"),
    path("admin/", admin.site.urls),
    path("accounts/login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", include("marketplace.urls")),
    # This media route currently serves public realtor profile photos from the demo filesystem.
    # Move uploads to durable object storage before commercial use.
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]
