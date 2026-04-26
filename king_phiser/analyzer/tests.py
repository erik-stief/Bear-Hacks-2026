import json

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


class FlagEmailViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pass")
        self.token = APIToken.objects.create(user=self.user, label="test")

    def _auth(self):
        return {"HTTP_AUTHORIZATION": f"Token {self.token.key}"}

    def test_flag_creates_record(self):
        payload = {
            "gmail_message_id": "msg001",
            "subject": "You won!",
            "sender_email": "evil@spam.com",
            "local_risk_label": "high",
            "raw_headers": "From: evil@spam.com\r\nSubject: You won!",
        }
        response = self.client.post(
            "/api/flag/",
            data=json.dumps(payload),
            content_type="application/json",
            **self._auth(),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(FlaggedEmail.objects.count(), 1)
        data = response.json()
        self.assertEqual(data["status"], "created")

    def test_flag_deduplicates(self):
        payload = {
            "gmail_message_id": "msg002",
            "subject": "Dup",
            "sender_email": "a@b.com",
            "local_risk_label": "mid",
            "raw_headers": "From: a@b.com",
        }
        self.client.post("/api/flag/", data=json.dumps(payload), content_type="application/json", **self._auth())
        response = self.client.post("/api/flag/", data=json.dumps(payload), content_type="application/json", **self._auth())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(FlaggedEmail.objects.count(), 1)
        self.assertEqual(response.json()["status"], "exists")

    def test_flag_rejects_missing_token(self):
        response = self.client.post("/api/flag/", data=json.dumps({}), content_type="application/json")
        self.assertEqual(response.status_code, 401)
