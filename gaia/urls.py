"""celula URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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

from .utils import login_user_bases, panel_bases, index_bases

urlpatterns = [
    path('admin/', admin.site.urls),

    path('bases/', include('bases.urls')),
    path('index/bases/', index_bases, name='index_bases'),
    path('panelcontrol/', panel_bases, name='panel_bases'),
    path('login/user/bases/', login_user_bases, name='login_user_bases'),
]
