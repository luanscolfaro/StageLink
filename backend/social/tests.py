from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Comment, Follow, Like, Post

User = get_user_model()


class SocialMVPTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.password = "Testpass123!"
        cls.alice = User.objects.create_user(
            username="alice",
            password=cls.password,
        )
        cls.bob = User.objects.create_user(
            username="bob",
            password=cls.password,
        )
        cls.charlie = User.objects.create_user(
            username="charlie",
            password=cls.password,
        )

    def login_as_alice(self):
        self.client.login(username="alice", password=self.password)

    def test_user_creates_post(self):
        self.login_as_alice()
        response = self.client.post(
            reverse("social:post_create"),
            {"content": "Meu primeiro post"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Post.objects.filter(author=self.alice, content="Meu primeiro post").exists()
        )

    def test_follow_creates_relation_and_prevents_self_follow(self):
        self.login_as_alice()

        self.client.post(
            reverse("social:toggle_follow", kwargs={"username": self.bob.username})
        )
        self.assertTrue(
            Follow.objects.filter(follower=self.alice, following=self.bob).exists()
        )

        self.client.post(
            reverse("social:toggle_follow", kwargs={"username": self.bob.username})
        )
        self.assertFalse(
            Follow.objects.filter(follower=self.alice, following=self.bob).exists()
        )

        self.client.post(
            reverse("social:toggle_follow", kwargs={"username": self.alice.username})
        )
        self.assertFalse(
            Follow.objects.filter(follower=self.alice, following=self.alice).exists()
        )

    def test_feed_shows_followed_and_own_posts_only(self):
        Post.objects.create(author=self.alice, content="post da alice")
        Post.objects.create(author=self.bob, content="post do bob")
        Post.objects.create(author=self.charlie, content="post do charlie")
        Follow.objects.create(follower=self.alice, following=self.bob)

        self.login_as_alice()
        response = self.client.get(reverse("social:feed"))

        self.assertContains(response, "post da alice")
        self.assertContains(response, "post do bob")
        self.assertNotContains(response, "post do charlie")

    def test_like_toggle_creates_and_removes(self):
        post = Post.objects.create(author=self.bob, content="post para like")
        self.login_as_alice()
        like_url = reverse("social:toggle_like", kwargs={"post_id": post.id})

        self.client.post(like_url)
        self.assertTrue(Like.objects.filter(post=post, user=self.alice).exists())

        self.client.post(like_url)
        self.assertFalse(Like.objects.filter(post=post, user=self.alice).exists())

    def test_comment_creates_comment(self):
        post = Post.objects.create(author=self.bob, content="post para comentario")
        self.login_as_alice()

        response = self.client.post(
            reverse("social:create_comment", kwargs={"post_id": post.id}),
            {"content": "Comentando no post"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Comment.objects.filter(
                post=post,
                author=self.alice,
                content="Comentando no post",
            ).exists()
        )

    def test_permissions_endpoints_require_login(self):
        post = Post.objects.create(author=self.bob, content="post protegido")
        protected_routes = [
            ("get", reverse("social:feed"), {}),
            ("get", reverse("social:post_create"), {}),
            ("get", reverse("social:following_list"), {}),
            ("get", reverse("social:followers_list"), {}),
            ("post", reverse("social:toggle_like", kwargs={"post_id": post.id}), {}),
            (
                "post",
                reverse("social:create_comment", kwargs={"post_id": post.id}),
                {"content": "Sem login"},
            ),
            (
                "post",
                reverse("social:toggle_follow", kwargs={"username": self.bob.username}),
                {},
            ),
        ]

        for method, url, payload in protected_routes:
            response = getattr(self.client, method)(url, payload)
            self.assertEqual(response.status_code, 302)
            self.assertIn("/accounts/login/", response.url)

    def test_like_and_comment_blocked_for_inactive_post(self):
        post = Post.objects.create(
            author=self.bob,
            content="inativo",
            is_active=False,
        )
        self.login_as_alice()

        like_response = self.client.post(
            reverse("social:toggle_like", kwargs={"post_id": post.id})
        )
        self.assertEqual(like_response.status_code, 404)
        self.assertFalse(Like.objects.filter(post=post, user=self.alice).exists())

        comment_response = self.client.post(
            reverse("social:create_comment", kwargs={"post_id": post.id}),
            {"content": "Tentativa"},
        )
        self.assertEqual(comment_response.status_code, 404)
        self.assertFalse(Comment.objects.filter(post=post, author=self.alice).exists())
