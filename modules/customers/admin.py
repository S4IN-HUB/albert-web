# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from modules.customers.models import Accounts, Locations, Plans, Rooms, Devices, Relays, IrButtons, Crons

# Register your models here.

admin.site.register(Accounts)
class LocationsAdmin(admin.ModelAdmin):
    list_display = ('account','name','lat','lon')

admin.site.register(Locations,LocationsAdmin)
admin.site.register(Plans)

class RoomsAdmin(admin.ModelAdmin):
    list_display = ('account','location','name',)
admin.site.register(Rooms,RoomsAdmin)


admin.site.register(IrButtons)


class InlineCrons(admin.StackedInline):
    model = Crons
    extra = 1

class RelayAdmin(admin.ModelAdmin):
    def open_relay(self, obj):
        return '<a class="btn btn-success" href="/relay-control/?relay=' + str(
            obj.id) + '&action=open"><i class="fa fa-power-off" aria-hidden="true"></i> Aç</a>'

    open_relay.allow_tags = True
    open_relay.short_description = u'Röleyi aç'

    def close_relay(self, obj):
        return '<a class="btn btn-danger" href="/relay-control/?relay=' + str(
            obj.id) + '&action=close"><i class="fa fa-power-off" aria-hidden="true"></i> Kapat</a>'

    close_relay.allow_tags = True
    close_relay.short_description = u'Röleyi aç'

    list_display = ('name','relay_no','type','room','device', 'open_relay', 'close_relay')
    inlines = [InlineCrons,]

admin.site.register(Relays,RelayAdmin)



class DevicesAdmin(admin.ModelAdmin):
    list_display = ('account','name','ip','port',)


admin.site.register(Devices,DevicesAdmin)