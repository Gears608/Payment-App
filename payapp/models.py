from django.contrib.auth.models import User
from django.db import models


class Currency(models.Model):
    # the user whose money it is
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # the value of money they currently have
    value = models.DecimalField(max_digits=16, decimal_places=2)
    # the currency that the money is in
    currency = models.CharField(max_length=3, default='GBP')

    def __str__(self):
        details = ''
        details += f'Username : {self.user}\n'
        details += f'Money : {self.value}\n'
        details += f'Currency : {self.currency}\n'
        return details


class CurrencyTransfer(models.Model):
    origin_account = models.CharField(max_length=50)
    destination_account = models.CharField(max_length=50)
    value = models.DecimalField(max_digits=16, decimal_places=2)

    def __str__(self):
        details = ''
        details += f'Origin : {self.origin_account}\n'
        details += f'Destination : {self.destination_account}\n'
        details += f'Value : {self.value}\n'
        return details


class Request(models.Model):
    origin_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_request')
    destination_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_request')
    value = models.DecimalField(max_digits=16, decimal_places=2)

    def __str__(self):
        details = ''
        details += f'Origin : {self.origin_user}\n'
        details += f'Destination : {self.destination_user}\n'
        details += f'Value : {self.value}\n'
        return details
