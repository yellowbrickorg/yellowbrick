from django.urls import path

from . import views
from .views import brick_list

urlpatterns = [
    # /
    path('', views.index, name='index'),

    # /finder/
    path('finder/', views.finder, name='finder'),

    # /library/
    path('library/', views.library, name='library'),

    # /help/
    path('docs/', views.docs, name='docs'),

    path('bricks/', brick_list, name='brick-list'),
]
