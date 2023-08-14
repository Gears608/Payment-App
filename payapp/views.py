import json
import ssl
import urllib.request
from _decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.shortcuts import render, redirect

from payapp import models
from payapp.forms import CurrencyTransferForm
from payapp.models import CurrencyTransfer, Request, Currency
from register.forms import RegisterForm


@login_required
def home(request):
    balance = get_balance(request)

    # gets the user's transactions from the database
    username = request.user.username
    try:
        user = models.Currency.objects.get(user=request.user)
    except ObjectDoesNotExist:
        return render(request, 'payapp/home.html', {'balance': balance})

    # gets requests
    users_requests = Request.objects.filter(destination_user=request.user)

    # gets transactions
    users_transactions = CurrencyTransfer.objects.filter(origin_account=username) | CurrencyTransfer.objects.\
        filter(destination_account=username)

    symbol = get_symbol(user)

    # converts to user's currency
    if user.currency != 'GBP':
        for r in users_requests:
            convert_currency(user, r)
            r.value = symbol + str(r.value)

        for t in users_transactions:
            convert_currency(user, t)
            t.value = symbol + str(t.value)
    else:
        for r in users_requests:
            r.value = symbol + str(r.value)
        for t in users_transactions:
            t.value = symbol + str(t.value)

    return render(request, 'payapp/home.html', {'balance': balance, 'requests': reversed(users_requests), 'transactions'
                  : reversed(users_transactions)})


@login_required
@transaction.atomic
def request_response(request):
    if request.method == 'POST':
        currency_request = models.Request.objects.get(id=request.POST.get('id'))

        if request.POST.get('action') == 'accept':
            money_to_transfer_gbp = currency_request.value
            money_to_receive = money_to_transfer_gbp
            money_to_transfer = money_to_transfer_gbp
            src_user = models.Currency.objects.get(user=currency_request.destination_user)
            dst_user = models.Currency.objects.get(user=currency_request.origin_user)

            # convert money to src_user's currency
            if src_user.currency != 'GBP':
                money_to_transfer = convert_currency(src_user, currency_request).value

            # convert money to dst_user's currency
            if dst_user.currency != 'GBP':
                money_to_receive = convert_currency(dst_user, currency_request).value

            if money_to_transfer < src_user.value:
                # removes the funds from source user
                src_user.value = src_user.value - money_to_transfer
                src_user.save()

                # adds the funds to destination user
                dst_user.value = dst_user.value + money_to_receive
                dst_user.save()
                # creates a currency transfer database object to store the transfer
                c = CurrencyTransfer(origin_account=src_user.user.username, destination_account=dst_user.user.
                                     username, value=money_to_transfer_gbp)
                c.save()
                currency_request.delete()
            else:
                print('invalid')

        else:
            currency_request.delete()

        return redirect('home')


@login_required
def convert_currency(user, o):
    url = f'https://127.0.0.1:8000/webapps2023/conversion/GBP/{user.currency}/{o.value}/'
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    response = urllib.request.urlopen(url, timeout=10, context=context)
    data = json.loads(response.read().decode())
    o.value = Decimal(data.get('value'))
    return o


@login_required
@transaction.atomic
def money_transfer(request):
    if request.method == 'POST':
        form = CurrencyTransferForm(request.POST)

        if form.is_valid():

            src_username = request.user.username
            dst_username = form.cleaned_data["destination_account"]

            # ensures the user is not sending money to their account
            if src_username == dst_username:
                balance = get_balance(request)
                messages.info(request, f"Transfer is not possible now.")
                return render(request, "payapp/transfer.html", {"form": form, 'balance': balance})

            money_to_transfer = form.cleaned_data["value"]

            # gets user's value and currency info from database
            src_user = models.Currency.objects.get(user=request.user)

            # gets the destination account
            try:
                dst_user = models.Currency.objects.select_related().get(user__username=dst_username)
            except ObjectDoesNotExist:
                balance = get_balance(request)
                messages.info(request, f"Transfer is not possible now.")
                return render(request, "payapp/transfer.html", {"form": form, 'balance': balance})

            # get conversion if the source and destination are using different currencies
            if src_user.currency != dst_user.currency:
                # convert to destination user's currency
                url = f'https://127.0.0.1:8000/webapps2023/conversion/{src_user.currency}/{dst_user.currency}/' \
                      f'{money_to_transfer}/'

                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE

                response = urllib.request.urlopen(url, timeout=10, context=context)
                data = json.loads(response.read().decode())
                converted_money_to_transfer = Decimal(data.get('value'))
            else:
                converted_money_to_transfer = money_to_transfer

            # checks the source user has enough funds & is not transferring negative money
            if src_user.value > money_to_transfer > 0:
                # removes the funds from source user
                src_user.value = src_user.value - money_to_transfer
                src_user.save()

                # adds the funds to destination user
                dst_user.value = dst_user.value + converted_money_to_transfer
                dst_user.save()

                # standardises the currency to GBP for storing the transaction
                if src_user.currency != 'GBP':
                    # convert to GBP
                    url = f'https://127.0.0.1:8000/webapps2023/conversion/{src_user.currency}/GBP' \
                          f'/{money_to_transfer}/'

                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE

                    response = urllib.request.urlopen(url, timeout=10, context=context)
                    data = json.loads(response.read().decode())
                    money_to_transfer = Decimal(data.get('value'))
                # creates a currency transfer database object to store the transfer
                c = CurrencyTransfer(origin_account=src_username, destination_account=dst_username,
                                     value=money_to_transfer)
                c.save()
                form = CurrencyTransferForm()
                messages.info(request, f"Transfer successful.")
            else:
                messages.info(request, f"Transfer is not possible now.")
        balance = get_balance(request)
        return render(request, "payapp/transfer.html", {"form": form, 'balance': balance})

    else:
        form = CurrencyTransferForm()
    balance = get_balance(request)
    return render(request, "payapp/transfer.html", {"form": form, 'balance': balance})


