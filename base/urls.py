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
                                     relay_control, cron_control, send_ir_command, read_ir, get_devices,
                                     get_device_relays, get_relay_rooms, get_relay_settings, api_register,
                                     add_location, add_room, add_device, add_remote, get_remotes, add_relay,
                                     get_ir_buttons, relay_command)
from modules.masterpage.views import index, about_us, contact, send_message

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^akilli-ev-sistemi-nedir/$', about_us, name='AboutUs'),
    url(r'^iletisim/$', contact, name='Contact'),
    url(r'^relay-control/$', relay_control, name='relay_control'),
    url(r'^cron-control/$', cron_control, name='cron_control'),
    url(r'^send_ir_command/$', send_ir_command, name='send_ir_command'),
    url(r'^read-ir/$', read_ir, name='read-ir'),
    url(r'^send-message/$', send_message, name='SendMessage'),
    url(r'^admin/', admin.site.urls),
    url(r'^api/login/$', api_login),
    url(r'^api/register/$', api_register),
    url(r'^api/logout/$', api_logout),
    url(r'^api/add_location/$', add_location),
    url(r'^api/add_room/$', add_room),
    url(r'^api/add_device/$', add_device),
    url(r'^api/add_remote/$', add_remote),
    url(r'^api/add_relay/$', add_relay),
    url(r'^api/list/locations/$', get_locations),
    url(r'^api/list/rooms/$', get_rooms),
    url(r'^api/list/devices/$', get_devices),
    url(r'^api/list/relays/$', get_relays),
    url(r'^api/list/remotes/$', get_remotes),
    url(r'^api/list/ir_buttons/$', get_ir_buttons),
    url(r'^api/list/relay_rooms/$', get_relay_rooms),
    url(r'^api/list/relay_settings/$', get_relay_settings),
    url(r'^api/list/device_relays/$', get_device_relays),
    url(r'^api/list/send-command/$', send_command),
    url(r'^api/relay_command/$', relay_command)

]
