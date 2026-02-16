from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import MusicianProfile, ContractorProfile

User = get_user_model()


class MusicianProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MusicianProfile
        fields = ["bio", "instruments", "genres", "available_for_gigs"]


class ContractorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractorProfile
        fields = ["company_name", "bio"]


class UserMeSerializer(serializers.ModelSerializer):
    musician_profile = MusicianProfileSerializer(read_only=True)
    contractor_profile = ContractorProfileSerializer(read_only=True)

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
            "musician_profile",
            "contractor_profile",
        ]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    account_type = serializers.ChoiceField(choices=[("musician", "Músico"), ("contractor", "Contratante")])

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "account_type",
            "phone",
            "city",
            "state",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
