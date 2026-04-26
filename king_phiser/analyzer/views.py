import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import APIToken, AnalysisResult, FlaggedEmail
from .services.header_analyzer import analyze_headers


def _authenticate_token(request):
    auth_header = request.META.get("HTTP_AUTHORIZATION", "")
    if auth_header.startswith("Token "):
        key = auth_header[6:].strip()
        try:
            return APIToken.objects.select_related("user").get(key=key)
        except APIToken.DoesNotExist:
            pass
    return None


def _compute_risk(analysis: dict) -> str:
    auth_results = analysis.get("authentication_results", [])
    if not auth_results:
        return "suspicious"

    first = auth_results[0]
    spf = first.get("spf") or ""
    dkim = first.get("dkim") or ""
    dmarc = first.get("dmarc") or ""

    failures = sum(1 for v in (spf, dkim, dmarc) if v in ("fail", "none", "softfail"))

    sender_domain = analysis.get("from", {}).get("domain", "")
    reply_to_domain = analysis.get("reply_to", {}).get("domain", "")
    domain_mismatch = (
        reply_to_domain and sender_domain and reply_to_domain != sender_domain
    )

    if failures >= 2 or (failures >= 1 and domain_mismatch):
        return "phishing"
    if failures == 1 or domain_mismatch:
        return "suspicious"
    return "safe"


@csrf_exempt
@require_POST
def analyze_headers_view(request):
    token = _authenticate_token(request)
    if token is None:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    raw_headers = payload.get("raw_headers", "").strip()
    if not raw_headers:
        return JsonResponse({"error": "raw_headers is required"}, status=400)

    analysis = analyze_headers(raw_headers)
    risk = _compute_risk(analysis)

    auth_results = analysis.get("authentication_results", [{}])
    first_auth = auth_results[0] if auth_results else {}

    AnalysisResult.objects.create(
        token=token,
        subject=analysis.get("subject", ""),
        sender_email=analysis.get("from", {}).get("email", ""),
        sender_domain=analysis.get("from", {}).get("domain", ""),
        reply_to_email=analysis.get("reply_to", {}).get("email", ""),
        spf=first_auth.get("spf") or "",
        dkim=first_auth.get("dkim") or "",
        dmarc=first_auth.get("dmarc") or "",
        provider=analysis.get("provider_hint", ""),
        risk_level=risk,
        raw_analysis=analysis,
    )

    return JsonResponse(
        {
            "status": "ok",
            "risk_level": risk,
            "analysis": analysis,
        },
        status=200,
    )


@csrf_exempt
@require_POST
def flag_email_view(request):
    token = _authenticate_token(request)
    if token is None:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    gmail_message_id = payload.get("gmail_message_id", "").strip()
    if not gmail_message_id:
        return JsonResponse({"error": "gmail_message_id is required"}, status=400)

    _, created = FlaggedEmail.objects.get_or_create(
        gmail_message_id=gmail_message_id,
        defaults={
            "subject": payload.get("subject", ""),
            "sender_email": payload.get("sender_email", ""),
            "local_risk_label": payload.get("local_risk_label", "mid"),
            "raw_headers": payload.get("raw_headers", ""),
        },
    )
    return JsonResponse({"status": "created" if created else "exists"})


def analyze_flagged_view(request, flag_id):
    return JsonResponse({"status": "not implemented"}, status=501)


def dismiss_flagged_view(request, flag_id):
    return JsonResponse({"status": "not implemented"}, status=501)
