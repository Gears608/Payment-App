import ssl
import urllib.request
from _decimal import Decimal

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
import json
from django.shortcuts import render, redirect

from payapp.models import Currency
from register.forms import RegisterForm


def login_view(request):
    if request.method == 'POST':
        login_form = AuthenticationForm(request, request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                return render(request, 'register/login.html', {'login_form': login_form})
        else:
            return render(request, 'register/login.html', {'login_form': login_form})
    else:
        login_form = AuthenticationForm()
        return render(request, 'register/login.html', {'login_form': login_form})


def register_view(request):
    if request.method == 'POST':
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            value = 1000.00
            currency = register_form.cleaned_data.get('currency')
            if currency != 'GBP':
                url = f'https://127.0.0.1:8000/webapps2023/conversion/{currency}/GBP/{value}/'

                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE

                response = urllib.request.urlopen(url, timeout=10, context=context)
                data = json.loads(response.read().decode())
                value = Decimal(data.get('value'))
            user = register_form.save()
            c = Currency(user=user, value=value, currency=currency)
            c.save()
            return redirect('login')
        else:
            return render(request, 'register/register.html', {'register_form': register_form})
    else:
        register_form = RegisterForm()
        return render(request, 'register/register.html', {'register_form': register_form})


def logout_user(request):
    logout(request)
    return redirect('login')
