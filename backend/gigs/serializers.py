from rest_framework import serializers
from .models import Gig, Application


class GigSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source="owner.username", read_only=True)

    class Meta:
        model = Gig
        fields = [
            "id",
            "owner",
            "owner_username",
            "title",
            "description",
            "city",
            "date",
            "fee",
            "tags",
            "created_at",
        ]
        read_only_fields = ["owner"]


class ApplicationSerializer(serializers.ModelSerializer):
    applicant_username = serializers.CharField(source="applicant.username", read_only=True)

    class Meta:
        model = Application
        fields = [
            "id",
            "gig",
            "applicant",
            "applicant_username",
            "message",
            "status",
            "created_at",
        ]
        read_only_fields = ["applicant", "status"]
