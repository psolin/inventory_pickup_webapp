from django.urls import path
from pickup import views

urlpatterns = [
    path('active/', views.active, name='active'),
    path('archived/', views.archived, name='archived'),
    path('transaction/<int:trx>/', views.transaction, name='transaction'),
    path('home/', views.home, name='home'),
    path('', views.home, name='home'),
]
