from django.contrib.auth.models import AbstractUser
from django.db import models

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
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="musician_profile"
    )
    bio = models.TextField(blank=True)
    instruments = models.CharField(max_length=180, blank=True)
    genres = models.CharField(max_length=180, blank=True)
    available_for_gigs = models.BooleanField(default=True)

    def __str__(self):
        return f"Perfil Músico: {self.user.username}"


class ContractorProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="contractor_profile"
    )
    company_name = models.CharField(max_length=120, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"Perfil Contratante: {self.user.username}"
