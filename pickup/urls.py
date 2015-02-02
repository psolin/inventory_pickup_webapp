#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.core.urlresolvers import reverse_lazy

from pickup import views

urlpatterns = [  # login form
                 # inventory management URLs
                 # Log out and redirect back to login form
    url(r'^$', 'django.contrib.auth.views.login', name='login'),
    url(r'^history/$', views.history, name='history'),
    url(r'^active/$', views.active, name='active'),
    url(r'^transaction/(\d{4,6}$)', views.transaction,
        name='transaction'),
    url(r'^home/$', views.home, name='home'),
    url(r'^logout/$', 'django.contrib.auth.views.logout',
        {'next_page': '/'}),
    ]