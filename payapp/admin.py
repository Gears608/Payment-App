from django.contrib import admin

from payapp.models import Currency, CurrencyTransfer, Request

# Register your models here.

admin.site.register(Currency)
admin.site.register(CurrencyTransfer)
admin.site.register(Request)
