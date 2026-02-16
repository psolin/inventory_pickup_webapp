from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from pickup.views import CustomLogoutView
from pickup.views import signup, profile, profile_edit, add_transaction, check_transaction_num

urlpatterns = [
    path('', include('pickup.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='pickup/login.html'), name="login"),
    path('logout/', CustomLogoutView.as_view(), name="logout"),
    path('signup/', signup, name='signup'),
    path('profile/', profile, name='profile'),
    path('profile/edit/', profile_edit, name='profile_edit'),
    path('add-transaction/', add_transaction, name='add_transaction'),
    path('check-transaction-num/', check_transaction_num, name='check_transaction_num'),
    # Password change paths
    path('password_change/',
         auth_views.PasswordChangeView.as_view(
             template_name='pickup/password_change.html'),
         name='password_change'),
    path('password_change/done/',
         auth_views.PasswordChangeDoneView.as_view(
             template_name='pickup/password_change_done.html'),
         name='password_change_done'),

    # Password reset paths
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='pickup/password_reset.html'),
         name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='pickup/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='pickup/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='pickup/password_reset_complete.html'),
         name='password_reset_complete'),

]
