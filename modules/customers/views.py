# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import socket
from datetime import datetime

import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login as doLogin
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.encoding import smart_str
from django.views.decorators.csrf import csrf_exempt

from modules.customers.models import Accounts, Relays, Crons, Devices, RelayCurrentValues


def PermitResponse(response):
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Credentials'] = 'true'
    response['Access-Control-Allow-Headers'] = 'Content-Type'
    response['Cache-Control'] = 'no-store, no-cache'
    return response


def JsonResponser(Status, Message="", Data=None):
    JsonData = {'response_message': Message,
                'response_code': Status,
                'response_data': Data
                }

    JsonData = json.dumps(JsonData, cls=DjangoJSONEncoder)
    response = HttpResponse(JsonData)
    return PermitResponse(response)


def GetParams(request):
    print request.POST
    print request.GET

    try:
        if request.POST:
            return request.POST
        return request.GET
    except:
        return {}


@csrf_exempt
def GetUser(request):
    AllParams = GetParams(request)
    Token = AllParams.get("token")
    Status = False
    Message = "Yeterli argüman gönderilmedi."
    JsonContent = {}

    _authuser = CheckUserSession(Token)

    if not _authuser:
        return JsonResponser(False, Message="Oturum Kapandı", Data=None)

    if AllParams.get("keyword"):

        _profiles = Accounts.objects.filter(Q(user__username__contains=AllParams.get("keyword")) | Q(
            user__first_name__contains=AllParams.get("keyword")) | Q(
            user__last_name__contains=AllParams.get("keyword")))

        if _profiles.count() > 0:

            JsonContent = []
            for _profile in _profiles:
                _user = _profile.user
                JsonContent.append({
                    'userid': str(_user.id),
                    'username': _user.username,
                    # 'user_is_staff': _user.is_staff,
                    # 'user_is_superuser': _user.is_superuser,
                    # 'email': _user.email,
                    'company': GetCompanyInfo(_user.Profiles),
                    'level': _user.Profiles.level.id if _user.Profiles.level else None,
                    'scoring': _user.Profiles.scoring,
                    'official': _user.Profiles.official,
                    'name': unicode(_user.get_full_name()),
                    'avatar': getThumb(_user.Profiles.avatar,
                                       '128x128') if _user.Profiles.avatar else 'default_avatar.jpg',
                    # 'biography': _user.Profiles.biography,
                    # 'is_followed': CheckFollow(_user, _authuser),
                    # 'stat_events': _user.Events.all().count(),
                    # 'stat_follower': _user.Followers.all().count(),
                    # 'stat_following': _user.Profiles.following.all().count(),
                    # 'stat_comments': _user.Profiles.Comments.all().count(),
                    # 'fav_sports': GetFavSportsJson(_user.Profiles.favorite_sports.all()),
                    # 'my_events': GetMyEvents(_user),
                    # 'my_comments': GetMyComments(_user),
                })
            Status = True
        else:
            return JsonResponser(False, Message="Not found any matched user", Data=None)

    if AllParams.get("id"):
        _user = User.objects.get(pk=AllParams.get("id"))

        if _user:
            JsonContent = {
                'userid': str(_user.id),
                'username': _user.username,
                'user_is_staff': _user.is_staff,
                'user_is_superuser': _user.is_superuser,
                'email': _user.email,
                'company': GetCompanyInfo(_user.Profiles),
                'level': _user.Profiles.level.id if _user.Profiles.level else None,
                'scoring': _user.Profiles.scoring,
                'official': _user.Profiles.official,
                'name': unicode(_user.get_full_name()),
                'avatar': getThumb(_user.Profiles.avatar, '128x128') if _user.Profiles.avatar else 'default_avatar.jpg',
                'biography': _user.Profiles.biography,
                'is_followed': CheckFollow(_user, _authuser),
                'stat_events': _user.Events.all().count(),
                'stat_follower': _user.Followers.all().count(),
                'stat_following': _user.Profiles.following.all().count(),
                'stat_comments': _user.Profiles.Comments.all().count(),
                'fav_sports': GetFavSportsJson(_user.Profiles.favorite_sports.all()),
                'my_events': GetMyEvents(_user),
                'my_comments': GetMyComments(_user),
            }
            Status = True

    return JsonResponser(Status, Message="", Data=JsonContent)

    MyComments = Comments.objects.filter(user=_user.Profiles, delete=False)
    Data = [{
        'id': item.id,
        'author': GetUserJson(item.author.user),
        'message': item.message,
        'create_date': item.create_date
    } for item in MyComments]

    return Data


