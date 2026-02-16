from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Post, Comment, Follow, Review
from .serializers import PostSerializer, CommentSerializer, ReviewSerializer
from django.db.models import Avg, Count

User = get_user_model()


class PostViewSet(ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        qs = Post.objects.all().order_by("-created_at")

        author = self.request.query_params.get("author")
        if author:
            qs = qs.filter(author__username=author)

        return qs


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

@api_view(["GET", "POST"])
@permission_classes([permissions.IsAuthenticated])
def profile_reviews(request, username: str):
    target = User.objects.filter(username=username).first()
    if not target:
        return Response({"detail": "Usuário não encontrado."}, status=404)

    if request.method == "GET":
        qs = Review.objects.filter(target=target).select_related("reviewer").order_by("-created_at")
        agg = qs.aggregate(avg=Avg("rating"), count=Count("id"))
        avg_rating = float(agg["avg"] or 0.0)
        count = int(agg["count"] or 0)

        mine = Review.objects.filter(target=target, reviewer=request.user).first()

        return Response({
            "target": {"id": target.id, "username": target.username, "account_type": getattr(target, "account_type", None)},
            "avg_rating": round(avg_rating, 2),
            "count": count,
            "my_review": ReviewSerializer(mine).data if mine else None,
            "items": ReviewSerializer(qs[:200], many=True).data,
        })

    # POST: cria ou atualiza (upsert)
    if request.user.id == target.id:
        return Response({"detail": "Você não pode avaliar você mesmo."}, status=400)

    rating = request.data.get("rating")
    text = request.data.get("text", "")

    try:
        rating_int = int(rating)
    except Exception:
        return Response({"detail": "Nota inválida."}, status=400)

    if rating_int < 1 or rating_int > 5:
        return Response({"detail": "A nota deve ser entre 1 e 5."}, status=400)

    review, created = Review.objects.get_or_create(
        reviewer=request.user,
        target=target,
        defaults={"rating": rating_int, "text": text or ""}
    )

    if not created:
        review.rating = rating_int
        review.text = text or ""
        review.save()

    return Response({"status": "ok", "created": created, "review": ReviewSerializer(review).data})