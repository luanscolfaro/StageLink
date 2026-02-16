from django.urls import path

from .views import (
    AccountLoginView,
    AccountLogoutView,
    ContractorProfileEditView,
    DashboardView,
    MusicianProfileEditView,
    ProfileEditView,
    PublicProfileView,
    RolesEditView,
    SignupView,
)

app_name = "accounts"

urlpatterns = [
    path("accounts/signup/", SignupView.as_view(), name="signup"),
    path("accounts/login/", AccountLoginView.as_view(), name="login"),
    path("accounts/logout/", AccountLogoutView.as_view(), name="logout"),
    path("accounts/me/", DashboardView.as_view(), name="dashboard"),
    path("accounts/me/edit/", ProfileEditView.as_view(), name="profile-edit"),
    path("accounts/me/roles/", RolesEditView.as_view(), name="roles-edit"),
    path(
        "accounts/me/musician/",
        MusicianProfileEditView.as_view(),
        name="musician-edit",
    ),
    path(
        "accounts/me/contractor/",
        ContractorProfileEditView.as_view(),
        name="contractor-edit",
    ),
    path("u/<str:username>/", PublicProfileView.as_view(), name="public-profile"),
]
