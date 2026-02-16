from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, MusicianProfile, ContractorProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if not created:
        return

    if instance.account_type == "musician":
        MusicianProfile.objects.create(user=instance)
    else:
        ContractorProfile.objects.create(user=instance)
