import sys

from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail, BadHeaderError
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.template import loader
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views.generic import ListView, DetailView
from django.db.models import Avg
from django.db.models import Q
from .forms import NewUserForm
from django.db.models import Max
from .models import (
    Brick,
    LegoSet,
    BrickInCollectionQuantity,
    SetInCollectionQuantity,
    BrickInSetQuantity,
    BrickStats,
)
from .models import UserCollection, User


def collection(request):
    logged_user = request.user
    if logged_user.is_authenticated:
        user_collection = UserCollection.objects.get(user=logged_user)
        set_themes = user_collection.sets.values_list("theme", flat=True).distinct()
        max_bricks = user_collection.sets.aggregate(
            max_bricks=Max("quantity_of_bricks")
        )["max_bricks"]

        if user_collection:
            theme = request.GET.get("theme")
            min_quantity = request.GET.get("start_quantity", 0)
            max_quantity = request.GET.get("end_quantity", max_bricks)

            if not min_quantity:
                min_quantity = 0
            else:
                min_quantity = int(min_quantity)

            if not max_quantity:
                max_quantity = sys.maxsize
            else:
                max_quantity = int(max_quantity)

            user_sets = user_collection.sets.through.objects.filter(
                collection=user_collection
            )
            if theme:
                user_sets = user_sets.filter(brick_set__theme=theme)

            if min_quantity <= max_quantity:
                user_sets = user_sets.filter(
                    brick_set__quantity_of_bricks__range=(min_quantity, max_quantity)
                )

            user_bricks = user_collection.bricks.through.objects.all().filter(
                collection=user_collection
            )
        else:
            user_sets = []
            user_bricks = []

        context = {
            "user_sets": user_sets,
            "user_bricks": user_bricks,
            "logged_user": logged_user,
            "set_themes": set_themes,
            "selected_theme": theme,
            "start_quantity": min_quantity,
            "end_quantity": max_quantity,
        }
        template = loader.get_template("bsf/collection.html")
        return HttpResponse(template.render(context, request))
    else:
        messages.info(request, "You need to be logged in to access collections.")
        return redirect("login")


class SetListView(ListView):
    paginate_by = 15
    model = LegoSet
    set_themes = LegoSet.objects.values_list("theme", flat=True).distinct()


def legoset_list(request):
    queryset = (
        LegoSet.objects.annotate(avg_rating=Avg("brickstats__likes"))
        .annotate(avg_time=Avg("brickstats__build_time"))
        .annotate(avg_age=Avg("brickstats__min_recommended_age"))
        .all()
    )

    max_bricks = queryset.aggregate(max_bricks=Max("quantity_of_bricks")).get(
        "max_bricks", 9999999
    )
    max_time = int(
        queryset.aggregate(max_time=Max("avg_time")).get("max_time", 9999999)
    )
    max_age = int(queryset.aggregate(max_age=Max("avg_age")).get("max_age", 9999999))

    set_themes = LegoSet.objects.values_list("theme", flat=True).distinct()

    start_quantity = zero_if_empty(request.GET.get("start_quantity"))
    end_quantity = default_if_empty(request.GET.get("end_quantity"), max_bricks)

    min_time = zero_if_empty(request.GET.get("min_time"))
    max_time = default_if_empty(request.GET.get("max_time"), max_time)

    min_age = zero_if_empty(request.GET.get("min_age"))
    max_age = default_if_empty(request.GET.get("max_age"), max_age)

    theme = request.GET.get("theme")

    if start_quantity <= end_quantity:
        queryset = queryset.filter(
            Q(quantity_of_bricks__range=(start_quantity, end_quantity)),
            Q(avg_time__range=(min_time, max_time)) | Q(avg_time__isnull=True),
            Q(avg_age__range=(min_age, max_age)) | Q(avg_age__isnull=True),
        )

    if theme:
        queryset = queryset.filter(theme=theme)

    paginator = Paginator(queryset, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "bsf/legoset_list.html",
        {
            "page_obj": page_obj,
            "start_quantity": start_quantity,
            "end_quantity": end_quantity,
            "min_time": min_time,
            "max_time": max_time,
            "min_age": min_age,
            "max_age": max_age,
            "set_themes": set_themes,
            "selected_theme": theme,
        },
    )


def add_review(request, id):
    lego_set = get_object_or_404(LegoSet, id=id)
    try:
        rating = int(request.POST.get("set_rating", False))
        age = int(request.POST.get("set_age", False))
        time = int(float(request.POST.get("set_time", False)) * 10)
    except:
        messages.error(
            request,
            f"Failed to add a review of {lego_set}",
        )
        return redirect(lego_set)
    else:
        logged_user = request.user
        BrickStats.objects.create(
            brick_set=lego_set,
            user=logged_user,
            likes=rating,
            min_recommended_age=age,
            build_time=time,
        )
        messages.success(
            request,
            f"Added review of {lego_set}.",
        )
        return redirect(lego_set)


