from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.core.urlresolvers import reverse_lazy

from pickup import views

urlpatterns = [
    # login form
    url(r'^$', 'django.contrib.auth.views.login', name='login'),
    
    # inventory management URLs
    url(r'^history/$', views.history, name='history'),
    url(r'^active/$', views.active, name='active'),
    url(r'^transaction/(\d{4,6}$)', views.transaction, name='transaction'),
    url(r'^home/$', views.home, name='home'),

    # Log out and redirect back to login form
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}), 
	
	# "We sent you an email..." password reset page
	url(r'^accounts/password/reset/done/$', 'django.contrib.auth.views.password_reset_done', name='password_reset_done'),
    
    url(r'^password/change/done/$', auth_views.password_change_done, name='auth_password_change_done'),
    url(r'^password/reset/$', auth_views.password_reset, {'post_reset_redirect': reverse_lazy('auth_password_reset_done')}, name='auth_password_reset'),

    # Redirect to / page after password reset (CONFIRM PAGE WONT REDIRECT PROPERLY FOR SOME ODD REASON!!)
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$', auth_views.password_reset_confirm, {'post_reset_redirect': "/"}, name='auth_password_reset_confirm'),
    url(r'^password/reset/done/$', auth_views.password_reset_done, name='auth_password_reset_done'),

    #url(r'^user/password/done/$', 'django.contrib.auth.views.password_reset_complete')
]
    