from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class User(AbstractUser):
    ACCOUNT_TYPES = (
        ("musician", "Músico"),
        ("contractor", "Contratante"),
    )

    account_type = models.CharField(
        max_length=20,
        choices=ACCOUNT_TYPES,
        default="musician"
    )
    phone = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=80, blank=True)
    state = models.CharField(max_length=2, blank=True)

    def __str__(self):
        return f"{self.username} ({self.account_type})"


class MusicianProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="musician_profile")
    photo = models.ImageField(upload_to="profiles/", blank=True, null=True)
    bio = models.TextField(blank=True)
    city = models.CharField(max_length=80, blank=True)
    state = models.CharField(max_length=2, blank=True)  # ex: PB, CE
    instruments = models.CharField(max_length=200, blank=True)  # "violão, guitarra, baixo"
    genres = models.CharField(max_length=200, blank=True)       # "forró, pop, worship"
    whatsapp = models.CharField(max_length=30, blank=True)
    instagram = models.CharField(max_length=60, blank=True)

    def __str__(self):
        return f"MusicianProfile({self.user.username})"


class ContractorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="contractor_profile")
    photo = models.ImageField(upload_to="profiles/", blank=True, null=True)
    bio = models.TextField(blank=True)
    city = models.CharField(max_length=80, blank=True)
    state = models.CharField(max_length=2, blank=True)
    company_name = models.CharField(max_length=120, blank=True)
    whatsapp = models.CharField(max_length=30, blank=True)
    instagram = models.CharField(max_length=60, blank=True)

    def __str__(self):
        return f"ContractorProfile({self.user.username})"