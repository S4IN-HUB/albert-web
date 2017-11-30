# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from datetime import datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login as do_login
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.encoding import smart_str
from django.views.decorators.csrf import csrf_exempt

from modules.customers.models import Accounts, Relays, Crons, Devices, IrButton, Rooms, Locations, IrRemote


@csrf_exempt
def permit_response(response):
    """BURAYA AÇIKLAMA GELECEK"""
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Credentials'] = 'true'
    response['Access-Control-Allow-Headers'] = 'Content-Type'
    response['Cache-Control'] = 'no-store, no-cache'
    return response


@csrf_exempt
def json_responser(status, message="", data=None):
    """BURAYA AÇIKLAMA GELECEK"""
    json_data = {'response_message': message,
                 'response_code': status,
                 'response_data': data
                 }

    json_data = json.dumps(json_data, cls=DjangoJSONEncoder)
    response = HttpResponse(json_data)
    return permit_response(response)


@csrf_exempt
def get_params(request):
    """BURAYA AÇIKLAMA GELECEK"""
    print request.POST
    # print request.GET
    try:
        if request.POST:
            return request.POST

        return request.GET

    except Exception as uee:
        return {}


@csrf_exempt
def get_user(request):
    """BURAYA AÇIKLAMA GELECEK"""
    all_params = get_params(request)
    token = all_params.get("token")
    status = False
    json_content = {}

    _authuser = check_user_session(token)

    if not _authuser:
        return json_responser(False, message="Oturum Kapandı")

    if all_params.get("keyword"):

        _profiles = Accounts.objects.filter(
            Q(user__username__contains=all_params.get("keyword")) |
            Q(user__first_name__contains=all_params.get("keyword")) |
            Q(user__last_name__contains=all_params.get("keyword")))

        if _profiles.count() > 0:

            json_content = []
            for _profile in _profiles:
                _user = _profile.user
                json_content.append({
                    'userid': str(_user.id),
                    'username': _user.username,
                    # 'user_is_staff': _user.is_staff,
                    # 'user_is_superuser': _user.is_superuser,
                    # 'email': _user.email,
                    # 'company': GetCompanyInfo(_user.Profiles),
                    'level': _user.Profiles.level.id if _user.Profiles.level else None,
                    'scoring': _user.Profiles.scoring,
                    'official': _user.Profiles.official,
                    'name': unicode(_user.get_full_name()),
                    # 'avatar': getThumb(_user.Profiles.avatar,
                    #                    '128x128') if _user.Profiles.avatar else 'default_avatar.jpg',
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
            status = True
        else:
            return json_responser(False, message="Not found any matched user")

    if all_params.get("id"):
        _user = User.objects.get(pk=all_params.get("id"))

        if _user:
            json_content = {
                'userid': str(_user.id),
                'username': _user.username,
                'user_is_staff': _user.is_staff,
                'user_is_superuser': _user.is_superuser,
                'email': _user.email,
                # 'company': GetCompanyInfo(_user.Profiles),
                'level': _user.Profiles.level.id if _user.Profiles.level else None,
                'scoring': _user.Profiles.scoring,
                'official': _user.Profiles.official,
                'name': unicode(_user.get_full_name()),
                # 'avatar': getThumb(_user.Profiles.avatar, '128x128') if _user.Profiles.avatar else 'default_avatar.jpg',
                'biography': _user.Profiles.biography,
                # 'is_followed': CheckFollow(_user, _authuser),
                'stat_events': _user.Events.all().count(),
                'stat_follower': _user.Followers.all().count(),
                'stat_following': _user.Profiles.following.all().count(),
                'stat_comments': _user.Profiles.Comments.all().count(),
                # 'fav_sports': GetFavSportsJson(_user.Profiles.favorite_sports.all()),
                # 'my_events': GetMyEvents(_user),
                # 'my_comments': GetMyComments(_user),
            }
            status = True

    return json_responser(status, message="", data=json_content)

    # MyComments = Comments.objects.filter(user=_user.Profiles, delete=False)
    # Data = [{
    #     'id': item.id,
    #     'author': GetUserJson(item.author.user),
    #     'message': item.message,
    #     'create_date': item.create_date
    # } for item in MyComments]
    #
    # return Data


def get_user_json(remote_user, **kwargs):
    """BURAYA AÇIKLAMA GELECEK"""
    get_all_info = kwargs.get("get_all", False)

    if get_all_info:

        if len(list(remote_user.groups.all())) > 0:
            groups = []
            for grp in remote_user.groups.all():
                groups.append(grp.name)
        else:
            groups = None

        json_content = {
            'userid': str(remote_user.id),
            'username': remote_user.username,
            'token': str(request.session.session_key),
            'user_is_staff': remote_user.is_staff,
            'user_is_superuser': remote_user.is_superuser,
            'user_groups': groups,
            'email': remote_user.email,
            'name': unicode(remote_user.get_full_name())
        }

    else:
        json_content = {
            'userid': str(remote_user.id),
            'username': remote_user.username,
            'user_is_staff': remote_user.is_staff,
            'user_is_superuser': remote_user.is_superuser,
            'email': remote_user.email,
            'name': unicode(remote_user.get_full_name()),
            'avatar': 'default_avatar.jpg',
            'account_type': remote_user.Accounts.user_type
        }

    return json_content


def login_user(request, remote_user):
    if remote_user.is_active:
        remote_user.backend = 'django.contrib.auth.backends.ModelBackend'
        do_login(request, remote_user)
        json_content = get_user_json(remote_user)
        json_content.update({'token': str(request.session.session_key)})
        message = "Giriş Başarılı"
        status = True
    else:
        json_content = {}
        message = "Hesabınız Aktif Değil"
        status = False
    return status, message, json_content


def base_login(request, **kwargs):
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
        as a dict, or returns status (False) and Error Message.
    """

    all_params = get_params(request)

    print "all_params", all_params

    for key, val in kwargs.iteritems():
        all_params.update({key, val})

    status = False
    message = "Yeterli argüman gönderilmedi."
    json_content = {}
    user_name = all_params.get("username")
    password = all_params.get("password")
    print user_name, password

    remote_user = None

    if user_name and password:
        try:

            try:
                remote_user = User.objects.get(username=user_name.lower())
            except:
                remote_user = User.objects.get(email=user_name.lower())

            remote_user = authenticate(username=remote_user.username, password=password)
            if remote_user is None:
                message = "Kullanıcı adı veya parolanız hatalı."

        except ObjectDoesNotExist:
            message = "'%s' Kullanıcısı Bulunamadı." % smart_str(user_name)
            status = False

        except Exception as uee:
            message = "Şifre yanlış."
            status = False

    if remote_user:
        return login_user(request, remote_user)

    return status, message, json_content


def check_user_session(token):
    """Checks wheather user is online or not.
    If user is online means: user has a session, it returns user object, if not: returns False
    """
    try:
        user_session = Session.objects.get(session_key=token)
        user_id = user_session.get_decoded().get('_auth_user_id')
        session_user = User.objects.get(id=user_id)
        return session_user
    except:
        return False


@csrf_exempt
def api_register(request):

    response_status = False
    response_message = ""
    response_data = []

    all_params = get_params(request)
    name = all_params.get("name")
    surname = all_params.get("surname")
    email = all_params.get("email")
    username = all_params.get("email")
    password = all_params.get("password")
    phone = all_params.get("phone")

    remote_user = None

    if name and surname and email and password:

        # if not validate_email(email, verify=False):
        #     response_message = "Please enter a valid email address."

        # else:
        userCheck = User.objects.filter(Q(username=username) | Q(email=email))[:1]

        if userCheck.count() == 0:

            user = User.objects.create_user(username, email, password)
            user.first_name = name
            user.last_name = surname
            user.save()

            user_account = Accounts(
                user=user,
            )
            user_account.save()

            try:

                try:
                    remote_user = User.objects.get(username=username.lower())
                except:
                    remote_user = User.objects.get(email=username.lower())

                remote_user = authenticate(username=remote_user.username, password=password)
                if remote_user is None:
                    response_message = "Kullanıcı adı veya parolanız hatalı."

            except ObjectDoesNotExist:
                response_message = "'%s' Kullanıcısı Bulunamadı." % smart_str(username)
                response_status = False

            except Exception as uee:
                response_message = "Şifre yanlış."
                response_status = False

            if remote_user and remote_user.is_active:

                remote_user.backend = 'django.contrib.auth.backends.ModelBackend'
                do_login(request, remote_user)

                response_data.append({
                    'user_id': user.id,
                    'name': name,
                    'surname': surname,
                    'username': user.username,
                    'email': user.email,
                    'password': user.password,
                    'token': str(request.session.session_key)
                })

                response_status = True
                response_message = "Login succeed."

        else:
            response_message = "Email already exists."

    else:
        response_message = "Please fill all the fields."

    return json_responser(response_status, response_message, response_data[0])


@csrf_exempt
def api_login(request, **kwargs):
    """Logins user"""
    json_response = base_login(request, **kwargs)
    return json_responser(json_response[0], json_response[1], json_response[2])


@csrf_exempt
def api_logout(request):
    """BURAYA AÇIKLAMA GELECEK"""
    all_params = get_params(request)
    token = all_params.get("token")

    requested_user = check_user_session(token)
    if requested_user:
        user_session = Session.objects.get(session_key=token)
        user_session.delete()
        status = True
        message = "Çıkış başarılı."
    else:
        status = False
        message = "Kullanıcı bulunamadı."

    return json_responser(status, message, None)


@csrf_exempt
def check_auth(request):
    """BURAYA AÇIKLAMA GELECEK"""
    all_params = get_params(request)
    token = all_params.get("token")
    status = False

    requested_user = check_user_session(token)
    if requested_user is False:
        message = "Kullanıcı oturumu kapalı."
        req_user = None
    else:
        status = True
        message = "Kullanıcı Oturumu açık."
        req_user = {'username': requested_user.username,
                    'firstName': requested_user.first_name,
                    'lastName': requested_user.last_name,
                    }

    return json_responser(status, message, req_user)


@csrf_exempt
def add_location(request):
    """BURAYA AÇIKLAMA GELECEK"""

    all_params = get_params(request)
    token = all_params.get("token")
    location_name = all_params.get("location_name")
    _authuser = check_user_session(token)
    response_data = []
    response_status = False

    if _authuser:
        response_data = []

        if all_params.get('token'):

            account = Accounts.objects.get(user=_authuser)

            new_location = Locations(

                account=account,
                name=location_name
            )
            new_location.save()

            response_status = True

            response_data.append({
                'name': location_name,
                'id': new_location.id
            })

            response_message = "Location is added."

        else:

            response_message = "Error."

    else:
        response_message = "Please login first."

    return json_responser(response_status, response_message, response_data[0])


@csrf_exempt
def add_room(request):
    """BURAYA AÇIKLAMA GELECEK"""

    all_params = get_params(request)
    token = all_params.get("token")
    location_id = all_params.get("location_id")
    room_name = all_params.get("room_name")
    _authuser = check_user_session(token)
    response_data = []
    response_status = False

    if _authuser:
        response_data = []

        if all_params.get('token'):

            account = Accounts.objects.get(user=_authuser)
            location = Locations.objects.get(id=location_id, account=account)

            new_room = Rooms(

                account=account,
                location=location,
                name=room_name
            )
            new_room.save()

            response_status = True

            response_data.append({
                'name': room_name,
                'id': new_room.id
            })

            response_message = "Room is added."

        else:

            response_message = "Error."

    else:
        response_message = "Please login first."

    return json_responser(response_status, response_message, response_data[0])


@csrf_exempt
def add_device(request):
    """BURAYA AÇIKLAMA GELECEK"""

    all_params = get_params(request)

    token = all_params.get("token")
    location_id = all_params.get("location_id")
    device_type = all_params.get("device_type")
    device_name = all_params.get("device_name")

    _authuser = check_user_session(token)
    response_data = []
    response_status = False
    response_message = ""

    if _authuser:
        response_data = []

        if all_params.get('token'):

            account = Accounts.objects.get(user=_authuser)
            location = Locations.objects.get(id=location_id, account=account)

            if device_type == "IR":

                room_id = all_params.get("room_id")
                room = Rooms.objects.get(id=room_id, account=account)

                new_ir_device = Devices(

                    account=account,
                    location=location,
                    type=device_type,
                    name=device_name,
                    room=room,
                )
                new_ir_device.save()

            else:
                new_device = Devices(

                    account=account,
                    location=location,
                    type=device_type,
                    name=device_name,
                )
                new_device.save()

                for item in range(0, 15):

                    new_relay = Relays(

                        device=new_device,
                        name=item,
                        relay_no=item,
                        type="switch",
                        icon="light",
                    ).save()

            response_status = True
            response_message = "Device is added."
        else:

            response_message = "Error."

    else:
        response_message = "Please login first."

    return json_responser(response_status, response_message, response_data)


@csrf_exempt
def get_rooms(request):
    """BURAYA AÇIKLAMA GELECEK"""
    all_params = get_params(request)
    token = all_params.get("token")
    _authuser = check_user_session(token)
    response_data = []

    if _authuser:
        response_status = True
        response_data = []
        response_message = ""

        if all_params.get('location_id'):
            account = Accounts.objects.filter(user=_authuser)
            _rooms = Rooms.objects.filter(location__id=all_params.get('location_id'), account=account)
        else:
            _rooms = Rooms.objects.filter(account=_authuser)

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
                'device': get_device_json(rooms.Devices.all()) if rooms.Devices.all().count() > 0 else False,
            })
    else:
        response_status = False
        response_message = "Oturum kapalı"

    return json_responser(response_status, response_message, response_data)


@csrf_exempt
def get_relay_rooms(request):
    """BURAYA AÇIKLAMA GELECEK"""
    all_params = get_params(request)
    token = all_params.get("token")
    room_id = all_params.get("room_id")
    _authuser = check_user_session(token)
    response_data = []

    if _authuser:
        response_status = True
        response_data = []
        response_message = ""

        if all_params.get('room_id'):
            account = Accounts.objects.filter(user=_authuser)
            room = Rooms.objects.get(id=all_params.get('room_id'), account=account)
            location_rooms = room.location.Rooms.all()

        else:
            location_rooms = Rooms.objects.filter(account=_authuser)

        for rooms in location_rooms:
            response_data.append({
                'id': rooms.id,
                'name': rooms.name,
                'location': rooms.location.name if rooms.location else '',
                'have_temp': True if rooms.Devices.all().filter(type='ir').count() > 0 else False,
                'have_current': True if rooms.Devices.all().filter(type='relay_current').count() > 0 else False,
                # 'device': GetDeviceJson(
                #     rooms.Devices.all().filter(type='relay_current')[0]) if rooms.Devices.all().filter(
                #     type='relay_current').count() > 0 else False,
                'device': get_device_json(rooms.Devices.all()) if rooms.Devices.all().count() > 0 else False,
            })
    else:
        response_status = False
        response_message = "Oturum kapalı"

    return json_responser(response_status, response_message, response_data)


@csrf_exempt
def get_devices(request):
    """BURAYA AÇIKLAMA GELECEK"""
    all_params = get_params(request)
    token = all_params.get("token")
    _authuser = check_user_session(token)
    response_data = []

    if _authuser:
        response_status = True
        response_data = []
        response_message = ""

        for device in _authuser.Accounts.Devices.all():
            response_data.append({
                'id': device.id,
                'name': device.name,
                'type': device.type,
                'location': device.location.id,
                'room': get_room_json(device.room),
                'description': device.description,
                'wan_ip': device.wan_ip,
                'ip': device.ip,
                'status': device.status,
                'temperature': device.temperature,
                'humidity': device.humidity
            })
    else:
        response_status = False
        response_message = "Oturum kapalı"

    return json_responser(response_status, response_message, response_data)


@csrf_exempt
def get_locations(request):
    """BURAYA AÇIKLAMA GELECEK"""
    all_params = get_params(request)
    token = all_params.get("token")
    _authuser = check_user_session(token)
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

    return json_responser(response_status, response_message, response_data)


@csrf_exempt
def get_temp(request):
    """BURAYA AÇIKLAMA GELECEK"""
    all_params = get_params(request)
    token = all_params.get("token")
    _authuser = check_user_session(token)
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

    return json_responser(response_status, response_message, response_data)


def get_device_json(devices):
    """BURAYA AÇIKLAMA GELECEK"""
    data = {}
    if devices:
        dev_nr = 0
        for device in devices:
            data.update({
                dev_nr: {
                    'id': device.id,
                    'name': device.name,
                    'lan_ip': device.ip,
                    'wan_ip': device.wan_ip,
                }
            })
            dev_nr += 1
    else:
        data = None

    return data


def get_room_json(room):
    """BURAYA AÇIKLAMA GELECEK"""
    if room:
        data = {
            'id': room.id,
            'name': room.name
        }
    else:
        data = None

    return data


@csrf_exempt
def get_relays(request):
    """BURAYA AÇIKLAMA GELECEK"""
    all_params = get_params(request)
    token = all_params.get("token")
    room_id = all_params.get("room_id", None)
    _authuser = check_user_session(token)
    response_data = []

    if _authuser:
        response_status = True
        response_data = []
        response_message = ""

        if room_id:
            _relays = Relays.objects.filter(room__id=room_id, room__account__user=_authuser)
        else:
            _relays = Relays.objects.filter(room__account__user=_authuser)

        _relays = _relays.order_by("device", "relay_no")

        for relay in _relays:
            response_data.append({
                'id': relay.id,
                'device': get_device_json([relay.device]),
                'room_id': relay.room.id,
                'room': get_room_json(relay.room),
                'pressed': relay.pressed,
                'name': relay.name,
                'relay_no': relay.relay_no,
                'type': relay.type,
                'icon': relay.icon,
                'total_instant_current': relay.total_instant_current,
                'total_instant_power': relay.total_instant_power,
            })

    else:
        response_status = False
        response_message = "Oturum kapalı"

    return json_responser(response_status, response_message, response_data)


@csrf_exempt
def get_relay_settings(request):
    """BURAYA AÇIKLAMA GELECEK"""

    response_status = False

    all_params = get_params(request)
    token = all_params.get("token")
    room_id = all_params.get("room_id")
    device_id = all_params.get("device_id")
    relay_id = all_params.get("relay_id")
    relay_name = all_params.get("relay_name")
    relay_type = all_params.get("relay_type")
    relay_icon = all_params.get("relay_icon")
    _authuser = check_user_session(token)
    response_data = []

    if _authuser:
        response_data = []
        response_message = ""

        if room_id and device_id:

            response_status = True

            new_relay_room = Rooms.objects.get(id=room_id)
            new_relay_device = Devices.objects.get(id=device_id)
            update_relay = Relays.objects.get(id=relay_id)

            update_relay.room = new_relay_room
            update_relay.device = new_relay_device
            update_relay.name = relay_name
            update_relay.type = relay_type
            update_relay.icon = relay_icon
            update_relay.save()

    else:

        response_message = "Oturum kapalı"

    return json_responser(response_status, response_message, response_data)


@csrf_exempt
def get_device_relays(request):
    """BURAYA AÇIKLAMA GELECEK"""
    all_params = get_params(request)
    token = all_params.get("token")
    device_id = all_params.get("device_id", None)
    _authuser = check_user_session(token)
    response_data = []

    if _authuser:
        response_status = True
        response_data = []
        response_message = ""

        if device_id:
            _relays = Relays.objects.filter(device__in=device_id, room__account__user=_authuser)
        else:
            _relays = Relays.objects.filter(room__account__user=_authuser)

        _relays = _relays.order_by("device", "relay_no")

        for relay in _relays:
            response_data.append({
                'id': relay.id,
                'room_id': relay.room.id,
                'room': get_room_json(relay.room),
                'pressed': relay.pressed,
                'name': relay.name,
                'relay_no': relay.relay_no,
                'type': relay.type,
                'icon': relay.icon,
                'total_instant_current': relay.total_instant_current,
                'total_instant_power': relay.total_instant_power,
            })

    else:
        response_status = False
        response_message = "Oturum kapalı"

    return json_responser(response_status, response_message, response_data)


@csrf_exempt
def add_remote(request):
    """BURAYA AÇIKLAMA GELECEK"""

    all_params = get_params(request)
    token = all_params.get("token")
    device_id = all_params.get("device_id", None)
    room_id = all_params.get("room_id", None)
    remote_name = all_params.get("remote_name")
    _authuser = check_user_session(token)

    response_data = []

    if _authuser:
        response_data = []

        if device_id and room_id:

            device = Devices.objects.get(id=device_id)
            room = Rooms.objects.get(id=room_id)

            new_remote = IrRemote(
                device=device,
                room=room,
                name=remote_name
            )
            new_remote.save()

            response_status = True
            response_message = "Remote controller is added."

        else:
            response_status = False
            response_message = "No value for device_id or room_id or both."

    else:
        response_status = False
        response_message = "Oturum kapalı"

    return json_responser(response_status, response_message, response_data)


@csrf_exempt
def get_remotes(request):
    """BURAYA AÇIKLAMA GELECEK"""
    all_params = get_params(request)
    token = all_params.get("token")
    device_id = all_params.get("device_id", None)
    _authuser = check_user_session(token)
    response_data = []
    response_status = False

    if _authuser:
        response_data = []
        response_message = ""

        if device_id:
            _remotes = IrRemote.objects.filter(device__id=device_id)

            for remote in _remotes:
                response_data.append({
                    'id': remote.id,
                    'name': remote.name,
                })

            response_status = True

    else:
        response_status = False
        response_message = "Oturum kapalı"

    return json_responser(response_status, response_message, response_data)


@csrf_exempt
def send_command(request, device=None, command=None):

    """BURAYA AÇIKLAMA GELECEK"""

    AllParams = get_params(request) if request is not None else None
    Token = AllParams.get("token") if AllParams is not None else None
    relay_id = AllParams.get("relay_id") if AllParams is not None else None

    _command = AllParams.get("command") if AllParams is not None else command
    _device_id = AllParams.get("device_id") if AllParams is not None else None
    _authuser = check_user_session(Token) if Token is not None else None

    if _command == 'LST':
        _relays = Relays.objects.filter(device__id=_device_id, room__account__user=_authuser)
        stats = []
        for item in _relays:
            stats.append({"DN": item.device.name, "RN": item.relay_no, "S": int(item.pressed)})

        return json_responser(status=True, data=stats)

    if _command == 'CIW':
        _relays = Relays.objects.filter(device__id=_device_id, room__account__user=_authuser)
        stats = []
        for item in _relays:
            stats.append({"DN": item.device.name, "RN": item.relay_no, "I": item.total_instant_current,
                          "W": item.total_instant_power})

        return json_responser(status=True, data=stats)

    try:
        _relay = Relays.objects.get(pk=relay_id, room__account__user=_authuser)
    except ObjectDoesNotExist:
        _relay = None


    if _relay is not None and (_relay.type == 'switch' or _relay.type == 'push'):

        if _command == '1':
            _cmd = cache.get(_relay.device.name, [])
            _cmd.append({"CMD": "RC", "RN": _relay.relay_no, "ST": 1})
            cache.set(_relay.device.name, _cmd)

            # _relay.pressed = True
            # _relay.save()
            return HttpResponse('OK-' + str(_relay.relay_no) + '-1')
        else:
            _cmd = cache.get(_relay.device.name, [])
            _cmd.append({"CMD": "RC", "RN": _relay.relay_no, "ST": 0})
            cache.set(_relay.device.name, _cmd)

            # _relay.pressed = False
            # _relay.save()
            return HttpResponse('OK-' + str(_relay.relay_no) + '-0')

    else:
        # IR Modüle komut gönderimi bu ELSE içinde yapılır.
        if _command == 'READIR':
            _cmd = cache.get(device.name, [])
            _cmd.append({"CMD": _command})


    return json_responser(status=True, data="required params token, command, device_id")

def relay_control(request):
    """BURAYA AÇIKLAMA GELECEK"""
    if request.GET.get("relay"):
        relay = Relays.objects.get(pk=request.GET.get("relay"))

        if request.GET.get("action", "") == "open":

            _cmd = cache.get(relay.device.name, [])
            _command = "RC#%s#%s" % (relay.relay_no, 1)
            _cmd.append({"CMD": _command, })
            cache.set(relay.device.name, _cmd)
            relay.pressed = True

        elif request.GET.get("action", "") == "close":
            _cmd = cache.get(relay.device.name, [])
            _command = "RC#%s#%s" % (relay.relay_no, 0)
            _cmd.append({"CMD": _command, })
            cache.set(relay.device.name, _cmd)
            relay.pressed = False

        relay.save()

        print cache.get(relay.device.name, [])

    return HttpResponse('OK')


def cron_control(request):
    """BURAYA AÇIKLAMA GELECEK"""
    open_count = 0
    close_count = 0
    now_date = datetime.now()

    _devices = Crons.objects.filter(day=now_date.weekday(),
                                    switch_on_time__hour=now_date.strftime('%H'),
                                    switch_on_time__minute=now_date.strftime('%M')).values('relay__device').distinct()

    for item in _devices:

        device_id = item['relay__device']

        _device = Devices.objects.get(pk=device_id)

        _inprocess = cache.get("in_process", {})
        _inprocess.update({_device.name: True})
        cache.set("in_process", _inprocess)

        crons = Crons.objects.filter(day=now_date.weekday(),
                                     switch_on_time__hour=now_date.strftime('%H'),
                                     switch_on_time__minute=now_date.strftime('%M'),
                                     relay__device=_device
                                     )
        for item in crons:
            try:
                _cmd = cache.get(item.relay.device.name, [])
                _cmd.append({"CMD": "RC", "RN": item.relay.relay_no, "ST": 1})
                cache.set(item.relay.device.name, _cmd)
                open_count += 1
            except:
                pass

        crons = Crons.objects.filter(day=now_date.weekday(),
                                     switch_off_time__hour=now_date.strftime('%H'),
                                     switch_off_time__minute=now_date.strftime('%M'),
                                     relay__device=_device
                                     )
        for item in crons:
            try:
                _cmd = cache.get(item.relay.device.name, [])
                _cmd.append({"CMD": "RC", "RN": item.relay.relay_no, "ST": 0})
                cache.set(item.relay.device.name, _cmd)
                open_count += 1
            except:
                pass

        _inprocess = cache.get("in_process", {})
        del _inprocess[_device.name]
        cache.set("in_process", _inprocess)

    return HttpResponse(
        "Open : %s, Close: %s Time: %s," % (
            str(open_count), str(close_count), now_date.strftime('%H:%M')))


def send_ir_command(request):
    """
    IR Modülünü Kumandalarına ait herhangi bir butonun IR Komutunu seçilen butona SET edebilmek için
    CACHE'e SET edilecek butona ait parametre ekler.
    Socket Listener IR modülünden alacağı IR set Komutu ile CACHE'de belirtilen butona gönderilen komutu kayıt eder.
    BIR IR modülüne ait AYNI ANDA SADECE BİR BUTON SET EDİLEBİLİR.

    :param request:
    :return:
    """

    if request.GET.get("button", None):

        try:
            button = IrButton.objects.get(pk=request.GET.get("button"))
        except ObjectDoesNotExist:
            messages.error(request, "Buton tanımına erişilemiyor.")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        _cmd = cache.get(button.device.name, [])

        _command = "SENDIR#%s#%s#%s" % (button.ir_type, button.ir_code, button.ir_bits)
        _cmd.append({'CMD': _command, })
        cache.set(button.device.name, _cmd)

    return HttpResponse('OK')


def read_ir(request):

    _device = Devices.objects.get(pk=request.GET.get('device_id'))
    _cmd = cache.get(_device.name, [])
    _cmd.append({'CMD':'READIR',})
    cache.set(_device.name, _cmd)

    return HttpResponse('OK')