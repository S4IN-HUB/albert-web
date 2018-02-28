# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

account_types = (
    (0, 'Ev'),
    (1, 'Endüstriyel')
)


class Accounts(models.Model):
    """ Kullanıcı Hesapları, genişletilmiş Django AuthUser modeli. """
    user = models.OneToOneField(User, related_name="Accounts", verbose_name="Kullanıcı")
    user_type = models.PositiveSmallIntegerField(default=0, choices=account_types, verbose_name="Hesap Tipi")
    favourite_relays = models.ManyToManyField('customers.Relays', related_name="favourited_relays", null=True, blank=True)
    favourite_rooms = models.ManyToManyField('customers.Rooms', related_name="favourited_rooms", null=True, blank=True)

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
    """Hesap Durumu modeli"""
    account = models.ForeignKey(Accounts, related_name="Plans", verbose_name="Hesap")
    limit = models.IntegerField(default=1, verbose_name="Donanım Limiti")
    status = models.CharField(max_length=15, default='pending', choices=plan_status, verbose_name="Durum")

    class Meta(object):
        verbose_name = "Üyelik"
        verbose_name_plural = "Üyelik"


class Locations(models.Model):
    """Hesabın kullanılacağı adresin GPS Koordinatı"""
    account = models.ForeignKey(Accounts, related_name="Locations", verbose_name="Hesap",
                                help_text="Konumun bağlanacağı hesap")
    name = models.CharField(max_length=50, verbose_name="Konum Adı",
                            help_text="Hesaba bağlı cihazların kurulacağı adresin konumu için isimlendirme")
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

    """Cihazların kayıt edildiği model"""

    device_types = (
        ('RC', 'Akım Sensörlü 16 Röle Kartı'),
        ('RL', '16 Röle Kartı'),
        ('IR', 'IR Modüle')
    )
    account = models.ForeignKey(Accounts, null=True, blank=True, related_name="Devices", verbose_name="Hesap")
    room = models.ForeignKey(Rooms, blank=True, null=True, related_name="Devices", verbose_name='Oda')
    location = models.ForeignKey(Locations, blank=True, null=True, related_name="Devices", verbose_name='Konum')
    type = models.CharField(max_length=15, choices=device_types, verbose_name="Cihaz Tipi")
    name = models.CharField(max_length=50, verbose_name="Cihaz Adı", default='')
    description = models.CharField(max_length=50, verbose_name="Cihaz Tanımı", default='')
    wan_ip = models.CharField(max_length=50, verbose_name="WAN IP adresi", default='0.0.0.0')
    ip = models.CharField(max_length=50,blank=True, null=True, verbose_name="IP adresi", default='0.0.0.0')
    status = models.BooleanField(default=True, verbose_name="Durum")

    target_temperature = models.DecimalField(max_digits=5, decimal_places=2, default=25, verbose_name="Hedef Sıcaklık")
    temperature = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Sıcaklık")
    humidity = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Nem")

    oto_on_off = models.BooleanField(default=False, verbose_name="Oto. Aç/Kapat")
    spec = models.PositiveSmallIntegerField(default=0, choices=((1, 'Klima Yaz Modu'), (2, 'Klima Kış Modu'), (3, 'Klima Kapat')), verbose_name="Özel Tanım")

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


Icons = (
    ('flaticon-technology-2', 'Aydınlatma'),
    ('flaticon-light-bulb', 'Ampul'),
    ('flaticon-airconditioner', 'Klima'),
    ('flaticon-stove', 'Fırın'),
    ('flaticon-swimming-pool', 'Yüzme Havuzu'),
    ('flaticon-blinds', 'Panjur'),
    ('flaticon-garage', 'Garaj Kapısı Aç'),
    ('flaticon-garage-1', 'Garaj Kapısı Kapat'),
    ('flaticon-monitor', 'Televizyon'),
    ('flaticon-water-valve', 'Musluk'),
    ('flaticon-gas-pipe', 'Doğalgaz Vanası'),
    ('flaticon-valve', 'Su Vanası'),
    ('flaticon-lock-1', 'Kapı Kilidi Aç'),
    ('flaticon-lock', 'Kapı Kilitle'),
    ('flaticon-air-conditioner', 'Klima Kış Modu Aç'),
    ('flaticon-air-conditioner-1', 'Klima Yaz Modu Aç'),
    ('flaticon-technology-18', 'Müzik Seti'),
    ('flaticon-bathroom', 'Duş'),
    ('flaticon-fashion-3', 'Çamaşır Makinesi')
)


class Relays(models.Model):
    """Rölelerin kayıt edildiği model"""
    RelayTypes = (
        ('switch', 'Aç / Kapat'),
        ('push', 'Bas - çek'),
    )
    room = models.ForeignKey(Rooms, null=True,blank=True, related_name="Relays", verbose_name="Oda")
    device = models.ForeignKey(Devices, related_name="Relays", verbose_name="Cihaz")
    name = models.CharField(max_length=50, verbose_name="Röle Tanımı")

    pressed = models.BooleanField(default=False, verbose_name="Basılı mı?")

    relay_no = models.IntegerField(verbose_name="Röle No")
    type = models.CharField(max_length=20, default='switch', choices=RelayTypes, verbose_name="Anahtar Tipi")
    icon = models.CharField(max_length=40, default='flaticon-light-bulb', choices=Icons, verbose_name="Simge")

    total_instant_current = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Anlık Akım", default=0)
    total_instant_power = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Anlık Watt", default=0)

    def __unicode__(self):
        if self.device.room:
            return "%s %s" % (self.name, self.device.room.name)
        else:
            return "%s %s" % (self.name, '')

    class Meta(object):
        verbose_name = "Röle"
        verbose_name_plural = "Röleler"

