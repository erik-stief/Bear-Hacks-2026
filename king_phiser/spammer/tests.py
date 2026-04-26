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
