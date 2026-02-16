from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL


class Gig(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="gigs"
    )
    title = models.CharField(max_length=120)
    description = models.TextField()
    city = models.CharField(max_length=80)
    date = models.DateField(blank=True, null=True)
    fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    tags = models.CharField(max_length=180, blank=True)  # exemplo: "forró, casamento, bar"
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.city}"


class Application(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pendente"),
        ("accepted", "Aceito"),
        ("rejected", "Recusado"),
    )

    gig = models.ForeignKey(
        Gig,
        on_delete=models.CASCADE,
        related_name="applications"
    )
    applicant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="applications"
    )
    message = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("gig", "applicant")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.applicant} -> {self.gig} ({self.status})"
