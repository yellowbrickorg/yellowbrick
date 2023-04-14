from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail, BadHeaderError
from django.db.models.query_utils import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.template import loader
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views.generic import ListView, DetailView

from .forms import NewUserForm
from .models import Brick, LegoSet, BrickInCollectionQuantity, SetInCollectionQuantity, BrickInSetQuantity
from .models import UserCollection, User


def collection(request):
    logged_user = request.user
    if logged_user.is_authenticated:
        user_collection = UserCollection.objects.get(user=logged_user)
        if user_collection:
            context = {
                'user_sets': user_collection.sets.through.objects.all().filter(collection=user_collection),
                'user_bricks': user_collection.bricks.through.objects.all().filter(collection=user_collection),
            }
        else:
            context = {
                'user_sets': [],
                'user_bricks': [],
            }
        template = loader.get_template('bsf/collection.html')
        return HttpResponse(template.render(context, request))
    else:
        messages.info(request, "You need to be logged in to access collections.")
        return redirect('login')


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
            brick_through = collection.bricks.through.objects.get(collection=collection, brick_id=brick_id)
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
    sets_of_user = SetInCollectionQuantity.objects.filter(collection=collection)
    bricks_of_user = BrickInCollectionQuantity.objects.filter(collection=collection)
    if qty > 0:
        try:
            set_through = sets_of_user.get(brick_set_id=id)
        except (KeyError, SetInCollectionQuantity.DoesNotExist):
            return HttpResponseRedirect(reverse('collection', args=()))
        else:
            real_qty = min(set_through.quantity, qty)
            brickinset_through = brickset.bricks.through.objects.all()
            for brickth in brickinset_through:
                try:
                    brick_through = bricks_of_user.get(brick_id=brickth.brick.brick_id)
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


def check_set(all_users_bricks, lego_set: LegoSet, single_diff=0, general_diff=0):
    for brick_data in BrickInSetQuantity.objects.filter(brick_set=lego_set):
        q_needed = brick_data.quantity
        q_collected = all_users_bricks[brick_data.brick]
        diff = q_needed - q_collected

        if diff > single_diff:
            return False

        general_diff -= max(0, diff)
        if general_diff < 0:
            return False
    return True


def get_dict_of_users_bricks(user: User, all_users_bricks=None):
    users_collection = UserCollection.objects.get(user=user)

    for brick_data in BrickInCollectionQuantity.objects.filter(collection=users_collection):
        q = brick_data.quantity
        if brick_data.brick in all_users_bricks:
            all_users_bricks[brick_data.brick] += q
        else:
            all_users_bricks[brick_data.brick] = q
    return all_users_bricks


def get_dict_of_users_bricks_from_sets(user: User, all_users_bricks=None):
    users_collection = UserCollection.objects.get(user=user)

    for set_data in SetInCollectionQuantity.objects.filter(collection=users_collection):
        users_set = set_data.brick_set
        for brick_data in BrickInSetQuantity.objects.filter(brick_set=users_set):
            q = brick_data.quantity
            if brick_data.brick in all_users_bricks:
                all_users_bricks[brick_data.brick] += q
            else:
                all_users_bricks[brick_data.brick] = q
    return all_users_bricks


def get_viable_sets(user: User, single_diff=0, general_diff=0):
    """
    Args:
        user: nazwa uzytkowanika
        single_diff: różnica mówiąca, ile klocków każdego rodzaju może nam brakować w danym zestawie
        general_diff: różnica mówiąca, ile klocków w sumie może nam brakować w danym zestawie
    """

    all_users_bricks = {}
    all_users_bricks = get_dict_of_users_bricks(user, all_users_bricks)
    all_users_bricks = get_dict_of_users_bricks_from_sets(user, all_users_bricks)

    viable_sets = []
    for lego_set in LegoSet.objects.all():
        if check_set(all_users_bricks, lego_set, single_diff, general_diff):
            viable_sets.append(lego_set)

    return viable_sets


def filter_collection(request):
    try:
        logged_user = request.user
        single_diff = int(request.POST.get('single_diff', False))
        general_diff = int(request.POST.get('general_diff', False))
    except:
        return HttpResponseRedirect(reverse('filter', args=()))
    else:
        template = loader.get_template('bsf/filter.html')
        context = {'viable_sets': get_viable_sets(logged_user, single_diff, general_diff)}
        return HttpResponse(template.render(context, request))


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


class SetDetailView(DetailView):
    model = LegoSet
    template_name = 'bsf/legoset_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bricks_in_set'] = BrickInSetQuantity.objects.filter(brick_set_id=self.kwargs['pk'])
        return context


def login(request):
    if request.user.is_authenticated:
        messages.error(request, "Already logged in. Logout to change account.")
        return redirect("index")
    elif request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("index")
            else:
                messages.error(request, "Username or password is incorrect.")
        else:
            messages.error(request, "Username or password is incorrect.")
    form = AuthenticationForm()
    return render(request=request, template_name="registration/login.html", context={"login_form": form})


def logout(request):
    auth_logout(request)
    messages.info(request, "Succesfully logged out.")
    return redirect('index')


def signup(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            new_collection = UserCollection(user=user)
            new_collection.save()
            messages.success(request, "Registration successful.")
            return redirect("index")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render(request=request, template_name="registration/signup.html", context={"register_form": form})


def password_reset(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "registration/password_reset_email.txt"
                    c = {
                        "email": user.email,
                        'domain': '127.0.0.1:8000',
                        'site_name': 'Website',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, 'password_reset@yellowbrick.com', [user.email], fail_silently=False)
                    except BadHeaderError:
                        messages.error(request, "Invalid header found.")
                        return redirect("index")
                    messages.info(request, "An email with reset password link has been sent.")
                    return redirect("index")
            messages.error(request, "An account with such email does not exist.")
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="registration/password_reset.html",
                  context={"password_reset_form": password_reset_form})
