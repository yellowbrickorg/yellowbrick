import sys

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
from django.views.generic import ListView, DetailView, View

from .forms import NewUserForm
from .models import (
    Brick,
    LegoSet,
    BrickInCollectionQuantity,
    SetInCollectionQuantity,
    BrickInSetQuantity,
    SetInWishlistQuantity,
    BrickInWishlistQuantity,
    ExchangeOffer,
    BrickInOfferQuantity,
    SetInOfferQuantity,
    Side,
    Wishlist,
)
from .models import UserCollection, User


def base_context(request):
    logged_user = request.user
    if not logged_user.is_authenticated:
        return {}

    user_sets_wishlist = SetInWishlistQuantity.objects.filter(user=logged_user, side=1)
    user_bricks_wishlist = BrickInWishlistQuantity.objects.filter(
        user=logged_user, side=1
    )
    user_sets_offers = SetInWishlistQuantity.objects.filter(user=logged_user, side=0)
    user_bricks_offers = BrickInWishlistQuantity.objects.filter(
        user=logged_user, side=0
    )

    context = {
        "user_sets_wishlist": user_sets_wishlist,
        "user_bricks_wishlist": user_bricks_wishlist,
        "user_sets_offers": user_sets_offers,
        "user_bricks_offers": user_bricks_offers,
        "logged_user": logged_user,
    }
    return context


def wishlist(request):
    logged_user = request.user
    if logged_user.is_authenticated:
        context = base_context(request)
        template = loader.get_template("bsf/wishlist.html")
        return HttpResponse(template.render(context, request))
    else:
        messages.info(request, "You need to be logged in to access collections.")
        return redirect("login")


def collection(request):
    logged_user = request.user
    if logged_user.is_authenticated:
        user_collection = UserCollection.objects.get(user=logged_user)
        if user_collection:
            user_sets = user_collection.sets.through.objects.all().filter(
                collection=user_collection
            )
            user_bricks = user_collection.bricks.through.objects.all().filter(
                collection=user_collection
            )
        else:
            user_sets = []
            user_bricks = []

        context = base_context(request)
        context.update(
            {
                "user_sets": user_sets,
                "user_bricks": user_bricks,
                "logged_user": logged_user,
            }
        )
        template = loader.get_template("bsf/collection.html")
        return HttpResponse(template.render(context, request))
    else:
        messages.info(request, "You need to be logged in to access collections.")
        return redirect("login")


def add_set(request, id):
    lego_set = get_object_or_404(LegoSet, id=id)
    try:
        qty = int(request.POST.get("quantity", False))
    except:
        return HttpResponseRedirect(reverse("collection", args=()))
    else:
        logged_user = request.user
        collection = UserCollection.objects.get(user=logged_user)
        if qty > 0:
            try:
                set_through = collection.sets.through.objects.get(
                    brick_set=lego_set, collection=collection
                )
            except:
                collection.sets.add(lego_set, through_defaults={"quantity": qty})
            else:
                set_through.quantity = min(set_through.quantity + qty, 100)
                set_through.save()
        messages.success(
            request,
            f"Added {qty} set(s) with set number {lego_set.id} to " f"collection.",
        )
        return HttpResponseRedirect(reverse("collection", args=()))


def add_set_to_wishlist(request, id, side):
    lego_set = get_object_or_404(LegoSet, id=id)
    try:
        qty = int(request.POST.get("quantity", False))
    except:
        return redirect(request.POST.get("next", "/"))
    else:
        logged_user = request.user
        wishlist = SetInWishlistQuantity.objects.filter(user=logged_user)
        if qty > 0:
            try:
                set_through = wishlist.get(legoset=lego_set, side=side)
            except:
                set_through = SetInWishlistQuantity(
                    user=logged_user, legoset=lego_set, quantity=qty, side=side
                )
                set_through.save()
            else:
                if side == Side.OFFERED:
                    collection = UserCollection.objects.get(user=logged_user)
                    sets_in_collection = SetInCollectionQuantity.objects.get(
                        brick_set=lego_set, collection=collection
                    )
                    if set_through.quantity + qty > sets_in_collection.quantity:
                        messages.error(request, "Can't offer more sets than you have.")
                        return redirect(request.POST.get("next", "/"))
                set_through.quantity = min(set_through.quantity + qty, 100)
                set_through.save()
        if side == 0:
            messages.success(
                request,
                f"Added {qty} set(s) with set number {lego_set.id} to "
                f"offered list.",
            )
        else:
            messages.success(
                request,
                f"Added {qty} set(s) with set number {lego_set.id} to " f"wishlist.",
            )
        return redirect(request.POST.get("next", "/"))


