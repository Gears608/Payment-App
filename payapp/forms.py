from django import forms
from . import models


class CurrencyTransferForm(forms.ModelForm):
    class Meta:
        model = models.CurrencyTransfer
        fields = ["destination_account", "value"]