def GetUserJson(RemoteUser, **kwargs):
    GetAllInfo = kwargs.get("GetAll")

    if GetAllInfo:

        if len(list(RemoteUser.groups.all())) > 0:
            Groups = []
            for grp in RemoteUser.groups.all():
                Groups.append(grp.name)
        else:
            Groups = None

        JsonContent = {
            'userid': str(RemoteUser.id),
            'username': RemoteUser.username,
            'token': str(request.session.session_key),
            'user_is_staff': RemoteUser.is_staff,
            'user_is_superuser': RemoteUser.is_superuser,
            'user_groups': Groups,
            'email': RemoteUser.email,
            'name': unicode(RemoteUser.get_full_name())
        }

    else:
        JsonContent = {
            'userid': str(RemoteUser.id),
            'username': RemoteUser.username,
            'user_is_staff': RemoteUser.is_staff,
            'user_is_superuser': RemoteUser.is_superuser,
            'email': RemoteUser.email,
            'name': unicode(RemoteUser.get_full_name()),
            'avatar': 'default_avatar.jpg',
        }

    return JsonContent


def LoginUser(request, RemoteUser):
    if RemoteUser.is_active:
        RemoteUser.backend = 'django.contrib.auth.backends.ModelBackend'
        doLogin(request, RemoteUser)
        JsonContent = GetUserJson(RemoteUser)
        JsonContent.update({'token': str(request.session.session_key)})
        Status = True
        Message = "Giriş Başarılı"
    else:
        Message = "Hesabınız Aktif Değil"
        Status = False
    return (Status, Message, JsonContent)


def BaseLogin(request, **kwargs):
    """Logins user. Required parameters are:
            username, password.
        returns:
                'userid': str(RemoteUser.id),
                'token': str(request.session.session_key),
                'user_is_staff': RemoteUser.is_staff,
                'user_is_superuser': RemoteUser.is_superuser,
                'user_groups': Groups,
                'email': RemoteUser.email,
                'name': unicode(RemoteUser.get_full_name())
        as a dict, or returns Status (False) and Error Message.
    """

    AllParams = GetParams(request)
    for key, val in kwargs.iteritems():
        AllParams.update({key, val})
    Status = False
    Message = "Yeterli argüman gönderilmedi."
    JsonContent = {}
    UserName = AllParams.get("username")
    Password = AllParams.get("password")
    print UserName, Password

    RemoteUser = None

    if UserName and Password:
        try:
            try:
                RemoteUser = User.objects.get(username=UserName.lower())
            except:
                RemoteUser = User.objects.get(email=UserName.lower())

            RemoteUser = authenticate(username=RemoteUser.username, password=Password)
            if RemoteUser is None:
                Message = "Kullanıcı adı veya parolanız hatalı."
        except ObjectDoesNotExist:
            Message = "'%s' Kullanıcısı Bulunamadı." % smart_str(UserName)
            Status = False
        except:
            Message = "Şifre yanlış."
            Status = False

    if RemoteUser:
        return LoginUser(request, RemoteUser)
    return (Status, Message, JsonContent)


def CheckUserSession(Token):
    """Checks wheather user is online or not.
    If user is online means: user has a session, it returns user object, if not: returns False
    """
    try:
        UserSession = Session.objects.get(session_key=Token)
        UserID = UserSession.get_decoded().get('_auth_user_id')
        SessionUser = User.objects.get(id=UserID)
        return SessionUser
    except:
        return False


@csrf_exempt
def ApiLogin(request, **kwargs):
    """Logins user"""

    JsonResponse = BaseLogin(request, **kwargs)
    return JsonResponser(JsonResponse[0], JsonResponse[1], JsonResponse[2])


@csrf_exempt
def ApiLogout(request):
    AllParams = GetParams(request)
    Token = AllParams.get("token")
    Status = False
    Message = "Yeterli argüman gönderilmedi."

    RequestedUser = CheckUserSession(Token)
    if RequestedUser:
        UserSession = Session.objects.get(session_key=Token)
        UserSession.delete()
        Status = True
        Message = "Çıkış başarılı."
    else:
        Status = False
        Message = "Kullanıcı bulunamadı."

    return JsonResponser(Status, Message, None)


