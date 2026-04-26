from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    
    # Dashboard URLs
    path('', views.dash_home, name='dash_home'),


]
