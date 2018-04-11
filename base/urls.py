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
                                     add_location, add_room, add_device, add_relay,
                                     get_ir_buttons, relay_command, favourite_relay, delete_room, delete_location,
                                     favourite_room,ir_command,read_ir_button,set_ir_shortcut, get_favourite_relays,
                                     get_room_info, get_favourite_rooms, delete_favourite_relay, relay_command_update,
                                     change_target_temp, delete_ir_button, delete_rl_button, change_ir_button, add_new_scenario,
                                     delete_scenario, list_user_scenarios, add_relay_to_scenario, delete_relay_from_scenario,
                                     list_relay_crons, delete_relay_cron, add_new_relay_cron, list_scenario_relays, activate_scenario)
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
    url(r'^api/add_relay/$', add_relay),
    url(r'^api/add_scenario/$', add_new_scenario),
    url(r'^api/add_relay_to_scenario/$', add_relay_to_scenario),
    url(r'^api/add_new_relay_cron/$', add_new_relay_cron),

    url(r'^api/favourite_relay/$', favourite_relay),
    url(r'^api/delete_fav_relay/$', delete_favourite_relay),
    url(r'^api/favourite_room/$', favourite_room),
    url(r'^api/delete_room/$', delete_room),
    url(r'^api/delete_scenario/$', delete_scenario),
    url(r'^api/delete_location/$', delete_location),
    url(r'^api/delete_ir_button/$', delete_ir_button),
    url(r'^api/delete_rl_button/$', delete_rl_button),
    url(r'^api/delete_relay_from_scenario/$', delete_relay_from_scenario),
    url(r'^api/delete_relay_cron/$', delete_relay_cron),
    url(r'^api/delete_location/$', delete_location),

    url(r'^api/settings_ir_button/$', change_ir_button),
    url(r'^api/list/locations/$', get_locations),
    url(r'^api/list/rooms/$', get_rooms),
    url(r'^api/list/devices/$', get_devices),
    url(r'^api/list/relays/$', get_relays),
    url(r'^api/list/ir_buttons/$', get_ir_buttons),
    url(r'^api/list/relay_rooms/$', get_relay_rooms),
    url(r'^api/list/relay_settings/$', get_relay_settings),
    url(r'^api/list/device_relays/$', get_device_relays),
    url(r'^api/list/send-command/$', send_command),
    url(r'^api/list/favourite_relays/$', get_favourite_relays),
    url(r'^api/list/favourite_rooms/$', get_favourite_rooms),
    url(r'^api/list/user_scenarios/$', list_user_scenarios),
    url(r'^api/list/list_scenario_relays/$', list_scenario_relays),
    url(r'^api/list/relay_crons/$', list_relay_crons),

    url(r'^api/relay_command/$', relay_command),
    url(r'^api/relay_command_update/$', relay_command_update),
    url(r'^api/get_room_info/$', get_room_info),
    url(r'^api/change_target_temp/$', change_target_temp),
    url(r'^api/ir_command/$', ir_command),
    url(r'^api/read_ir_button/$', read_ir_button),
    url(r'^api/set/ir_shortcut/$', set_ir_shortcut),
    url(r'^api/activate_scenario/$', activate_scenario),

]
