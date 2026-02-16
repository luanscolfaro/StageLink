def active_roles(request):
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {"active_role_keys": []}

    profile = getattr(user, "profile", None)
    if not profile:
        return {"active_role_keys": []}

    return {
        "active_role_keys": list(profile.roles.values_list("key", flat=True)),
    }
