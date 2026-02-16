from django.urls import path
from .views import RegisterView, MeView
from .views import my_profile


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", MeView.as_view(), name="me"),
    path("my-profile/", my_profile, name="my-profile"),

]
