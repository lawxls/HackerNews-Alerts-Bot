import environ
from django.conf import settings
from django.contrib import admin
from django.urls import include, path

env = environ.Env()
environ.Env.read_env(str(settings.BASE_DIR.joinpath(".env")))

urlpatterns = [
    path(env("ADMIN_URL"), admin.site.urls),
    path("__debug__/", include("debug_toolbar.urls")),
]
