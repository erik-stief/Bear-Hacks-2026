from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import StreamingHttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from analyzer.models import AnalysisResult


@login_required
def spam_home(request):
    targets = AnalysisResult.objects.filter(
        risk_level__in=["phishing", "suspicious"]
    )
    return render(request, "spammer/index.html", {"targets": targets})


@login_required
@require_POST
def spam_sender_view(request, result_id):
    result = get_object_or_404(AnalysisResult, id=result_id)
    target_email = result.sender_email

    def email_stream():
        for i in range(1, 101):
            try:
                send_mail(
                    subject="Get King Phished!",
                    message="This is a counter-attack from King Phisher.",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[target_email],
                    fail_silently=False,
                )
                yield f"[{i:03d}/100] Sending to {target_email}... ✓\n"
            except Exception:
                yield f"[{i:03d}/100] Sending to {target_email}... ✗ (failed)\n"
        yield "═══ ATTACK COMPLETE — 100 emails delivered. ═══\n"

    return StreamingHttpResponse(email_stream(), content_type="text/plain")
