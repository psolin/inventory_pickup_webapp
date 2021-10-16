#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.views.generic import TemplateView
from django.urls import path, re_path

from pickup import views

urlpatterns = [  # login form
                 # inventory management URLs
                 # Log out and redirect back to login form
    re_path(r'^history/$', views.history, name='history'),
    re_path(r'^active/$', views.active, name='active'),
    re_path(r'^transaction/(\d{4,6}$)', views.transaction,
            name='transaction'),
    path('home/', views.home, name='home'),
    path('', views.home, name='home'),
    path('signup/', TemplateView.as_view(template_name="pickup/signup.html"))
]
