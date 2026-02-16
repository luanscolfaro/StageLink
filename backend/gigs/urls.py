from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import GigViewSet, ApplicationManageViewSet

router = DefaultRouter()
router.register("gigs", GigViewSet, basename="gig")
router.register("applications", ApplicationManageViewSet, basename="application")

urlpatterns = [
    path("", include(router.urls)),
]
