from django.http import StreamingHttpResponse
from django.shortcuts import render


def index(request):
    return render(request, 'pages/index.html')

def login(request):
    return render(request, 'pages/login.html')

def library(request):
    return render(request, 'pages/library.html')

def books(request):
    return render(request, 'pages/books.html')