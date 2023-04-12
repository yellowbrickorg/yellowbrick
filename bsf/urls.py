from django.urls import path

from . import views
from .views import BrickListView

urlpatterns = [
    # /
    path('', views.index, name='index'),

    # /finder/
    path('finder/', views.finder, name='finder'),

    # /library/
    path('library/', views.library, name='library'),

    # /help/
    path('docs/', views.docs, name='docs'),

    # /bricks/
    path('bricks/', BrickListView.as_view(), name='brick_list'),
]
