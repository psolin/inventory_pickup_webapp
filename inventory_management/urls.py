from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import include
from django.urls import path

urlpatterns = [
    path('', include('pickup.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('login/', LoginView.as_view(template_name='pickup/registration/login.html'), name="login"),
]
