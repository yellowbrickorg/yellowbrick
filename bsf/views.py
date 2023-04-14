from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from .models import UserCollection
from django.template import loader
from django.views.generic import ListView, DetailView
from .models import Brick, LegoSet, BrickInCollectionQuantity, SetInCollectionQuantity
from django.urls import reverse
from django.db import transaction


def collection(request):
    logged_user = request.user
    if logged_user.is_authenticated:
        user_collection = UserCollection.objects.get(user=logged_user.id)
        if user_collection:
            context = {
                'user_sets': user_collection.sets.through.objects.all(),
                'user_bricks': user_collection.bricks.through.objects.all(),
            }
        else:
            context = {
                'user_sets': [],
                'user_bricks': [],
            }
        template = loader.get_template('bsf/collection.html')
        return HttpResponse(template.render(context, request))
    else:
        """ TODO: link do strony logowania """
        return render(request, 'admin/index.html')


class SetListView(ListView):
    paginate_by = 15
    model = LegoSet

    def get_queryset(self):
        return self.model.objects.all().filter(bricks__isnull=True).distinct()


def add_set(request, id):
    lego_set = get_object_or_404(LegoSet, id=id)
    try:
        qty = int(request.POST.get('quantity', False))
    except:
        return HttpResponseRedirect(reverse('collection', args=()))
    else:
        logged_user = request.user
        collection = UserCollection.objects.get(user=logged_user)
        if qty > 0:
            try:
                set_through = collection.sets.through.objects.get(id=id)
            except (KeyError, SetInCollectionQuantity.DoesNotExist):
                collection.sets.add(lego_set, through_defaults={"quantity": qty})
            else:
                set_through.quantity = min(set_through.quantity + qty, 100)
                set_through.save()
        return HttpResponseRedirect(reverse('collection', args=()))


def add_brick(request, brick_id):
    brick = get_object_or_404(Brick, brick_id=brick_id)
    qty = int(request.POST.get('quantity', False))
    logged_user = request.user
    collection = UserCollection.objects.get(user=logged_user)
    if qty > 0:
        try:
            brick_through = collection.bricks.through.objects.get(brick_id=brick_id)
        except (KeyError, BrickInCollectionQuantity.DoesNotExist):
            collection.bricks.add(brick, through_defaults={"quantity": qty})
        else:
            brick_through.quantity = min(brick_through.quantity + qty, 10000)
            brick_through.save()
    return HttpResponseRedirect(reverse('collection', args=()))


def del_set(request, id):
    lego_set = get_object_or_404(LegoSet, id=id)
    try:
        qty = int(request.POST.get('quantity', False))
    except:
        return HttpResponseRedirect(reverse('collection', args=()))
    else:
        logged_user = request.user
        collection = UserCollection.objects.get(user=logged_user)
        if qty > 0:
            try:
                set_through = collection.sets.through.objects.get(brick_set_id=id)
            except (KeyError, SetInCollectionQuantity.DoesNotExist):
                collection.sets.add(lego_set, through_defaults={"quantity": qty})
            else:
                if set_through.quantity <= qty:
                    collection.sets.remove(lego_set)
                else:
                    set_through.quantity -= qty
                    set_through.save()
        return HttpResponseRedirect(reverse('collection', args=()))


def del_brick(request, brick_id):
    brick = get_object_or_404(Brick, brick_id=brick_id)
    qty = int(request.POST.get('quantity', False))
    logged_user = request.user
    collection = UserCollection.objects.get(user=logged_user)
    if qty > 0:
        try:
            brick_through = collection.bricks.through.objects.get(brick_id=brick_id)
        except (KeyError, BrickInCollectionQuantity.DoesNotExist):
            collection.bricks.add(brick, through_defaults={"quantity": qty})
        else:
            if brick_through.quantity <= qty:
                collection.bricks.remove(brick)
            else:
                brick_through.quantity -= qty
                brick_through.save()
    return HttpResponseRedirect(reverse('collection', args=()))


def convert(request, id):
    brickset = get_object_or_404(LegoSet, id=id)
    qty = int(request.POST.get('quantity', False))
    logged_user = request.user
    collection = UserCollection.objects.get(user=logged_user)
    if qty > 0:
        try:
            set_through = collection.sets.through.objects.get(brick_set_id=id)
        except (KeyError, SetInCollectionQuantity.DoesNotExist):
            return HttpResponseRedirect(reverse('collection', args=()))
        else:
            real_qty = min(set_through.quantity, qty)
            brickinset_through = brickset.bricks.through.objects.all()
            for brickth in brickinset_through:
                try:
                    brick_through = collection.bricks.through.objects.get(brick_id=brickth.brick.brick_id)
                except (KeyError, BrickInCollectionQuantity.DoesNotExist):
                    collection.bricks.add(brickth.brick, through_defaults={"quantity": real_qty * brickth.quantity})
                else:
                    brick_through.quantity = min(brick_through.quantity + real_qty * brickth.quantity, 10000)
                    brick_through.save()
            if set_through.quantity <= qty:
                collection.sets.remove(brickset)
            else:
                set_through.quantity -= qty
                set_through.save()
    return HttpResponseRedirect(reverse('collection', args=()))

def filter_collection(request):
    try:
        logged_user = request.user
        single_diff = int(request.POST.get('single_diff', False))
        general_diff = int(request.POST.get('general_diff', False))
    except:
        return HttpResponseRedirect(reverse('filter', args=()))
    else:
        viable_sets = CollectionFilter.get_viable_sets(logged_user, single_diff, general_diff)
        return HttpResponseRedirect(reverse('filter', args=({viable_sets: viable_sets})))

def index(request):
    return render(request, 'bsf/index.html')


def finder(request):
    return render(request, 'bsf/filter.html')


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
    
class FilterListView(ListView):
    paginate_by = 15
    model = LegoSet

 
