from unicodedata import name
from django.urls import path, include, re_path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from .pres_pdf import prescription_pdf
from django.views.static import serve


# from . --> same directory
# Views functions and urls must be linked. # of views == # of urls
# App URL file - urls related to healthcenter

urlpatterns = [
    path('', views.healthcenter_home, name='healthcenter_home'),

    path('notifications',views.notifications,name="notifications"),
    path('clear-notifications',views.clear_notification,name="clear-notifications"),
    path('read-notifications',views.read_notifications,name="read-notifications"),
    path('all-notifications',views.all_notifications,name="all-notifications"),
    path('delete-notifications/<id>/',views.delete_notification,name="delete-notifications"),
    path('latest/notification/', views.latest_notification, name='latest_notification'),

    path('search/', views.search, name='search'),

    path('get_appointments_data/<int:pk>/', views.get_appointments_data, name='get_appointments_data'),
    path('get_waitlist_count/', views.get_waitlist_count, name='get_waitlist_count'),

    path('cancel-appointment/<int:pk>/',views.cancel_appointment, name='cancel-appointment'),
    path('confirm-appointment/<int:pk>/',views.confirm_appointment, name='confirm-appointment'),

    path('change-password/<int:pk>', views.change_password, name='change-password'),
    path('appointments/', views.appointments, name='appointments'),
    path('edit-prescription/', views.edit_prescription, name='edit-prescription'),
    # path('forgot-password/', views.forgot_password,name='forgot-password'),
    path('patient-dashboard/',views.patient_dashboard, name='patient-dashboard'),
    path('patient-records/',views.patient_record, name='patient-records'),
    path('privacy-policy/', views.privacy_policy, name='privacy-policy'),
    path('profile-settings/',views.profile_settings, name='profile-settings'),
    path('about-us/', views.about_us, name='about-us'),
    path('patient-register/', views.patient_register, name='patient-register'),
    path('patient-verification/', views.submit_verification, name='patient-verification'),
    path('create-medical-record-request/<int:medical_id>/', views.create_medical_record_request, name='create-medical-record-request'),
    path('create-doctor-record-request/<int:patient_id>/', views.create_doctor_record_request, name='create-doctor-record-request'),
    path('logout/', views.logoutUser, name='logout'),
    path('multiple-healthcenter/', views.multiple_healthcenter, name='multiple-healthcenter'),
    path('chat/<int:pk>/', views.chat, name='chat'),
    path('chat-doctor/', views.chat_doctor, name='chat-doctor'),
    path('healthcenter-profile/<int:pk>/', views.healthcenter_profile, name='healthcenter-profile'),
    path('admin-healthcenter-profile/<int:pk>/', views.admin_healthcenter_profile, name='admin-healthcenter-profile'),
    path('inventory/', views.inventory, name='inventory'),
    path('data-table/', views.data_table, name='data-table'),
    path('testing/',views.testing, name='testing'),
    path('healthcenter-doctor-list/<int:pk>/', views.healthcenter_doctor_list, name='healthcenter-doctor-list'),
    path('view-medical/<int:pk>', views.view_medical, name='view-medical'),
    path('prescription-view/<int:pk>', views.prescription_view, name='prescription-view'),
    path('pres_pdf/<int:pk>/',views.prescription_pdf, name='pres_pdf'),
    path('delete-prescription/<int:pk>/', views.delete_prescription, name='delete-prescription'),
    path('delete-report/<int:pk>/', views.delete_report, name='delete-report'),
    path('roles_new', views.roles_new, name='roles_new'),

    path('vaccination-view/<int:pk>', views.vaccination_view, name='vaccination-view'),
    path('vaccination-pdf/', views.vaccination_pdf, name='vaccination-pdf'),
    path('immunization-view/<int:pk>', views.immunization_view, name='immunization-view')

]

urlpatterns += [ re_path(r'^static/images/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT})]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