@csrf_exempt
def CheckAuth(request):
    AllParams = GetParams(request)
    Token = AllParams.get("token")
    Status = False
    Message = "Yeterli argüman gönderilmedi."

    RequestedUser = CheckUserSession(Token)
    if RequestedUser is False:
        Message = "Kullanıcı oturumu kapalı."
        ReqUser = None
    else:
        Status = True
        Message = "Kullanıcı Oturumu açık."
        ReqUser = {'username': RequestedUser.username,
                   'firstName': RequestedUser.first_name,
                   'lastName': RequestedUser.last_name,
                   }

    return JsonResponser(Status, Message, ReqUser)


@csrf_exempt
def GetRooms(request):
    AllParams = GetParams(request)
    Token = AllParams.get("token")
    _authuser = CheckUserSession(Token)
    response_data = []

    if _authuser:
        response_status = True
        response_data = []
        response_message = ""

        if AllParams.get('location_id'):
            _rooms = _authuser.Accounts.Rooms.filter(location__id=AllParams.get('location_id'))
        else:
            _rooms = _authuser.Accounts.Rooms.all()

        for rooms in _rooms:
            response_data.append({
                'id': rooms.id,
                'name': rooms.name,
                'location': rooms.location.name if rooms.location else '',
                'have_temp': True if rooms.Devices.all().filter(type='ir').count() > 0 else False,
                'have_current': True if rooms.Devices.all().filter(type='relay_current').count() > 0 else False,
                # 'device': GetDeviceJson(
                #     rooms.Devices.all().filter(type='relay_current')[0]) if rooms.Devices.all().filter(
                #     type='relay_current').count() > 0 else False,
                'device': GetDeviceJson(rooms.Devices.all()) if rooms.Devices.all().count() > 0 else False,
            })
    else:
        response_status = False
        response_message = "Oturum kapalı"

    return JsonResponser(response_status, response_message, response_data)


@csrf_exempt
def GetLocations(request):
    AllParams = GetParams(request)
    Token = AllParams.get("token")
    _authuser = CheckUserSession(Token)
    response_data = []

    if _authuser:
        response_status = True
        response_data = []
        response_message = ""

        for location in _authuser.Accounts.Locations.all():
            response_data.append({
                'id': location.id,
                'name': location.name,
            })
    else:
        response_status = False
        response_message = "Oturum kapalı"

    return JsonResponser(response_status, response_message, response_data)


@csrf_exempt
def GetTemp(request):
    AllParams = GetParams(request)
    Token = AllParams.get("token")
    room_id = AllParams.get("room_id")
    _authuser = CheckUserSession(Token)
    response_data = []

    if _authuser:
        response_status = True
        response_data = []
        response_message = ""

        for location in _authuser.Accounts.Locations.all():
            response_data.append({
                'id': location.id,
                'name': location.name,
            })
    else:
        response_status = False
        response_message = "Oturum kapalı"

    return JsonResponser(response_status, response_message, response_data)


def GetDeviceJson(devices):
    for device in devices:
        Data = {device: {
                'id': device.id,
                'name': device.name,
                'lan_ip': device.ip,
                'wan_ip': device.wan_ip,
                'port': device.port,
            }
        }
    else:
        Data = None

    return Data


def GetRoomJson(room):
    if room:
        Data = {
            'id': room.id,
            'name': room.name
        }
    else:
        Data = None

    return Data


@csrf_exempt
def GetRelays(request):
    AllParams = GetParams(request)
    Token = AllParams.get("token")
    room_id = AllParams.get("room_id", None)
    _authuser = CheckUserSession(Token)
    response_data = []

    if _authuser:
        response_status = True
        response_data = []
        response_message = ""

        if room_id:
            _relays = Relays.objects.filter(room__id=room_id, room__account__user=_authuser)
        else:
            _relays = Relays.objects.filter(room__account__user=_authuser)

        for relay in _relays:
            response_data.append({
                'id': relay.id,
                'device': GetDeviceJson(relay.device),
                'room_id': relay.room.id,
                'room': GetRoomJson(relay.room),
                'pressed': relay.pressed,
                'name': relay.name,
                'relay_no': relay.relay_no,
                'type': relay.type,
                'icon': relay.icon,
                'total_instant_current':relay.total_instant_current,
                'total_instant_power':relay.total_instant_power,
            })

    else:
        response_status = False
        response_message = "Oturum kapalı"

    return JsonResponser(response_status, response_message, response_data)


