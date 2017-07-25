# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from modules.customers.models import Accounts, Locations, Plans, Rooms, Devices, Relays
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.encoding import smart_str
from django.db.models import Q
from django.contrib.auth import authenticate, login as doLogin , logout as doLogout
from django.contrib.sessions.models import Session
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
import json
import socket


def PermitResponse(response):
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Credentials'] = 'true'
    response['Access-Control-Allow-Headers'] = 'Content-Type'

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

        _profiles = Accounts.objects.filter(Q(user__username__contains=AllParams.get("keyword"))|Q(user__first_name__contains=AllParams.get("keyword"))|Q(user__last_name__contains=AllParams.get("keyword")))

        if _profiles.count() > 0:

            JsonContent = []
            for _profile in _profiles:
                _user = _profile.user
                JsonContent.append({
                'userid': str(_user.id),
                'username': _user.username,
                #'user_is_staff': _user.is_staff,
                #'user_is_superuser': _user.is_superuser,
                #'email': _user.email,
                'company': GetCompanyInfo(_user.Profiles),
                'level': _user.Profiles.level.id if _user.Profiles.level else None,
                'scoring': _user.Profiles.scoring,
                'official': _user.Profiles.official,
                'name': unicode(_user.get_full_name()),
                'avatar': getThumb(_user.Profiles.avatar, '128x128') if _user.Profiles.avatar else 'default_avatar.jpg',
                #'biography': _user.Profiles.biography,
                #'is_followed': CheckFollow(_user, _authuser),
                #'stat_events': _user.Events.all().count(),
                #'stat_follower': _user.Followers.all().count(),
                #'stat_following': _user.Profiles.following.all().count(),
                #'stat_comments': _user.Profiles.Comments.all().count(),
                #'fav_sports': GetFavSportsJson(_user.Profiles.favorite_sports.all()),
                #'my_events': GetMyEvents(_user),
                #'my_comments': GetMyComments(_user),
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
                'company':GetCompanyInfo(_user.Profiles),
                'level': _user.Profiles.level.id if _user.Profiles.level else None,
                'scoring': _user.Profiles.scoring,
                'official': _user.Profiles.official,
                'name': unicode(_user.get_full_name()),
                'avatar': getThumb(_user.Profiles.avatar, '128x128') if _user.Profiles.avatar else 'default_avatar.jpg',
                'biography':_user.Profiles.biography,
                'is_followed': CheckFollow(_user,_authuser),
                'stat_events': _user.Events.all().count(),
                'stat_follower':_user.Followers.all().count(),
                'stat_following': _user.Profiles.following.all().count(),
                'stat_comments': _user.Profiles.Comments.all().count(),
                'fav_sports': GetFavSportsJson(_user.Profiles.favorite_sports.all()),
                'my_events':GetMyEvents(_user),
                'my_comments': GetMyComments(_user),
            }
            Status=True

    return JsonResponser(Status, Message="", Data=JsonContent)




    MyComments = Comments.objects.filter(user=_user.Profiles,delete=False)
    Data = [{
        'id': item.id,
        'author':GetUserJson(item.author.user),
        'message':item.message,
        'create_date':item.create_date
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
        UserSession = Session.objects.get(session_key = Token)
        UserID = UserSession.get_decoded().get('_auth_user_id')
        SessionUser = User.objects.get(id = UserID)
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


        for rooms in _authuser.Accounts.Rooms.all():
            response_data.append({
                'id': rooms.id,
                'name': rooms.name,
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


def GetDeviceJson(device):

    if device:
        Data = {
            'id': device.id,
            'name': device.name,
            'ip': device.ip,
            'port': device.port,
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
    room_id = AllParams.get("room_id")
    _authuser = CheckUserSession(Token)
    response_data = []

    if _authuser:
        response_status = True
        response_data = []
        response_message = ""

        if room_id:
            _relays =  Relays.objects.filter(room__id=room_id,room__account__user=_authuser)
        else:
            _relays = Relays.objects.filter(room__account__user=_authuser)

        for relay in _relays:
            response_data.append({
                'id':relay.id,
                'device':GetDeviceJson(relay.device),
                'room_id':relay.room.id,
                'room': GetRoomJson(relay.room),
                'pressed':relay.pressed,
                'name':relay.name,
                'relay_no':relay.relay_no,
                'type':relay.type,
                'icon':relay.icon,
                'count':relay.count,
                'days':relay.days,
                'start_day':relay.start_day,
                'finish_day':relay.finish_day,
                'switch_on_time':relay.switch_on_time,
                'switch_off_time':relay.switch_off_time,
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
    _authuser = CheckUserSession(Token)


    _relay = Relays.objects.get(pk=relay_id, room__account__user=_authuser)

    host = _relay.device.ip
    port = _relay.device.port

    mySocket = socket.socket()
    mySocket.settimeout(2)
    mySocket.connect((host, port))

    if _relay.type == 'switch' or _relay.type == 'push':
        if _command == '1':
            cmd = 1
            _relay.pressed = True
            _relay.save()
        else:
            cmd = 2
            _relay.pressed = False
            _relay.save()

        message = bytearray(
            [0xaa, 0X0F, _relay.relay_no, cmd, 0X01, 0X01, 0X01, 0X01, 0X01, 0X01, 0X01, 0X01, 0X01, 0X01, 0X01, 0X01, 0X01,
             0X01, 0X01, 0xbb])
        mySocket.send(message)

    mySocket.close()

    return JsonResponser(True, None, _relay.pressed)