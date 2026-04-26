from django.urls import path, include
from . import views

app_name = 'targeter'

urlpatterns = [
    
    # Targeter URL
    path('', views.targ_home, name='targ_home'),
    
]
