from django.urls import path

from . import views
from .views import BrickListView, BrickDetailView

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

    path('bricks/<int:pk>/', BrickDetailView.as_view(), name='brick-detail'),

]
