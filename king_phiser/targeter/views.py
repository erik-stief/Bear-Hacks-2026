from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect, render

def targ_home(request):
    return render(request, 'targeter/index.html')
