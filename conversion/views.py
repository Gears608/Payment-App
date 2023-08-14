from _decimal import Decimal

from django.http import JsonResponse


def conversion(request, currency1, currency2, amount_of_currency1):
    exchange_rates = {
        'USD': {'EUR': 0.83, 'GBP': 0.75},
        'EUR': {'USD': 1.20, 'GBP': 0.90},
        'GBP': {'USD': 1.33, 'EUR': 1.11},
    }

    if currency1 not in exchange_rates or currency2 not in exchange_rates[currency1]:
        return JsonResponse({'Error': 'Invalid Currency', 'status': 404})

    converted_value = Decimal(amount_of_currency1) * Decimal(exchange_rates[currency1][currency2])

    return JsonResponse({'exchange_rate': exchange_rates[currency1][currency2], 'value': round(converted_value, 2)})
