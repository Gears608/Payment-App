"""
URL configuration for webapps2023 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from register import views as register_views
from payapp import views as payapp_views

urlpatterns = [
    path('webapps2023/register/', register_views.register_view, name='register'),
    path('webapps2023/login/', register_views.login_view, name='login'),
    path('webapps2023/logout/', register_views.logout_user, name='logout'),
    path('webapps2023/home/', payapp_views.home, name='home'),
    path('webapps2023/transfer/', payapp_views.money_transfer, name='transfer'),
    path('webapps2023/conversion/', include('conversion.urls')),
    path('webapps2023/request/', payapp_views.request_transfer, name='request'),
    path('webapps2023/response/', payapp_views.request_response, name='response'),
    path('webapps2023/admin-transactions/', payapp_views.admin_transactions, name='transactions'),
    path('webapps2023/all-users/', payapp_views.all_users, name='all-users'),
    path('webapps2023/register-admin/', payapp_views.register_admin, name='register-admin'),
    path('', payapp_views.home),
    path('webapps2023/', payapp_views.home),
    path('admin/', admin.site.urls),
]
