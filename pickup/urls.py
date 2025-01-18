from django.views.generic import TemplateView
from django.urls import path, re_path
from pickup import views

urlpatterns = [
    # Inventory management URLs
    re_path(r'^history/$', views.history, name='history'),
    re_path(r'^active/$', views.active, name='active'),
    re_path(r'^transaction/(\d{4,6}$)', views.transaction, name='transaction'),

    # Home page
    path('home/', views.home, name='home'),
    path('', views.home, name='home'),

    # Signup page
    path('signup/', TemplateView.as_view(template_name="pickup/signup.html"), name='signup')
]
