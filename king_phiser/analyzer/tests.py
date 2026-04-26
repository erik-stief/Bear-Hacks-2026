from django.test import TestCase
from django.contrib.auth.models import User
from .models import APIToken, FlaggedEmail, AnalysisResult


class FlaggedEmailModelTest(TestCase):
    def test_create_flagged_email(self):
        email = FlaggedEmail.objects.create(
            gmail_message_id="abc123",
            subject="Win a prize",
            sender_email="spammer@evil.com",
            local_risk_label="high",
            raw_headers="From: spammer@evil.com\r\nSubject: Win a prize",
        )
        self.assertEqual(FlaggedEmail.objects.count(), 1)
        self.assertEqual(email.gmail_message_id, "abc123")

    def test_gmail_message_id_is_unique(self):
        FlaggedEmail.objects.create(
            gmail_message_id="dup001",
            subject="Test",
            sender_email="a@b.com",
            local_risk_label="mid",
            raw_headers="From: a@b.com",
        )
        with self.assertRaises(Exception):
            FlaggedEmail.objects.create(
                gmail_message_id="dup001",
                subject="Test2",
                sender_email="a@b.com",
                local_risk_label="mid",
                raw_headers="From: a@b.com",
            )
