from django.contrib.auth import get_user_model
from django.db import transaction

from .models import ContractorProfile, MusicianProfile, Profile, Role


CORE_ROLES = {
    Role.Key.MUSICIAN: "Musico",
    Role.Key.CONTRACTOR: "Contratante",
}


@transaction.atomic
def ensure_core_roles():
    roles_by_key = {}
    for key, name in CORE_ROLES.items():
        role, _ = Role.objects.get_or_create(key=key, defaults={"name": name})
        if role.name != name:
            role.name = name
            role.save(update_fields=["name"])
        roles_by_key[key] = role
    return roles_by_key


def _default_display_name(user):
    full_name = user.get_full_name().strip()
    return full_name or user.username


@transaction.atomic
def ensure_profile_for_user(user):
    profile, created = Profile.objects.get_or_create(
        user=user,
        defaults={
            "display_name": _default_display_name(user),
            "city": getattr(user, "city", "") or "",
            "bio": "",
        },
    )

    if not created:
        changed_fields = []
        if not profile.display_name:
            profile.display_name = _default_display_name(user)
            changed_fields.append("display_name")
        if not profile.city and getattr(user, "city", ""):
            profile.city = user.city
            changed_fields.append("city")
        if changed_fields:
            profile.save(update_fields=changed_fields + ["updated_at"])

    return profile


def _sync_legacy_account_type(profile):
    user = profile.user
    if not hasattr(user, "account_type"):
        return

    roles = profile.role_keys()
    desired = "musician"
    if roles == {Role.Key.CONTRACTOR}:
        desired = "contractor"

    if user.account_type != desired:
        user.account_type = desired
        user.save(update_fields=["account_type"])


@transaction.atomic
def ensure_subprofiles_for_roles(profile):
    role_keys = profile.role_keys()

    if Role.Key.MUSICIAN in role_keys:
        MusicianProfile.objects.get_or_create(profile=profile)

    if Role.Key.CONTRACTOR in role_keys:
        ContractorProfile.objects.get_or_create(profile=profile)


@transaction.atomic
def set_profile_roles(profile, role_keys):
    normalized_keys = {key.upper() for key in (role_keys or [])}
    valid_keys = [key for key in normalized_keys if key in CORE_ROLES]

    if not valid_keys:
        profile.roles.clear()
        _sync_legacy_account_type(profile)
        return profile

    roles_by_key = ensure_core_roles()
    roles = [roles_by_key[key] for key in valid_keys]
    profile.roles.set(roles)
    ensure_subprofiles_for_roles(profile)
    _sync_legacy_account_type(profile)
    return profile


@transaction.atomic
def set_profile_roles_from_flags(profile, musician=False, contractor=False):
    role_keys = []
    if musician:
        role_keys.append(Role.Key.MUSICIAN)
    if contractor:
        role_keys.append(Role.Key.CONTRACTOR)
    return set_profile_roles(profile, role_keys)


@transaction.atomic
def create_user_with_profile(
    *,
    username,
    password,
    email="",
    first_name="",
    last_name="",
    display_name="",
    city="",
    bio="",
    is_public=True,
    phone="",
    state="",
    role_keys=None,
    account_type="",
):
    User = get_user_model()
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )

    changed_user_fields = []
    if hasattr(user, "phone") and phone:
        user.phone = phone
        changed_user_fields.append("phone")
    if hasattr(user, "city") and city:
        user.city = city
        changed_user_fields.append("city")
    if hasattr(user, "state") and state:
        user.state = state
        changed_user_fields.append("state")
    if changed_user_fields:
        user.save(update_fields=changed_user_fields)

    profile = ensure_profile_for_user(user)

    changed_profile_fields = []
    if display_name:
        profile.display_name = display_name
        changed_profile_fields.append("display_name")
    if city:
        profile.city = city
        changed_profile_fields.append("city")
    if bio:
        profile.bio = bio
        changed_profile_fields.append("bio")
    if profile.is_public != bool(is_public):
        profile.is_public = bool(is_public)
        changed_profile_fields.append("is_public")

    if changed_profile_fields:
        profile.save(update_fields=changed_profile_fields + ["updated_at"])

    resolved_roles = set(role_keys or [])
    if account_type == "musician":
        resolved_roles.add(Role.Key.MUSICIAN)
    elif account_type == "contractor":
        resolved_roles.add(Role.Key.CONTRACTOR)

    set_profile_roles(profile, list(resolved_roles))
    return user
