from django.urls import path, include
from . import views

app_name = 'dashboard'

urlpatterns = [
    
    # Dashboard URLs
    path('', views.dash_home, name='dash_home'),

    # Spammer URL
    path('spammer/', include("spammer.urls")),
    
]
