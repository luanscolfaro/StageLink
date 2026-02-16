from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import ContractorProfile, MusicianProfile, Profile, Role, User


class MusicianProfileInline(admin.StackedInline):
    model = MusicianProfile
    extra = 0
    can_delete = False


class ContractorProfileInline(admin.StackedInline):
    model = ContractorProfile
    extra = 0
    can_delete = False


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "display_name", "is_public", "roles_list", "updated_at")
    list_filter = ("is_public", "roles")
    search_fields = ("user__username", "display_name", "city")
    filter_horizontal = ("roles",)
    inlines = (MusicianProfileInline, ContractorProfileInline)

    def roles_list(self, obj):
        return ", ".join(obj.roles.values_list("key", flat=True))


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("key", "name")
    search_fields = ("key", "name")


@admin.register(MusicianProfile)
class MusicianProfileAdmin(admin.ModelAdmin):
    list_display = ("profile", "available_for_gigs", "updated_at")
    search_fields = ("profile__user__username", "instruments", "genres")


@admin.register(ContractorProfile)
class ContractorProfileAdmin(admin.ModelAdmin):
    list_display = ("profile", "company_name", "updated_at")
    search_fields = ("profile__user__username", "company_name")


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        (
            "Campos Legados",
            {
                "fields": (
                    "account_type",
                    "phone",
                    "city",
                    "state",
                )
            },
        ),
    )
