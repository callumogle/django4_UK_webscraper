from django.shortcuts import render
from django.http import HttpResponse
from .models import Webscraper

def index(request):
    context = {"context" : Webscraper.objects.all()}
    return render(request, 'webscraper/index.html', context)
