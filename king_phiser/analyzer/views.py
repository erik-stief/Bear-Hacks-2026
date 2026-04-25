import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .services.header_analyzer import analyze_headers


@require_POST
def analyze_headers_view(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON body"},
            status=400,
        )

    raw_headers = payload.get("raw_headers", "").strip()

    if not raw_headers:
        return JsonResponse(
            {"error": "raw_headers is required"},
            status=400,
        )

    results = analyze_headers(raw_headers)

    return JsonResponse(
        {
            "status": "ok",
            "analysis": results,
        },
        status=200,
    )