def del_review(request, id):
    lego_set = get_object_or_404(LegoSet, id=id)
    logged_user = request.user
    BrickStats.objects.filter(brick_set=lego_set, user=logged_user).delete()
    messages.success(
        request,
        f"Deleted review of {lego_set}.",
    )
    return redirect(lego_set)


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


def get_avg_likes(reviews):
    avg_likes = reviews.aggregate(Avg("likes"))["likes__avg"]
    if avg_likes != None:
        avg_likes = round(avg_likes, 1)
    return avg_likes


def get_avg_age(reviews):
    avg_age = reviews.aggregate(Avg("min_recommended_age"))["min_recommended_age__avg"]
    if avg_age != None:
        avg_age = round(avg_age, 1)
    return avg_age


def get_avg_time(reviews):
    avg_time = reviews.aggregate(Avg("build_time"))["build_time__avg"]
    if avg_time != None:
        avg_time = round(avg_time, 0)
    return avg_time


def get_review_exists(brick_set: LegoSet, user: User):
    review = BrickStats.objects.filter(brick_set=brick_set, user=user)
    return review.exists()


def get_review_data(brick_set: LegoSet, user: User):
    return (
        BrickStats.objects.filter(brick_set=brick_set, user=user)
        .values("likes", "min_recommended_age", "build_time")
        .first()
    )


def maxsize_if_empty(_str):
    return sys.maxsize if not _str else int(_str)


def default_if_empty(_str, default):
    return default if not _str else int(_str)


def zero_if_empty(_str):
    return 0 if not _str else int(_str)


def filter_collection(request):
    logged_user = request.user
    queryset = LegoSet.objects.all()
    max_bricks = queryset.aggregate(max_bricks=Max("quantity_of_bricks"))["max_bricks"]
    set_themes = LegoSet.objects.values_list("theme", flat=True).distinct()
    theme = request.POST.get("theme")
    min_quantity = request.POST.get("start_quantity")
    max_quantity = request.POST.get("end_quantity", max_bricks)

    if request.method == "POST":
        single_diff = maxsize_if_empty(request.POST.get("single_diff"))
        general_diff = maxsize_if_empty(request.POST.get("general_diff"))
    else:
        single_diff = general_diff = sys.maxsize

    template = loader.get_template("bsf/filter.html")
    viable_sets = get_viable_sets(logged_user, single_diff, general_diff)

    if theme:
        viable_sets = [set for set in viable_sets if set["lego_set"].theme == theme]

    if not min_quantity:
        min_quantity = 0
    else:
        min_quantity = int(min_quantity)

    if not max_quantity:
        max_quantity = 99999999
    else:
        max_quantity = int(max_quantity)

    viable_sets = [
        set
        for set in viable_sets
        if int(min_quantity) <= set["lego_set"].quantity_of_bricks <= int(max_quantity)
    ]

    context = {
        "viable_sets": viable_sets,
        "single_diff": None if single_diff == sys.maxsize else single_diff,
        "general_diff": None if general_diff == sys.maxsize else general_diff,
        "set_themes": set_themes,
        "selected_theme": theme,
        "start_quantity": min_quantity,
        "end_quantity": max_quantity,
    }
    return HttpResponse(template.render(context, request))


def index(request):
    return render(request, "bsf/index.html")


def brick_list(request):
    bricks = Brick.objects.all()
    context = {"bricks": bricks}
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


class BrickListView(ListView):
    paginate_by = 15
    model = Brick


class FilterListView(ListView):
    paginate_by = 15
    model = LegoSet


class SetDetailView(DetailView):
    model = LegoSet
    template_name = "bsf/legoset_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bricks_in_set"] = BrickInSetQuantity.objects.filter(
            brick_set_id=self.kwargs["pk"]
        )
        all_reviews = BrickStats.objects.filter(brick_set=self.get_object())
        context.update(
            {
                "likes": get_avg_likes(all_reviews),
                "age": get_avg_age(all_reviews),
                "time": get_avg_time(all_reviews),
                "review_count": all_reviews.count(),
            }
        )
        if self.request.user.id:
            context["review_exists"] = get_review_exists(
                self.get_object(), self.request.user
            )
            review_data = get_review_data(self.get_object(), self.request.user)
            if context["review_exists"]:
                context.update(
                    {
                        "review_likes": review_data["likes"],
                        "review_age": review_data["min_recommended_age"],
                        "review_time": review_data["build_time"],
                    }
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
    return render(
        request=request,
        template_name="registration/login.html",
        context={"login_form": form},
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
            new_collection = UserCollection(user=user)
            new_collection.save()
            messages.success(request, "Registration successful.")
            return redirect("index")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render(
        request=request,
        template_name="registration/signup.html",
        context={"register_form": form},
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
    return render(
        request=request,
        template_name="registration/password_reset.html",
        context={"password_reset_form": password_reset_form},
    )
