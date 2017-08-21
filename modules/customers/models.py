# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

class Accounts(models.Model):
    user = models.OneToOneField(User, related_name="Accounts",verbose_name="Kullanıcı")

    def __unicode__(self):
        return "%s" % self.user.username

plan_status = (
    ('pending','Beklemede'),
    ('active','Aktif'),
    ('expired','Sona erdi'),
    ('canceled', 'İptal Edildi'),
)

class Plans(models.Model):
    account = models.ForeignKey(Accounts,related_name="Plans",verbose_name="Hesap")
    limit = models.IntegerField(default=1,verbose_name="Donanım Limiti")
    status = models.CharField(max_length=15,default='pending',choices=plan_status,verbose_name="Durum")

class Locations(models.Model):
    account = models.ForeignKey(Accounts, related_name="Locations", verbose_name="Hesap")
    name = models.CharField(max_length=50,verbose_name="Lokasyon Tanımı")
    lat = models.DecimalField(default=0,max_digits=10,decimal_places=8,verbose_name="Enlem")
    lon = models.DecimalField(default=0,max_digits=10, decimal_places=8, verbose_name="Boylam")

    def __unicode__(self):
        return "%s" % self.name

class Rooms(models.Model):
    account = models.ForeignKey(Accounts, related_name="Rooms", verbose_name="Hesap")
    location = models.ForeignKey(Locations,related_name="Rooms",verbose_name="Konum")
    name = models.CharField(max_length=50, verbose_name="Oda Tanımı")


    def __unicode__(self):
        return "%s" % self.name

class Devices(models.Model):
    account = models.ForeignKey(Accounts, related_name="Devices", verbose_name="Hesap")
    room = models.ForeignKey(Rooms,blank=True,null=True,related_name="Devices")
    type = models.CharField(max_length=15, choices=(('relay_current','Akım Sensörlü 16 Röle Kartı'),('relay','16 Röle Kartı'),('ir','IR Modüle')), verbose_name="Cihaz Tipi")
    name = models.CharField(max_length=50, verbose_name="Cihaz Tanımı")
    ip  = models.CharField(max_length=50,verbose_name="IP adresi")
    port = models.IntegerField(verbose_name="Port")

    def __unicode__(self):
        return "%s" % self.name

RelayIcons = (
    ('light','Ampül'),
    ('aircond','Klima'),
    ('fan','Fan'),
    ('su','Su Vanası'),
    ('gas','Gaz Vanası'),
)

RelayTypes = (
    ('switch','Aç / Kapat'),
    ('push','Bas - çek'),
    ('count', 'Geri Sayım'),
    ('scheduled','Zamanlanmış'),
)

class Relays(models.Model):
    device = models.ForeignKey(Devices, related_name="Relays", verbose_name="Cihaz")
    room = models.ForeignKey(Rooms, related_name="Relays", verbose_name="Oda")
    name = models.CharField(max_length=50, verbose_name="Röle Tanımı")

    pressed = models.BooleanField(default=False,verbose_name="Basılı mı?")

    relay_no = models.IntegerField(verbose_name="Röle No")
    type = models.CharField(max_length=20,choices=RelayTypes,verbose_name="Anahtar Tipi")
    icon = models.CharField(max_length=20,choices=RelayIcons,verbose_name="Simge")
    count = models.PositiveIntegerField(blank=True,null=True, verbose_name="Geri Sayım - dakika")

    days = models.CharField(max_length=7,default="0000000",verbose_name="Uygulanacak Günler")
    start_day = models.DateField(blank=True,null=True, verbose_name="Başlama Tarihi")
    finish_day = models.DateField(blank=True,null=True, verbose_name="Bitiş Tarihi")
    switch_on_time = models.TimeField(blank=True,null=True, verbose_name="Açma Zaman")
    switch_off_time = models.TimeField(blank=True, null=True, verbose_name="Kapama Zaman")


    def __unicode__(self):
        return "%s %s" % (self.name, self.room.name)

DAYS = (
    (1,"Pazartesi"),
    (2,"Salı"),
    (3,"Çarşamba"),
    (4,"Perşembe"),
    (5,"Cuma"),
    (6,"Cumartesi"),
    (7,"Pazar"),
)
class Crons(models.Model):
    relay = models.ForeignKey(Relays,verbose_name="Röle")
    day = models.IntegerField(choices=DAYS, verbose_name="Uygulanacak Günler")
    switch_on_time = models.TimeField(verbose_name="Açma Zaman")
    switch_off_time = models.TimeField(verbose_name="Kapama Zaman")



class IrButtons(models.Model):

    device = models.ForeignKey(Devices, related_name="IrButtons", verbose_name="Cihaz")
    room = models.ForeignKey(Rooms, related_name="IrButtons", verbose_name="Oda")
    name = models.CharField(max_length=50, verbose_name="Röle Tanımı")

    icon = models.CharField(max_length=20, choices=RelayIcons, verbose_name="Simge")

    ir_type = models.CharField(max_length=20,verbose_name="IR Tipi")
    ir_code = models.CharField(max_length=16,verbose_name="IR Code")
    ir_bits = models.IntegerField(verbose_name="Bits")

    def __unicode__(self):
        return "%s %s" % (self.name, self.room.name)