# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from modules.customers.models import (Accounts, Locations, Plans, Rooms, Devices, Relays, Crons, RelayCurrentValues,
                                      IrRemote, IrButton)

admin.site.register(Accounts)
admin.site.register(Plans)


@admin.register(Locations)
class LocationsAdmin(admin.ModelAdmin):
    """BURAYA AÇIKLAMA GELECEK"""
    list_display = ('account', 'name', 'lat', 'lon')

    def get_queryset(self, request):
        qs = super(LocationsAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(account__user=request.user)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):

        if db_field.name == "account":
            if not request.user.is_superuser:
                Queryset = Accounts.objects.filter(user=request.user)
                kwargs["queryset"] = Queryset

        return super(LocationsAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Rooms)
class RoomsAdmin(admin.ModelAdmin):
    """BURAYA AÇIKLAMA GELECEK"""
    list_display = ('location_account', 'name', 'location')

    def location_account(self, obj):
        return obj.location.account

    location_account.short_description = 'Account'
    location_account.admin_order_field = 'location'

    def get_queryset(self, request):
        qs = super(RoomsAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(account__user=request.user)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):

        if db_field.name == "account":
            if not request.user.is_superuser:
                Queryset = Accounts.objects.filter(user=request.user)
                kwargs["queryset"] = Queryset

        if db_field.name == "location":
            if not request.user.is_superuser:
                Queryset = Locations.objects.filter(account__user=request.user)
                kwargs["queryset"] = Queryset

        return super(RoomsAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Devices)
class DevicesAdmin(admin.ModelAdmin):
    """BURAYA AÇIKLAMA GELECEK"""
    def get_queryset(self, request):

        qs = super(DevicesAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(account__user=request.user)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):

        if db_field.name == "account":
            if not request.user.is_superuser:
                Queryset = Accounts.objects.filter(user=request.user)
                kwargs["queryset"] = Queryset

        if db_field.name == "room":
            if not request.user.is_superuser:
                Queryset = Rooms.objects.filter(account__user=request.user)
                kwargs["queryset"] = Queryset

        return super(DevicesAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def get_total_instant_current(self, obj):
        return obj.total_instant_current

    get_total_instant_current.short_description = u'Toplam Anlık Akım'

    def get_total_instant_power(self, obj):
        return obj.total_instant_power

    get_total_instant_power.short_description = u'Toplam Anlık Güç'

    def room_location(self, obj):
        return obj.room.location

    room_location.short_description = 'Location'
    room_location.admin_order_field = 'room'

    list_display = ('room_location', 'room', 'name', 'description', 'wan_ip', 'ip', 'port', 'status',
                    'get_total_instant_current', 'get_total_instant_power')


class InlineCrons(admin.StackedInline):
    """BURAYA AÇIKLAMA GELECEK"""
    model = Crons
    extra = 1


@admin.register(Relays)
class RelayAdmin(admin.ModelAdmin):
    """BURAYA AÇIKLAMA GELECEK"""
    def get_queryset(self, request):

        qs = super(RelayAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(device__account__user=request.user)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):

        if db_field.name == "account":
            if not request.user.is_superuser:
                Queryset = Accounts.objects.filter(user=request.user)
                kwargs["queryset"] = Queryset

        if db_field.name == "device":
            if not request.user.is_superuser:
                Queryset = Devices.objects.filter(account__user=request.user)
                kwargs["queryset"] = Queryset

        if db_field.name == "room":
            if not request.user.is_superuser:
                Queryset = Rooms.objects.filter(account__user=request.user)
                kwargs["queryset"] = Queryset

        return super(RelayAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

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

    list_display = ('name', 'relay_no', 'type', 'device', 'pressed', 'open_relay', 'close_relay',
                    'total_instant_current', 'total_instant_power')
    inlines = [InlineCrons, ]


@admin.register(RelayCurrentValues)
class RelayCurrentValuesAdmin(admin.ModelAdmin):
    """BURAYA AÇIKLAMA GELECEK"""
    list_display = ('relay', 'device_name', 'current_value', 'power_cons', 'create_date')

    def device_name(self, obj):
        return obj.relay.device.name

    def get_queryset(self, request):
        qs = super(RelayCurrentValuesAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(relay__device__account__user=request.user)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):

        if db_field.name == "relay":
            if not request.user.is_superuser:
                Queryset = Relays.objects.filter(device__account__user=request.user)
                kwargs["queryset"] = Queryset

        return super(RelayCurrentValuesAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(IrButton)
class IrButtonAdmin(admin.ModelAdmin):
    """BURAYA AÇIKLAMA GELECEK"""
    pass


@admin.register(IrRemote)
class IrRemoteAdmin(admin.ModelAdmin):
    """BURAYA AÇIKLAMA GELECEK"""
    pass
