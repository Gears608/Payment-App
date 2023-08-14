from django.urls import path

from conversion.views import conversion

urlpatterns = [
    path('<str:currency1>/<str:currency2>/<str:amount_of_currency1>/', conversion),
]