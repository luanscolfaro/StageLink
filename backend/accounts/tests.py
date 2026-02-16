from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import MusicianProfile, Role
from .permissions import is_contractor, is_musician
from .services import ensure_profile_for_user, set_profile_roles

User = get_user_model()


class AccountsFlowTests(TestCase):
    def test_signup_creates_user_and_profile(self):
        response = self.client.post(
            reverse("accounts:signup"),
            {
                "username": "alice",
                "email": "alice@example.com",
                "password1": "StrongPass123",
                "password2": "StrongPass123",
                "display_name": "Alice",
                "musician": "on",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("accounts:dashboard"))

        user = User.objects.get(username="alice")
        self.assertTrue(hasattr(user, "profile"))

    def test_activating_musician_role_creates_subprofile(self):
        user = User.objects.create_user(username="musician_user", password="pass12345")
        profile = ensure_profile_for_user(user)

        self.client.force_login(user)
        response = self.client.post(reverse("accounts:roles-edit"), {"musician": "on"})

        self.assertEqual(response.status_code, 302)
        profile.refresh_from_db()
        self.assertTrue(profile.has_role(Role.Key.MUSICIAN))
        self.assertTrue(hasattr(profile, "musician_profile"))

    def test_activating_contractor_role_creates_subprofile(self):
        user = User.objects.create_user(username="contractor_user", password="pass12345")
        profile = ensure_profile_for_user(user)

        self.client.force_login(user)
        response = self.client.post(reverse("accounts:roles-edit"), {"contractor": "on"})

        self.assertEqual(response.status_code, 302)
        profile.refresh_from_db()
        self.assertTrue(profile.has_role(Role.Key.CONTRACTOR))
        self.assertTrue(hasattr(profile, "contractor_profile"))

    def test_user_with_both_roles_passes_permission_helpers(self):
        user = User.objects.create_user(username="hybrid", password="pass12345")
        profile = ensure_profile_for_user(user)
        set_profile_roles(profile, [Role.Key.MUSICIAN, Role.Key.CONTRACTOR])

        user.refresh_from_db()
        self.assertTrue(is_musician(user))
        self.assertTrue(is_contractor(user))

    def test_removing_role_does_not_delete_subprofile(self):
        user = User.objects.create_user(username="soft_disable", password="pass12345")
        profile = ensure_profile_for_user(user)
        set_profile_roles(profile, [Role.Key.MUSICIAN])

        musician_profile_id = profile.musician_profile.id

        self.client.force_login(user)
        response = self.client.post(reverse("accounts:roles-edit"), {})

        self.assertEqual(response.status_code, 302)
        profile.refresh_from_db()
        self.assertFalse(profile.has_role(Role.Key.MUSICIAN))
        self.assertTrue(MusicianProfile.objects.filter(id=musician_profile_id).exists())

    def test_musician_required_mixin_blocks_when_role_missing(self):
        user = User.objects.create_user(username="blocked", password="pass12345")
        ensure_profile_for_user(user)

        self.client.force_login(user)
        response = self.client.get(reverse("accounts:musician-edit"))

        self.assertEqual(response.status_code, 403)
