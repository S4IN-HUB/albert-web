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
from unidecode import unidecode

from modules.customers.models import Accounts, Relays, Crons, Devices, IrButton, Rooms, Locations, Scenarios, \
    ScenarioRelays


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


@csrf_exempt
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


@csrf_exempt
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


@csrf_exempt
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


@csrf_exempt
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
            response_message = "E-mail zaten kayıtlı."

    else:
        response_message = "Lütfen bütün alanları doldurunuz."

    return json_responser(response_status, response_message, response_data)


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
def delete_location(request):
    """BURAYA AÇIKLAMA GELECEK"""

    all_params = get_params(request)
    token = all_params.get("token")
    location_id = all_params.get("location_id")
    _authuser = check_user_session(token)
    response_data = []
    response_status = False

    if _authuser:
        response_data = []

        if location_id:

            account = Accounts.objects.get(user=_authuser)
            location = Locations.objects.get(pk=location_id, account=account)

            _rooms = Rooms.objects.filter(location__id=location_id, account=account)

            for room in _rooms:
                room.delete()

            location.delete()

            response_status = True
            response_message = "Location is deleted."

        else:

            response_message = "Please send location to delete."

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

            chack_device = Devices.objects.filter(type=device_type, name=device_name)
            if chack_device.count() > 0:
                if chack_device[0].account != None and chack_device[0].account != account:
                    return json_responser(False, "Bu cihaz zaten başka bir kullanıcıya tanımlanmış", response_data)

            if device_type == "IR":

                room_id = all_params.get("room_id")
                room = Rooms.objects.get(id=room_id, account=account)

                if chack_device.count() > 0:
                    new_ir_device = chack_device[0]
                    new_ir_device.account = account
                    new_ir_device.location = location
                    new_ir_device.type = device_type
                    new_ir_device.name = device_name
                    new_ir_device.description = device_name
                    new_ir_device.room = room

                else:
                    new_ir_device = Devices(
                        account=account,
                        location=location,
                        type=device_type,
                        name=device_name,
                        description=device_name,
                        room=room,
                    )
                new_ir_device.save()

            else:

                if chack_device.count() > 0:
                    new_device = chack_device[0]
                    new_device.account = account
                    new_device.location = location
                    new_device.type = device_type
                    new_device.name = device_name
                    new_device.description = device_name
                else:
                    new_device = Devices(
                        account=account,
                        location=location,
                        type=device_type,
                        name=device_name,
                        description=device_name,
                    )
                new_device.save()

            response_status = True
            response_message = "Device is added."
        else:

            response_message = "Error."

    else:
        response_message = "Please login first."

    return json_responser(response_status, response_message, response_data)


@csrf_exempt
def add_relay(request):
    """BURAYA AÇIKLAMA GELECEK"""

    all_params = get_params(request)
    token = all_params.get("token")
    room_id = all_params.get("room_id")
    device_id = all_params.get("device_id")
    relay_name = all_params.get("relay_name")
    relay_no = all_params.get("relay_no")
    relay_type = all_params.get("relay_type")
    relay_icon = all_params.get("relay_icon")

    _authuser = check_user_session(token)
    response_data = []
    response_status = False
    response_message = ""

    if _authuser:
        response_data = []

        if all_params.get('token'):

            account = Accounts.objects.get(user=_authuser)
            device = Devices.objects.get(id=device_id, account=account)
            room = Rooms.objects.get(id=room_id, account=account)

            new_relay = Relays(
                room=room,
                device=device,
                name=relay_name,
                relay_no=relay_no,
                type=relay_type,
                icon=relay_icon,
            )
            new_relay.save()

            response_status = True
            response_message = "New relay is added."

            response_data.append({
                "room": new_relay.room.id,
                "device": new_relay.device.id,
                "name": new_relay.name,
                "relay_no": new_relay.relay_no,
                "typ": new_relay.type,
                "icon": new_relay.icon,
            })
        else:
            response_message = "Error."

    else:
        response_message = "Please login first."

    return json_responser(response_status, response_message, response_data)


