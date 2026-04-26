from django.urls import path, include
from . import views

app_name = 'spammer'

urlpatterns = [

    # Spammer URL
    path('', views.spam_home, name='spam_home'),
    path('send-email/<int:customer_id>/', views.send_duplicate_email_view, name='send_duplicate_email'),
]
