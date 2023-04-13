from django.shortcuts import render
from .models import Brick

from django.views.generic import ListView, DetailView


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
    context = {'bricks': bricks}
    return render(request, 'bsf/brick_list.html', context)

class BrickDetailView(DetailView):
    model = Brick
    template_name = 'bsf/brick_detail.html'
class BrickListView(ListView):
    paginate_by = 15
    model = Brick
