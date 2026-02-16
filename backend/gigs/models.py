from datetime import date

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify


class Tag(models.Model):
    name = models.SlugField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Gig(models.Model):
    class PayType(models.TextChoices):
        FIXED = "FIXED", "Fixed"
        NEGOTIABLE = "NEGOTIABLE", "Negotiable"
        UNPAID = "UNPAID", "Unpaid"

    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        CLOSED = "CLOSED", "Closed"
        CANCELLED = "CANCELLED", "Cancelled"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_gigs",
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField()
    city = models.CharField(max_length=120)
    venue = models.CharField(max_length=120, blank=True)
    event_date = models.DateField()
    pay_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
    )
    pay_currency = models.CharField(max_length=8, default="BRL")
    pay_type = models.CharField(
        max_length=12,
        choices=PayType.choices,
        default=PayType.NEGOTIABLE,
    )
    instruments_needed = models.CharField(
        max_length=255,
        blank=True,
        help_text="Comma-separated list (e.g. guitar, drums, vocals)",
    )
    genres = models.CharField(
        max_length=255,
        blank=True,
        help_text="Comma-separated list (e.g. samba, jazz, rock)",
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="gigs")
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.OPEN,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["event_date", "-created_at"]

    def __str__(self):
        return self.title

    @property
    def is_open(self):
        return self.status == self.Status.OPEN

    def clean(self):
        errors = {}

        if self.event_date and self.event_date < date.today():
            errors["event_date"] = "Event date cannot be in the past."

        if self.pay_type == self.PayType.FIXED and self.pay_amount is None:
            errors["pay_amount"] = "Pay amount is required when pay type is FIXED."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)[:245] or "gig"
            slug = base_slug
            suffix = 2
            while Gig.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                slug = f"{base_slug}-{suffix}"
                suffix += 1
            self.slug = slug

        super().save(*args, **kwargs)


class GigApplication(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ACCEPTED = "ACCEPTED", "Accepted"
        REJECTED = "REJECTED", "Rejected"
        WITHDRAWN = "WITHDRAWN", "Withdrawn"

    gig = models.ForeignKey(
        Gig,
        on_delete=models.CASCADE,
        related_name="applications",
    )
    musician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="gig_applications",
    )
    message = models.TextField()
    portfolio_url = models.URLField(blank=True)
    attachment = models.FileField(upload_to="gig_applications/", blank=True, null=True)
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["gig", "musician"],
                name="unique_gig_application_per_musician",
            ),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.musician} -> {self.gig} ({self.status})"

    def clean(self):
        errors = {}
        if self.gig_id and self.gig.status != Gig.Status.OPEN:
            errors["gig"] = "This gig is not open for applications."

        if self.musician_id and getattr(self.musician, "account_type", None) != "musician":
            errors["musician"] = "Only musicians can apply to gigs."

        if errors:
            raise ValidationError(errors)