@csrf_exempt
def favourite_relay(request):
    """BURAYA AÇIKLAMA GELECEK"""

    all_params = get_params(request)
    token = all_params.get("token")
    _relay = all_params.get("relay")

    _authuser = check_user_session(token)
    response_data = []
    response_status = False

    if _authuser:
        response_data = []

        if _relay:

            account = Accounts.objects.get(user=_authuser)
            relay = Relays.objects.get(pk=_relay)
            account.favourite_relays.add(relay)

            response_status = True
            response_message = "Relay is added into favourites."

        else:

            response_message = "Please select a relay to add into favourites."

    else:
        response_message = "Please login first."

    return json_responser(response_status, response_message, response_data)


@csrf_exempt
def delete_favourite_relay(request):
    """BURAYA AÇIKLAMA GELECEK"""

    all_params = get_params(request)
    token = all_params.get("token")
    _relay = all_params.get("relay")

    _authuser = check_user_session(token)
    response_data = []
    response_status = False

    if _authuser:
        response_data = []

        if _relay:

            account = Accounts.objects.get(user=_authuser)
            relay = Relays.objects.get(pk=_relay)
            account.favourite_relays.remove(relay)

            response_status = True
            response_message = "Relay is deleted from favourites."

        else:

            response_message = "Please select a relay to delete from favourites."

    else:
        response_message = "Please login first."

    return json_responser(response_status, response_message, response_data)


@csrf_exempt
def get_favourite_relays(request):
    """BURAYA AÇIKLAMA GELECEK"""

    all_params = get_params(request)
    token = all_params.get("token")

    _authuser = check_user_session(token)

    response_data = []
    response_status = False
    response_message = ""

    if _authuser:
        response_data = []

        account = Accounts.objects.get(user=_authuser)

        _relays = account.favourite_relays.all()

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

            response_status = True

    else:
        response_status = False
        response_message = "Oturum kapalı"

    return json_responser(response_status, response_message, response_data)


@csrf_exempt
def favourite_room(request):
    """BURAYA AÇIKLAMA GELECEK"""

    all_params = get_params(request)
    token = all_params.get("token")
    _room = all_params.get("room")

    _authuser = check_user_session(token)
    response_data = []
    response_status = False

    if _authuser:
        response_data = []

        if _room:

            account = Accounts.objects.get(user=_authuser)
            room = Rooms.objects.get(pk=_room)
            account.favourite_rooms.add(room)

            response_status = True
            response_message = "Room is added into favourites."

        else:

            response_message = "Please select a room to add into favourites."

    else:
        response_message = "Please login first."

    return json_responser(response_status, response_message, response_data)


@csrf_exempt
def set_ir_shortcut(request):
    """BURAYA AÇIKLAMA GELECEK"""

    all_params = get_params(request)
    token = all_params.get("token")
    button_id = all_params.get("button_id")
    spec = all_params.get("spec")

    _authuser = check_user_session(token)
    response_data = []
    response_status = False

    if _authuser:
        response_data = []

        if button_id:

            _button = IrButton.objects.get(pk=button_id, device__account__user=_authuser)
            _button.spec = int(spec)
            _button.save()

            response_status = True
            response_message = "Buton kısa yol olarak tanımlandı"

        else:

            response_message = "Please select a room to add into favourites."

    else:
        response_message = "Please login first."

    return json_responser(response_status, response_message, response_data)


