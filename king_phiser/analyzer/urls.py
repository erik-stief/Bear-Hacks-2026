from django.urls import path
from .views import analyze_headers_view

urlpatterns = [
    path('analyze/', analyze_headers_view, name='analyze-headers'),
]
