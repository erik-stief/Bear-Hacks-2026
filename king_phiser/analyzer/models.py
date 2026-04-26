import secrets

from django.contrib.auth.models import User
from django.db import models


class APIToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="api_tokens")
    key = models.CharField(max_length=64, unique=True)
    label = models.CharField(max_length=100, default="Extension token")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = secrets.token_hex(32)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} — {self.label}"


class AnalysisResult(models.Model):
    RISK_CHOICES = [
        ("safe", "Safe"),
        ("suspicious", "Suspicious"),
        ("phishing", "Phishing"),
    ]

    token = models.ForeignKey(
        APIToken, null=True, blank=True, on_delete=models.SET_NULL, related_name="results"
    )
    subject = models.TextField(blank=True)
    sender_email = models.EmailField(blank=True)
    sender_domain = models.CharField(max_length=255, blank=True)
    reply_to_email = models.EmailField(blank=True)
    spf = models.CharField(max_length=50, blank=True)
    dkim = models.CharField(max_length=50, blank=True)
    dmarc = models.CharField(max_length=50, blank=True)
    provider = models.CharField(max_length=50, blank=True)
    risk_level = models.CharField(max_length=20, choices=RISK_CHOICES, default="safe")
    raw_analysis = models.JSONField()
    analyzed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-analyzed_at"]

    def __str__(self):
        return f"[{self.risk_level}] {self.subject[:60]} ({self.analyzed_at:%Y-%m-%d %H:%M})"


class FlaggedEmail(models.Model):
    RISK_LABEL_CHOICES = [("mid", "Mid"), ("high", "High")]

    gmail_message_id = models.CharField(max_length=64, unique=True)
    subject = models.TextField(blank=True)
    sender_email = models.CharField(max_length=255, blank=True)
    local_risk_label = models.CharField(max_length=10, choices=RISK_LABEL_CHOICES)
    raw_headers = models.TextField()
    flagged_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-flagged_at"]

    def __str__(self):
        return f"[{self.local_risk_label}] {self.subject[:60]}"
