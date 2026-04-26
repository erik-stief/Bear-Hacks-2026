from django.shortcuts import render

from analyzer.models import AnalysisResult, FlaggedEmail


def dash_home(request):
    flagged = FlaggedEmail.objects.all()
    records = AnalysisResult.objects.all()[:50]
    return render(request, 'dashboard/index.html', {
        "flagged": flagged,
        "records": records,
    })
