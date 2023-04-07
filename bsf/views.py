from django.shortcuts import render


# Create your views here.


def index(request):
    return render(request, 'bsf/index.html')


def library(request):
    return render(request, 'bsf/library.html')


def finder(request):
    return render(request, 'bsf/finder.html')


def docs(request):
    return render(request, 'bsf/docs.html')