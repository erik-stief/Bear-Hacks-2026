from django.urls import path, include
from . import views

app_name = 'spammer'

urlpatterns = [

    # Spammer URL
    path('', views.spam_home, name='spam_home'),
    path('send-email/<int:result_id>/', views.spam_sender_view, name='spam_sender'),
]
