"""Mediqs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from healthcenter import views
from django.views.static import serve

# For forgot password views and reset password views
from django.contrib.auth import views as auth_views
import notifications.urls

# ROOT url file

# All urls paths of different pages will be in url patterns below

urlpatterns = [
    path('inbox/notifications/', include(notifications.urls, namespace='notifications')),

    path('admin/', admin.site.urls),
    path('login/', views.login_user, name='login'),
    path('', include('healthcenter.urls')),
    path('doctor/', include('doctor.urls')),
    path('api/', include('api.urls')),
    path('healthcenter_admin/', include('healthcenter_admin.urls')),
    path('chat/', include('ChatApp.urls')),
    path('inventory/', include('inventory.urls')),
    path('__debug__/', include('debug_toolbar.urls')),
    
    #Email verification
    path('verification/', include('verify_email.urls')),

    # For forgot password views and reset password views
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name="reset_password.html"),name="reset-password"),
    # path('reset_password/', auth_views.PasswordResetView.as_view(),name="reset-password"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="reset_password_sent.html"),name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="reset.html"),name="password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="reset_password_complete.html"),name="password_reset_complete"),
    
]

urlpatterns += [ re_path(r'^static/images/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT})]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# if settings.debug:
#     import debug_toolbar
#     urlpatterns = [
#         path('__debug__/', include(debug_toolbar.urls)),
#     ] + urlpatterns

"""
Forgot password views

1 - User submits email for reset
2 - email is sent to user
3 - user clicks link in email
4 - user is redirected to reset password page

"""

