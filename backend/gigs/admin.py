from django.contrib import admin

from .models import Gig, GigApplication, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Gig)
class GigAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "city", "status", "event_date", "created_at")
    list_filter = ("status", "pay_type", "city", "event_date")
    search_fields = ("title", "description", "city", "owner__username")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags",)


@admin.register(GigApplication)
class GigApplicationAdmin(admin.ModelAdmin):
    list_display = ("gig", "musician", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("gig__title", "musician__username", "message")