def add_brick(request, brick_id):
    brick = get_object_or_404(Brick, brick_id=brick_id)
    qty = int(request.POST.get("quantity", False))
    logged_user = request.user
    collection = UserCollection.objects.get(user=logged_user)
    if qty > 0:
        try:
            brick_through = collection.bricks.through.objects.get(
                collection=collection, brick_id=brick_id
            )
        except:
            collection.bricks.add(brick, through_defaults={"quantity": qty})
        else:
            brick_through.quantity = min(brick_through.quantity + qty, 10000)
            brick_through.save()
    messages.success(
        request,
        f"Added {qty} brick(s) with part number {brick.part_num} " f"to collection.",
    )
    return HttpResponseRedirect(reverse("collection", args=()))


def add_brick_to_wishlist(request, id, side):
    brick = get_object_or_404(Brick, brick_id=id)
    try:
        qty = int(request.POST.get("quantity", False))
    except:
        return redirect(request.POST.get("next", "/"))
    else:
        logged_user = request.user
        wishlist = BrickInWishlistQuantity.objects.filter(user=logged_user)
        if qty > 0:
            try:
                brick_through = wishlist.get(brick=brick, side=side)
            except:
                brick_through = BrickInWishlistQuantity(
                    user=logged_user, brick=brick, quantity=qty, side=side
                )
                brick_through.save()
            else:
                collection = UserCollection.objects.get(user=logged_user)
                bricks_in_collection = BrickInCollectionQuantity.objects.get(
                    brick=brick, collection=collection
                )
                if brick_through.quantity + qty > bricks_in_collection.quantity:
                    messages.error(request, "Can't offer more bricks than you have.")
                    return redirect(request.POST.get("next", "/"))
                brick_through.quantity = min(brick_through.quantity + qty, 10000)
                brick_through.save()
        if side == 0:
            messages.success(
                request,
                f"Added {qty} brick(s) with part number {brick.part_num} to "
                f"offered list.",
            )
        else:
            messages.success(
                request,
                f"Added {qty} brick(s) with part number {brick.part_num} to "
                f"wishlist.",
            )
        return redirect(request.POST.get("next", "/"))


def del_set(request, id):
    lego_set = get_object_or_404(LegoSet, id=id)
    try:
        qty = int(request.POST.get("quantity", False))
    except:
        return HttpResponseRedirect(reverse("collection", args=()))
    else:
        logged_user = request.user
        collection = UserCollection.objects.get(user=logged_user)
        if qty > 0:
            try:
                set_through = collection.sets.through.objects.get(
                    brick_set_id=id, collection=collection
                )
            except (KeyError, SetInCollectionQuantity.DoesNotExist):
                collection.sets.add(lego_set, through_defaults={"quantity": qty})
            else:
                if set_through.quantity <= qty:
                    collection.sets.remove(lego_set)
                else:
                    set_through.quantity -= qty
                    set_through.save()
        messages.success(
            request,
            f"Removed {qty} set(s) with set number {lego_set.id} from " f"collection.",
        )
        return HttpResponseRedirect(reverse("collection", args=()))


def del_set_from_wishlist(request, id, side):
    lego_set = get_object_or_404(LegoSet, id=id)
    try:
        qty = int(request.POST.get("quantity", False))
    except:
        return redirect(request.POST.get("next", "/"))
    else:
        logged_user = request.user
        wishlist = SetInWishlistQuantity.objects.filter(user=logged_user)
        if qty > 0:
            try:
                set_through = wishlist.get(legoset=lego_set, side=side)
            except:
                return redirect(request.POST.get("next", "/"))
            else:
                if set_through.quantity <= qty:
                    set_through.delete()
                else:
                    set_through.quantity -= qty
                    set_through.save()
        if side == 0:
            messages.success(
                request,
                f"Removed {qty} set(s) with set number {lego_set.id} from "
                f"offered list.",
            )
        else:
            messages.success(
                request,
                f"Removed {qty} set(s) with set number {lego_set.id} from "
                f"wishlist.",
            )

        return redirect(request.POST.get("next", "/"))


