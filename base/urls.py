"""albert URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from modules.customers.views import ApiLogin, ApiLogout, GetRooms, GetRelays, SendCommand
from modules.masterpage.views import Index,AboutUs,Contact,SendMessage
urlpatterns = [
    url(r'^$', Index, name='index'),
    url(r'^akilli-ev-sistemi-nedir/$',AboutUs, name='AboutUs'),
    url(r'^iletisim/$', Contact, name='Contact'),
    url(r'^send-message/$', SendMessage, name='SendMessage'),
    url(r'^admin/', admin.site.urls),
    url(r'^api/login/$', ApiLogin),
    url(r'^api/logout/$', ApiLogout),
    url(r'^api/list/rooms/$', GetRooms),
    url(r'^api/list/relays/$', GetRelays),
    url(r'^api/list/send-command/$', SendCommand)



]
