from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied

from .models import Role


def _has_role(user, role_key):
    if not user or not user.is_authenticated:
        return False

    profile = getattr(user, "profile", None)
    if profile is None:
        return False

    return profile.has_role(role_key)


def is_musician(user):
    return _has_role(user, Role.Key.MUSICIAN)


def is_contractor(user):
    return _has_role(user, Role.Key.CONTRACTOR)


def role_required(role_key):
    return user_passes_test(lambda user: _has_role(user, role_key))


def musician_required(view_func):
    return role_required(Role.Key.MUSICIAN)(view_func)


def contractor_required(view_func):
    return role_required(Role.Key.CONTRACTOR)(view_func)


class RoleRequiredMixin(UserPassesTestMixin):
    role_key = None

    def test_func(self):
        return _has_role(self.request.user, self.role_key)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        raise PermissionDenied("Voce nao possui o papel necessario para acessar esta pagina.")


class MusicianRequiredMixin(RoleRequiredMixin):
    role_key = Role.Key.MUSICIAN


class ContractorRequiredMixin(RoleRequiredMixin):
    role_key = Role.Key.CONTRACTOR