def del_brick(request, brick_id):
    brick = get_object_or_404(Brick, brick_id=brick_id)
    qty = int(request.POST.get("quantity", False))
    logged_user = request.user
    collection = UserCollection.objects.get(user=logged_user)
    if qty > 0:
        try:
            brick_through = collection.bricks.through.objects.get(
                brick_id=brick_id, collection=collection
            )
        except (KeyError, BrickInCollectionQuantity.DoesNotExist):
            collection.bricks.add(brick, through_defaults={"quantity": qty})
        else:
            if brick_through.quantity <= qty:
                collection.bricks.remove(brick)
            else:
                brick_through.quantity -= qty
                brick_through.save()
    messages.success(
        request,
        f"Removed {qty} brick(s) with part number"
        f" {brick.part_num} from collection.",
    )
    return HttpResponseRedirect(reverse("collection", args=()))


def del_brick_from_wishlist(request, brick_id, side):
    brick = get_object_or_404(Brick, brick_id=brick_id)
    qty = int(request.POST.get("quantity", False))
    logged_user = request.user
    if qty > 0:
        wishlist = BrickInWishlistQuantity.objects.filter(user=logged_user)
        try:
            brick_through = wishlist.get(brick_id=brick_id, side=side)
        except (KeyError, BrickInCollectionQuantity.DoesNotExist):
            return redirect(request.POST.get("next", "/"))
        else:
            if brick_through.quantity <= qty:
                brick_through.delete()
            else:
                brick_through.quantity -= qty
                brick_through.save()
    if side == 0:
        messages.success(
            request,
            f"Removed {qty} brick(s) with part number {brick.part_num} from "
            f"offered list.",
        )
    else:
        messages.success(
            request,
            f"Removed {qty} brick(s) with part number {brick.part_num} from "
            f"wishlist.",
        )
    return redirect(request.POST.get("next", "/"))


def convert(request, id):
    brickset = get_object_or_404(LegoSet, id=id)
    qty = int(request.POST.get("quantity", False))
    logged_user = request.user
    collection = UserCollection.objects.get(user=logged_user)
    sets_of_user = SetInCollectionQuantity.objects.filter(collection=collection)
    bricks_of_user = BrickInCollectionQuantity.objects.filter(collection=collection)
    if qty > 0:
        try:
            set_through = sets_of_user.get(brick_set_id=id)
        except (KeyError, SetInCollectionQuantity.DoesNotExist):
            return HttpResponseRedirect(reverse("collection", args=()))
        else:
            real_qty = min(set_through.quantity, qty)
            brickinset_through = brickset.bricks.through.objects.filter(
                brick_set=brickset
            )
            for brickth in brickinset_through:
                try:
                    brick_through = bricks_of_user.get(
                        brick_id=brickth.brick.brick_id, collection=collection
                    )
                except (KeyError, BrickInCollectionQuantity.DoesNotExist):
                    collection.bricks.add(
                        brickth.brick,
                        through_defaults={"quantity": real_qty * brickth.quantity},
                    )
                else:
                    brick_through.quantity = min(
                        brick_through.quantity + real_qty * brickth.quantity, 10000
                    )
                    brick_through.save()
            if set_through.quantity <= qty:
                collection.sets.remove(brickset)
            else:
                set_through.quantity -= qty
                set_through.save()
    messages.success(
        request,
        f"Successfully converted {qty} set(s) with part number"
        f" {brickset.id} to loose bricks.",
    )
    return HttpResponseRedirect(reverse("collection", args=()))