@login_required
def request_transfer(request):
    if request.method == 'POST':
        form = CurrencyTransferForm(request.POST)
        if form.is_valid():
            sender = request.user
            recipient_username = form.cleaned_data['destination_account']
            # ensures the request isn't made to self
            if sender.username != recipient_username:
                amount = form.cleaned_data['value']
                sender = models.Currency.objects.get(user=request.user)

                # ensures the request is a positive number
                if amount > 0:
                    try:
                        recipient = models.User.objects.select_related().get(username=recipient_username)
                        recipient_currency = models.Currency.objects.get(user=recipient).currency
                    except ObjectDoesNotExist:
                        balance = get_balance(request)
                        messages.info(request, f"Transfer is not possible now.")
                        return render(request, "payapp/transfer.html", {"form": form, 'balance': balance})

                    # converts to GBP for storage on database
                    if sender.currency != 'GBP':
                        url = f'https://127.0.0.1:8000/webapps2023/conversion/{sender.currency}/{recipient_currency}' \
                              f'/{amount}/'
                        context = ssl.create_default_context()
                        context.check_hostname = False
                        context.verify_mode = ssl.CERT_NONE

                        response = urllib.request.urlopen(url, timeout=10, context=context)
                        data = json.loads(response.read().decode())
                        amount = Decimal(data.get('value'))

                    r = Request(origin_user=request.user, destination_user=recipient, value=amount)
                    r.save()
                    messages.info(request, f"Request sent.")
                else:
                    messages.info(request, f"Request is not possible now.")
            else:
                messages.info(request, f"Request is not possible now.")
            balance = get_balance(request)
            return render(request, "payapp/request.html", {"form": form, 'balance': balance})
    else:
        form = CurrencyTransferForm()
    balance = get_balance(request)
    return render(request, "payapp/request.html", {"form": form, 'balance': balance})


@login_required
def get_balance(request):
    # gets the user's current balance from the database
    try:
        user = models.Currency.objects.get(user=request.user)
    except ObjectDoesNotExist:
        return 'N/A'

    balance = get_symbol(user) + str(user.value)
    return balance


@user_passes_test(lambda user: user.is_staff)
def admin_transactions(request):
    transactions = models.CurrencyTransfer.objects.all()
    return render(request, 'payapp/admin-transactions.html', {'transactions': transactions})


@user_passes_test(lambda user: user.is_staff)
def register_admin(request):
    if request.method == 'POST':
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            value = 1000.00
            currency = register_form.cleaned_data['currency']
            if currency != 'GBP':
                url = f'https://127.0.0.1:8000/webapps2023/conversion/{currency}/GBP/{value}/'

                response = urllib.request.urlopen(url, timeout=10)
                data = json.loads(response.read().decode())
                value = Decimal(data.get('value'))
            user = register_form.save()
            user.is_staff = True
            user.save()
            c = Currency(user=user, value=value, currency=currency)
            c.save()
            register_form = RegisterForm()
            message = 'Admin User Created.'
            return render(request, 'payapp/register-admin.html', {'register_form': register_form, 'error_message':
                          message})
        else:
            return render(request, 'payapp/register-admin.html', {'register_form': register_form})
    else:
        register_form = RegisterForm()
        return render(request, 'payapp/register-admin.html', {'register_form': register_form})


@user_passes_test(lambda user: user.is_staff)
def all_users(request):
    users = models.Currency.objects.all()

    for u in users:
        u.value = get_symbol(u) + str(u.value)

    return render(request, 'payapp/admin-users.html', {'users': users})


@login_required
def get_symbol(user):
    symbols = {
        'GBP': '£',
        'USD': '$',
        'EUR': '€',
    }

    return symbols.get(user.currency)

