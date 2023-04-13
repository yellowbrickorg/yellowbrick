from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from .models import UserCollection
from django.template import loader
from django.views.generic import ListView, DetailView
from .models import Brick, LegoSet, BrickInCollectionQuantity, SetInCollectionQuantity
from django.urls import reverse


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


def legoset_list(request):
    sets = LegoSet.objects.all()
    context = {'sets': sets}
    return render(request, 'bsf/set_list.html', context)


class SetListView(ListView):
    paginate_by = 15
    model = LegoSet


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
            brick_through = collection.bricks.through.objects.get(brick=brick_id)
        except (KeyError, BrickInCollectionQuantity.DoesNotExist):
            collection.bricks.add(brick, through_defaults={"quantity": qty})
        else:
            brick_through.quantity = min(brick_through.quantity + qty, 10000)
            brick_through.save()
    return HttpResponseRedirect(reverse('collection', args=()))


def del_set(request, set_id):
    lego_set = get_object_or_404(LegoSet, id=set_id)
    try:
        qty = int(request.POST.get('quantity', False))
    except:
        return HttpResponseRedirect(reverse('collection', args=()))
    else:
        logged_user = request.user
        collection = UserCollection.objects.get(userid=logged_user.id)
        if qty > 0:
            try:
                set_through = collection.sets.through.objects.get(id=set_id)
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
    collection = UserCollection.objects.get(userid=logged_user.id)
    if qty > 0:
        try:
            brick_through = collection.bricks.through.objects.get(brickset_id=brick_id)
        except (KeyError, BrickInCollectionQuantity.DoesNotExist):
            collection.bricks.add(brick, through_defaults={"quantity": qty})
        else:
            if brick_through.quantity <= qty:
                collection.bricks.remove(brick)
            else:
                brick_through.quantity -= qty
                brick_through.save()
    return HttpResponseRedirect(reverse('collection', args=()))


def convert(request, set_id):
    brickset = get_object_or_404(LegoSet, id=set_id)
    qty = int(request.POST.get('quantity', False))
    logged_user = request.user
    collection = UserCollection.objects.get(userid=logged_user.id)
    if qty > 0:
        try:
            set_through = collection.sets.through.objects.get(brickset_id=set_id)
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


def index(request):
    return render(request, 'bsf/index.html')


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