@csrf_exempt
def get_favourite_rooms(request):
    """BURAYA AÇIKLAMA GELECEK"""

    all_params = get_params(request)
    token = all_params.get("token")

    _authuser = check_user_session(token)

    response_data = []
    response_status = False
    response_message = ""

    if _authuser:
        response_data = []

        account = Accounts.objects.get(user=_authuser)

        _rooms = account.favourite_rooms.all()
        if _rooms:

            for room in _rooms:

                if room.Devices.all().filter(type='ir').count() > 0:

                    try:
                        ir_device = room.Devices.all().get(type='ir')
                    except:
                        ir_device = None

                    if ir_device:
                        response_data.append({
                            'id': room.id,
                            'name': room.name,
                            'location': room.location.name if room.location else '',
                            'temperature': int(ir_device.temperature),
                            'otoOnOff': ir_device.oto_on_off,
                            'spec': ir_device.spec,
                            'targetTemp': int(ir_device.target_temperature),
                            'humidity': int(ir_device.humidity),
                            'device': get_device_json(
                                room.Devices.all().filter(type='ir')) if room.Devices.all().filter(
                                type='ir').count() > 0 else False,
                            'have_ir': True if ir_device else False,
                            'ir_cold': ir_device.IrButtons.all().filter(spec=1)[
                                0].id if ir_device.IrButtons.all().filter(
                                spec=1).count() > 0 else False,
                            'ir_hot': ir_device.IrButtons.all().filter(spec=2)[
                                0].id if ir_device.IrButtons.all().filter(
                                spec=2).count() > 0 else False,
                            'ir_off': ir_device.IrButtons.all().filter(spec=3)[
                                0].id if ir_device.IrButtons.all().filter(
                                spec=3).count() > 0 else False,

                        })

        response_status = True

    else:
        response_status = False
        response_message = "Oturum kapalı"

    print response_status, response_message, response_data

    return json_responser(response_status, response_message, response_data)


@csrf_exempt
def get_room_info(request):
    """BURAYA AÇIKLAMA GELECEK"""

    all_params = get_params(request)
    token = all_params.get("token")
    room_id = all_params.get("room_id")

    _authuser = check_user_session(token)

    response_data = []
    response_status = False
    response_message = ""

    if _authuser:
        response_data = []

        account = Accounts.objects.get(user=_authuser)

        room = Rooms.objects.get(id=room_id, account=account)

        if room:

            if room.Devices.all().filter(type='ir').count() > 0:

                try:
                    ir_device = room.Devices.all().filter(type='ir')[0]
                except:
                    ir_device = None

                if ir_device:
                    response_data.append({
                        'id': room.id,
                        'name': room.name,
                        'location': room.location.name if room.location else '',
                        'temperature': int(ir_device.temperature),
                        'targetTemp': int(ir_device.target_temperature),
                        'humidity': int(ir_device.humidity),
                        'device': get_device_json(room.Devices.filter(type='ir')) if room.Devices.filter(
                            type='ir').count() > 0 else False,
                        'have_ir': True,
                        'ir_cold': ir_device.IrButtons.all().filter(spec=1)[
                            0].id if ir_device.IrButtons.all().filter(
                            spec=1).count() > 0 else False,
                        'ir_hot': ir_device.IrButtons.all().filter(spec=2)[
                            0].id if ir_device.IrButtons.all().filter(
                            spec=2).count() > 0 else False,
                        'ir_off': ir_device.IrButtons.all().filter(spec=3)[
                            0].id if ir_device.IrButtons.all().filter(
                            spec=3).count() > 0 else False,

                    })

            else:
                response_data.append({

                    'id': room.id,
                    'name': room.name,
                    'location': room.location.name if room.location else '',
                    'have_ir': False,
                })

        response_status = True

    else:
        response_status = False
        response_message = "Oturum kapalı"

    return json_responser(response_status, response_message, response_data)


