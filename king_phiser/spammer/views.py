from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect, render

def spam_home(request):
    return render(request, 'spammer/index.html')
