from django.urls import path, include, re_path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve




urlpatterns = [
    path('', views.admin_login, name='admin-login'),
    path('admin-dashboard/',views.admin_dashboard, name='admin-dashboard'),
    path('healthcenter-admin-profile/<int:pk>/', views.healthcenter_admin_profile,name='healthcenter-admin-profile'),
    path('appointment-list',views.appointment_list, name='appointment-list'),
    path('forgot-password/', views.admin_forgot_password,name='admin_forgot_password'),
    path('healthcenter-list/', views.healthcenter_list,name='healthcenter-list'),
    path('add-healthcenter/', views.add_healthcenter,name='add-healthcenter'),
    path('edit-healthcenter/<int:pk>/', views.edit_healthcenter,name='edit-healthcenter'),
    path('delete-healthcenter/<int:pk>/', views.delete_healthcenter,name='delete-healthcenter'),
    path('admin-doctor-profile/<int:pk>/', views.admin_doctor_profile,name='admin-doctor-profile'),
    path('add-doctor/', views.doctor_register,name='add-doctor'),
    path('delete-doctor/<int:pk>/', views.delete_doctor,name='delete-doctor'),
    path('doctor-list/', views.view_doctor,name='doctor-list'),

    path('add-staff/', views.staff_register,name='add-staff'),
    path('delete-staff/<int:pk>/', views.delete_staff,name='delete-staff'),
    path('staff-list/', views.view_staff,name='staff-list'),
    path('add-inventorymanager/', views.add_inventorymanager,name='add-inventorymanager'),
    #path('edit-healthcenter/', views.edit_healthcenter,name='edit-healthcenter'),
    path('invoice/',views.invoice, name='invoice'),
    path('invoice-report/',views.invoice_report, name='invoice_report'),
    path('lock-screen/', views.lock_screen,name='lock_screen'),
    path('login/',views.admin_login,name='admin_login'),
    path('patient-list/',views.patient_list, name='patient-list'),
    # path('register/', views.register,name='register'),
    path('admin_register/',views.admin_register,name='admin_register'),
    path('transactions-list/',views.transactions_list, name='transactions_list'),
    path('admin-logout/', views.logoutAdmin, name='admin-logout'),
    path('emergency/', views.emergency_details,name='emergency'),
    path('edit-emergency-information/<int:pk>/', views.edit_emergency_information,name='edit-emergency-information'),
    path('healthcenter-profile/', views.healthcenter_profile ,name='healthcenter-profile'),
    path('healthcenter-admin-profile/<int:pk>/', views.healthcenter_admin_profile,name='healthcenter-admin-profile'),
    path('create-report/<int:pk>/', views.create_report,name='create-report'),
    path('add-lab-worker/', views.add_lab_worker,name='add-lab-worker'),
    path('lab-worker-list/', views.view_lab_worker,name='lab-worker-list'),
    path('edit-lab-worker/<int:pk>/', views.edit_lab_worker,name='edit-lab-worker'),

    #medicine
    path('medicine-list/', views.medicine_list,name='medicine-list'),
    path('medicine-list-view/', views.medicine_list_view,name='medicine-list-view'),
    path('medicine-list-manage/<int:pk>/', views.medicine_list_manage,name='medicine-list-manage'),
    path('add-medicine/', views.add_medicine,name='add-medicine'),
    path('edit-medicine/<int:pk>/', views.edit_medicine,name='edit-medicine'),
    path('delete-medicine/<int:pk>/', views.delete_medicine,name='delete-medicine'),
    #medical equipment
    path('medical-equipment-list/', views.medical_equipment_list,name='medical-equipment-list'),
    path('medical-equipment-list-view/', views.medical_equipment_list_view,name='medical-equipment-list-view'),
    path('medical-equipment-list-manage/<int:pk>/', views.medical_equipment_list_manage,name='medical-equipment-list-manage'),
    path('add-medical-equipment/', views.add_medical_equipment,name='add-medical-equipment'),
    path('edit-medical-equipment/<int:pk>/', views.edit_medical_equipment,name='edit-medical-equipment'),
    path('delete-medical-equipment/<int:pk>/', views.delete_medical_equipment,name='delete-medical-equipment'),

    #medical supply
    path('medical-supply-list/', views.medical_supply_list,name='medical-supply-list'),
    path('medical-supply-list-view/', views.medical_supply_list_view,name='medical-supply-list-view'),
    path('medical-supply-list-manage/<int:pk>/', views.medical_supply_list_manage,name='medical-supply-list-manage'),
    path('add-medical-supply/', views.add_medical_supply,name='add-medical-supply'),
    path('edit-medical-supply/<int:pk>/', views.edit_medical_supply,name='edit-medical-supply'),
    path('delete-medical-supply/<int:pk>/', views.delete_medical_supply,name='delete-medical-supply'),

    path('delete-service/<int:pk>/<int:pk2>/',views.delete_service,name='delete-service'),
    path('labworker-dashboard/', views.labworker_dashboard,name='labworker-dashboard'),
    path('inventorymanager-list/', views.view_inventorymanager,name='inventorymanager-list'),
    path('edit-inventorymanager/<int:pk>/', views.edit_inventorymanager,name='edit-inventorymanager'),
    path('mypatient-list/', views.mypatient_list,name='mypatient-list'),
    path('prescription-list/<int:pk>', views.prescription_list,name='prescription-list'),
    path('add-test/', views.add_test,name='add-test'),
    path('test-list/', views.test_list,name='test-list'),
    path('delete-test/<int:pk>/', views.delete_test,name='delete-test'),
    path('inventorymanager-dashboard/', views.inventorymanager_dashboard,name='inventorymanager-dashboard'),
    path('report-history/', views.report_history,name='report-history'),
    
    #Login
     path('inventory-manager-login',views.inventorymanager_login,name='inventorymanager_login'),
     path('midwife-login',views.midwife_login,name='midwife_login'),
     path('manager-profile/<int:pk>/', views.manager_profile,name='manager-profile'),
     path('admin-staff-profile/<int:pk>/', views.admin_staff_profile,name='admin-staff-profile'),
     path('admin-invmanager-profile/<int:pk>/', views.admin_invmanager_profile,name='admin-invmanager-profile'),
     path('admin-inventorymanager/<int:pk>/', views.delete_inventorymanager,name='delete-inventorymanager'),
    
]
  


urlpatterns += [ re_path(r'^static/images/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT})]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
