from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Mantemos campos legados para compatibilidade de APIs antigas.
    A autorizacao por papel passa a ser feita via Profile.roles.
    """

    ACCOUNT_TYPES = (
        ("musician", "Musico"),
        ("contractor", "Contratante"),
    )

    account_type = models.CharField(
        max_length=20,
        choices=ACCOUNT_TYPES,
        default="musician",
    )
    phone = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=80, blank=True)
    state = models.CharField(max_length=2, blank=True)

    def __str__(self):
        return self.username


class Role(models.Model):
    class Key(models.TextChoices):
        MUSICIAN = "MUSICIAN", "Musico"
        CONTRACTOR = "CONTRACTOR", "Contratante"

    key = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=80)

    class Meta:
        ordering = ("key",)

    def save(self, *args, **kwargs):
        self.key = self.key.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.key})"


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    display_name = models.CharField(max_length=150)
    city = models.CharField(max_length=80, blank=True)
    bio = models.TextField(blank=True)
    roles = models.ManyToManyField(Role, blank=True, related_name="profiles")
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def role_keys(self):
        return set(self.roles.values_list("key", flat=True))

    def has_role(self, role_key):
        if not role_key:
            return False
        return self.roles.filter(key=role_key.upper()).exists()

    def __str__(self):
        return f"Profile<{self.user.username}>"


class MusicianProfile(models.Model):
    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        related_name="musician_profile",
    )
    instruments = models.TextField(blank=True)
    genres = models.TextField(blank=True)
    available_for_gigs = models.BooleanField(default=True)
    spotify_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"MusicianProfile<{self.profile.user.username}>"


class ContractorProfile(models.Model):
    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        related_name="contractor_profile",
    )
    company_name = models.CharField(max_length=120, blank=True)
    company_website = models.URLField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ContractorProfile<{self.profile.user.username}>"
