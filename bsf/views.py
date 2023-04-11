from django.shortcuts import render
from .models import Brick

# Create your views here.


def index(request):
    return render(request, 'bsf/index.html')


def library(request):
    return render(request, 'bsf/library.html')


def finder(request):
    return render(request, 'bsf/finder.html')


def docs(request):
    return render(request, 'bsf/docs.html')

def brick_list(request):
    bricks = Brick.objects.all()
    return render(request, 'brick_list.html', {'bricks': bricks})