sensor_types = (('current', 'Akın Sensörü'),)


class TempValues(models.Model):

    device = models.ForeignKey(Devices, related_name="TempValues", verbose_name="Cihaz")
    temperature = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Sıcaklık")
    humidity = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Nem")
    create_date = models.DateTimeField(verbose_name='Eklenme Tarihi', auto_now_add=True)

    def __unicode__(self):
        return "%s %s %s" % (self.device.name, self.temperature, self.humidity)

    class Meta(object):
        verbose_name = "Sıcaklı Nem Değeri"
        verbose_name_plural = "Sıcaklı Nem Değerleri"

    def save(self, *args, **kwargs):
        super(TempValues, self).save(*args, **kwargs)

        self.device.temperature = self.temperature
        self.device.humidity = self.humidity
        self.device.save()


class RelayCurrentValues(models.Model):
    """Röle Akım değerlerinin kayıt edildiği model"""
    relay = models.ForeignKey(Relays, related_name="CurrentValues", verbose_name="Röle")
    current_value = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Akım Değeri (Amper)")
    power_cons = models.DecimalField(max_digits=8, decimal_places=2, default=0,
                                     verbose_name="Kullanılan Güç (Watt/saat)")
    create_date = models.DateTimeField(verbose_name='Eklenme Tarihi', auto_now_add=True)

    def __unicode__(self):
        return "%s %s" % (self.relay.name, self.relay.device.room.name)

    class Meta(object):
        verbose_name = "Röle Akım Değeri"
        verbose_name_plural = "Röle Akım Değerleri"

    def save(self, *args, **kwargs):
        super(RelayCurrentValues, self).save(*args, **kwargs)
        self.relay.total_instant_current = self.current_value
        self.relay.total_instant_power = self.power_cons
        self.relay.save()


DAYS = (
    (0, "Pazartesi"),
    (1, "Salı"),
    (2, "Çarşamba"),
    (3, "Perşembe"),
    (4, "Cuma"),
    (5, "Cumartesi"),
    (6, "Pazar"),
    (7, "Her gün")
)


class Crons(models.Model):
    relay = models.ForeignKey(Relays, related_name="Crons", verbose_name="Röle")
    day = models.IntegerField(choices=DAYS, verbose_name="Uygulanacak Günler")
    switch_on_time = models.TimeField(verbose_name="Açma Zaman")
    switch_off_time = models.TimeField(verbose_name="Kapama Zaman")

    class Meta(object):
        verbose_name = "Zamanlama"
        verbose_name_plural = "Zamanlamalar"


class IrButton(models.Model):
    device = models.ForeignKey(Devices, related_name="IrButtons", verbose_name="Cihaz", null=True, blank=True)
    name = models.CharField(verbose_name="Buton Adı", max_length=50)
    icon = models.CharField(max_length=40, choices=Icons, verbose_name="Simge")
    ir_type = models.CharField(max_length=20, verbose_name="IR Tipi", null=True, blank=True)
    ir_code = models.CharField(max_length=16, verbose_name="IR Code", null=True, blank=True)
    ir_bits = models.IntegerField(verbose_name="Bits", null=True, blank=True)
    spec = models.PositiveSmallIntegerField(default=0, choices=((0,'Tanımsız'),(1,'Klima Yaz Modu'),(2,'Klima Kış Modu'),(3,'Klima Kapat')), verbose_name="Özel Tanım")

    def __unicode__(self):
        return "%s" %  self.name

    def save(self, *args, **kwargs):

        super(IrButton, self).save(*args, **kwargs)

        if self.spec != 0:
            _all = IrButton.objects.filter(device=self.device,spec=self.spec).exclude(pk=self.id)
            for item in _all:
                item.spec = 0
                item.save()

    class Meta(object):
        verbose_name = "IR Buton"
        verbose_name_plural = "IR Butonları"


class IrCrons(models.Model):
    ir_button = models.ForeignKey(IrButton, related_name="IrCrons", verbose_name="IR Butonu")
    day = models.IntegerField(choices=DAYS, verbose_name="Uygulanacak Günler")
    switch_on_time = models.TimeField(verbose_name="Açma Zaman")
    switch_off_time = models.TimeField(verbose_name="Kapama Zaman")

    class Meta(object):
        verbose_name = "Zamanlama"
        verbose_name_plural = "Zamanlamalar"


class Scenarios(models.Model):

    account = models.ForeignKey(Accounts, null=True, blank=True, related_name="Scenarios", verbose_name="Hesap")
    name = models.CharField(max_length=50, verbose_name="Senaryo Adı", default='')
    scenario_relays = models.ManyToManyField('customers.Relays', related_name="scenario_relays", verbose_name="Senaryo Röleleri", null=True, blank=True)
    scenario_ir_buttons = models.ManyToManyField('customers.IrButton', related_name="scenario_ir_buttons", verbose_name="Senaryo IR Butonları", null=True, blank=True)

    def __unicode__(self):
        return "%s" % self.name

    class Meta(object):
        verbose_name = "Senaryo"
        verbose_name_plural = "Senaryolar"
