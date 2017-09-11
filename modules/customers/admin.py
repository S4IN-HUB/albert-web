# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from modules.customers.models import Accounts, Locations, Plans, Rooms, Devices, Relays, IrButtons, Crons, \
    RelayCurrentValues

# Register your models here.

admin.site.register(Accounts)


class LocationsAdmin(admin.ModelAdmin):
    list_display = ('account', 'name', 'lat', 'lon')


admin.site.register(Locations, LocationsAdmin)
admin.site.register(Plans)


class RoomsAdmin(admin.ModelAdmin):
    list_display = ('account', 'location', 'name',)


admin.site.register(Rooms, RoomsAdmin)

admin.site.register(IrButtons)


class InlineCrons(admin.StackedInline):
    model = Crons
    extra = 1


class RelayAdmin(admin.ModelAdmin):
    def get_total_instant_current(self, obj):
        return 0
        return obj.total_instant_current

    get_total_instant_current.short_description = u'Toplam Anlık Akım'

    def get_total_instant_power(self, obj):
        return 0
        return obj.total_instant_power

    get_total_instant_power.short_description = u'Toplam Anlık Akım'

    def open_relay(self, obj):
        return '<a class="btn btn-success" href="/relay-control/?relay=' + str(
            obj.id) + '&action=open" target="process"><i class="fa fa-power-off" aria-hidden="true"></i> Aç</a>'

    open_relay.allow_tags = True
    open_relay.short_description = u'Röleyi aç'

    def close_relay(self, obj):
        return '<a class="btn btn-danger" href="/relay-control/?relay=' + str(
            obj.id) + '&action=close"  target="process"><i class="fa fa-power-off" aria-hidden="true"></i> Kapat</a>'

    close_relay.allow_tags = True
    close_relay.short_description = u'Röleyi Kapat'

    list_display = ('name', 'relay_no', 'type', 'room', 'device', 'pressed', 'open_relay', 'close_relay',
                    'get_total_instant_current', 'get_total_instant_power')
    inlines = [InlineCrons, ]


admin.site.register(Relays, RelayAdmin)


class DevicesAdmin(admin.ModelAdmin):
    def get_total_instant_current(self, obj):
        return obj.total_instant_current

    get_total_instant_current.short_description = u'Toplam Anlık Akım'

    def get_total_instant_power(self, obj):
        return obj.total_instant_power

    get_total_instant_power.short_description = u'Toplam Anlık Güç'

    list_display = ('account', 'name', 'description', 'wan_ip', 'ip', 'port', 'status', 'get_total_instant_current',
                    'get_total_instant_power')


admin.site.register(Devices, DevicesAdmin)


class RelayCurrentValuesAdmin(admin.ModelAdmin):
    list_display = ('relay', 'current_value', 'power_cons', 'create_date')


admin.site.register(RelayCurrentValues, RelayCurrentValuesAdmin)
