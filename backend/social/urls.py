from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    PostViewSet,
    CommentViewSet,
    follow_user,
    unfollow_user,
    suggestions,
    search_users,
    profile_detail,
    profile_followers,
    profile_following,
)

router = DefaultRouter()
router.register(r"posts", PostViewSet, basename="posts")

comment_list = CommentViewSet.as_view({
    "get": "list",
    "post": "create",
})

urlpatterns = [
    path("", include(router.urls)),

    path("posts/<int:post_pk>/comments/", comment_list, name="post-comments"),

    path("follow/<int:user_id>/", follow_user, name="follow-user"),
    path("unfollow/<int:user_id>/", unfollow_user, name="unfollow-user"),
    path("suggestions/", suggestions, name="suggestions"),

    path("users/search/", search_users, name="search-users"),
    path("profile/<str:username>/", profile_detail, name="profile-detail"),
    path("profile/<str:username>/followers/", profile_followers, name="profile-followers"),
    path("profile/<str:username>/following/", profile_following, name="profile-following"),
]