@csrf_exempt
def delete_room(request):
    """BURAYA AÇIKLAMA GELECEK"""
    all_params = get_params(request)
    token = all_params.get("token")
    room_id = all_params.get("room_id")
    _authuser = check_user_session(token)
    response_data = []
    response_status = False

    if _authuser:
        response_data = []

        if room_id:
            account = Accounts.objects.filter(user=_authuser)
            room = Rooms.objects.filter(pk=room_id, account=account)
            room.delete()

            response_status = True
            response_message = "Room is deleted."

        else:

            response_message = "Please select a room to delete."

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
                'location': device.location.id if device.location else None,
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
def change_target_temp(request):
    """BURAYA AÇIKLAMA GELECEK"""

    all_params = get_params(request)
    token = all_params.get("token")
    device_id = all_params.get("device_id")
    value = all_params.get("value")
    _authuser = check_user_session(token)
    response_data = []

    if _authuser:
        response_status = True
        response_message = ""

        if device_id and value:

            device = Devices.objects.get(id=device_id)

            if value == '0':
                device.target_temperature -= 1
                device.save()
                return HttpResponse("Derece azaltıldı.")

            if value == '1':
                device.target_temperature += 1
                device.save()
                return HttpResponse('Derece arttırıldı')

        else:

            response_status = False
            response_message = "Eksik parametre gönderdiniz."

    else:
        response_status = False
        response_message = "Kullanıcı doğrulanamadı."

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


@csrf_exempt
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


