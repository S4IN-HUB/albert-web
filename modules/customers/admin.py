# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from modules.customers.models import Accounts, Locations, Plans, Rooms, Devices, Relays
from django.contrib import admin

# Register your models here.

admin.site.register(Accounts)
admin.site.register(Locations)
admin.site.register(Plans)
admin.site.register(Rooms)


class RelayAdmin(admin.ModelAdmin):
    list_display = ('name','relay_no','type','room','device')


admin.site.register(Relays,RelayAdmin)
admin.site.register(Devices)