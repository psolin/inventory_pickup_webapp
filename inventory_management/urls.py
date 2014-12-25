from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^', include('pickup.urls')),
    url(r'^admin/', include(admin.site.urls)),
]