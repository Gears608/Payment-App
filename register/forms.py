from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30, required=True, label="First Name")
    last_name = forms.CharField(max_length=30, required=True, label="Last Name")
    currencies = {
        ('USD', 'USD'),
        ('GBP', 'GBP'),
        ('EUR', 'EUR'),
    }
    currency = forms.ChoiceField(choices=currencies, label="Preferred currency")

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password1", "password2"]
