from django.urls import path

from .views import (
    FeedView,
    FollowersListView,
    FollowingListView,
    PostCreateView,
    PostDetailView,
    UserProfileView,
    create_comment,
    toggle_follow,
    toggle_like,
)

app_name = "social"

urlpatterns = [
    path("feed/", FeedView.as_view(), name="feed"),
    path("posts/create/", PostCreateView.as_view(), name="post_create"),
    path("posts/<int:pk>/", PostDetailView.as_view(), name="post_detail"),
    path("posts/<int:post_id>/like/", toggle_like, name="toggle_like"),
    path("posts/<int:post_id>/comment/", create_comment, name="create_comment"),
    path("users/<str:username>/", UserProfileView.as_view(), name="user_profile"),
    path("users/<str:username>/follow/", toggle_follow, name="toggle_follow"),
    path("me/following/", FollowingListView.as_view(), name="following_list"),
    path("me/followers/", FollowersListView.as_view(), name="followers_list"),
]
