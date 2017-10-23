"""albert URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from modules.customers.views import (api_login, api_logout, get_rooms, get_relays, send_command, get_locations,
                                     relay_control, cron_control)
from modules.masterpage.views import index, about_us, contact, send_message

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^akilli-ev-sistemi-nedir/$', about_us, name='AboutUs'),
    url(r'^iletisim/$', contact, name='Contact'),
    url(r'^relay-control/$', relay_control, name='relay_control'),
    url(r'^cron-control/$', cron_control, name='cron_control'),
    url(r'^send-message/$', send_message, name='SendMessage'),
    url(r'^admin/', admin.site.urls),
    url(r'^api/login/$', api_login),
    url(r'^api/logout/$', api_logout),
    url(r'^api/list/locations/$', get_locations),
    url(r'^api/list/rooms/$', get_rooms),
    url(r'^api/list/relays/$', get_relays),
    url(r'^api/list/send-command/$', send_command)

]
