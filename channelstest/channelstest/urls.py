"""channelstest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path
from django.conf.urls import include
from allauth.account.views import login

from .views import mainPage, testCallback

urlpatterns = [
    path('', mainPage),
    path('callback', testCallback),
    path('admin/', admin.site.urls),
    path('chat/', include('chat.urls')),
    path('accounts/', include('allauth.urls')),
    path('accounts/social/signup/', login, name="account_signup"),
    path('accounts/signup', login, name="account_signup"),
]

print(urlpatterns)
