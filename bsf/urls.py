from django.urls import path
from .views import BrickListView, SetListView
from . import views

urlpatterns = [
    # /
    path('', views.index, name='index'),

    # /finder/
    path('finder/', views.finder, name='finder'),

    # /library/
    path('library/', views.library, name='library'),

    # /help/
    path('docs/', views.docs, name='docs'),

    # /my_bricks/
    path('my_bricks', views.my_bricks, name='my_bricks'),

    # /bricks/
    path('bricks/', BrickListView.as_view(), name='brick_list'),
    
    # /sets/
    path('sets/', SetListView.as_view(), name='legoset_list'),

    path('<int:brick_id>/add_brick/', views.add_brick, name='add_brick'),
    path('<int:set_id>/add_set', views.add_set, name='add_set'),
    path('<int:brick_id>/del_brick', views.del_brick, name='del_brick'),
    path('<int:set_id>/del_set', views.del_set, name='del_set'),
    path('<int:set_id>/convert', views.convert, name='convert'),
]
