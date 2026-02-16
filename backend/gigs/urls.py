from django.urls import path

from .views import (
    GigApplicationCreateView,
    GigApplicationDecisionView,
    GigApplicationWithdrawView,
    GigCreateView,
    GigDetailView,
    GigListView,
    GigStatusUpdateView,
    GigUpdateView,
    ManageGigApplicationsView,
    ManageGigsView,
    MyApplicationsView,
)

app_name = "gigs"

urlpatterns = [
    path("", GigListView.as_view(), name="list"),
    path("create/", GigCreateView.as_view(), name="create"),
    path("applications/", MyApplicationsView.as_view(), name="my_applications"),
    path(
        "applications/<int:application_id>/withdraw/",
        GigApplicationWithdrawView.as_view(),
        name="withdraw_application",
    ),
    path("manage/", ManageGigsView.as_view(), name="manage_gigs"),
    path("manage/<int:gig_id>/edit/", GigUpdateView.as_view(), name="edit"),
    path(
        "manage/<int:gig_id>/applications/",
        ManageGigApplicationsView.as_view(),
        name="manage_applications",
    ),
    path(
        "manage/<int:gig_id>/applications/<int:application_id>/<str:action>/",
        GigApplicationDecisionView.as_view(),
        name="application_decision",
    ),
    path(
        "manage/<int:gig_id>/status/<str:new_status>/",
        GigStatusUpdateView.as_view(),
        name="change_status",
    ),
    path("<str:identifier>/apply/", GigApplicationCreateView.as_view(), name="apply"),
    path("<str:identifier>/", GigDetailView.as_view(), name="detail"),
]
