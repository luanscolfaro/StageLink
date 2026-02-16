from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import ContractorProfile, MusicianProfile, Profile, Role
from .services import create_user_with_profile

User = get_user_model()


class MusicianProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MusicianProfile
        fields = [
            "instruments",
            "genres",
            "available_for_gigs",
            "spotify_url",
            "youtube_url",
            "instagram_url",
            "updated_at",
        ]


class ContractorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractorProfile
        fields = ["company_name", "company_website", "updated_at"]


class ProfileSerializer(serializers.ModelSerializer):
    roles = serializers.SlugRelatedField(many=True, read_only=True, slug_field="key")
    musician_profile = MusicianProfileSerializer(read_only=True)
    contractor_profile = ContractorProfileSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = [
            "display_name",
            "city",
            "bio",
            "is_public",
            "roles",
            "musician_profile",
            "contractor_profile",
        ]


class UserMeSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "account_type",
            "phone",
            "city",
            "state",
            "profile",
        ]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    display_name = serializers.CharField(required=False, allow_blank=True)
    bio = serializers.CharField(required=False, allow_blank=True)
    is_public = serializers.BooleanField(required=False, default=True)
    musician = serializers.BooleanField(required=False, default=False)
    contractor = serializers.BooleanField(required=False, default=False)
    account_type = serializers.ChoiceField(
        choices=[("musician", "Musico"), ("contractor", "Contratante")],
        required=False,
        allow_blank=True,
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "display_name",
            "bio",
            "is_public",
            "musician",
            "contractor",
            "account_type",
            "phone",
            "city",
            "state",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")
        musician = validated_data.pop("musician", False)
        contractor = validated_data.pop("contractor", False)
        display_name = validated_data.pop("display_name", "")
        bio = validated_data.pop("bio", "")
        is_public = validated_data.pop("is_public", True)
        account_type = validated_data.pop("account_type", "")

        role_keys = []
        if musician:
            role_keys.append(Role.Key.MUSICIAN)
        if contractor:
            role_keys.append(Role.Key.CONTRACTOR)

        user = create_user_with_profile(
            username=validated_data["username"],
            password=password,
            email=validated_data.get("email", ""),
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            phone=validated_data.get("phone", ""),
            city=validated_data.get("city", ""),
            state=validated_data.get("state", ""),
            display_name=display_name,
            bio=bio,
            is_public=is_public,
            role_keys=role_keys,
            account_type=account_type,
        )
        return user
