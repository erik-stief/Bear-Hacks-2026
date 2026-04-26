from django.urls import path
from .views import analyze_headers_view, flag_email_view, analyze_flagged_view, dismiss_flagged_view, delete_result_view

urlpatterns = [
    path('analyze/', analyze_headers_view, name='analyze-headers'),
    path('flag/', flag_email_view, name='flag-email'),
    path('flagged/<int:flag_id>/analyze/', analyze_flagged_view, name='analyze-flagged'),
    path('flagged/<int:flag_id>/dismiss/', dismiss_flagged_view, name='dismiss-flagged'),
    path('result/<int:result_id>/delete/', delete_result_view, name='delete-result'),
]