def check_set(
    all_users_bricks,
    lego_set: LegoSet,
):
    max_diff = 0
    gdiff = 0

    for brick_data in BrickInSetQuantity.objects.filter(brick_set=lego_set):
        q_needed = brick_data.quantity
        q_collected = all_users_bricks.get(brick_data.brick, 0)
        diff = q_needed - q_collected
        max_diff = max(max_diff, diff)
        gdiff += max(0, diff)

    return max_diff, gdiff


def get_dict_of_users_bricks(user: User, all_users_bricks=None):
    users_collection = UserCollection.objects.get(user=user)

    for brick_data in BrickInCollectionQuantity.objects.filter(
        collection=users_collection
    ):
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
            q = brick_data.quantity * set_data.quantity
            if brick_data.brick in all_users_bricks:
                all_users_bricks[brick_data.brick] += q
            else:
                all_users_bricks[brick_data.brick] = q
    return all_users_bricks


def get_viable_sets(user: User, single_diff=sys.maxsize, general_diff=sys.maxsize):
    """
    Args:
        user: nazwa uzytkowanika
        single_diff: różnica mówiąca, ile klocków każdego rodzaju może nam brakować w danym zestawie
        general_diff: różnica mówiąca, ile klocków w sumie może nam brakować w danym zestawie
    """
    viable_sets = []

    if single_diff == general_diff == sys.maxsize:
        for lego_set in LegoSet.objects.all():
            viable_sets.append(
                {"lego_set": lego_set, "single_diff": "-", "general_diff": "-"}
            )
        return viable_sets

    all_users_bricks = {}
    all_users_bricks = get_dict_of_users_bricks(user, all_users_bricks)
    all_users_bricks = get_dict_of_users_bricks_from_sets(user, all_users_bricks)

    for lego_set in LegoSet.objects.all():
        diff, gdiff = check_set(all_users_bricks, lego_set)
        if diff <= single_diff and gdiff <= general_diff:
            viable_sets.append(
                {
                    "lego_set": lego_set,
                    "single_diff": "-" if single_diff == sys.maxsize else diff,
                    "general_diff": "-" if general_diff == sys.maxsize else gdiff,
                }
            )

    return viable_sets


def maxsize_if_empty(_str):
    return sys.maxsize if _str == "" else int(_str)


def filter_collection(request):
    logged_user = request.user

    if request.method == "POST":
        single_diff = maxsize_if_empty(request.POST.get("single_diff"))
        general_diff = maxsize_if_empty(request.POST.get("general_diff"))
    else:
        single_diff = general_diff = sys.maxsize

    template = loader.get_template("bsf/filter.html")
    context = base_context(request)
    context.update(
        {"viable_sets": get_viable_sets(logged_user, single_diff, general_diff)}
    )
    return HttpResponse(template.render(context, request))


def index(request):
    return render(request, "bsf/index.html", context=base_context(request))


def brick_list(request):
    bricks = Brick.objects.all()
    context = base_context(request)
    context.update({"bricks": bricks})
    return render(request, "bsf/brick_list.html", context)


class BrickDetailView(DetailView):
    model = Brick
    template_name = "bsf/brick_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["related_sets"] = BrickInSetQuantity.objects.filter(
            brick=self.kwargs["pk"]
        )
        return context