@csrf_exempt
def SendCommand(request):
    AllParams = GetParams(request)
    Token = AllParams.get("token")
    relay_id = AllParams.get("relay_id")
    _command = AllParams.get("command")
    _device_id = AllParams.get("device_id")
    _authuser = CheckUserSession(Token)


    if _command == 'LST':
        _relays = Relays.objects.filter(device__id=_device_id, room__account__user=_authuser)
        stats = []
        for item in _relays:
            stats.append({"DN":item.device.name,"RN":item.relay_no,"S":int(item.pressed)})

        return JsonResponser(True, None, stats)

    if _command == 'CIW':
        _relays = Relays.objects.filter(device__id=_device_id, room__account__user=_authuser)
        stats = []
        for item in _relays:
            stats.append({"DN":item.device.name,"RN":item.relay_no,"I":item.total_instant_current,"W":item.total_instant_power})

        return JsonResponser(True, None, stats)

    _relay = Relays.objects.get(pk=relay_id, room__account__user=_authuser)

    host = _relay.device.ip
    port = _relay.device.port

    if _relay.type == 'switch' or _relay.type == 'push':
        if _command == '1':

            _cmd = cache.get(_relay.relay.device.name, [])
            _cmd.append({"CMD": "RC", "RN": _relay.relay.relay_no, "ST": 1})
            cache.set(_relay.relay.device.name, _cmd)

            _relay.pressed = True
            _relay.save()
            return HttpResponse('OK-' + str(_relay.relay_no) + '-1')
        else:
            _cmd = cache.get(_relay.relay.device.name, [])
            _cmd.append({"CMD": "RC", "RN": _relay.relay.relay_no, "ST": 0})
            cache.set(_relay.relay.device.name, _cmd)


            _relay.pressed = False
            _relay.save()
            return HttpResponse('OK-' + str(_relay.relay_no) + '-0')


def relay_control(request):
    if request.GET.get("relay"):
        relay = Relays.objects.get(pk=request.GET.get("relay"))

        if request.GET.get("action", "") == "open":

            _cmd = cache.get(relay.device.name, [])
            _cmd.append({"CMD": "RC", "RN": relay.relay_no, "ST": 1})
            cache.set(relay.device.name, _cmd)
            relay.pressed = True

        elif request.GET.get("action", "") == "close":
            _cmd = cache.get(relay.device.name, [])
            _cmd.append({"CMD": "RC", "RN": relay.relay_no, "ST": 0})
            cache.set(relay.device.name, _cmd)
            relay.pressed = False

        relay.save()

        print cache.get(relay.device.name,[])

    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def cron_control(request):
    open_count = 0
    close_count = 0
    now_date = datetime.now()
    crons = Crons.objects.filter(day=now_date.weekday(),
                                 switch_on_time__hour=now_date.strftime('%H'),
                                 switch_on_time__minute=now_date.strftime('%M'))

    for item in crons:

        try:
            _cmd = cache.get(item.relay.device.name, [])
            _cmd.append({"CMD":"RC", "RN":item.relay.relay_no, "ST":1 })
            cache.set(item.relay.device.name, _cmd)
            open_count += 1
        except:
            pass

    crons = Crons.objects.filter(day=now_date.weekday(),
                                 switch_off_time__hour=now_date.strftime('%H'),
                                 switch_off_time__minute=now_date.strftime('%M'))

    for item in crons:

        try:
            _cmd = cache.get(item.relay.device.name, [])
            _cmd.append({"CMD": "RC", "RN": item.relay.relay_no, "ST": 0})
            cache.set(item.relay.device.name, _cmd)
            close_count += 1
        except:
            pass

    # connected_devices = 0
    # updated_relays = 0
    # for device in Devices.objects.filter(status=True):
    #     try:
    #         r = requests.get('http://' + device.ip + ':' + str(device.port) + '/?cmd=A', timeout=15)
    #         connected_devices += 1
    #         curr_data = json.loads(r.text)
    #         for _relay in curr_data:
    #             relay_obj = Relays.objects.filter(device=device, relay_no=_relay.get("N"))[:1]
    #             if relay_obj.count() == 1:
    #
    #                 RelayCurrentValues(relay=relay_obj[0], current_value=_relay.get("A", 0),
    #                                    power_cons=_relay.get("W", 0)).save()
    #                 updated_relays += 1
    #
    #     except:
    #         pass
    #

    return HttpResponse(
        "Open : %s, Close: %s Time: %s, Connected Devices: %s, Updated Relays: %s" % (
        str(open_count), str(close_count), now_date.strftime('%H:%M'), str(connected_devices), str(updated_relays)))
