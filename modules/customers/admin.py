# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from modules.customers.models import Accounts, Locations, Plans, Rooms, Devices, Relays, IrButtons
from django.contrib import admin

# Register your models here.

admin.site.register(Accounts)
class LocationsAdmin(admin.ModelAdmin):
    list_display = ('account','name','lat','lon')

admin.site.register(Locations,LocationsAdmin)
admin.site.register(Plans)

class RoomsAdmin(admin.ModelAdmin):
    list_display = ('account','name',)
admin.site.register(Rooms,RoomsAdmin)


admin.site.register(IrButtons)


class RelayAdmin(admin.ModelAdmin):
    list_display = ('name','relay_no','type','room','device')


admin.site.register(Relays,RelayAdmin)



class DevicesAdmin(admin.ModelAdmin):
    list_display = ('account','name','ip','port',)


admin.site.register(Devices,DevicesAdmin)