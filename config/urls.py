import environ
from django.conf import settings
from django.contrib import admin
from django.urls import path

env = environ.Env()
environ.Env.read_env(str(settings.BASE_DIR.joinpath(".env")), overwrite=True)

urlpatterns = [
    path(env("ADMIN_URL"), admin.site.urls),
]
