from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect, render

def dash_home(request):
    return render(request, 'dashboard/index.html')
