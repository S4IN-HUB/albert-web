# -*- coding: utf-8 -*-
"""Web sayfalarının barındığı modül"""
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP

from django.http import HttpResponse
from django.shortcuts import render

from base.settings import SMTP_HOST, SMTP_PASS, SMTP_USER, SMTP_PORT


def index(request):
    """
    Index sayfası
    :param request:
    :return:
    """
    return render(request, 'home.html')


def about_us(request):
    """
    Hakkımızda sayfası
    :param request:
    :return:
    """
    return render(request, 'about.html')


def contact(request):
    """
    İletişim sayfası
    :param request:
    :return:
    """
    return render(request, 'contact.html')


def send_message(request):
    """
    Eposta ile başvuru
    :param request:
    :return:
    """
    from_addr = SMTP_USER
    from_pass = SMTP_PASS
    message = request.POST.get('message')
    name = request.POST.get('name')
    email = request.POST.get('email')
    msg = MIMEMultipart('alternative')
    msg['From'] = from_addr
    msg['Subject'] = ''

    msg['To'] = to_addr = 'info@albertoakilliev.com'

    html = u"""<html>
                   <head>
                   <style>
                       @import url(//fonts.googleapis.com/css?family=Titillium+Web:400,300,300italic,600,700,600italic,400italic&subset=latin,latin-ext);
                       @import url(//fonts.googleapis.com/css?family=Open+Sans:400,300&subset=latin,latin-ext);
                       body{
                           font-family: "Titillium Web";
                           background: #FFFFFF;
                       }
                       *{
                       font-family: 'Titillium Web' !important;
                       -webkit-font-smoothing: antialiased;
                       -moz-osx-font-smoothing: grayscale;
                       }
                   </style>
                   </head>
                   <body>
                        <ul>
                            <li>
                                İsim :%s
                            </li>
                            <li>
                                Email :%s
                            </li>
                            <li>
                                Mesaj :%s
                            </li>
                        </ul>
                   </body>
                   </html>""" % (name, email, message)

    htmlBody = MIMEText(html, 'html', _charset="UTF-8")
    msg.attach(htmlBody)

    smtp = SMTP()
    smtp.set_debuglevel(0)
    smtp.connect(SMTP_HOST, SMTP_PORT)

    smtp.login(from_addr, from_pass)
    smtp.sendmail(from_addr, to_addr, msg.as_string())
    smtp.quit()

    return HttpResponse('true', content_type="application/json")
