from django.urls import path
from . import views

app_name = 'spammer'

urlpatterns = [
    path('', views.spam_home, name='spam_home'),
    path('send/<int:result_id>/', views.spam_sender_view, name='spam_sender'),
]
