from django.urls import path

from . import views

urlpatterns = [
    # /bsf/
    path('', views.index, name='index'),
]
