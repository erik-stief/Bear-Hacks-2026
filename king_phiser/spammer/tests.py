from unittest.mock import patch

from django.test import TestCase, Client
from django.contrib.auth.models import User

from analyzer.models import AnalysisResult, APIToken


def _make_result(token, sender_email, risk_level):
    return AnalysisResult.objects.create(
        token=token,
        sender_email=sender_email,
        sender_domain=sender_email.split("@")[1],
        subject=f"Test email from {sender_email}",
        risk_level=risk_level,
        raw_analysis={},
    )


class SpamHomeViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("tester", password="testpass123")
        self.client.login(username="tester", password="testpass123")
        self.token = APIToken.objects.create(user=self.user)

    def test_returns_200(self):
        response = self.client.get("/dashboard/spammer/")
        self.assertEqual(response.status_code, 200)

    def test_includes_phishing_and_suspicious(self):
        _make_result(self.token, "evil@phish.com", "phishing")
        _make_result(self.token, "sus@scam.net", "suspicious")
        response = self.client.get("/dashboard/spammer/")
        emails = [t.sender_email for t in response.context["targets"]]
        self.assertIn("evil@phish.com", emails)
        self.assertIn("sus@scam.net", emails)

    def test_excludes_safe(self):
        _make_result(self.token, "ok@good.com", "safe")
        response = self.client.get("/dashboard/spammer/")
        emails = [t.sender_email for t in response.context["targets"]]
        self.assertNotIn("ok@good.com", emails)

    def test_redirects_when_logged_out(self):
        self.client.logout()
        response = self.client.get("/dashboard/spammer/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])


class SpamSenderViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("attacker", password="testpass123")
        self.client.login(username="attacker", password="testpass123")
        self.token = APIToken.objects.create(user=self.user)
        self.result = _make_result(self.token, "evil@phish.com", "phishing")

    @patch("spammer.views.send_mail")
    def test_streams_100_lines(self, mock_send_mail):
        response = self.client.post(f"/dashboard/spammer/send/{self.result.id}/")
        self.assertEqual(response.status_code, 200)
        content = b"".join(response.streaming_content).decode()
        self.assertIn("[001/100]", content)
        self.assertIn("[100/100]", content)
        self.assertIn("ATTACK COMPLETE", content)
        self.assertEqual(mock_send_mail.call_count, 100)

    @patch("spammer.views.send_mail")
    def test_sends_to_result_sender_email(self, mock_send_mail):
        response = self.client.post(f"/dashboard/spammer/send/{self.result.id}/")
        b"".join(response.streaming_content)
        for call in mock_send_mail.call_args_list:
            recipient_list = call.kwargs["recipient_list"]
            self.assertIn("evil@phish.com", recipient_list)

    def test_requires_post(self):
        response = self.client.get(f"/dashboard/spammer/send/{self.result.id}/")
        self.assertEqual(response.status_code, 405)

    def test_requires_login(self):
        self.client.logout()
        response = self.client.post(f"/dashboard/spammer/send/{self.result.id}/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

    def test_returns_404_for_missing_result(self):
        response = self.client.post("/dashboard/spammer/send/99999/")
        self.assertEqual(response.status_code, 404)
