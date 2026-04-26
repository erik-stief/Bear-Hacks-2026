from django.shortcuts import render

from analyzer.models import AnalysisResult


def dash_home(request):
    records = AnalysisResult.objects.all()[:50]
    return render(request, 'dashboard/index.html', {"records": records})
