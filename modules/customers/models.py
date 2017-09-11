# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models


class Accounts(models.Model):
    user = models.OneToOneField(User, related_name="Accounts", verbose_name="Kullanıcı")

    def __unicode__(self):
        return "%s" % self.user.username

    class Meta(object):
        verbose_name = "Hesap"
        verbose_name_plural = "Hesaplar"


plan_status = (
    ('pending', 'Beklemede'),
    ('active', 'Aktif'),
    ('expired', 'Sona erdi'),
    ('canceled', 'İptal Edildi'),
)


class Plans(models.Model):
    account = models.ForeignKey(Accounts, related_name="Plans", verbose_name="Hesap")
    limit = models.IntegerField(default=1, verbose_name="Donanım Limiti")
    status = models.CharField(max_length=15, default='pending', choices=plan_status, verbose_name="Durum")

    class Meta(object):
        verbose_name = "Üyelik"
        verbose_name_plural = "Üyelik"


class Locations(models.Model):
    account = models.ForeignKey(Accounts, related_name="Locations", verbose_name="Hesap")
    name = models.CharField(max_length=50, verbose_name="Lokasyon Tanımı")
    lat = models.DecimalField(default=0, max_digits=10, decimal_places=8, verbose_name="Enlem")
    lon = models.DecimalField(default=0, max_digits=10, decimal_places=8, verbose_name="Boylam")

    def __unicode__(self):
        return "%s" % self.name

    class Meta(object):
        verbose_name = "Konum"
        verbose_name_plural = "Konumlar"


class Rooms(models.Model):
    account = models.ForeignKey(Accounts, related_name="Rooms", verbose_name="Hesap")
    location = models.ForeignKey(Locations, related_name="Rooms", verbose_name="Konum")
    name = models.CharField(max_length=50, verbose_name="Oda Tanımı")

    def __unicode__(self):
        return "%s" % self.name

    class Meta(object):
        verbose_name = "Odalar"
        verbose_name_plural = "Oda"


class Devices(models.Model):
    device_types = (
        ('relay_current', 'Akım Sensörlü 16 Röle Kartı'),
        ('relay', '16 Röle Kartı'),
        ('ir', 'IR Modüle')
    )
    account = models.ForeignKey(Accounts, related_name="Devices", verbose_name="Hesap")
    room = models.ForeignKey(Rooms, blank=True, null=True, related_name="Devices")
    type = models.CharField(max_length=15, choices=device_types, verbose_name="Cihaz Tipi")
    name = models.CharField(max_length=50, verbose_name="Cihaz Adı", default='')
    description = models.CharField(max_length=50, verbose_name="Cihaz Tanımı", default='')
    wan_ip = models.CharField(max_length=50, verbose_name="WAN IP adresi", default='0.0.0.0')
    ip = models.CharField(max_length=50, verbose_name="LAN IP adresi", default='0.0.0.0')
    port = models.IntegerField(verbose_name="Port")
    status = models.BooleanField(default=True, verbose_name="Durum")

    @property
    def total_instant_current(self):
        total_current = 0
        for relay in self.Relays.all():
            last_val = relay.CurrentValues.all().order_by("-create_date")[:1]
            if last_val.count() == 1:
                total_current = last_val[0].current_value
        return total_current



    @property
    def total_instant_power(self):
        total_power = 0
        for relay in self.Relays.all():
            last_val = relay.CurrentValues.all().order_by("-create_date")[:1]
            if last_val.count() == 1:
                total_power = last_val[0].power_cons
        return total_power


    def __unicode__(self):
        return "%s" % self.name

    class Meta(object):
        verbose_name = "Cihaz"
        verbose_name_plural = "Cihazlar"


RelayIcons = (
    ('light', 'Ampül'),
    ('aircond', 'Klima'),
    ('fan', 'Fan'),
    ('su', 'Su Vanası'),
    ('gas', 'Gaz Vanası'),
    ('blinds', 'Pajnur'),
)

RelayTypes = (
    ('switch', 'Aç / Kapat'),
    ('push', 'Bas - çek'),
    ('count', 'Geri Sayım'),
    ('scheduled', 'Zamanlanmış'),
)


class Relays(models.Model):
    device = models.ForeignKey(Devices, related_name="Relays", verbose_name="Cihaz")
    room = models.ForeignKey(Rooms, related_name="Relays", verbose_name="Oda")
    name = models.CharField(max_length=50, verbose_name="Röle Tanımı")

    pressed = models.BooleanField(default=False, verbose_name="Basılı mı?")

    relay_no = models.IntegerField(verbose_name="Röle No")
    type = models.CharField(max_length=20, choices=RelayTypes, verbose_name="Anahtar Tipi")
    icon = models.CharField(max_length=20, choices=RelayIcons, verbose_name="Simge")

    @property
    def total_instant_current(self):
        total_current = 0
        last_val = self.CurrentValues.all().order_by("-create_date")[:1]
        if last_val.count() == 1:
            total_current = last_val[0].current_value
        return total_current

    @property
    def total_instant_power(self):
        total_power = 0

        last_val = self.CurrentValues.all().order_by("-create_date")[:1]
        if last_val.count() == 1:
            total_power = last_val[0].power_cons
        return total_power

    def __unicode__(self):
        return "%s %s" % (self.name, self.room.name)

    class Meta(object):
        verbose_name = "Röle"
        verbose_name_plural = "Röleler"


sensor_types = (('current', 'Akın Sensörü'),)


class RelayCurrentValues(models.Model):
    relay = models.ForeignKey(Relays, related_name="CurrentValues", verbose_name="Röle")
    current_value = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Akım Değeri (Amper)")
    power_cons = models.DecimalField(max_digits=8, decimal_places=2, default=0,
                                     verbose_name="Kullanılan Güç (Watt/saat)")
    create_date = models.DateTimeField(verbose_name='Eklenme Tarihi', auto_now_add=True)

    def __unicode__(self):
        return "%s %s" % (self.relay.name, self.relay.room.name)

    class Meta(object):
        verbose_name = "Röle Akım Değeri"
        verbose_name_plural = "Röle Akım Değerleri"


DAYS = (
    (0, "Pazartesi"),
    (1, "Salı"),
    (2, "Çarşamba"),
    (3, "Perşembe"),
    (4, "Cuma"),
    (5, "Cumartesi"),
    (6, "Pazar"),
)


class Crons(models.Model):
    relay = models.ForeignKey(Relays, verbose_name="Röle")
    day = models.IntegerField(choices=DAYS, verbose_name="Uygulanacak Günler")
    switch_on_time = models.TimeField(verbose_name="Açma Zaman")
    switch_off_time = models.TimeField(verbose_name="Kapama Zaman")

    class Meta(object):
        verbose_name = "Zamanlama"
        verbose_name_plural = "Zamanlamalar"


class IrButtons(models.Model):
    device = models.ForeignKey(Devices, related_name="IrButtons", verbose_name="Cihaz")
    room = models.ForeignKey(Rooms, related_name="IrButtons", verbose_name="Oda")
    name = models.CharField(max_length=50, verbose_name="Röle Tanımı")

    icon = models.CharField(max_length=20, choices=RelayIcons, verbose_name="Simge")

    ir_type = models.CharField(max_length=20, verbose_name="IR Tipi")
    ir_code = models.CharField(max_length=16, verbose_name="IR Code")
    ir_bits = models.IntegerField(verbose_name="Bits")

    def __unicode__(self):
        return "%s %s" % (self.name, self.room.name)

    class Meta(object):
        verbose_name = "IR"
        verbose_name_plural = "IR"