class ContextListView(ListView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(base_context(self.request))
        return context


class ContextDetailView(DetailView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(base_context(self.request))
        return context


class BrickListView(ContextListView):
    paginate_by = 15
    model = Brick


class SetListView(ContextListView):
    paginate_by = 15
    model = LegoSet


class FilterListView(ContextListView):
    paginate_by = 15
    model = LegoSet


class SetDetailView(ContextDetailView):
    model = LegoSet
    template_name = "bsf/legoset_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bricks_in_set"] = BrickInSetQuantity.objects.filter(
            brick_set_id=self.kwargs["pk"]
        )
        return context


def login(request):
    if request.user.is_authenticated:
        messages.error(request, "Already logged in. Logout to change account.")
        return redirect("index")
    elif request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
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
    context = base_context(request)
    context["login_form"] = form
    return render(
        request=request,
        template_name="registration/login.html",
        context=context,
    )


def logout(request):
    auth_logout(request)
    messages.info(request, "Succesfully logged out.")
    return redirect("index")


def signup(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            UserCollection.objects.create(user=user)
            Wishlist.objects.create(user=user)
            messages.success(request, "Registration successful.")
            return redirect("index")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    context = base_context(request)
    context["register_form"] = form
    return render(
        request=request,
        template_name="registration/signup.html",
        context=context,
    )


def password_reset(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data["email"]
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "registration/password_reset_email.txt"
                    c = {
                        "email": user.email,
                        "domain": "127.0.0.1:8000",
                        "site_name": "Website",
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        "token": default_token_generator.make_token(user),
                        "protocol": "http",
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(
                            subject,
                            email,
                            "password_reset@yellowbrick.com",
                            [user.email],
                            fail_silently=False,
                        )
                    except BadHeaderError:
                        messages.error(request, "Invalid header found.")
                        return redirect("index")
                    messages.info(
                        request, "An email with reset password link has been sent."
                    )
                    return redirect("index")
            messages.error(request, "An account with such email does not exist.")
    password_reset_form = PasswordResetForm()
    context = base_context(request)
    context["password_reset_form"] = password_reset_form
    return render(
        request=request,
        template_name="registration/password_reset.html",
        context=context,
    )


def generate_possible_offers(logged_user, other=None):
    """
    We are looking for users with whom we could trade bricks. They are sorted
    by min(what we can offer, what we can receive)
    """

    wanted_bricks = logged_user.wishlist_bricks.filter(side=Side.WANTED)
    offered_bricks = logged_user.wishlist_bricks.filter(side=Side.OFFERED)
    wanted_sets = logged_user.wishlist_sets.filter(side=Side.WANTED)
    offered_sets = logged_user.wishlist_sets.filter(side=Side.OFFERED)

    possible_offers = []
    if other is not None:
        possible_offers = [
            {
                "user": User.objects.get(username=other),
                "brick_quantity_offered": [],
                "brick_quantity_wanted": [],
                "set_quantity_offered": [],
                "set_quantity_wanted": [],
                "sum_offered": 0,
                "sum_wanted": 0,
            }
        ]
    else:
        for u in User.objects.all():
            if u != logged_user:
                possible_offers.append(
                    {
                        "user": u,
                        "brick_quantity_offered": [],
                        "brick_quantity_wanted": [],
                        "set_quantity_offered": [],
                        "set_quantity_wanted": [],
                        "sum_offered": 0,
                        "sum_wanted": 0,
                    }
                )

    for p_o in possible_offers:
        other_wanted_bricks = p_o["user"].wishlist_bricks.filter(side=Side.WANTED)
        other_offered_bricks = p_o["user"].wishlist_bricks.filter(side=Side.OFFERED)
        other_wanted_sets = p_o["user"].wishlist_sets.filter(side=Side.WANTED)
        other_offered_sets = p_o["user"].wishlist_sets.filter(side=Side.OFFERED)

        for brick_wanted in other_wanted_bricks:
            """Can we offer 'brick_wanted'"""
            if offered_bricks.filter(brick=brick_wanted.brick).exists():
                bricks_to_trade = min(
                    offered_bricks.filter(brick=brick_wanted.brick).get().quantity,
                    brick_wanted.quantity,
                )
                p_o["brick_quantity_offered"].append(
                    {"brick": brick_wanted.brick, "quantity": bricks_to_trade}
                )
                p_o["sum_offered"] += bricks_to_trade

        for brick_offered in other_offered_bricks:
            """Do we want 'brick_offered'"""
            if wanted_bricks.filter(brick=brick_offered.brick).exists():
                bricks_to_trade = min(
                    wanted_bricks.filter(brick=brick_offered.brick).get().quantity,
                    brick_offered.quantity,
                )
                p_o["brick_quantity_wanted"].append(
                    {"brick": brick_offered.brick, "quantity": bricks_to_trade}
                )
                p_o["sum_wanted"] += bricks_to_trade

        for set_wanted in other_wanted_sets:
            """Can we offer 'set_wanted'"""
            if offered_sets.filter(legoset=set_wanted.legoset).exists():
                sets_to_trade = min(
                    offered_sets.filter(legoset=set_wanted.legoset).get().quantity,
                    set_wanted.quantity,
                )
                p_o["set_quantity_offered"].append(
                    {"legoset": set_wanted.legoset, "quantity": sets_to_trade}
                )
                p_o["sum_offered"] += (
                    sets_to_trade * set_wanted.legoset.number_of_bricks()
                )

        for set_offered in other_offered_sets:
            """Do we want 'set_offered'"""
            if wanted_sets.filter(legoset=set_offered.legoset).exists():
                sets_to_trade = min(
                    wanted_sets.filter(legoset=set_offered.legoset).get().quantity,
                    set_offered.quantity,
                )
                p_o["set_quantity_wanted"].append(
                    {"legoset": set_offered.legoset, "quantity": sets_to_trade}
                )
                p_o["sum_wanted"] += (
                    sets_to_trade * set_offered.legoset.number_of_bricks()
                )

    possible_offers = [
        u for u in possible_offers if u["sum_offered"] + u["sum_wanted"] > 0
    ]
    sorted(
        possible_offers,
        key=lambda p_o: p_o["sum_offered"] + p_o["sum_wanted"],
        reverse=True,
    )
    return possible_offers


def exchange(request):
    logged_user = request.user
    if not logged_user.is_authenticated:
        messages.error(request, "You need to be logged in to access brick exchange.")
        return redirect("index")

    possible_offers = generate_possible_offers(logged_user)
    context = base_context(request)
    context.update(
        {
            "possible_offers": possible_offers,
        }
    )
    return render(
        request=request,
        context=context,
        template_name="bsf/exchange.html",
    )


def exchange_make_offer(request):
    logged_user = request.user
    if not logged_user.is_authenticated:
        messages.error(request, "You need to be logged in to access brick exchange.")
        return redirect("index")
    other_user = request.POST.get("other_user")
    if other_user is None:
        return redirect("index")
    other_user = User.objects.get(username=other_user)
    possible_offers = generate_possible_offers(logged_user, other_user)

    new_offer = ExchangeOffer(offer_author=request.user, offer_receiver=other_user)

    bricks_in_offer = []
    sets_in_offer = []

    for brick in possible_offers[0]["brick_quantity_offered"]:
        """Bricks offered"""
        amount = request.POST.get("offer_brick_" + str(brick["brick"].pk))
        if amount == "":
            continue
        amount = int(amount)
        if amount > 0:
            bioq = BrickInOfferQuantity(
                offer=new_offer,
                brick=brick["brick"],
                quantity=amount,
                side=Side.OFFERED,
            )
            bricks_in_offer.append(bioq)

    for brick in possible_offers[0]["brick_quantity_wanted"]:
        """Bricks wanted"""
        amount = request.POST.get("want_brick_" + str(brick["brick"].pk))
        if amount == "":
            continue
        amount = int(amount)
        if amount > 0:
            bioq = BrickInOfferQuantity(
                offer=new_offer, brick=brick["brick"], quantity=amount, side=Side.WANTED
            )
            bricks_in_offer.append(bioq)

    for legoset in possible_offers[0]["set_quantity_offered"]:
        """Sets offered"""
        amount = request.POST.get("offer_set_" + str(legoset["legoset"].pk))
        if amount == "":
            continue
        amount = int(amount)
        if amount > 0:
            sioq = SetInOfferQuantity(
                offer=new_offer,
                legoset=legoset["legoset"],
                quantity=amount,
                side=Side.OFFERED,
            )
            bricks_in_offer.append(sioq)

    for legoset in possible_offers[0]["set_quantity_wanted"]:
        """Sets wanted"""
        amount = request.POST.get("want_set_" + str(legoset["legoset"].pk))
        if amount == "":
            continue
        amount = int(amount)
        if amount > 0:
            sioq = SetInOfferQuantity(
                offer=new_offer,
                legoset=legoset["legoset"],
                quantity=amount,
                side=Side.WANTED,
            )
            bricks_in_offer.append(sioq)

    if len(bricks_in_offer) + len(sets_in_offer) == 0:
        messages.error(request, "Can't submit an empty offer.")
        return redirect("exchange")

    new_offer.save()
    for bioq in bricks_in_offer:
        bioq.save()

    for sioq in sets_in_offer:
        sioq.save()

    """ Send an email notifying the other person about the new offer """
    subject = "New offer"
    email_template_name = "bsf/new_offer_notification.txt"
    c = {
        "email": other_user.email,
        "domain": "127.0.0.1:8000",
        "user": other_user,
        "author": logged_user,
        "protocol": "http",
    }
    email = render_to_string(email_template_name, c)
    try:
        send_mail(
            subject,
            email,
            "exchange@yellowbrick.com",
            [other_user.email],
            fail_silently=False,
        )
    except BadHeaderError:
        pass

    return redirect("exchange_offers")


def get_button_action_for(user, offer):
    is_author = offer.offer_author == user

    match offer.author_state, offer.receiver_state:
        case ExchangeOffer.Status.EXCHANGED, ExchangeOffer.Status.EXCHANGED:
            return None
        case ExchangeOffer.Status.ACCEPTED, ExchangeOffer.Status.PENDING:
            if is_author:
                return None
            else:
                return "Accept"
        case ExchangeOffer.Status.ACCEPTED, ExchangeOffer.Status.ACCEPTED:
            return "Exchange"
        case ExchangeOffer.Status.EXCHANGED, ExchangeOffer.Status.ACCEPTED:
            return None if is_author else "Exchange"
        case ExchangeOffer.Status.ACCEPTED, ExchangeOffer.Status.EXCHANGED:
            return None if not is_author else "Exchange"


def exchange_offers(request):
    logged_user = request.user
    if not logged_user.is_authenticated:
        messages.error(request, "You need to be logged in to access brick exchange.")
        return redirect("index")

    offers_made = ExchangeOffer.objects.filter(offer_author=logged_user)
    offers_received = ExchangeOffer.objects.filter(offer_receiver=logged_user)

    offers_made_context = []
    offers_received_context = []

    for offer in offers_made:
        offers_made_context.append(
            {
                "offer": offer,
                "offered_sets": SetInOfferQuantity.objects.filter(
                    offer=offer, side=Side.OFFERED
                ),
                "offered_bricks": BrickInOfferQuantity.objects.filter(
                    offer=offer, side=Side.OFFERED
                ),
                "wanted_sets": SetInOfferQuantity.objects.filter(
                    offer=offer, side=Side.WANTED
                ),
                "wanted_bricks": BrickInOfferQuantity.objects.filter(
                    offer=offer, side=Side.WANTED
                ),
                "button_action": get_button_action_for(logged_user, offer),
            }
        )

    for offer in offers_received:
        offers_received_context.append(
            {
                "offer": offer,
                "offered_sets": SetInOfferQuantity.objects.filter(
                    offer=offer, side=Side.OFFERED
                ),
                "offered_bricks": BrickInOfferQuantity.objects.filter(
                    offer=offer, side=Side.OFFERED
                ),
                "wanted_sets": SetInOfferQuantity.objects.filter(
                    offer=offer, side=Side.WANTED
                ),
                "wanted_bricks": BrickInOfferQuantity.objects.filter(
                    offer=offer, side=Side.WANTED
                ),
                "button_action": get_button_action_for(logged_user, offer),
            }
        )

    context = base_context(request)
    context.update(
        {
            "offers_made": offers_made_context,
            "offers_received": offers_received_context,
        }
    )

    return render(
        request=request,
        template_name="bsf/exchange_offers.html",
        context=context,
    )


def exchange_items(request, offer):
    receivers_collection = UserCollection.objects.get(user=offer.offer_receiver)
    receivers_wishlist = Wishlist.objects.get(user=offer.offer_receiver)
    authors_collection = UserCollection.objects.get(user=offer.offer_author)
    authors_wishlist = Wishlist.objects.get(user=offer.offer_author)

    for set_in_offer in SetInOfferQuantity.objects.filter(offer=offer):
        rel = 1 if set_in_offer.side == Side.OFFERED else -1
        receivers_collection.modify_set_quantity(
            set_in_offer.legoset, rel * set_in_offer.quantity
        )
        authors_collection.modify_set_quantity(
            set_in_offer.legoset, -rel * set_in_offer.quantity
        )

        receivers_wishlist.modify_sets_quantity(
            set_in_offer.legoset,
            -set_in_offer.quantity,
            Side.WANTED if rel == 1 else Side.OFFERED,
        )
        authors_wishlist.modify_sets_quantity(
            set_in_offer.legoset,
            -set_in_offer.quantity,
            Side.OFFERED if rel == 1 else Side.WANTED,
        )

    for brick_in_offer in BrickInOfferQuantity.objects.filter(offer=offer):
        rel = 1 if brick_in_offer.side == Side.OFFERED else -1
        receivers_collection.modify_brick_quantity(
            brick_in_offer.brick, rel * brick_in_offer.quantity
        )
        authors_collection.modify_brick_quantity(
            brick_in_offer.brick, -rel * brick_in_offer.quantity
        )

        receivers_wishlist.modify_bricks_quantity(
            brick_in_offer.brick,
            -brick_in_offer.quantity,
            Side.WANTED if rel == 1 else Side.OFFERED,
        )
        authors_wishlist.modify_bricks_quantity(
            brick_in_offer.brick,
            -brick_in_offer.quantity,
            Side.OFFERED if rel == 1 else Side.WANTED,
        )

    offer.exchanged = True

    messages.info(request, "Items exchanged!")


def exchange_offer_continue(request):
    logged_user = request.user
    if not logged_user.is_authenticated:
        messages.error(request, "You need to be logged in to access brick exchange.")
        return redirect("exchange_offers")

    offer_id = request.POST.get("offer_accepted")
    if offer_id is None:
        messages.error(request, "Offer not found.")
        return redirect("exchange_offers")

    offer = ExchangeOffer.objects.get(pk=int(offer_id))
    is_author = offer.offer_author == logged_user

    match offer.author_state, offer.receiver_state:
        case _, ExchangeOffer.Status.PENDING:
            if not is_author:
                offer.receiver_state = ExchangeOffer.Status.ACCEPTED
                messages.success(request, "Offer accepted!")
        case _, ExchangeOffer.Status.ACCEPTED:
            if is_author:
                offer.author_state = ExchangeOffer.Status.EXCHANGED
            else:
                offer.receiver_state = ExchangeOffer.Status.EXCHANGED
            messages.success(request, "Items marked as exchanged successfully!")
        case ExchangeOffer.Status.ACCEPTED, ExchangeOffer.Status.EXCHANGED:
            if is_author:
                offer.author_state = ExchangeOffer.Status.EXCHANGED

    if (offer.author_state, offer.receiver_state) == (
        ExchangeOffer.Status.EXCHANGED,
        ExchangeOffer.Status.EXCHANGED,
    ):
        exchange_items(request, offer)
        messages.success(
            request, "Exchange completed and updated in system successfully!"
        )

    offer.save()

    return redirect("exchange_offers")


def exchange_offer_accepted(request):
    logged_user = request.user
    if not logged_user.is_authenticated:
        messages.error(request, "You need to be logged in to access brick exchange.")
        return redirect("index")

    offer_id = request.POST.get("offer_accepted")
    if offer_id is None:
        messages.error(request, "Offer not found.")
        return redirect("index")

    offer = ExchangeOffer.objects.get(pk=int(offer_id))

    exchange_items(offer)

    return redirect("index")


def exchange_delete_offer(request):
    logged_user = request.user
    if not logged_user.is_authenticated:
        messages.error(request, "You need to be logged in to access brick exchange.")
        return redirect("index")

    offer_id = request.POST.get("offer_id")
    if offer_id is None:
        messages.error(request, "Offer not found.")
        return redirect("index")

    offer = ExchangeOffer.objects.get(pk=int(offer_id))
    bioq_set = BrickInOfferQuantity.objects.filter(offer=offer)
    sioq_set = SetInOfferQuantity.objects.filter(offer=offer)

    for bioq in bioq_set:
        bioq.delete()

    for sioq in sioq_set:
        sioq.delete()

    offer.delete()

    return redirect("exchange_offers")
