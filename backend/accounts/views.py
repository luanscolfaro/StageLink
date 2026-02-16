from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, UserMeSerializer, MusicianProfileSerializer, ContractorProfileSerializer
from .models import MusicianProfile, ContractorProfile

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeView(generics.RetrieveAPIView):
    serializer_class = UserMeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

@api_view(["GET", "PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def my_profile(request):
    user = request.user
    account_type = getattr(user, "account_type", None)

    if account_type == "musician":
        profile, _ = MusicianProfile.objects.get_or_create(user=user)
        serializer_class = MusicianProfileSerializer
    else:
        profile, _ = ContractorProfile.objects.get_or_create(user=user)
        serializer_class = ContractorProfileSerializer

    if request.method == "GET":
        return Response({
            "account_type": account_type,
            "profile": serializer_class(profile).data
        })

    # PUT/PATCH
    serializer = serializer_class(profile, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response({
        "status": "ok",
        "account_type": account_type,
        "profile": serializer_class(profile).data
    })