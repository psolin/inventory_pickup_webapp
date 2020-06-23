from django.contrib import admin
from django.urls import include, path, re_path
from pickup.views import home
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.urls import path, re_path
from django.contrib.auth.views import LoginView

from pickup import views

urlpatterns = [
    path('', include('pickup.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('login/', LoginView.as_view(template_name='login.html'), name="login"),
]