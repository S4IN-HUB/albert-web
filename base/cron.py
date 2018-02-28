# -*- coding: utf-8 -*-

from modules.customers.models import Crons, IrCrons
from datetime import datetime
import sys
from django.core.cache import cache


class CronFunctions:

    def __init__(self):
        return

    def control_relays(self):

        now_date = datetime.now()

        _switch_on_crons = Crons.objects.filter(day__in=[now_date.weekday(), 8], switch_on_time__hour=now_date.strftime('%H'),
                                                switch_on_time__minute=now_date.strftime('%M')).values_list('relay')

        for item in _switch_on_crons:
            try:
                _cmd = cache.get(item.relay.device.name, [])
                _command = "RC#%s#%s" % (item.relay.relay_no, 1)
                _cmd.append({"CMD": _command, })
                cache.set(item.relay.device.name, _cmd)
                item.relay.pressed = True
            except:
                pass

        _switch_off_crons = Crons.objects.filter(day__in=[now_date.weekday(), 8], switch_off_time__hour=now_date.strftime('%H'),
                                                 switch_off_time__minute=now_date.strftime('%M')).values_list('relay')

        for item in _switch_off_crons:
            try:
                _cmd = cache.get(item.relay.device.name, [])
                _command = "RC#%s#%s" % (item.relay.relay_no, 0)
                _cmd.append({"CMD": _command, })
                cache.set(item.relay.device.name, _cmd)
                item.relay.pressed = False
            except:
                pass

    def control_ir_buttons(self):

        now_date = datetime.now()

        _switch_on_crons = IrCrons.objects.filter(day__in=[now_date.weekday(), 8],
                                                  switch_on_time__hour=now_date.strftime('%H'),
                                                  switch_on_time__minute=now_date.strftime('%M')).values_list('ir_button')

        for item in _switch_on_crons:
            try:
                _cmd = cache.get(item.ir_button.device.name, [])

                _command = "SENDIR#%s#%s#%s" % (item.ir_button.ir_type, item.ir_button.ir_code, item.ir_button.ir_bits)
                _cmd.append({'CMD': _command, })
                cache.set(item.ir_button.device.name, _cmd)
            except:
                pass

        _switch_off_crons = IrCrons.objects.filter(day__in=[now_date.weekday(), 8],
                                                   switch_off_time__hour=now_date.strftime('%H'),
                                                   switch_off_time__minute=now_date.strftime('%M')).values_list('ir_button')

        for item in _switch_off_crons:
            try:
                _cmd = cache.get(item.ir_button.device.name, [])

                _command = "SENDIR#%s#%s#%s" % (item.ir_button.ir_type, item.ir_button.ir_code, item.ir_button.ir_bits)
                _cmd.append({'CMD': _command, })
                cache.set(item.ir_button.device.name, _cmd)
            except:
                pass


if __name__ == "__main__":

    args = sys.argv
    cronList = CronFunctions

    for arg in args:

        if hasattr(cronList, arg):
            getattr(cronList, arg)()
