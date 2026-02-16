from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User
from .services import ensure_profile_for_user


@receiver(post_save, sender=User)
def create_profile_for_new_user(sender, instance, created, **kwargs):
    if created:
        ensure_profile_for_user(instance)
