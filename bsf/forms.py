from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, \
    AuthenticationForm
from .models import User
from django import forms
from django.forms.widgets import PasswordInput, TextInput


class BootstrapAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput(
        attrs={'class': 'form-control'}))
    password = forms.CharField(widget=PasswordInput(
        attrs={'class': 'form-control mb-3'}))


class NewUserForm(UserCreationForm):
    username = forms.CharField(widget=TextInput(
        attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Email",
                             required=True,
                             widget=TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password",
                                          'class': 'form-control'}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password",
                                          'class': 'form-control'}),
        strip=False,
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class PassResetForm(PasswordResetForm):
    class Meta:
        model = User
        fields = "email"
