from django.urls import path, include, re_path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .pdf import report_pdf
from django.views.static import serve


# from . --> same directory
# Views functions and urls must be linked. # of views == # of urls
# App URL file - urls related to healthcenter

urlpatterns = [
    path('', views.doctor_login, name='doctor-login'),
    path('staff-dashboard/',views.staff_dashboard, name='staff-dashboard'),
    path('staff-profile/<int:pk>/',views.staff_profile, name='staff-profile'),
    path('doctor-dashboard/',views.doctor_dashboard, name='doctor-dashboard'),
    path('doctor-profile/<int:pk>/', views.doctor_profile, name='doctor-profile'),
    path('doctor-change-password/<int:pk>', views.doctor_change_password,name='doctor-change-password'),
    path('doctor-profile-settings/', views.doctor_profile_settings,name='doctor-profile-settings'),
    path('doctor-logout/', views.logoutDoctor, name='doctor-logout'),
    path('my-patients/', views.my_patients, name='my-patients'),
    path('booking/<int:pk>/', views.booking, name='booking'),
    path('booking-success/', views.booking_success, name='booking-success'),
    path('schedule-timings/', views.schedule_timings, name='schedule-timings'),
    path('patient-id/', views.patient_id, name='patient-id'),
    path('create-prescription/<str:type>/<int:pk>/', views.create_prescription, name='create-prescription'),
    path('create-medical/<str:type>/<int:pk>/', views.create_medical, name='create-medical'),
    path('edit-prescription/<int:pk>/', views.edit_prescription, name='edit-prescription'),
    path('edit-medical/<int:pk>/', views.edit_medical, name='edit-medical'),
    path('patient-profile/<int:pk>/',views.patient_profile, name='patient-profile'),
    path('delete-education/<int:pk>/',views.delete_education, name='delete-education'),
    path('delete-experience/<int:pk>/',views.delete_experience, name='delete-experience'),
    path('appointments/',views.appointments, name='appointments'),
    path('walkin-registration/', views.walkin_registration, name='walkin-registration'),
    path('accept-appointment/<int:pk>/',views.accept_appointment, name='accept-appointment'),
    path('reject-appointment/<int:pk>/',views.reject_appointment, name='reject-appointment'),
    path('patient-search/<int:pk>/', views.patient_search, name='patient-search'),
    path('pdf/<int:pk>/',views.record_pdf, name='pdf'),
    path('doctor_review/<int:pk>/', views.doctor_review, name='doctor_review'),
    path('doctor-test-list/', views.doctor_test_list, name='doctor-test-list'),
    path('doctor-view-prescription/<int:pk>/', views.doctor_view_prescription, name='doctor-view-prescription'),
    path('doctor-view-medical/<int:pk>/', views.doctor_view_medical, name='doctor-view-medical'),
    path('doctor-view-history/<int:pk>/', views.doctor_view_history, name='doctor-view-history'),

    path('disease-statistics/', views.disease_statistics, name='disease-statistics'),
    path('forecasting/<str:disease_name>/', views.forecasting, name='forecasting'),

    path('all_fetch_alltime_data/', views.all_fetch_alltime_data, name='all_fetch_alltime_data'),
    path('all_fetch_30D_data/', views.all_fetch_30D_data, name='all_fetch_30D_data'),
    path('all_fetch_7D_data/', views.all_fetch_7D_data, name='all_fetch_7D_data'),
    path('all_fetch_1D_data/', views.all_fetch_1D_data, name='all_fetch_1D_data'),
    path('fetch_alltime_data/', views.fetch_alltime_data, name='fetch_alltime_data'),
    path('fetch_30D_data/', views.fetch_30D_data, name='fetch_30D_data'),
    path('fetch_7D_data/', views.fetch_7D_data, name='fetch_7D_data'),
    path('fetch_1D_data/', views.fetch_1D_data, name='fetch_1D_data'),

    path('patient-accept-verifications/', views.patient_verifications, name='patient-accept-verifications'),
    path('accept-verification/<int:pk>/',views.accept_verification, name='accept-verification'),
    path('reject-verification/<int:pk>/',views.reject_verification, name='reject-verification'),

    path('patient-medical-requests/',views.patient_medical_requests, name='patient-medical-requests'),
    path('accept-medical-requests/<int:pk>/',views.accept_patient_request, name='accept-medical-requests'),
    path('reject-medical-requests/<int:pk>/',views.reject_patient_request, name='reject-medical-requests'),

    path('doctor-medical-requests/',views.doctor_medical_requests, name='doctor-medical-requests'),
    path('accept-doctor-requests/<int:pk>/',views.accept_doctor_request, name='accept-doctor-requests'),
    path('reject-doctor-requests/<int:pk>/',views.reject_doctor_request, name='reject-doctor-requests'),
    path('doctor-view-other-record/<int:pk>/',views.doctor_view_other_record, name='doctor-view-other-record'),

    path('create-vaccination/', views.create_vaccination, name='create-vaccination'),
    path('create-immunization/', views.create_immunization, name='create-immunization')
]


urlpatterns += [ re_path(r'^static/images/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT})]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
