# -*- coding: utf-8 -*-

from django.http import HttpResponse,HttpResponseGone
from django.shortcuts import render
from django.template import RequestContext

from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from smtplib import SMTP, email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from base.settings import SMTP_HOST,SMTP_PASS,SMTP_USER,SMTP_NAME,SMTP_PORT
from django.utils import translation
from django.template import loader, Context


def Index(request):

    return render(request,'home.html')


def AboutUs(request):
    return render(request, 'about.html')

def Contact(request):
    return render(request, 'contact.html')



def SendMessage(request):


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
                   </html>""" % (name,email,message)

        htmlBody = MIMEText(html, 'html', _charset="UTF-8")
        msg.attach(htmlBody)

        smtp = SMTP()
        smtp.set_debuglevel(0)
        smtp.connect(SMTP_HOST, SMTP_PORT)

        smtp.login(from_addr, from_pass)
        smtp.sendmail(from_addr, to_addr, msg.as_string())
        smtp.quit()

        return HttpResponse('true', content_type="application/json")