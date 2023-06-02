from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail, BadHeaderError
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from bsf.forms import *
from bsf.models import (
    Wishlist,
)
from .base import *


def login(request):
    if request.user.is_authenticated:
        messages.error(request, "Already logged in. Logout to change account.")
        return redirect("index")
    elif request.method == "POST":
        form = BootstrapAuthenticationForm(request, data=request.POST)
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
    form = BootstrapAuthenticationForm()
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
                        "domain": "yellowbrick.babia-gora.pl",
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
                            "contact@yellowbrick.babia-gora.pl",
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