@csrf_exempt
def get_room_json(room):
    """BURAYA AÇIKLAMA GELECEK"""
    if room:
        data = {
            'id': room.id,
            'name': room.name,
            'location': room.location.name if room.location else "Tanımsız"
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

        if relay_id and device_id:

            response_status = True
            update_relay = Relays.objects.get(id=relay_id)
            new_relay_device = Devices.objects.get(id=device_id)

            update_relay.device = new_relay_device
            update_relay.save()

            if room_id:
                new_relay_room = Rooms.objects.get(id=room_id)
                update_relay.room = new_relay_room
                update_relay.save()

            if relay_name:
                update_relay.name = relay_name
                update_relay.save()

            if relay_type:
                update_relay.type = relay_type
                update_relay.save()

            if relay_icon:
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
            _relays = Relays.objects.filter(device__id=device_id, device__account__user=_authuser)
        else:
            _relays = Relays.objects.filter(device__account__user=_authuser)

        _relays = _relays.order_by("device", "relay_no")

        for relay in _relays:
            response_data.append({
                'id': relay.id,
                'room_id': relay.room.id if relay.room else None,
                'room': get_room_json(relay.room) if relay.room else None,
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
def get_ir_buttons(request):
    """BURAYA AÇIKLAMA GELECEK"""
    all_params = get_params(request)
    token = all_params.get("token")
    device_id = all_params.get("device_id")
    _authuser = check_user_session(token)
    response_data = []
    response_status = False

    if _authuser:
        response_data = []
        response_message = ""

        if device_id:
            _buttons = IrButton.objects.filter(device__id=device_id)

            for button in _buttons:
                response_data.append({
                    'id': button.id,
                    'name': button.name,
                    'icon': button.icon,
                    'room': get_room_json(button.device.room),
                    'ir_type': button.ir_type,
                    'ir_code': button.ir_code,
                    'ir_bits': button.ir_bits
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


@csrf_exempt
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


@csrf_exempt
def relay_command(request):
    """BURAYA AÇIKLAMA GELECEK"""

    all_params = get_params(request)
    token = all_params.get("token")
    _relay = all_params.get("relay")
    _action = all_params.get("action")
    _authuser = check_user_session(token)
    response_data = []
    response_status = False

    if _authuser:
        response_data = []
        response_message = ""

        if _relay:
            relay = Relays.objects.get(pk=_relay)

            if _action == "open":

                _cmd = cache.get(relay.device.name, [])
                _command = "RC#%s#%s" % (relay.relay_no, 1)
                _cmd.append({"CMD": _command, })
                cache.set(relay.device.name, _cmd)
                relay.pressed = True

            elif _action == "close":
                _cmd = cache.get(relay.device.name, [])
                _command = "RC#%s#%s" % (relay.relay_no, 0)
                _cmd.append({"CMD": _command, })
                cache.set(relay.device.name, _cmd)
                relay.pressed = False

            relay.save()

            print cache.get(relay.device.name, [])

            return json_responser(True, "OK", {})

    else:
        response_status = False
        response_message = "Oturum kapalı"

    return json_responser(response_status, response_message, response_data)


@csrf_exempt
def relay_command_update(request):
    """BURAYA AÇIKLAMA GELECEK"""

    all_params = get_params(request)
    token = all_params.get("token")
    _relay = all_params.get("relay")
    _authuser = check_user_session(token)
    response_data = []
    response_status = False

    if _authuser:
        response_data = []
        response_message = ""

        if _relay:
            relay = Relays.objects.get(pk=_relay)

            relay.pressed = False
            relay.save()

        return HttpResponse('OK')

    else:
        response_status = False
        response_message = "Oturum kapalı"

    return json_responser(response_status, response_message, response_data)


@csrf_exempt
def cron_control(request):
    """BURAYA AÇIKLAMA GELECEK"""

    now_date = datetime.now()

    _devices = Crons.objects.filter(day=now_date.weekday(),
                                    switch_on_time__hour=now_date.strftime('%H'),
                                    switch_on_time__minute=now_date.strftime('%M')).values('relay__device').distinct()

    for item in _devices:

        device_id = item['relay__device']

        _device = Devices.objects.get(pk=device_id)

        crons = Crons.objects.filter(day=now_date.weekday(),
                                     switch_on_time__hour=now_date.strftime('%H'),
                                     switch_on_time__minute=now_date.strftime('%M'),
                                     relay__device=_device
                                     )
        for item in crons:
            try:
                _cmd = cache.get(item.relay.device.name, [])
                _command = "RC#%s#%s" % (item.relay.relay_no, 1)
                _cmd.append({"CMD": _command, })
                cache.set(item.relay.device.name, _cmd)
                item.relay.pressed = True

                _cmd = cache.get(item.relay.device.name, [])
                _command = "#LST#"
                _cmd.append({"CMD": _command, })
                cache.set(item.relay.device.name, _cmd)

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
                _command = "RC#%s#%s" % (item.relay.relay_no, 0)
                _cmd.append({"CMD": _command, })
                cache.set(item.relay.device.name, _cmd)
                item.relay.pressed = False
            except:
                pass


@csrf_exempt
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


@csrf_exempt
def read_ir(request):
    _device = Devices.objects.get(pk=request.GET.get('device_id'))
    _cmd = cache.get(_device.name, [])
    _cmd.append({'CMD': 'READIR', })
    cache.set(_device.name, _cmd)

    return HttpResponse('OK')


@csrf_exempt
def read_ir_button(request):
    """BURAYA AÇIKLAMA GELECEK"""

    all_params = get_params(request)
    token = all_params.get("token")
    device_id = all_params.get("device_id")

    _authuser = check_user_session(token)
    response_data = []
    response_status = False
    response_message = ""

    if _authuser:

        response_status = True

        if device_id:

            _device = Devices.objects.get(pk=device_id)

            _cmd = cache.get(_device.name, [])
            _cmd.append({'CMD': 'READIR', })
            cache.set(_device.name, _cmd)

            return HttpResponse('OK')

        else:
            response_status = False
            response_message = "Please send device id."

    else:
        response_message = "Please login first."

    return json_responser(response_status, response_message, response_data)


@csrf_exempt
def ir_command(request):
    """BURAYA AÇIKLAMA GELECEK"""

    all_params = get_params(request)
    token = all_params.get("token")
    button_id = all_params.get("button_id")

    _authuser = check_user_session(token)
    response_data = []
    response_status = False
    response_message = ""

    if _authuser:

        response_status = True

        try:
            button = IrButton.objects.get(pk=button_id, device__account__user=_authuser)
        except ObjectDoesNotExist:
            messages.error(request, "Buton tanımına erişilemiyor.")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        _cmd = cache.get(button.device.name, [])

        _command = "SENDIR#%s#%s#%s" % (button.ir_type, button.ir_code, button.ir_bits)
        _cmd.append({'CMD': _command, })
        cache.set(button.device.name, _cmd)

    else:
        response_message = "Please login first."

    return json_responser(response_status, response_message, response_data)


@csrf_exempt
def delete_ir_button(request):
    """ BURAYA AÇIKLAMA GELECEK """

    all_params = get_params(request)
    token = all_params.get("token")
    ir_button_id = all_params.get("button_id")

    _authuser = check_user_session(token)
    response_data = []
    response_status = False
    response_message = ""

    if _authuser:

        response_status = True

        try:
            button = IrButton.objects.get(pk=ir_button_id, device__account__user=_authuser)
            button.delete()
            response_message = "IR butonu silindi."

        except ObjectDoesNotExist:
            messages.error(request, "Buton tanımına erişilemiyor")
            return HttpResponseRedirect(request.META.get("HTTP _REFERER"))

    else:
        response_message = "Lütfen giriş yapınız."

    return json_responser(response_status, response_message, response_data)


@csrf_exempt
def delete_rl_button(request):
    """ BURAYA AÇIKLAMA GELECEK """

    all_params = get_params(request)
    token = all_params.get("token")
    rl_button_id = all_params.get("button_id")

    _authuser = check_user_session(token)
    response_data = []
    response_status = False
    response_message = ""

    if _authuser:

        response_status = True

        try:
            button = Relays.objects.get(pk=rl_button_id, device__account__user=_authuser)
            button.delete()
            response_message = "RL butonu silindi."

        except ObjectDoesNotExist:
            messages.error(request, "Buton tanımına erişilemiyor")
            return HttpResponseRedirect(request.META.get("HTTP _REFERER"))

    else:
        response_message = "Lütfen giriş yapınız."

    return json_responser(response_status, response_message, response_data)


@csrf_exempt
def change_ir_button(request):
    """ BURAYA AÇIKLAMA GELECEK """

    all_params = get_params(request)
    token = all_params.get("token")
    ir_button_id = all_params.get("button_id")
    ir_button_name = all_params.get("button_name")

    _authuser = check_user_session(token)
    response_data = []
    response_status = False
    response_message = ""

    if _authuser:

        response_status = True

        try:
            button = IrButton.objects.get(pk=ir_button_id, device__account__user=_authuser)
            button.name = ir_button_name
            button.save()
            response_message = "IR butonu ismi değiştirildi."

        except ObjectDoesNotExist:
            messages.error(request, "Buton tanımına erişilemiyor")
            return HttpResponseRedirect(request.META.get("HTTP _REFERER"))

    else:
        response_message = "Lütfen giriş yapınız."

    return json_responser(response_status, response_message, response_data)


@csrf_exempt
def add_new_scenario(request):
    """BURAYA AÇIKLAMA GELECEK"""

    all_params = get_params(request)
    token = all_params.get("token")
    scenario_name = all_params.get("scenario_name")

    _authuser = check_user_session(token)
    response_data = []
    response_status = False

    if _authuser:

        account = Accounts.objects.get(user=_authuser)

        new_scenario = Scenarios(
            account=account,
            name=scenario_name
        )
        new_scenario.save()

        response_message = "Senaryo eklendi."
        response_status = True

    else:
        response_message = "Lütfen giriş yapınız."

    return json_responser(response_status, response_message, response_data)


@csrf_exempt
def delete_scenario(request):
    """BURAYA AÇIKLAMA GELECEK"""

    all_params = get_params(request)
    token = all_params.get("token")
    scenario_id = all_params.get("scenario_id")

    _authuser = check_user_session(token)
    response_data = []
    response_status = False

    if _authuser:

        account = Accounts.objects.get(user=_authuser)
        scenario = Scenarios.objects.get(account=account, pk=scenario_id)
        scenario.delete()

        response_message = "Senaryo silindi."
        response_status = True

    else:
        response_message = "Lütfen giriş yapınız."

    return json_responser(response_status, response_message, response_data)


@csrf_exempt
def list_user_scenarios(request):
    """KULLANICININ TANIMLADIĞI SENARYOLARI GETİRİR"""

    response_status = False
    response_data = []

    all_params = get_params(request)

    token = all_params.get('token')

    _authuser = check_user_session(token)

    if _authuser:

        account = Accounts.objects.get(user=_authuser)

        scenarios = Scenarios.objects.filter(account=account)

        if scenarios.count() > 0:

            for scenario in scenarios:
                response_data.append({
                    'scenario_id': scenario.id,
                    'scenario_name': scenario.name,
                    'timer': scenario.switch_on_time.strftime('%H-%M')
                })

            response_status = True
            response_message = "Senaryolar"

        else:
            response_message = "Senaryo bulunamadı"

    else:
        response_message = "Lütfen giriş yapınız."

    return json_responser(response_status, response_message, response_data)


@csrf_exempt
def list_scenario_relays(request):
    """Seçili senaryodaki röleleri listeler"""

    response_data = []
    response_message = ""
    response_status = False

    all_params = get_params(request)

    token = all_params.get('token')
    scenario_id = all_params.get('scenario_id')

    _authUser = check_user_session(token)

    if _authUser:

        scenario = Scenarios.objects.get(pk=scenario_id)
        scenario_relays = ScenarioRelays.objects.filter(scenario=scenario)

        if scenario_relays.count() > 0:

            for item in scenario_relays:

                response_data.append({
                    'id': item.id,
                    'relay_id': item.relay.id,
                    'room': get_room_json(item.relay.room),
                    'name': item.relay.name,
                    'icon': item.relay.icon,
                    'pressed': item.relay.pressed,
                })

            response_status = True

        else:
            response_status = True
            response_message = "Senaryo rölesi bulunamadı."

    else:
        response_message = "Lütfen giriş yapınız."

    return json_responser(response_status, response_message, response_data)


@csrf_exempt
def add_relay_to_scenario(request):
    """BURAYA AÇIKLAMA GELECEK"""

    all_params = get_params(request)
    token = all_params.get("token")
    _scenario = all_params.get("scenario")
    _relay = all_params.get("relay")
    action = all_params.get("action")

    _authuser = check_user_session(token)
    response_data = []
    response_status = False

    if _authuser:
        response_data = []

        if _relay:

            account = Accounts.objects.get(user=_authuser)
            scenario = Scenarios.objects.get(id=_scenario, account=account)
            relay = Relays.objects.get(pk=_relay)

            if not ScenarioRelays.objects.filter(scenario=scenario, relay=relay).count() > 0:

                new_scenario_relay = ScenarioRelays(
                    scenario=scenario,
                    relay=relay,
                    action=action
                )
                new_scenario_relay.save()

                response_status = True
                response_message = "Röle senaryoya eklendi."

            else:
                response_message = "Röle zaten senaryoda bulunuyor"

        else:

            response_message = "Röle bulunamadı."

    else:
        response_message = "Lütfen giriş yapınız."

    return json_responser(response_status, response_message, response_data)


@csrf_exempt
def delete_relay_from_scenario(request):
    """BURAYA AÇIKLAMA GELECEK"""

    all_params = get_params(request)
    token = all_params.get("token")
    _scenario = all_params.get("scenario")
    _relay = all_params.get("relay")

    _authuser = check_user_session(token)
    response_data = []
    response_status = False

    if _authuser:
        response_data = []

        if _relay:

            account = Accounts.objects.get(user=_authuser)
            scenario = Scenarios.objects.get(id=_scenario, account=account)
            relay = Relays.objects.get(pk=_relay)

            scenario_relay = ScenarioRelays.objects.get(scenario=scenario, relay=relay)
            scenario_relay.delete()

            response_status = True
            response_message = "Röle senaryodan çıkarıldı"

        else:

            response_message = "Röle bulunmadı"

    else:
        response_message = "Lütfen giriş yapınız."

    return json_responser(response_status, response_message, response_data)


@csrf_exempt
def activate_scenario(request):
    """Senaryoyu aktif etmek için kullanılır"""

    response_data = []
    response_status = False

    all_params = get_params(request)

    token = all_params.get('token')
    scenario_id = all_params.get('scenario_id')

    _authUser = check_user_session(token)

    if _authUser:

        account = Accounts.objects.get(user=_authUser)
        scenario = Scenarios.objects.get(id=scenario_id, account=account)

        scenario_relays = ScenarioRelays.objects.filter(scenario=scenario)

        if scenario_relays.count() > 0:

            for item in scenario_relays:

                if item.action == 1:

                    _cmd = cache.get(item.relay.device.name, [])
                    _command = "RC#%s#%s" % (item.relay.relay_no, 1)
                    _cmd.append({"CMD": _command, })
                    cache.set(item.relay.device.name, _cmd)
                    item.relay.pressed = True


                elif item.action == 2:
                    _cmd = cache.get(item.relay.device.name, [])
                    _command = "RC#%s#%s" % (item.relay.relay_no, 0)
                    _cmd.append({"CMD": _command, })
                    cache.set(item.relay.device.name, _cmd)
                    item.relay.pressed = False

                item.relay.save()

            response_status = True
            response_message = "Senaryo röleleri aktifleştirildi."

        else:
            response_status = True
            response_message = "Senaryo rölesi bulunamadı."

    else:
        response_message = "Lütfen giriş yapınız."

    return json_responser(response_status, response_message, response_data)


@csrf_exempt
def list_relay_crons(request):
    """Röleye ait zamanlamaları listeler"""

    response_data = []
    response_message = ""
    response_status = False

    all_params = get_params(request)

    token = all_params.get('token')
    relay_id = all_params.get('relay_id')

    _authUser = check_user_session(token)

    if _authUser:

        account = Accounts.objects.get(user=_authUser)
        relay = Relays.objects.get(device__account=account, pk=relay_id)
        crons = Crons.objects.filter(relay=relay)

        if crons.count() > 0:

            for cron in crons:

                response_data.append({
                    'id': cron.id,
                    'day': unidecode(cron.get_day_display()),
                    'open_time': cron.switch_on_time.strftime('%H:%M'),
                    'close_time': cron.switch_off_time.strftime('%H:%M')
                })

            response_status = True

        else:
            response_status = True
            response_message = "Tanımlanmış zamanlama bulunamadı."

    else:
        response_message = "Lütfen giriş yapınız."

    return json_responser(response_status, response_message, response_data)


@csrf_exempt
def delete_relay_cron(request):
    """Seçili röle cronunu siler"""

    response_data = []
    response_message = ""
    response_status = False

    all_params = get_params(request)

    token = all_params.get('token')
    cron_id = all_params.get('cron_id')

    _authUser = check_user_session(token)

    if _authUser:

        cron = Crons.objects.get(pk=cron_id)
        cron.delete()

        response_status = True

    else:
        response_message = "Lütfen giriş yapınız."

    return json_responser(response_status, response_message, response_data)


@csrf_exempt
def add_new_relay_cron(request):
    """Yeni röle cronu eklemeyi sağlar"""

    response_data = []
    response_status = False
    response_message = ""

    all_params = get_params(request)

    token = all_params.get('token')
    relay_id = all_params.get('relay_id')
    day = all_params.get('cron_day')
    open_time = all_params.get('open_time')
    close_time = all_params.get('close_time')

    _authUser = check_user_session(token)

    if _authUser:

        account = Accounts.objects.get(user=_authUser)
        relay = Relays.objects.get(device__account=account, pk=relay_id)

        new_cron = Crons(
            relay=relay,
            day=day,
            switch_on_time=open_time,
            switch_off_time=close_time
        )
        new_cron.save()

        response_status = True

    else:
        response_message = "Lütfen giriş yapınız."

    return json_responser(response_status, response_message, response_data)
