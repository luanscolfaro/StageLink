from rest_framework import serializers
from .models import Post, Comment
from django.contrib.auth import get_user_model
from .models import Review

User = get_user_model()

class PostSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source="author.username", read_only=True)
    likes_count = serializers.IntegerField(source="likes.count", read_only=True)
    comments_count = serializers.IntegerField(source="comments.count", read_only=True)
    image = serializers.ImageField(required=False, allow_null=True)
    liked_by_me = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "author_username",
            "content",
            "image",
            "created_at",
            "likes_count",
            "comments_count",
            "liked_by_me",
        ]
        read_only_fields = ["author"]

    def get_liked_by_me(self, obj):
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            return False
        return obj.likes.filter(id=request.user.id).exists()


class CommentSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "post", "user", "user_username", "text", "created_at"]
        read_only_fields = ["user", "post"]  # <-- AQUI está a correção

class ReviewSerializer(serializers.ModelSerializer):
    reviewer_username = serializers.CharField(source="reviewer.username", read_only=True)

    class Meta:
        model = Review
        fields = ["id", "reviewer", "reviewer_username", "target", "rating", "text", "created_at", "updated_at"]
        read_only_fields = ["reviewer", "target", "created_at", "updated_at"]