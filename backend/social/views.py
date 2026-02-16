from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Post, Comment, Follow
from .serializers import PostSerializer, CommentSerializer

User = get_user_model()


class PostViewSet(ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        # Feed: posts mais recentes (simples e estável)
        return Post.objects.all().order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        post = self.get_object()
        post.likes.add(request.user)
        return Response(
            {"status": "liked", "likes_count": post.likes.count()},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def unlike(self, request, pk=None):
        post = self.get_object()
        post.likes.remove(request.user)
        return Response(
            {"status": "unliked", "likes_count": post.likes.count()},
            status=status.HTTP_200_OK
        )


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(post_id=self.kwargs["post_pk"]).order_by("created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, post_id=self.kwargs["post_pk"])


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def follow_user(request, user_id: int):
    if request.user.id == user_id:
        return Response({"detail": "Você não pode seguir você mesmo."}, status=400)

    target = User.objects.filter(id=user_id).first()
    if not target:
        return Response({"detail": "Usuário não encontrado."}, status=404)

    Follow.objects.get_or_create(follower=request.user, following=target)
    return Response({"status": "followed"})


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def unfollow_user(request, user_id: int):
    Follow.objects.filter(follower=request.user, following_id=user_id).delete()
    return Response({"status": "unfollowed"})


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def suggestions(request):
    user = request.user
    following_ids = Follow.objects.filter(follower=user).values_list("following_id", flat=True)

    qs = (
        User.objects
        .exclude(id=user.id)
        .exclude(id__in=following_ids)
        .order_by("username")[:10]
    )

    data = [{"id": u.id, "username": u.username, "account_type": u.account_type} for u in qs]
    return Response(data)

@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def search_users(request):
    q = (request.GET.get("q") or "").strip()

    qs = User.objects.exclude(id=request.user.id).order_by("username")
    if q:
        qs = qs.filter(username__icontains=q)

    qs = qs[:30]
    data = [
        {
            "id": u.id,
            "username": u.username,
            "account_type": getattr(u, "account_type", None),
        }
        for u in qs
    ]
    return Response(data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def profile_detail(request, username: str):
    u = User.objects.filter(username=username).first()
    if not u:
        return Response({"detail": "Usuário não encontrado."}, status=404)

    followers_count = Follow.objects.filter(following=u).count()
    following_count = Follow.objects.filter(follower=u).count()
    is_following = Follow.objects.filter(follower=request.user, following=u).exists()

    data = {
        "id": u.id,
        "username": u.username,
        "account_type": getattr(u, "account_type", None),
        "followers_count": followers_count,
        "following_count": following_count,
        "is_following": is_following,
    }
    return Response(data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def profile_followers(request, username: str):
    u = User.objects.filter(username=username).first()
    if not u:
        return Response({"detail": "Usuário não encontrado."}, status=404)

    qs = Follow.objects.filter(following=u).select_related("follower").order_by("-created_at")[:200]
    data = [
        {
            "id": f.follower.id,
            "username": f.follower.username,
            "account_type": getattr(f.follower, "account_type", None),
        }
        for f in qs
    ]
    return Response(data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def profile_following(request, username: str):
    u = User.objects.filter(username=username).first()
    if not u:
        return Response({"detail": "Usuário não encontrado."}, status=404)

    qs = Follow.objects.filter(follower=u).select_related("following").order_by("-created_at")[:200]
    data = [
        {
            "id": f.following.id,
            "username": f.following.username,
            "account_type": getattr(f.following, "account_type", None),
        }
        for f in qs
    ]
    return Response(data)
