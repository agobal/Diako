from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns = patterns('Fara.views',
    url(r'^$', 'list', name='list'),
    url(r'^list/$', 'list', name='list'),
    url(r'^show/$', 'show', name='show'),
    url(r'^register/$', 'register', name='register'),
    url(r'^login/$', 'user_login', name='login'),
    url(r'^logout/$', 'user_logout', name='logout'),
    url(r'^NonElecShow/$', 'NonElecShow', name='NonElecShow'),
    url(r'^static/example.txt', 'send_file')
)