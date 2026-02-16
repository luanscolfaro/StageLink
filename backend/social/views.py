from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Exists, OuterRef, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DetailView, ListView

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Like, Post

User = get_user_model()


def _with_post_metrics(queryset, user):
    queryset = queryset.select_related("author").annotate(
        likes_count=Count("likes", distinct=True),
        comments_count=Count(
            "comments",
            filter=Q(comments__is_active=True),
            distinct=True,
        ),
    )

    if user.is_authenticated:
        queryset = queryset.annotate(
            is_liked=Exists(Like.objects.filter(post_id=OuterRef("pk"), user=user))
        )

    return queryset


def _querystring_without_page(request):
    query_params = request.GET.copy()
    query_params.pop("page", None)
    return query_params.urlencode()


def _redirect_back(request, fallback_url):
    next_url = (
        request.POST.get("next")
        or request.GET.get("next")
        or request.META.get("HTTP_REFERER")
    )
    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
    ):
        return redirect(next_url)
    return redirect(fallback_url)


class FeedView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "social/feed.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        following_ids = list(
            Follow.objects.filter(follower=self.request.user).values_list(
                "following_id",
                flat=True,
            )
        )
        author_ids = following_ids + [self.request.user.id]
        queryset = Post.objects.filter(
            is_active=True,
            author_id__in=author_ids,
        ).order_by("-created_at")
        return _with_post_metrics(queryset, self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["querystring"] = _querystring_without_page(self.request)
        context["has_following"] = Follow.objects.filter(
            follower=self.request.user
        ).exists()
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "social/post_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("social:feed")


class PostDetailView(DetailView):
    model = Post
    template_name = "social/post_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        queryset = Post.objects.filter(is_active=True)
        return _with_post_metrics(queryset, self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comments"] = (
            Comment.objects.filter(post=self.object, is_active=True)
            .select_related("author")
            .order_by("-created_at")
        )
        if self.request.user.is_authenticated:
            context["comment_form"] = CommentForm()
        return context


class UserProfileView(ListView):
    model = Post
    template_name = "social/user_profile.html"
    context_object_name = "posts"
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        self.profile_user = get_object_or_404(User, username=kwargs["username"])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Post.objects.filter(
            author=self.profile_user,
            is_active=True,
        ).order_by("-created_at")
        return _with_post_metrics(queryset, self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        is_self = self.request.user.is_authenticated and (
            self.request.user == self.profile_user
        )
        context["profile_user"] = self.profile_user
        context["is_self"] = is_self
        context["is_following"] = (
            self.request.user.is_authenticated
            and not is_self
            and Follow.objects.filter(
                follower=self.request.user,
                following=self.profile_user,
            ).exists()
        )
        context["followers_count"] = Follow.objects.filter(
            following=self.profile_user
        ).count()
        context["following_count"] = Follow.objects.filter(
            follower=self.profile_user
        ).count()
        context["querystring"] = _querystring_without_page(self.request)
        return context


class FollowingListView(LoginRequiredMixin, ListView):
    model = Follow
    template_name = "social/following_list.html"
    context_object_name = "relations"
    paginate_by = 20

    def get_queryset(self):
        return (
            Follow.objects.filter(follower=self.request.user)
            .select_related("following")
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["querystring"] = _querystring_without_page(self.request)
        return context


class FollowersListView(LoginRequiredMixin, ListView):
    model = Follow
    template_name = "social/followers_list.html"
    context_object_name = "relations"
    paginate_by = 20

    def get_queryset(self):
        return (
            Follow.objects.filter(following=self.request.user)
            .select_related("follower")
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["querystring"] = _querystring_without_page(self.request)
        return context


@login_required
@require_POST
def toggle_like(request, post_id):
    post = get_object_or_404(Post, pk=post_id, is_active=True)
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
    return _redirect_back(
        request,
        reverse("social:post_detail", kwargs={"pk": post.id}),
    )


@login_required
@require_POST
def create_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id, is_active=True)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
    else:
        messages.error(request, "Could not publish your comment.")

    return _redirect_back(
        request,
        reverse("social:post_detail", kwargs={"pk": post.id}),
    )


@login_required
@require_POST
def toggle_follow(request, username):
    target_user = get_object_or_404(User, username=username)
    fallback_url = reverse(
        "social:user_profile",
        kwargs={"username": target_user.username},
    )

    if target_user == request.user:
        messages.error(request, "You cannot follow yourself.")
        return _redirect_back(request, fallback_url)

    relation = Follow.objects.filter(follower=request.user, following=target_user)
    if relation.exists():
        relation.delete()
    else:
        Follow.objects.create(follower=request.user, following=target_user)

    return _redirect_back(request, fallback_url)
