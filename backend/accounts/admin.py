from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, MusicianProfile, ContractorProfile

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("StageLink", {"fields": ("account_type", "phone", "city", "state")}),
    )
    list_display = ("username", "email", "account_type", "is_staff", "is_active")
    list_filter = ("account_type", "is_staff", "is_active")


admin.site.register(MusicianProfile)
admin.site.register(ContractorProfile)
