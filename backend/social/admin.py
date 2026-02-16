from django.contrib import admin

from .models import Comment, Follow, Like, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "created_at", "updated_at", "is_active")
    list_filter = ("is_active", "created_at")
    search_fields = ("author__username", "content")
    ordering = ("-created_at",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "author", "created_at", "is_active")
    list_filter = ("is_active", "created_at")
    search_fields = ("author__username", "content")
    ordering = ("-created_at",)


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "user", "created_at")
    search_fields = ("post__id", "user__username")
    ordering = ("-created_at",)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("id", "follower", "following", "created_at")
    search_fields = ("follower__username", "following__username")
    ordering = ("-created_at",)
