# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from modules.customers.models import (Accounts, Locations, Plans, Rooms, Devices, Relays, Crons, RelayCurrentValues,
                                      IrRemote, IrButton)


@admin.register(Plans)
class PlansAdmin(admin.ModelAdmin):
    list_display = ('account', 'limit', 'status')


@admin.register(Accounts)
class AccountsAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'user_type')
    list_display_links = ('user', 'first_name', 'last_name', 'user_type')

    def first_name(self, obj):
        return obj.user.first_name

    first_name.short_description = 'Adı'
    first_name.admin_order_field = 'user'

    def last_name(self, obj):
        return obj.user.last_name

    last_name.short_description = 'Soyadı'
    last_name.admin_order_field = 'user'


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
        if obj.room:
            return obj.room.location
        else:
            return '-'

    room_location.short_description = 'Konum'
    room_location.admin_order_field = 'room'


    def read_ir_button(self,obj):
        if obj.type == 'IR':
            return '<a class="btn btn-info" href="/read-ir/?device_id=' + str(obj.id) + '"  target="process"><i class="fa fa-power-off" aria-hidden="true"></i> IR Oku</a>'
        else:
            return '-'

    read_ir_button.allow_tags = True
    read_ir_button.short_description = 'IR Oku'


    list_display = ('name', 'description', 'room_location', 'room', 'wan_ip', 'status',
                    'get_total_instant_current', 'get_total_instant_power','read_ir_button')


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


@admin.register(IrRemote)
class IrRemoteAdmin(admin.ModelAdmin):
    """IR Kumanda listesi"""
    list_display = ('name', 'device', 'room')


@admin.register(IrButton)
class IrButtonAdmin(admin.ModelAdmin):
    """IR Kumanda butonları yönetim paneli"""

    list_display = ('icon', 'name', 'ir_remote', 'ir_type', 'ir_code', 'ir_bits', 'set_ir_command')
    list_display_links = ('icon', 'name', 'ir_remote')

    def set_ir_command(self, obj):
        """
        Seçilen butona IR komutunun set edilmesi için CACHE'e o butonun set edilebilir olduğuna dair ibare yazmaya yarar
        Bir butona set edilmek için tıklandığında cacheteki butonun bağlı olduğunu cihaza ait diğer butonların SET
        dururmu kapatılır. BIR IR modülüne ait AYNI ANDA SADECE BİR BUTON SET EDİLEBİLİR.
        :param obj:
        :return:
        """
        return '<a class="btn btn-danger" href="/set_ir_command/?button=' + str(
            obj.id) + '"  target="process"><i class="fa fa-gear" aria-hidden="true"></i></a>'

    set_ir_command.allow_tags = True
    set_ir_command.short_description = u'Ayarla'
