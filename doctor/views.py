import email
from email import message
from multiprocessing import context
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from healthcenter_admin.views import prescription_list
from .forms import DoctorForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import cache_control
from healthcenter.models import User, Patient, Healthcenter_Information,VerificationRequest,MedicalRecordRequest
from healthcenter_admin.models import Admin_Information,Clinical_Laboratory_Technician
from .models import Doctor_Information, Appointment, Education, Experience, Prescription_medicine, Report,Specimen,Test, Prescription_test, Prescription, Doctor_review, MedicalRecord, Staff, Walkin,DoctorRecordRequest,Vaccination, Immunization, Waitlist
from healthcenter_admin.models import Admin_Information,Clinical_Laboratory_Technician, Test_Information
from django.db.models import Q, Count, F, FloatField, ExpressionWrapper
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.functions import TruncDate, TruncDay, TruncHour, TruncMinute, TruncSecond
from django.dispatch import receiver
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
import random
import string
from datetime import datetime, timedelta, time
import datetime
import re
import os
import tensorflow as tf
from django.core.mail import BadHeaderError, send_mail
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.utils.html import strip_tags
from io import BytesIO
from urllib import response
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.core.files.storage import FileSystemStorage
from .models import Report
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import plotly.express as px
import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.utils.crypto import get_random_string
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import render
from healthcenter.forms import PatientForm, CustomUserCreationForm, ExtraInfoForm
from django.utils import timezone
from django.db import transaction
from notifications.signals import notify
from django.urls import reverse
from .forecasting.forecasting import get_forecast #forecasting
from django.core.exceptions import ValidationError
from django.db import IntegrityError
import re

# Create your views here.
def generate_random_string():
    N = 8
    string_var = ""
    string_var = ''.join(random.choices(
        string.ascii_uppercase + string.digits, k=N))
    return string_var

@transaction.atomic
def reschedule(appointment):
    # Get the highest scored patient on the waitlist for this date and time
    highest_score_patient = Waitlist.objects.filter(desired_date=appointment.date, desired_time=appointment.time).order_by('-score', '-timestamp').first()
    
    if highest_score_patient is not None:
        # Create appointment
        appointment = Appointment(patient=highest_score_patient.patient, healthcenter=highest_score_patient.healthcenter)
        appointment.date = highest_score_patient.desired_date
        appointment.time = highest_score_patient.desired_time
        appointment.appointment_status = 'pending'
        appointment.serial_number = generate_random_string()
        appointment.appointment_type = highest_score_patient.appointment_type
        appointment.urgency = highest_score_patient.urgency
        appointment.message = highest_score_patient.message
        appointment.symptoms = highest_score_patient.symptoms
        appointment.save()

        # Send notification after rescheduling appointment
        notify.send(highest_score_patient.patient.health_center, recipient=highest_score_patient.patient.user, 
                    verb='An appointment slot has opened', 
                    description=f'An appointment slot has opened on {appointment.date} at {appointment.time}. Kindly confirm your appointment slot.', 
                    redirect=f'/confirm-appointment/{appointment.id}', icon='calendar')

        # Delete from waitlist
        highest_score_patient.delete()

@login_required(login_url="login")
def doctor_change_password(request,pk):
    doctor = Doctor_Information.objects.get(user_id=pk)
    context={'doctor':doctor}
    if request.method == "POST":
         
        new_password = request.POST["new_password"]
        confirm_password = request.POST["confirm_password"]
        if new_password == confirm_password:
            
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request,"Password Changed Successfully")
            return redirect("doctor-dashboard")
            
        else:
            messages.error(request,"New Password and Confirm Password is not same")
            return redirect("change-password",pk)
    return render(request, 'doctor-change-password.html',context)

@csrf_exempt
@login_required(login_url="login")
def schedule_timings(request):
    doctor = Doctor_Information.objects.get(user=request.user)
    context = {'doctor': doctor}
    
    return render(request, 'schedule-timings.html', context)

@csrf_exempt
@login_required(login_url="login")
def patient_id(request):
    return render(request, 'patient-id.html')

@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logoutDoctor(request):
    user = User.objects.get(id=request.user.id)
    if user.is_doctor:
        user.login_status == "offline"
        user.save()
        logout(request)
    else:
        logout(request)
        messages.error(request, 'You are already logged out')
        return redirect('login')
    
    messages.error(request, 'User Logged out')
    return render(request,'login.html')

def doctor_login(request):
    # page = 'patient_login'
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'Username does not exist')
                
        user = authenticate(username=username, password=password)
        
        if user is not None:
            
            login(request, user)
            if request.user.is_doctor:
                # user.login_status = "online"
                # user.save()
                messages.success(request, 'Welcome Doctor!')
                return redirect('doctor-dashboard')
            else:
                messages.error(request, 'Invalid credentials. Not a Doctor')
                return redirect('logout')   
        else:
            messages.error(request, 'Invalid username or password')
            
    return render(request, 'login.html')

@login_required(login_url="login")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def doctor_dashboard(request):
        if request.user.is_authenticated:    
            if request.user.is_doctor:
                # doctor = Doctor_Information.objects.get(user_id=pk)
                doctor = Doctor_Information.objects.get(user=request.user)
                healthcenter = Healthcenter_Information.objects.get(healthcenter_id=doctor.health_center.healthcenter_id)
                # appointments = Appointment.objects.filter(doctor=doctor).filter(Q(appointment_status='pending') | Q(appointment_status='confirmed'))
                current_date = datetime.date.today()
                current_date_str = str(current_date)  
                today_appointments = Appointment.objects.filter(date=current_date_str).filter(healthcenter=healthcenter).filter(appointment_status='pending')
                today_walkins = Walkin.objects.filter(date=current_date_str).filter(healthcenter=healthcenter) 

                next_date = current_date + datetime.timedelta(days=1) # next days date 
                next_date_str = str(next_date)  
                next_days_appointment = Appointment.objects.filter(date=next_date_str).filter(healthcenter=healthcenter).filter(Q(appointment_status='pending') | Q(appointment_status='confirmed')).count()
                
                total_appointments_count = Appointment.objects.filter(healthcenter=healthcenter).annotate(count=Count('id'))
                total_walkins_count = Walkin.objects.filter(healthcenter=healthcenter).annotate(count=Count('id'))

                today_appointment_count = Appointment.objects.filter(date=current_date_str, healthcenter=healthcenter).aggregate(count=Count('patient'))['count']
                today_walkin_count = Walkin.objects.filter(date=current_date_str, healthcenter=healthcenter).aggregate(count=Count('patient'))['count']

                today_patient_count = today_appointment_count + today_walkin_count

            else:
                return redirect('logout')
            
            context = {'doctor': doctor, 'healthcenter': healthcenter,'today_walkin_count': today_walkin_count, 'today_appointment_count': today_appointment_count, 'today_appointments': today_appointments, 'today_walkins': today_walkins, 'today_patient_count': today_patient_count, 'total_walkins_count': total_walkins_count, 'total_appointments_count': total_appointments_count, 'next_days_appointment': next_days_appointment, 'current_date': current_date_str, 'next_date': next_date_str}
            return render(request, 'doctor-dashboard.html', context)
        else:
            return redirect('login')

def generate_username(name, dob):
    username = "".join(char for char in name if char.isalnum())
    username += dob.strftime('%m%d%Y')
    # Check for username uniqueness
    while User.objects.filter(username=username).exists():
        username += str(random.randint(0, 9))  # Append a random digit
    return username

def send_email(username, password, email, request):
    subject = 'Your Health Center Portal Credentials'
    message = render_to_string('patient_credentials_email.html', {
        'username': username,
        'password': password,
    })
    from_email = 'noreply<mediqs@healthcenter.com>'
    recipient_list = [email]
    try:
        send_mail(subject, message, from_email, recipient_list)
    except Exception as e:
        messages.error(request, str(e))
        return False
    return True

@transaction.atomic
def create_new_user(request, patient_form, email, healthcenter, page, staff, patients, creationtype):
    name = patient_form.cleaned_data['name']
    dob = patient_form.cleaned_data['dob']       

    try:
        username = generate_username(name, dob)
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        
        user = User.objects.create_user(username=username, password=password, email=email)
        user.is_patient = True
        user.save()

        if creationtype == 'walkin':
            patient = Patient(
                user=user,
                name=name,
                email=email,
                dob=dob,
                age=patient_form.cleaned_data['age'],
                gender=patient_form.cleaned_data['gender'],
                phone_number=patient_form.cleaned_data['phone_number'],
                address=patient_form.cleaned_data['address'],
                health_center=healthcenter
            )
            patient.save()
        elif creationtype == 'vaccination' or 'immunization':
            patient = Patient(
                user=user,
                name=name,
                email=email,
                dob=dob,
                age=patient_form.cleaned_data['age'],
                gender=patient_form.cleaned_data['gender'],
                phone_number=patient_form.cleaned_data['phone_number'],
                address=patient_form.cleaned_data['address'],
                father_name=patient_form.cleaned_data['father_name'],
                mother_name=patient_form.cleaned_data['mother_name'],
                fam_num=patient_form.cleaned_data['fam_num'],
                barangay_num=patient_form.cleaned_data['barangay_num'],
                birth_weight=patient_form.cleaned_data['birth_weight'],
                birth_height=patient_form.cleaned_data['birth_height'],
                place_birth=patient_form.cleaned_data['place_birth'],
                health_center=healthcenter
            )
            patient.save()
        else:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect('staff-dashboard')

        if send_email(username, password, email, request):
            messages.success(request, 'Patient account created and email sent with username and password.')
        else:
            if creationtype == 'walkin':
                messages.error(request, 'Failed to send email with username and password. Please try again.')
                return render(request, 'walkin_registration.html', {'page': page, 'staff': staff, 'healthcenter': healthcenter, 'patients': patients, 'patient_form': patient_form}) 
            elif creationtype == 'immunization':
                messages.error(request, 'Failed to send email with username and password. Please try again.')
                return render(request, 'create-immunization.html', {'page': page, 'staff': staff, 'healthcenter': healthcenter, 'patients': patients, 'patient_form': patient_form}) 
            elif creationtype == 'vaccination':
                messages.error(request, 'Failed to send email with username and password. Please try again.')
                return render(request, 'create-vaccination.html', {'page': page, 'staff': staff, 'healthcenter': healthcenter, 'patients': patients, 'patient_form': patient_form}) 
            else:
                messages.error(request, 'Something went wrong. Please try again.')
                return redirect('staff-dashboard')
        return patient
    except Exception as e:
        messages.error(request, e)
        return None

@transaction.atomic
@login_required(login_url="login")
def walkin_registration(request):
    page = 'walkin-registration'
    patient_form= PatientForm()
    staff = Staff.objects.get(user=request.user)
    healthcenter = Healthcenter_Information.objects.get(healthcenter_id=staff.health_center.healthcenter_id)
    patients = Patient.objects.filter(health_center=healthcenter)
    creationtype = 'walkin'

    if request.method == "POST":
        patient_id = request.POST.get('patient_id')
        reason = request.POST.get('reason')
        walk_in_type = request.POST.get('walk_in_type')
        symptoms = request.POST['symptoms']
        no_account = request.POST.get('check')  # Get the value of the checkbox

        if no_account:  # If the checkbox is checked
            patient_form = PatientForm(request.POST)

            if patient_form.is_valid():
                email = request.POST.get('email')
                # Check if another patient with the same email already exists
                if Patient.objects.filter(email=email).exists():
                    error_message = "A patient with this email already exists."
                    messages.error(request, error_message)
                    return render(request, 'walkin_registration.html', {'page': page, 'staff': staff, 'healthcenter': healthcenter, 'patients': patients, 'patient_form': patient_form})
                else:
                    patient = create_new_user(request, patient_form, email, healthcenter, page, staff, patients, creationtype)
                    if patient is None:
                        messages.error(request, 'An error occurred during registration. Please check the form for errors.')
                        return render(request, 'walkin_registration.html', {'page': page, 'staff': staff, 'healthcenter': healthcenter, 'patients': patients, 'patient_form': patient_form})
            else:
                messages.error(request, 'An error occurred during registration. Please check the form for errors.')
                return render(request, 'walkin_registration.html', {'page': page, 'staff': staff, 'healthcenter': healthcenter, 'patients': patients, 'patient_form': patient_form})
        else:
            patient = Patient.objects.get(pk=patient_id)


        # Record the walk-in
        walkin = Walkin(
            date=datetime.date.today(),
            time=datetime.datetime.now().time(),  # To get only current time
            healthcenter=healthcenter,
            patient=patient,
            reason=reason,
            walk_in_type=walk_in_type,
            symptoms=symptoms,
            serial_number=generate_random_string() 
        )
        walkin.save()

        # Create a new notification for request
        notify.send(patient.health_center, recipient=patient.user, verb='Thank you for coming!', 
                    description=f'Your walk-in earlier at {patient.health_center.name} has been registered by {staff.name}.', 
                    redirect=f'/patient-dashboard/', icon='walk-outline') 

        messages.success(request, 'Walk-in registration completed')
        return redirect('walkin-registration')

    context = {'staff': staff, 'healthcenter': healthcenter, 'patients': patients,'patient_form':patient_form}
    return render(request, 'walkin_registration.html', context)
    

@login_required(login_url="login")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def staff_dashboard(request):
        if request.user.is_authenticated:    
            if request.user.is_staff:
                staff = Staff.objects.get(user=request.user)
                healthcenter = Healthcenter_Information.objects.get(healthcenter_id=staff.health_center.healthcenter_id)
                # appointments = Appointment.objects.filter(doctor=doctor).filter(Q(appointment_status='pending') | Q(appointment_status='confirmed'))
                current_date = datetime.date.today()
                current_date_str = str(current_date)  
                today_appointments = Appointment.objects.filter(date=current_date_str).filter(healthcenter=healthcenter).filter(appointment_status='pending')
                today_walkins = Walkin.objects.filter(date=current_date_str).filter(healthcenter=healthcenter) 

                next_date = current_date + datetime.timedelta(days=1) # next days date 
                next_date_str = str(next_date)  
                next_days_appointment = Appointment.objects.filter(date=next_date_str).filter(healthcenter=healthcenter).filter(Q(appointment_status='pending') | Q(appointment_status='confirmed')).count()
                
                total_appointments_count = Appointment.objects.filter(healthcenter=healthcenter).annotate(count=Count('id'))
                total_walkins_count = Walkin.objects.filter(healthcenter=healthcenter).annotate(count=Count('id'))

                today_appointment_count = Appointment.objects.filter(date=current_date_str, healthcenter=healthcenter).aggregate(count=Count('patient'))['count']
                today_walkin_count = Walkin.objects.filter(date=current_date_str, healthcenter=healthcenter).aggregate(count=Count('patient'))['count']

                today_patient_count = today_appointment_count + today_walkin_count

            else:
                return redirect('logout')
            
            context = {'staff': staff, 'healthcenter': healthcenter,'today_walkin_count': today_walkin_count, 'today_appointment_count': today_appointment_count, 'today_appointments': today_appointments, 'today_walkins': today_walkins, 'today_patient_count': today_patient_count, 'total_walkins_count': total_walkins_count, 'total_appointments_count': total_appointments_count, 'next_days_appointment': next_days_appointment, 'current_date': current_date_str, 'next_date': next_date_str}
            return render(request, 'staff-dashboard.html', context)
        else:
            return redirect('login')
        
#Medical Records Requested by Doctor
@login_required(login_url="login")
def doctor_medical_requests(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            staff = Staff.objects.get(user=request.user)
            healthcenter = Healthcenter_Information.objects.get(healthcenter_id=staff.health_center.healthcenter_id)
            record_requests = DoctorRecordRequest.objects.filter(patient__health_center=healthcenter, status=DoctorRecordRequest.STATUS_CHOICES[0][0]).order_by('request_date')
            context = {'staff': staff, 'healthcenter': healthcenter, 'record_requests': record_requests}
            return render(request, 'doctor-medical-requests.html', context)
        else:
            messages.error(request, 'No permission for this action')
            return redirect('logout')
    else:
        return redirect('login')

#Accept Medical Records Requests by Doctors
@transaction.atomic
@login_required(login_url="login")
def accept_doctor_request(request, pk):
    if request.user.is_authenticated:
        if request.user.is_staff:
            record_request = DoctorRecordRequest.objects.get(id=pk)
            record_request.status = DoctorRecordRequest.STATUS_CHOICES[1][0]  # Set status to 'Approved'
            record_request.save()

            staff = Staff.objects.get(user=request.user)

            doctor = record_request.doctor
            # Perform any necessary actions after accepting the medical record request
            notify.send(staff.health_center, recipient=doctor.user, verb='Medical Record Request Accepted!', 
                        description=f'Your medical record request has been accepted by {staff.health_center.name}.', 
                        redirect=f'/doctor/doctor-view-other-record/{record_request.patient.patient_id}', icon='medical-outline') 
            

            # Mailtrap
            doctor_email = record_request.doctor.email
            doctor_name = record_request.doctor.name
            doctor_username = record_request.doctor.username
            request_date = record_request.request_date
            id = record_request.id

            subject = "Medical Records Request Email"

            values = {
                "email": doctor_email,
                "name": doctor_name,
                "username": doctor_username,
                "status": record_request.status,
                "request_date": request_date,
                "id": id,
              
            }

            html_message = render_to_string('doctor-accept-request-mail.html', {'values': values})
            plain_message = strip_tags(html_message)

            try:
                send_mail(subject, plain_message, 'healthcenter_admin@gmail.com', [doctor_email], html_message=html_message, fail_silently=False)
            except BadHeaderError:
                return HttpResponse('Invalid header found')

            messages.success(request, 'Request for Medical Record Accepted')
            return redirect('doctor-medical-requests')
        else:
            messages.error(request, 'No permission for this action')
            return redirect('logout')
    else:
        return redirect('login')
    
#Reject Medical Records Requests by Doctors
@transaction.atomic
@login_required(login_url="login")
def reject_doctor_request(request, pk):
    if request.user.is_authenticated:
        if request.user.is_staff:
            record_request = DoctorRecordRequest.objects.get(id=pk)
            record_request.status = DoctorRecordRequest.STATUS_CHOICES[2][0]  # Set status to 'Denied'
            record_request.save()

            doctor = record_request.doctor
            staff = Staff.objects.get(user=request.user)

            # Create a new notification for rejecting doctor request
            notify.send(staff.health_center, recipient=doctor.user, verb='Medical Record Request Denied!', 
                        description=f'Your medical record request has been denied by {staff.health_center.name}.', 
                        redirect=f'/doctor/doctor-dashboard/', icon='medical-outline')

            # Mailtrap
            doctor_email = record_request.doctor.email
            doctor_name = record_request.doctor.name
            doctor_username = record_request.doctor.username
            request_date = record_request.request_date
            id = record_request.id

            subject = "Medical Records Request Email"

            values = {
                "email": doctor_email,
                "name": doctor_name,
                "username": doctor_username,
                "status": record_request.status,
                "request_date": request_date,
                "id": id,
            }

            html_message = render_to_string('doctor-request-reject-mail.html', {'values': values})
            plain_message = strip_tags(html_message)

            try:
                send_mail(subject, plain_message, 'healthcenter_admin@gmail.com', [doctor_email], html_message=html_message, fail_silently=False)
            except BadHeaderError:
                return HttpResponse('Invalid header found')

            messages.error(request, 'Request for Medical Record Denied')
            return redirect('doctor-medical-requests')
        else:
            messages.error(request, 'No permission for this action')
            return redirect('logout')
    else:
        return redirect('login')


#Medical Records Request By Patients
@login_required(login_url="login")
def patient_medical_requests(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            staff = Staff.objects.get(user=request.user)
            healthcenter = Healthcenter_Information.objects.get(healthcenter_id=staff.health_center.healthcenter_id)
            record_requests = MedicalRecordRequest.objects.filter(patient__health_center=healthcenter, status=MedicalRecordRequest.STATUS_CHOICES[0][0]).order_by('request_date')
            context = {'staff': staff, 'healthcenter': healthcenter, 'record_requests': record_requests}
            return render(request, 'patient-medical-requests.html', context)
        else:
            messages.error(request, 'No permission for this action')
            return redirect('logout')
    else:
        return redirect('login')
    
#Accept Medical Records Requests by Patients
@transaction.atomic
@login_required(login_url="login")
def accept_patient_request(request, pk):
    if request.user.is_authenticated:
        if request.user.is_staff:
            record_request = MedicalRecordRequest.objects.get(id=pk)
            record_request.status = MedicalRecordRequest.STATUS_CHOICES[1][0]  # Set status to 'Approved'
            record_request.save()

            patient = record_request.patient
            # Perform any necessary actions after accepting the medical record request

            # Create a new notification for accepting patient request
            notify.send(patient.health_center, recipient=patient.user, verb='Medical Record Request Accepted!', 
                        description=f'Your medical record request has been accepted by {patient.health_center.name}.', 
                        redirect=f'/view-medical/{record_request.record.medical_id}', icon='medical-outline') 

             # Mailtrap
            patient_email = record_request.patient.email
            patient_name = record_request.patient.name
            patient_username = record_request.patient.username
            request_date = record_request.request_date
            id = record_request.id

            subject = "Medical Records Request Email"

            values = {
                "email": patient_email,
                "name": patient_name,
                "username": patient_username,
                "status": record_request.status,
                "request_date":request_date,
                "id":id

            }

            html_message = render_to_string('patient-accept-request-mail.html', {'values': values})
            plain_message = strip_tags(html_message)

            try:
                send_mail(subject, plain_message, 'healthcenter_admin@gmail.com', [patient_email], html_message=html_message, fail_silently=False)
            except BadHeaderError:
                return HttpResponse('Invalid header found')

            messages.success(request, 'Request for Medical Record Accepted')
            return redirect('staff-dashboard')
        else:
            messages.error(request, 'No permission for this action')
            return redirect('logout')
    else:
        return redirect('login')
    

#Reject Medical Record Requests by Patient
@transaction.atomic
@login_required(login_url="login")
def reject_patient_request(request, pk):
    if request.user.is_authenticated:
        if request.user.is_staff:
            record_request = MedicalRecordRequest.objects.get(id=pk)
            record_request.status = MedicalRecordRequest.STATUS_CHOICES[2][0]  # Set status to 'Denied'
            record_request.save()

            patient = record_request.patient
            # Perform any necessary actions after rejecting the medical record request
            # Create a new notification for accepting patient request
            notify.send(patient.health_center, recipient=patient.user, verb='Medical Record Request Denied!', 
                        description=f'Your medical record request has been denied by {patient.health_center.name}.', 
                        redirect=f'/patient-dashboard/', icon='medical-outline')

             # Mailtrap
            patient_email = record_request.patient.email
            patient_name = record_request.patient.name
            patient_username = record_request.patient.username
            request_date = record_request.request_date
            id = record_request.id

            subject = "Medical Records Request Email"

            values = {
                "email": patient_email,
                "name": patient_name,
                "username": patient_username,
                "status": record_request.status,
                "request_date":request_date,
                "id":id

            }
            html_message = render_to_string('patient-request-reject-mail.html', {'values': values})
            plain_message = strip_tags(html_message)

            try:
                send_mail(subject, plain_message, 'healthcenter_admin@gmail.com', [patient_email], html_message=html_message, fail_silently=False)
            except BadHeaderError:
                return HttpResponse('Invalid header found')

            messages.error(request, 'Request for Medical Record Denied')
            return redirect('staff-dashboard')
        else:
            messages.error(request, 'No permission for this action')
            return redirect('logout')
    else:
        return redirect('login')


#Verification Requests
@login_required(login_url="login")
def patient_verifications(request):
    if request.user.is_authenticated:    
        if request.user.is_staff:
            staff = Staff.objects.get(user=request.user)
            healthcenter = Healthcenter_Information.objects.get(healthcenter_id=staff.health_center.healthcenter_id)
            verification_requests = VerificationRequest.objects.filter(patient__health_center=healthcenter, status=VerificationRequest.PENDING).order_by('request_date')
            context = {'staff': staff, 'healthcenter': healthcenter, 'verification_requests': verification_requests}
            return render(request, 'patient-accept-verifications.html', context)
        else:
            messages.error(request, 'No permission for this action')
            return redirect('logout')
    else:
        return redirect('login')
#Accept PATIENT VERIFICATION
@transaction.atomic
@login_required(login_url="login")
def accept_verification(request, pk):
    if request.user.is_authenticated:    
        if request.user.is_staff:
            verification_request = VerificationRequest.objects.get(id=pk)
            verification_request.status = VerificationRequest.APPROVED
            verification_request.save()

            patient=verification_request.patient
            patient.is_verified = True
            patient.save()

            # Create a new notification for verification
            notify.send(patient.health_center, recipient=patient.user, verb='Verification Request Accepted!', 
                        description=f'Your verification request for {patient.health_center.name} has been accepted. Thank you for your patience.', 
                        redirect=f'/patient-dashboard/', icon='checkmark-circle-outline')  

            # Mailtrap
            patient_email = verification_request.patient.email
            patient_name = verification_request.patient.name
            patient_username = verification_request.patient.username

            proof_of_billing = verification_request.proof_of_billing
            id_proof_front = verification_request.id_proof_front
            id_proof_back = verification_request.id_proof_back
            id_selfie = verification_request.selfie_with_id.url
            request_date = verification_request.request_date,
            id = verification_request.id

            subject = "Verification Acceptance Email"

            values = {
                "email": patient_email,
                "name": patient_name,
                "username": patient_username,
                "status": verification_request.status,
                "proof_of_billing": proof_of_billing,
                "id_proof_front": id_proof_front,
                "id_proof_back": id_proof_back,
                "id_selfie": id_selfie,
                "request_date":request_date,
                "id":id
            }

            html_message = render_to_string('verification_accept_mail.html', {'values': values})
            plain_message = strip_tags(html_message)

            try:
                send_mail(subject, plain_message, 'healthcenter_admin@gmail.com', [patient_email], html_message=html_message, fail_silently=False)
            except BadHeaderError:
                return HttpResponse('Invalid header found')

            messages.success(request, 'Verification Accepted')
            return redirect('staff-dashboard')
        else:
            messages.error(request, 'No permission for this action')
            return redirect('logout')
    else:
        return redirect('login')

# Reject Patient Verification
@transaction.atomic
@login_required(login_url="login")
def reject_verification(request, pk):
    if request.user.is_authenticated:    
        if request.user.is_staff:
            verification_request = VerificationRequest.objects.get(id=pk)
            verification_request.status = VerificationRequest.REJECTED
            verification_request.save()

            patient=verification_request.patient
            patient.is_verified = False
            patient.save()

            # Create a new notification for verification
            notify.send(patient.health_center, recipient=patient.user, verb='Verification Request Denied!', 
                        description=f'Your verification request for {patient.health_center.name} has been denied. Thank you for your patience.', 
                        redirect=f'/patient-dashboard/', icon='checkmark-circle-outline')  

            # Mailtrap
            patient_email = verification_request.patient.email
            patient_name = verification_request.patient.name
            patient_username = verification_request.patient.username

            subject = "Verification Rejection Email"

            values = {
                "email": patient_email,
                "name": patient_name,
                "username": patient_username,
                "status": verification_request.status,
            }

            html_message = render_to_string('verification_reject_mail.html', {'values': values})
            plain_message = strip_tags(html_message)

            try:
                send_mail(subject, plain_message, 'healthcenter_admin@gmail.com', [patient_email], html_message=html_message, fail_silently=False)
            except BadHeaderError:
                return HttpResponse('Invalid header found')

            messages.error(request, 'Verification Rejected')

            return redirect('staff-dashboard')
        else:
            messages.error(request, 'No permission for this action')
            return redirect('logout')
    else:
        return redirect('login')

 
@login_required(login_url="login")
def appointments(request):
    staff = Staff.objects.get(user=request.user)
    healthcenter = Healthcenter_Information.objects.get(healthcenter_id=staff.health_center.healthcenter_id)
    appointments = Appointment.objects.filter(healthcenter=healthcenter).filter(appointment_status='pending').order_by('date')
    context = {'staff': staff, 'healthcenter': healthcenter, 'appointments': appointments}
    return render(request, 'appointments.html', context) 
 
@transaction.atomic
@login_required(login_url="login")
def accept_appointment(request, pk):
    appointment = Appointment.objects.get(id=pk)
    appointment.appointment_status = 'confirmed'
    appointment.save()

    patient = appointment.patient

    # Create a new notification for verification
    notify.send(patient.health_center, recipient=patient.user, verb='Thank you for showing up!', 
                description=f'Please stay healthy! :)', 
                redirect=f'/patient-dashboard/', icon='heart-outline')  
    
    # Mailtrap
    
    patient_email = appointment.patient.email
    patient_name = appointment.patient.name
    patient_username = appointment.patient.username
    patient_serial_number = appointment.patient.serial_number
    healthcenter = appointment.healthcenter.name

    appointment_serial_number = appointment.serial_number
    appointment_date = appointment.date
    appointment_time = appointment.time
    appointment_status = appointment.appointment_status
    
    subject = "Appointment Acceptance Email"
    
    values = {
            "email":patient_email,
            "name":patient_name,
            "username":patient_username,
            "serial_number":patient_serial_number,
            "healthcenter": healthcenter,
            "appointment_serial_num":appointment_serial_number,
            "appointment_date":appointment_date,
            "appointment_time":appointment_time,
            "appointment_status":appointment_status,
    }
    
    html_message = render_to_string('appointment_accept_mail.html', {'values': values})
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(subject, plain_message, 'healthcenter_admin@gmail.com',  [patient_email], html_message=html_message, fail_silently=False)
    except BadHeaderError:
        return HttpResponse('Invalid header found')
    
    messages.success(request, 'Appointment Accepted')
    
    return redirect('staff-dashboard')

@transaction.atomic
@login_required(login_url="login")
def reject_appointment(request, pk):
    appointment = Appointment.objects.get(id=pk)
    appointment_time_str = appointment.time.split('-')[0].strip()  # Get the start time of the time slot
    appointment_date_str = str(appointment.date)

    # Merge date and time into a single string and convert it to datetime
    appointment_datetime_str = f"{appointment_date_str} {appointment_time_str}"
    appointment_datetime = datetime.datetime.strptime(appointment_datetime_str, "%Y-%m-%d %I:%M %p")

    # Get current datetime
    now = datetime.datetime.now()

    # Allow rescheduling if it's within 30 minutes past the start of the appointment time slot
    if now <= appointment_datetime + timedelta(minutes=30):
        appointment.appointment_status = 'cancelled'
        appointment.save()

        # Increment the patient's no_shows count
        patient = appointment.patient
        patient.no_shows += 1
        patient.save()

        # Create a new notification for verification
        notify.send(patient.health_center, recipient=patient.user, verb='We\'re sorry, you didn\'t make it :(', 
                    description=f'We hope to see you soon.', 
                    redirect=f'/patient-dashboard/', icon='heart-outline')  

        #fill up the spot
        reschedule(appointment)

        messages.error(request, 'Patient\'s appointment has been marked as no-show.')
        return redirect('staff-dashboard')
    else:
        appointment.appointment_status = 'cancelled'
        appointment.save()

        # Increment the patient's no_shows count
        patient = appointment.patient
        patient.no_shows += 1
        patient.save()

        # Create a new notification for verification
        notify.send(patient.health_center, recipient=patient.user, verb='We\'re sorry, you didn\'t make it :(', 
                    description=f'We hope to see you soon.', 
                    redirect=f'/patient-dashboard/', icon='heart-outline')  

        messages.error(request, 'Patient\'s appointment has been marked as no-show.')
        return redirect('staff-dashboard')

#         end_year = doctor.end_year
#         end_year = re.sub("'", "", end_year)
#         end_year = end_year.replace("[", "")
#         end_year = end_year.replace("]", "")
#         end_year = end_year.replace(",", "")
#         end_year_array = end_year.split()       
#         experience = zip(work_place_array, designation_array, start_year_array, end_year_array)

@login_required(login_url="login")
def doctor_profile(request, pk):
    # request.user --> get logged in user
    if request.user.is_patient:
        patient = request.user.patient
    else:
        patient = None
    
    doctor = Doctor_Information.objects.get(doctor_id=pk)
    # doctor = Doctor_Information.objects.filter(doctor_id=pk).order_by('-doctor_id')
    healthcenter = Healthcenter_Information.objects.get(healthcenter_id=doctor.health_center.healthcenter_id)
    educations = Education.objects.filter(doctor=doctor).order_by('-year_of_completion')
    experiences = Experience.objects.filter(doctor=doctor).order_by('-from_year','-to_year') 
    doctor_review = Doctor_review.objects.filter(doctor=doctor)
            
    context = {'doctor': doctor, 'patient': patient, 'educations': educations, 'experiences': experiences, 'doctor_review': doctor_review, 'healthcenter': healthcenter}
    return render(request, 'doctor-profile.html', context)

def clean_name(name):
    errors = []
    if not name:
        errors.append('Please provide your name.')
    else:
        if re.search(r'[^A-Za-z.\s]', name):
            errors.append('First name should only contain letters.')
        
        if len(name) > 70:
            errors.append('First name should not exceed 70 characters.')

    if errors:
        raise ValidationError(errors)

def clean_dob(dob):
    errors = []
    if not dob:
        errors.append('Please provide your date of birth.')
    
    else:
        dob_date = datetime.datetime.strptime(dob, '%Y-%m-%d').date()
        today_date = datetime.datetime.today().date()
        
        if dob_date > today_date:
            errors.append('Please provide a valid date of birth.')
    
    if errors:
        raise ValidationError(errors)

def clean_phone_number(phone_number):
    errors = []
    if not phone_number:
        errors.append('Please provide a phone number.')
    else:
        if not re.match(r'^(\+639|0)\d{10}$', phone_number):
            errors.append('Invalid phone number format: Must start with +639 or 0 and be followed by a 10-digit number')
    if errors:
        raise ValidationError(errors)

def clean_barangay_num(barangay_num):
    errors = []
    try:
        barangay_num = int(barangay_num)
        if barangay_num < 0:
            errors.append('Please provide a valid barangay number.')
    except ValueError:
        errors.append('Please provide a valid barangay number.')
    if errors:
        raise ValidationError(errors)

def clean_zip_code(zip_code):
    errors = []
    try:
        zip_code = int(zip_code)
        if zip_code < 0:
            errors.append('Please provide a valid zip code number.')
    except ValueError:
        errors.append('Please provide a valid zip code number.')
    if errors:
        raise ValidationError(errors)

def clean_gender(gender):
    errors = []
    if not gender:
        errors.append('Please select a gender.')
    if errors:
        raise ValidationError(errors)

def clean_state(state):
    errors = []
    if not state.isalpha():
        errors.append('State should contain only alphabetic characters.')
    if errors:
        raise ValidationError(errors)

@login_required(login_url="login")
def staff_profile(request, pk):
    # request.user --> get logged in user
    if request.user.is_patient:
        patient = request.user.patient
    else:
        patient = None
    
    staff = Staff.objects.get(staff_id=pk)
    health_center = staff.health_center
    context = {'staff': staff, 'patient': patient, 'health_center': health_center}

    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        if form_type == 'update_personal_details':
            name = request.POST.get('name')
            date_of_birth = request.POST.get('date_of_birth')
            phone_number = request.POST.get('phone_number')
            address = request.POST.get('address')
            city = request.POST.get('city')
            state = request.POST.get('state')
            zip_code = request.POST.get('zip_code')
            country = request.POST.get('country')

            try:
                if name != staff.name:
                    clean_name(name)
                    staff.name = name

                if date_of_birth != staff.date_of_birth:
                    clean_dob(date_of_birth)
                    staff.date_of_birth = date_of_birth

                if phone_number != staff.phone_number:
                    clean_phone_number(phone_number)
                    staff.phone_number = phone_number
                
                if address != staff.address:
                    staff.address = address
                
                if city != staff.city:
                    staff.city = city
                
                if state != staff.state:
                    clean_state(state)
                    staff.state = state
                
                if zip_code != staff.zip_code:
                    clean_zip_code(zip_code)
                    staff.zip_code = zip_code
                
                if country != staff.country:
                    clean_barangay_num(country)
                    staff.country = country

                
                staff.save()
                messages.success(request, 'Personal details updated successfully')
            except ValidationError as e:
                errors = e.args[0]
                error_msg = ' '.join(errors)
                messages.error(request, error_msg)
                return redirect("staff-profile", pk)

        elif form_type == 'change_password':
            prev_password = request.POST.get("old_password_input")
            new_password = request.POST.get("new_password_input")
            confirm_password = request.POST.get("confirm_password_input")
            if prev_password and new_password and confirm_password:
                # Check if the old password is correct
                if not request.user.check_password(prev_password):
                    messages.error(request, "Current password is incorrect")
                    return redirect("staff-profile", pk)

                # Check if the new password and confirm password match
                if new_password == confirm_password:
                    request.user.set_password(new_password)
                    request.user.save()
                    messages.success(request, "Password Changed Successfully")
                    return redirect("login")
                else:
                    messages.error(request, "New Password and Confirm Password do not match")
                    return redirect("staff-profile", pk)
            else:
                messages.error(request, "Please fill in all the fields")
                return redirect("staff-profile", pk)

    
    return render(request, 'staff-profile.html', context)

@transaction.atomic
@login_required(login_url="login")
def delete_education(request, pk):
    if request.user.is_doctor:
        doctor = Doctor_Information.objects.get(user=request.user)
        
        educations = Education.objects.get(education_id=pk)
        educations.delete()
        
        messages.success(request, 'Education Deleted')
        return redirect('doctor-profile-settings')

@transaction.atomic
@login_required(login_url="login")
def delete_experience(request, pk):
    if request.user.is_doctor:
        doctor = Doctor_Information.objects.get(user=request.user)
        
        experiences = Experience.objects.get(experience_id=pk)
        experiences.delete()
        
        messages.success(request, 'Experience Deleted')
        return redirect('doctor-profile-settings')
      
@transaction.atomic
@login_required(login_url="login")
def doctor_profile_settings(request):
    # profile_Settings.js
    if request.user.is_doctor:
        doctor = Doctor_Information.objects.get(user=request.user)
        old_featured_image = doctor.featured_image
        

        if request.method == 'GET':
            educations = Education.objects.filter(doctor=doctor)
            experiences = Experience.objects.filter(doctor=doctor)
                    
            context = {'doctor': doctor, 'educations': educations, 'experiences': experiences}
            return render(request, 'doctor-profile-settings.html', context)
        elif request.method == 'POST':
            if 'featured_image' in request.FILES:
                featured_image = request.FILES['featured_image']
            else:
                featured_image = old_featured_image
                
            name = request.POST.get('name')
            number = request.POST.get('number')
            gender = request.POST.get('gender')
            dob = request.POST.get('dob')
            description = request.POST.get('description')
            nid = request.POST.get('nid')
            visit_hour = request.POST.get('visit_hour')
            
            degree = request.POST.getlist('degree')
            institute = request.POST.getlist('institute')
            year_complete = request.POST.getlist('year_complete')
            hospital_name = request.POST.getlist('hospital_name')     
            start_year= request.POST.getlist('from')
            end_year = request.POST.getlist('to')
            designation = request.POST.getlist('designation')

            try:
                if name != doctor.name:
                    clean_name(name)
                    doctor.name = name

                if dob != doctor.dob:
                    clean_dob(dob)
                    doctor.dob = dob

                if number != doctor.phone_number:
                    clean_phone_number(number)
                    doctor.phone_number = number

                if visit_hour != doctor.visiting_hour:
                    doctor.visiting_hour = visit_hour

                if nid != doctor.nid:
                    doctor.nid = nid
                
                if gender != doctor.gender:
                    clean_gender(gender)
                    doctor.gender = gender

                if featured_image != doctor.featured_image:
                    doctor.featured_image = featured_image

                if description != doctor.description:
                    doctor.description = description

                doctor.save()
                
                # Education
                for i in range(len(degree)):
                    education = Education(doctor=doctor)
                    education.degree = degree[i]
                    education.institute = institute[i]
                    education.year_of_completion = year_complete[i]
                    education.save()

                # Experience
                for i in range(len(hospital_name)):
                    experience = Experience(doctor=doctor)
                    experience.work_place_name = hospital_name[i]
                    experience.from_year = start_year[i]
                    experience.to_year = end_year[i]
                    experience.designation = designation[i]
                    experience.save()
        
                # context = {'degree': degree}
                messages.success(request, 'Profile Updated')
                return redirect('doctor-profile-settings')
            
            except ValidationError as e:
                errors = e.args[0]
                error_msg = ' '.join(errors)
                messages.error(request, error_msg)
                return redirect("doctor-profile-settings")
    else:
        redirect('logout')
               
@csrf_exempt    
@login_required(login_url="login")      
def booking_success(request):
    return render(request, 'booking-success.html')

def normalize_score(score, max_score):
    if max_score == 0 or score == 0:
        return 0
    else:
        return score / max_score

def get_urgency_score(urgency_level):
    weights = {"low": 1, "medium": 2, "high": 3}
    return weights.get(urgency_level, 1)

@transaction.atomic
@login_required(login_url="login")
def booking(request, pk):
    if request.user.is_patient:
        patient = request.user.patient
        if(patient.is_verified):
            healthcenter = Healthcenter_Information.objects.get(healthcenter_id=pk)

            if patient.health_center != healthcenter:
                messages.error(request, 'You are not associated with this health center.')
                return redirect('patient-dashboard')

            valid_appointment_time = ['8:00 am - 9:00 am', '10:00 am - 11:00 am', '1:00 pm - 2:00 pm', '3:00 pm - 4:00 pm']
            try:
                if request.method == 'POST':
                    date = request.POST['appoint_date']
                    time = request.POST['appoint_time']
                    appointment_type = request.POST['appointment_type']
                    urgency = request.POST['urgency']
                    message = request.POST['message']
                    symptoms = request.POST['symptoms']

                    transformed_date = str(date)
                    
                    check = datetime.datetime.strptime(date,'%Y-%m-%d')

                    # Check if the date is a Sunday
                    if check.weekday() == 5:
                        messages.error(request, 'Appointments cannot be booked on Saturday.')
                        return redirect('patient-dashboard')
                    elif check.weekday() == 6:
                        messages.error(request, 'Appointments cannot be booked on Sunday.')
                        return redirect('patient-dashboard')
                    
                    # Compare the appointment date with today's date
                    today_date = datetime.datetime.now().date()
                    appointment_date = datetime.datetime.strptime(date, '%Y-%m-%d').date()

                    if appointment_date < today_date:
                        messages.error(request, 'Appointment date cannot be in the past.')
                        return redirect('booking', pk=pk)
                        
                    # If appointment date is today, check if the appointment time is in the past
                    if appointment_date == today_date:
                        now_time = datetime.datetime.now().time()
                        appointment_time = datetime.datetime.strptime(time.split(" - ")[1], '%I:%M %p').time()
                        
                        if appointment_time < now_time:
                            messages.error(request, 'Appointment time cannot be in the past.')
                            return redirect('booking', pk=pk)
                    
                    # Check if the patient already has an appointment on this date
                    if Appointment.objects.filter(healthcenter=healthcenter, date=transformed_date, patient=patient).exists():
                        messages.error(request, 'You already have an appointment on this date.')
                        return redirect('booking', pk=pk)

                    # Check if there are already 4 appointments for this date and time
                    existing_appointments = Appointment.objects.filter(healthcenter=healthcenter, date=transformed_date, time=time).count()
                    if existing_appointments >= 4:
                        # Check if the patient is already in the waitlist
                        if Waitlist.objects.filter(healthcenter=healthcenter, desired_date=transformed_date, desired_time=time, patient=patient).exists():
                            messages.error(request, 'You are already on the waitlist for this date and time.')
                            return redirect('booking', pk=pk)
                        
                        # Calculate raw scores
                        age_score_raw = patient.age
                        urgency_score_raw = get_urgency_score(urgency)
                        no_show_score_raw = patient.no_shows
                        cancellations_score_raw = patient.cancellations

                        # Calculate maximum possible scores
                        oldest_patient = Patient.objects.all().order_by('-age').first()

                        max_age_score = oldest_patient.age if oldest_patient is not None else 0
                        max_urgency_score = 3
                        patient_with_max_no_shows = Patient.objects.all().order_by('-no_shows').first()
                        max_no_show_score = patient_with_max_no_shows.no_shows if patient_with_max_no_shows is not None else 0

                        patient_with_max_cancellations = Patient.objects.all().order_by('-cancellations').first()
                        max_cancellations_score = patient_with_max_cancellations.cancellations if patient_with_max_cancellations is not None else 0

                        # Normalize scores
                        if patient.age <= 18:
                            age_score = normalize_score(age_score_raw, max_age_score) * 1.5
                        elif patient.age <= 60:
                            age_score = normalize_score(age_score_raw, max_age_score)
                        else:
                            age_score = normalize_score(age_score_raw, max_age_score) * 2

                        urgency_score = normalize_score(urgency_score_raw, max_urgency_score) * 2  # Multiply by 2 to give urgency a higher weight
                        no_show_score = normalize_score(no_show_score_raw, max_no_show_score) * -1  # Negate to penalize frequent no-shows
                        cancellations_score = normalize_score(cancellations_score_raw, max_cancellations_score) * -1  # Negate to penalize frequent cancellations

                        heuristic_score = urgency_score + no_show_score + cancellations_score + age_score


                        # Add patient to the waitlist
                        waitlist_entry = Waitlist(patient=patient, healthcenter=healthcenter, desired_date=transformed_date, desired_time=time, appointment_type=appointment_type, urgency=urgency, message=message, score=heuristic_score, symptoms=symptoms)
                        waitlist_entry.save()

                        # Create the notification
                        notify.send(patient.health_center, recipient=patient.user, verb='You have been added to the waitlist!', 
                            description=f'You have been added to the waitlist on {waitlist_entry.desired_date} at {waitlist_entry.desired_time} for {patient.health_center.name}. ', 
                            redirect=f'/patient-dashboard/', icon='calendar')

                        messages.info(request, 'You have been added to the waitlist.')
                        return redirect('booking', pk=pk)
                    
                    # Check if the appointment type is valid
                    if time not in valid_appointment_time:
                        messages.error(request, 'Invalid appointment type.')
                        return redirect('booking', pk=pk)
                    
                    appointment = Appointment(patient=patient, healthcenter=healthcenter)
                    appointment.date = transformed_date
                    appointment.time = time
                    appointment.appointment_status = 'pending'
                    appointment.urgency = urgency
                    appointment.serial_number = generate_random_string()
                    appointment.appointment_type = appointment_type
                    appointment.message = message
                    appointment.symptoms = symptoms
                    appointment.save()

                    if appointment_date == (today_date + datetime.timedelta(days=1)) and datetime.datetime.now().time() >= datetime.time(12, 0):
                        # Notify the patient to confirm the appointment if the appointment is for the next day and it's past 12 PM
                        notify.send(patient.health_center, recipient=patient.user, verb='You have a new appointment', 
                                    description=f'You have a new appointment on {appointment.date} at {appointment.time}. Do you want to confirm it?', 
                                    redirect=f'/confirm-appointment/{appointment.id}', icon='calendar', appointment=appointment.id)
                    else:
                        # Notify the patient that the appointment has been booked if the appointment is for later days or if it's for the next day but it's not past 12 PM yet
                        notify.send(patient.health_center, recipient=patient.user, verb='You have a new appointment', 
                                    description=f'You have successfully booked an appointment on {appointment.date} at {appointment.time}. You will receive a notification later shortly for confirmation.', 
                                    redirect=f'/patient-dashboard/', icon='calendar', appointment=appointment.id)

                    if message:
                        # Mailtrap
                        patient_email = appointment.patient.email
                        patient_name = appointment.patient.name
                        patient_username = appointment.patient.username
                        patient_phone_number = appointment.patient.phone_number
                        healthcenter = appointment.healthcenter.name
                    
                        subject = "Appointment Request"
                        
                        values = {
                                "email":patient_email,
                                "name":patient_name,
                                "username":patient_username,
                                "phone_number":patient_phone_number,
                                "healthcenter":healthcenter,
                                "message":message,
                            }
                        
                        html_message = render_to_string('appointment-request-mail.html', {'values': values})
                        plain_message = strip_tags(html_message)
                        
                        try:
                            send_mail(subject, plain_message, 'healthcenter_admin@gmail.com',  [patient_email], html_message=html_message, fail_silently=False)
                        except BadHeaderError:
                            return HttpResponse('Invalid header found')
                    
                    
                    messages.success(request, 'Appointment Booked')
                    return redirect('booking', pk=pk)
            except Exception as e:
                messages.error(request, 'Something went wrong, please try again.')
                return redirect('booking', pk=pk)
        else:
            messages.error(request, 'Please get verified first')
            return redirect('patient-verification')
    else:
        messages.error(request, 'No permission to view this page')
        return redirect('login')

    context = {'patient': patient, 'healthcenter': healthcenter, 'pk': pk}
    return render(request, 'booking.html', context)

def get_ranking_difference(stats_past_week, stats_previous_week):
    ranking_difference = []
    
    stats_past_week_list = list(stats_past_week)
    stats_previous_week_list = list(stats_previous_week)

    for current in stats_past_week_list:
        current_rank = stats_past_week_list.index(current)
        previous_rank = -1
        for previous in stats_previous_week_list:
            if current['disease_condition'] == previous['disease_condition']:
                previous_rank = stats_previous_week_list.index(previous)
                break

        if previous_rank == -1:
            ranking_difference.append('new')
        elif current_rank < previous_rank:
            ranking_difference.append('up')
        elif current_rank > previous_rank:
            ranking_difference.append('down')
        else:
            ranking_difference.append('same')

    return ranking_difference

def create_age_group_chart(cases_data):
    cases_by_age_df = pd.DataFrame.from_records(cases_data)

     # Check if the data frame is empty
    if cases_by_age_df.empty:
        # Create a DataFrame with the necessary columns filled with zero
        cases_by_age_df = pd.DataFrame({'patient__age': [0], 'total_cases': [0], 'disease_condition': ['No Case Today']})

    age_group_chart = px.bar(cases_by_age_df, x='patient__age', y='total_cases', color='disease_condition', title='Cases by Age Group',
                             labels={'patient__age': 'Patient Age', 'total_cases': 'Total Cases', 'disease_condition': 'Name of Disease'})
    return age_group_chart.to_html(full_html=False)

def create_gender_chart(cases_data):
    cases_by_gender_df = pd.DataFrame.from_records(cases_data)

     # Check if the data frame is empty
    if cases_by_gender_df.empty:
        # Create a DataFrame with the necessary columns filled with zero
        cases_by_gender_df = pd.DataFrame({'patient__gender': [0], 'total_cases': [0], 'disease_condition': ['No Case Today']})

    gender_chart = px.bar(cases_by_gender_df, x='patient__gender', y='total_cases', color='disease_condition', title='Cases by Gender',
                          labels={'patient__gender': 'Patient Gender', 'total_cases': 'Total Cases', 'disease_condition': 'Name of Disease'})
    return gender_chart.to_html(full_html=False)

def create_time_series_chart(cases_data):
    cases_by_date_df = pd.DataFrame.from_records(cases_data)

    # Check if the data frame is empty
    if cases_by_date_df.empty:
        # Create a DataFrame with the necessary columns filled with zero
        cases_by_date_df = pd.DataFrame({'create_date': [0], 'total_cases': [0], 'disease_condition': ['No Case Today']})

    time_series_chart = px.line(cases_by_date_df, x='create_date', y='total_cases', color='disease_condition', title='Cases Over Time',
                                labels={'create_date': 'Date', 'total_cases': 'Total Cases', 'disease_condition': 'Name of Disease'})
    return time_series_chart.to_html(full_html=False)

def create_severity_chart(cases_data):
    cases_by_severity_df = pd.DataFrame.from_records(cases_data)

    # Check if the data frame is empty
    if cases_by_severity_df.empty:
        # Create a DataFrame with the necessary columns filled with zero
        cases_by_severity_df = pd.DataFrame({'severity': [0], 'total_cases': [0], 'disease_condition': ['No Case Today']})

    severity_chart = px.bar(cases_by_severity_df, x='severity', y='total_cases', color='disease_condition', title='Cases by Severity',
                            labels={'severity': 'Severity', 'total_cases': 'Total Cases', 'disease_condition': 'Name of Disease'})
    return severity_chart.to_html(full_html=False)

def load_dataset(path, sheet):
    df = pd.ExcelFile(path)
    df = pd.read_excel(df, sheet, parse_dates=True, index_col=0,)
    df.dropna(how='any', inplace=True)
    df.index = pd.to_datetime(df.index)
    df.sort_index(inplace=True)
    return df

def outbreak_threshold(df):
    cases = df.iloc[:, -1]
    return round(cases.mean() + 2 * cases.std(), 2)

def check_outbreak(forecast_dict, min_cases):
    outbreak_dict = {}
    for date, forecast in zip(forecast_dict['date'], forecast_dict['forecast']):
        if isinstance(forecast, str):  # Check if forecast is a str
            # Extract the numeric value from the string using regular expressions
            match = re.match(r'tf\.Tensor\(([\d.]+)', forecast)
            if match:
                forecast_np = float(match.group(1))
                if forecast_np >= min_cases:
                    datetime_date = date.to_pydatetime()
                    formatted_date = datetime_date.strftime('%B %d, %Y')
                    outbreak_dict[formatted_date] = forecast_np
        else:
            forecast_np = forecast.numpy()  # Converting TensorFlow tensor to numpy
            if forecast_np >= min_cases:
                datetime_date = date.to_pydatetime()  # Convert Pandas Timestamp to Python datetime
                formatted_date = datetime_date.strftime('%B %d, %Y')  # Formats the date to the desired format
                outbreak_dict[formatted_date] = forecast_np
    return outbreak_dict

@login_required(login_url="login")
def forecasting(request, disease_name):
    # Mapping from disease names to sheet names
    disease_sheet_map = {
        'Dengue': 'Sheet1',
        'Hepatitis A': 'Sheet2',
        'Chikungunya': 'Sheet3',
        'Typhoid Fever': 'Sheet4',
        'Acute bloody diarrhea': 'Sheet5',
        'Leptospirosis': 'Sheet6',
        'Measles': 'Sheet7',
        'Cholera': 'Sheet8',
        'Influenza-like illness': 'Sheet9',
        'Covid-19': 'Sheet11',
        'Rotavirus': 'Sheet12',
        'Bacterial Meningitis': 'Sheet13',
    }

    doctor = Doctor_Information.objects.get(user=request.user)
    disease_sheet = disease_sheet_map.get(disease_name)  # Get the sheet name for the disease

    if disease_name in ['Dengue', 'Covid-19']:
        if disease_sheet is not None:
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            PATH = os.path.join(BASE_DIR, 'doctor', 'forecasting', 'data-updated.xlsx')
            df = load_dataset(PATH, disease_sheet)

            if disease_name == 'Dengue':
                BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                PATH = os.path.join(BASE_DIR, 'doctor', 'forecasting', 'dengue.xlsx')
            else:  # disease_name == 'Covid-19'
                BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                PATH = os.path.join(BASE_DIR, 'doctor', 'forecasting', 'covid.xlsx')

            forecast = pd.read_excel(PATH)

            # Convert the DataFrame to forecast_dict
            forecast_dict = {
                'date': forecast['date'].tolist(),
                'forecast': forecast['forecast'].tolist()
            }

            # Get the outbreak_dict using check_outbreak function
            outbreak_threshold_value = outbreak_threshold(df)
            outbreak_dict = check_outbreak(forecast_dict, outbreak_threshold_value)

    elif disease_sheet is not None:
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        PATH = os.path.join(BASE_DIR, 'doctor', 'forecasting', 'data-updated.xlsx')
        df = load_dataset(PATH, disease_sheet)
        outbreak_threshold_value = outbreak_threshold(df)
        forecast_dict = get_forecast(disease_sheet)  # Call the function with the sheet name
        outbreak_dict = check_outbreak(forecast_dict, outbreak_threshold_value)
    else:
        messages.error(request, 'Something went wrong, please try again.')
        return redirect('doctor-dashboard') 

    return render(request, 'forecasting.html', {'doctor': doctor, 'disease_name': disease_name, 'min_cases': outbreak_threshold_value, 'outbreak_dict': outbreak_dict})


@login_required(login_url="login")
def disease_statistics(request):
    doctor = Doctor_Information.objects.get(user=request.user)
    
    health_center_id = doctor.health_center.healthcenter_id

    now = datetime.datetime.now().date()
    past_60_days = now - timedelta(days=60)
    past_30_days = now - timedelta(days=30)
    past_14_days = now - timedelta(days=14)
    past_7_days = now - timedelta(days=7)
    past_48_hours = now - timedelta(days=2)
    past_24_hours = now - timedelta(days=1)
    
    #Specific Healthcenter
    # Disease count for all time
    all_overall_stats_all_time = MedicalRecord.objects.filter(doctor__health_center__healthcenter_id=health_center_id).values('disease_condition').annotate(total_cases=Count('disease_condition')).order_by('-total_cases')

    # Disease count for the last 60 days
    all_overall_stats_past_60_days = MedicalRecord.objects.filter(create_date__range=(past_60_days, past_30_days), doctor__health_center__healthcenter_id=health_center_id).values('disease_condition').annotate(total_cases=Count('disease_condition')).order_by('-total_cases')

    # Disease count for the last 30 days
    all_overall_stats_past_30_days = MedicalRecord.objects.filter(create_date__range=(past_30_days, now), doctor__health_center__healthcenter_id=health_center_id).values('disease_condition').annotate(total_cases=Count('disease_condition')).order_by('-total_cases')
    
    # Disease count for the last 14 days
    all_overall_stats_past_14_days = MedicalRecord.objects.filter(create_date__range=(past_14_days, past_7_days), doctor__health_center__healthcenter_id=health_center_id).values('disease_condition').annotate(total_cases=Count('disease_condition')).order_by('-total_cases')
    
    # Disease count for the last 7 days
    all_overall_stats_past_7_days = MedicalRecord.objects.filter(create_date__range=(past_7_days, now), doctor__health_center__healthcenter_id=health_center_id).values('disease_condition').annotate(total_cases=Count('disease_condition')).order_by('-total_cases')

    # Disease count for the last 48 hours
    all_overall_stats_past_48_hours = MedicalRecord.objects.filter(create_date__range=(past_48_hours, past_24_hours), doctor__health_center__healthcenter_id=health_center_id).values('disease_condition').annotate(total_cases=Count('disease_condition')).order_by('-total_cases')

    # Disease count for the last 24 hours
    all_overall_stats_past_24_hours = MedicalRecord.objects.filter(create_date__range=(past_24_hours, now), doctor__health_center__healthcenter_id=health_center_id).values('disease_condition').annotate(total_cases=Count('disease_condition')).order_by('-total_cases')
    
    # Calculate percentage increase in cases from past 30 to past 7 days
    all_percentage_increase_past_30_days = []
    for all_current in all_overall_stats_past_30_days:
        all_previous_cases = 0
        for all_previous in all_overall_stats_past_7_days:
            if all_current['disease_condition'] == all_previous['disease_condition']:
                all_previous_cases = all_previous['total_cases']
                break

        all_increase = ((all_current['total_cases'] - all_previous_cases) / all_previous_cases) * 100 if all_previous_cases > 0 else 0
        all_percentage_increase_past_30_days.append({
            'disease_condition': all_current['disease_condition'],
            'total_cases': all_current['total_cases'],
            'percentage_increase': all_increase
        })

    # Calculate percentage increase in cases from past 7 to past 24 hours
    all_percentage_increase_past_7_days = []
    for all_current in all_overall_stats_past_7_days:
        all_previous_cases = 0
        for all_previous in all_overall_stats_past_24_hours:
            if all_current['disease_condition'] == all_previous['disease_condition']:
                all_previous_cases = all_previous['total_cases']
                break

        all_increase = ((all_current['total_cases'] - all_previous_cases) / all_previous_cases) * 100 if all_previous_cases > 0 else 0
        all_percentage_increase_past_7_days.append({
            'disease_condition': all_current['disease_condition'],
            'total_cases': all_current['total_cases'],
            'percentage_increase': all_increase
        })

    # Calculate percentage increase in cases from past 24 hours
    all_percentage_increase_past_24_hours = []
    for all_current in all_overall_stats_past_24_hours:
        all_previous_cases = 0
        for all_previous in all_overall_stats_past_48_hours:
            if all_current['disease_condition'] == all_previous['disease_condition']:
                all_previous_cases = all_previous['total_cases']
                break

        all_increase = ((all_current['total_cases'] - all_previous_cases) / all_previous_cases) * 100 if all_previous_cases > 0 else 0
        all_percentage_increase_past_24_hours.append({
            'disease_condition': all_current['disease_condition'],
            'total_cases': all_current['total_cases'],
            'percentage_increase': all_increase
        })
    
    # Get total number of cases for each disease currently
    all_overall_stats_current = MedicalRecord.objects.filter(doctor__health_center__healthcenter_id=health_center_id).values('disease_condition').annotate(total_cases=Count('disease_condition')).order_by('-total_cases')

    # Get ranking difference
    all_ranking_difference_all_time = get_ranking_difference(all_overall_stats_all_time, all_overall_stats_current)
    all_ranking_difference_past_30_days = get_ranking_difference(all_overall_stats_past_30_days, all_overall_stats_past_60_days)
    all_ranking_difference_past_7_days = get_ranking_difference(all_overall_stats_past_7_days, all_overall_stats_past_14_days)
    all_ranking_difference_past_1_day = get_ranking_difference(all_overall_stats_past_24_hours, all_overall_stats_past_48_hours)

    #plotly
    # query
    # All Time
    all_cases_all_time = MedicalRecord.objects.filter(doctor__health_center__healthcenter_id=health_center_id).values('patient__age', 'patient__gender', 'create_date', 'severity', 'disease_condition').annotate(total_cases=Count('disease_condition'))

    # 30D
    all_cases_past_30_days = MedicalRecord.objects.filter(create_date__range=(past_30_days, now), doctor__health_center__healthcenter_id=health_center_id).values('patient__age', 'patient__gender', 'create_date', 'severity', 'disease_condition').annotate(total_cases=Count('disease_condition'))

    # 7D
    all_cases_past_7_days = MedicalRecord.objects.filter(create_date__range=(past_7_days, now), doctor__health_center__healthcenter_id=health_center_id).values('patient__age', 'patient__gender', 'create_date', 'severity', 'disease_condition').annotate(total_cases=Count('disease_condition'))

    # 1D
    all_cases_past_1_day = MedicalRecord.objects.filter(create_date__range=(past_24_hours, now), doctor__health_center__healthcenter_id=health_center_id).values('patient__age', 'patient__gender', 'create_date', 'severity', 'disease_condition').annotate(total_cases=Count('disease_condition'))
    
    # Create visualizations
    all_age_group_chart_all_time = create_age_group_chart(all_cases_all_time)
    all_age_group_chart_30D = create_age_group_chart(all_cases_past_30_days)
    all_age_group_chart_7D = create_age_group_chart(all_cases_past_7_days)
    all_age_group_chart_1D = create_age_group_chart(all_cases_past_1_day)

    all_gender_chart_all_time = create_gender_chart(all_cases_all_time)
    all_gender_chart_30D = create_gender_chart(all_cases_past_30_days)
    all_gender_chart_7D = create_gender_chart(all_cases_past_7_days)
    all_gender_chart_1D = create_gender_chart(all_cases_past_1_day)

    all_time_series_chart_all_time = create_time_series_chart(all_cases_all_time)
    all_time_series_chart_30D = create_time_series_chart(all_cases_past_30_days)
    all_time_series_chart_7D = create_time_series_chart(all_cases_past_7_days)
    all_time_series_chart_1D = create_time_series_chart(all_cases_past_1_day)

    all_severity_chart_all_time = create_severity_chart(all_cases_all_time)
    all_severity_chart_30D = create_severity_chart(all_cases_past_30_days)
    all_severity_chart_7D = create_severity_chart(all_cases_past_7_days)
    all_severity_chart_1D = create_severity_chart(all_cases_past_1_day)

    #All Healthcenter
    # Disease count for all time
    overall_stats_all_time = MedicalRecord.objects.values('disease_condition').annotate(total_cases=Count('disease_condition')).order_by('-total_cases')

    # Disease count for the last 60 days
    overall_stats_past_60_days = MedicalRecord.objects.filter(create_date__range=(past_60_days, past_30_days)).values('disease_condition').annotate(total_cases=Count('disease_condition')).order_by('-total_cases')

    # Disease count for the last 30 days
    overall_stats_past_30_days = MedicalRecord.objects.filter(create_date__range=(past_30_days, now)).values('disease_condition').annotate(total_cases=Count('disease_condition')).order_by('-total_cases')
    
    # Disease count for the last 14 days
    overall_stats_past_14_days = MedicalRecord.objects.filter(create_date__range=(past_14_days, past_7_days)).values('disease_condition').annotate(total_cases=Count('disease_condition')).order_by('-total_cases')
    
    # Disease count for the last 7 days
    overall_stats_past_7_days = MedicalRecord.objects.filter(create_date__range=(past_7_days, now)).values('disease_condition').annotate(total_cases=Count('disease_condition')).order_by('-total_cases')

    # Disease count for the last 48 hours
    overall_stats_past_48_hours = MedicalRecord.objects.filter(create_date__range=(past_48_hours, past_24_hours)).values('disease_condition').annotate(total_cases=Count('disease_condition')).order_by('-total_cases')

    # Disease count for the last 24 hours
    overall_stats_past_24_hours = MedicalRecord.objects.filter(create_date__range=(past_24_hours, now)).values('disease_condition').annotate(total_cases=Count('disease_condition')).order_by('-total_cases')
    
    # Calculate percentage increase in cases from past 30 to past 7 days
    percentage_increase_past_30_days = []
    for current in overall_stats_past_30_days:
        previous_cases = 0
        for previous in overall_stats_past_7_days:
            if current['disease_condition'] == previous['disease_condition']:
                previous_cases = previous['total_cases']
                break

        increase = ((current['total_cases'] - previous_cases) / previous_cases) * 100 if previous_cases > 0 else 0
        percentage_increase_past_30_days.append({
            'disease_condition': current['disease_condition'],
            'total_cases': current['total_cases'],
            'percentage_increase': increase
        })

    # Calculate percentage increase in cases from past 7 to past 24 hours
    percentage_increase_past_7_days = []
    for current in overall_stats_past_7_days:
        previous_cases = 0
        for previous in overall_stats_past_24_hours:
            if current['disease_condition'] == previous['disease_condition']:
                previous_cases = previous['total_cases']
                break

        increase = ((current['total_cases'] - previous_cases) / previous_cases) * 100 if previous_cases > 0 else 0
        percentage_increase_past_7_days.append({
            'disease_condition': current['disease_condition'],
            'total_cases': current['total_cases'],
            'percentage_increase': increase
        })

    # Calculate percentage increase in cases from past 24 hours
    percentage_increase_past_24_hours = []
    for current in overall_stats_past_24_hours:
        previous_cases = 0
        for previous in overall_stats_past_48_hours:
            if current['disease_condition'] == previous['disease_condition']:
                previous_cases = previous['total_cases']
                break

        increase = ((current['total_cases'] - previous_cases) / previous_cases) * 100 if previous_cases > 0 else 0
        percentage_increase_past_24_hours.append({
            'disease_condition': current['disease_condition'],
            'total_cases': current['total_cases'],
            'percentage_increase': increase
        })
    
    # Get total number of cases for each disease currently
    overall_stats_current = MedicalRecord.objects.values('disease_condition').annotate(total_cases=Count('disease_condition')).order_by('-total_cases')

    # Get ranking difference
    ranking_difference_all_time = get_ranking_difference(overall_stats_all_time, overall_stats_current)
    ranking_difference_past_30_days = get_ranking_difference(overall_stats_past_30_days, overall_stats_past_60_days)
    ranking_difference_past_7_days = get_ranking_difference(overall_stats_past_7_days, overall_stats_past_14_days)
    ranking_difference_past_1_day = get_ranking_difference(overall_stats_past_24_hours, overall_stats_past_48_hours)

    #plotly
    # query
    # All Time
    cases_all_time = MedicalRecord.objects.values('patient__age', 'patient__gender', 'create_date', 'severity', 'disease_condition').annotate(total_cases=Count('disease_condition'))

    # 30D
    cases_past_30_days = MedicalRecord.objects.filter(create_date__range=(past_30_days, now)).values('patient__age', 'patient__gender', 'create_date', 'severity', 'disease_condition').annotate(total_cases=Count('disease_condition'))

    # 7D
    cases_past_7_days = MedicalRecord.objects.filter(create_date__range=(past_7_days, now)).values('patient__age', 'patient__gender', 'create_date', 'severity', 'disease_condition').annotate(total_cases=Count('disease_condition'))

    # 1D
    cases_past_1_day = MedicalRecord.objects.filter(create_date__range=(past_24_hours, now)).values('patient__age', 'patient__gender', 'create_date', 'severity', 'disease_condition').annotate(total_cases=Count('disease_condition'))
    
    # Create visualizations
    age_group_chart_all_time = create_age_group_chart(cases_all_time)
    age_group_chart_30D = create_age_group_chart(cases_past_30_days)
    age_group_chart_7D = create_age_group_chart(cases_past_7_days)
    age_group_chart_1D = create_age_group_chart(cases_past_1_day)

    gender_chart_all_time = create_gender_chart(cases_all_time)
    gender_chart_30D = create_gender_chart(cases_past_30_days)
    gender_chart_7D = create_gender_chart(cases_past_7_days)
    gender_chart_1D = create_gender_chart(cases_past_1_day)

    time_series_chart_all_time = create_time_series_chart(cases_all_time)
    time_series_chart_30D = create_time_series_chart(cases_past_30_days)
    time_series_chart_7D = create_time_series_chart(cases_past_7_days)
    time_series_chart_1D = create_time_series_chart(cases_past_1_day)

    severity_chart_all_time = create_severity_chart(cases_all_time)
    severity_chart_30D = create_severity_chart(cases_past_30_days)
    severity_chart_7D = create_severity_chart(cases_past_7_days)
    severity_chart_1D = create_severity_chart(cases_past_1_day)

    context = {
        'doctor': doctor,
        'overall_stats_past_30_days': overall_stats_past_30_days,
        'overall_stats_past_7_days': overall_stats_past_7_days,
        'overall_stats_past_24_hours': overall_stats_past_24_hours,
        'percentage_increase_past_30_days': percentage_increase_past_30_days,
        'percentage_increase_past_7_days': percentage_increase_past_7_days,
        'percentage_increase_past_24_hours': percentage_increase_past_24_hours,
        'overall_stats_current': overall_stats_current,
        'ranking_difference_past_7_days': ranking_difference_past_7_days,
        'ranking_difference_past_1_day': ranking_difference_past_1_day,
        'ranking_difference_past_30_days': ranking_difference_past_30_days,
        'ranking_difference_all_time': ranking_difference_all_time,
        'age_group_chart_all_time': age_group_chart_all_time,
        'age_group_chart_30D': age_group_chart_30D,
        'age_group_chart_7D': age_group_chart_7D,
        'age_group_chart_1D': age_group_chart_1D,
        'gender_chart_all_time': gender_chart_all_time,
        'gender_chart_30D': gender_chart_30D,
        'gender_chart_7D': gender_chart_7D,
        'gender_chart_1D': gender_chart_1D,
        'time_series_chart_all_time': time_series_chart_all_time,
        'time_series_chart_30D': time_series_chart_30D,
        'time_series_chart_7D': time_series_chart_7D,
        'time_series_chart_1D': time_series_chart_1D,
        'severity_chart_all_time': severity_chart_all_time,
        'severity_chart_30D': severity_chart_30D,
        'severity_chart_7D': severity_chart_7D,
        'severity_chart_1D': severity_chart_1D,
        'all_overall_stats_past_30_days': all_overall_stats_past_30_days,
        'all_overall_stats_past_7_days': all_overall_stats_past_7_days,
        'all_overall_stats_past_24_hours': all_overall_stats_past_24_hours,
        'all_percentage_increase_past_30_days': all_percentage_increase_past_30_days,
        'all_percentage_increase_past_7_days': all_percentage_increase_past_7_days,
        'all_percentage_increase_past_24_hours': all_percentage_increase_past_24_hours,
        'all_overall_stats_current': all_overall_stats_current,
        'all_ranking_difference_past_7_days': all_ranking_difference_past_7_days,
        'all_ranking_difference_past_1_day': all_ranking_difference_past_1_day,
        'all_ranking_difference_past_30_days': all_ranking_difference_past_30_days,
        'all_ranking_difference_all_time': all_ranking_difference_all_time,
        'all_age_group_chart_all_time': all_age_group_chart_all_time,
        'all_age_group_chart_30D': all_age_group_chart_30D,
        'all_age_group_chart_7D': all_age_group_chart_7D,
        'all_age_group_chart_1D': all_age_group_chart_1D,
        'all_gender_chart_all_time': all_gender_chart_all_time,
        'all_gender_chart_30D': all_gender_chart_30D,
        'all_gender_chart_7D': all_gender_chart_7D,
        'all_gender_chart_1D': all_gender_chart_1D,
        'all_time_series_chart_all_time': all_time_series_chart_all_time,
        'all_time_series_chart_30D': all_time_series_chart_30D,
        'all_time_series_chart_7D': all_time_series_chart_7D,
        'all_time_series_chart_1D': all_time_series_chart_1D,
        'all_severity_chart_all_time': all_severity_chart_all_time,
        'all_severity_chart_30D': all_severity_chart_30D,
        'all_severity_chart_7D': all_severity_chart_7D,
        'all_severity_chart_1D': all_severity_chart_1D
    }

    return render(request, 'disease_statistics.html', context)

#Specific Healthcenter
@login_required(login_url="login")
def all_fetch_alltime_data(request):
    doctor = Doctor_Information.objects.get(user=request.user)
    
    health_center_id = doctor.health_center.healthcenter_id

    overall_stats_current = MedicalRecord.objects.filter(doctor__health_center__healthcenter_id=health_center_id).values('disease_condition').annotate(total_cases=Count('disease_condition')).order_by('-total_cases')
    data = [
        {
            'name': stat['disease_condition'],
            'y': stat['total_cases']
        } for stat in overall_stats_current
    ]
    return JsonResponse(data, safe=False)

@login_required(login_url="login")
def all_fetch_30D_data(request):
    doctor = Doctor_Information.objects.get(user=request.user)
    
    health_center_id = doctor.health_center.healthcenter_id

    # Disease count for the last 30 days
    now = datetime.datetime.now().date()
    past_30_days = now - timedelta(days=30)
    overall_stats_past_30_days = MedicalRecord.objects.filter(create_date__range=(past_30_days, now), doctor__health_center__healthcenter_id=health_center_id).values('disease_condition').annotate(total_cases=Count('disease_condition')).order_by('-total_cases')    
    data = [
        {
            'name': stat['disease_condition'],
            'y': stat['total_cases']
        } for stat in overall_stats_past_30_days
    ]
    return JsonResponse(data, safe=False)

@login_required(login_url="login")
def all_fetch_7D_data(request):
    doctor = Doctor_Information.objects.get(user=request.user)
    
    health_center_id = doctor.health_center.healthcenter_id

    # Disease count for the last 7 days
    now = datetime.datetime.now().date()
    past_7_days = now - timedelta(days=7)
    overall_stats_past_7_days = MedicalRecord.objects.filter(create_date__range=(past_7_days, now), doctor__health_center__healthcenter_id=health_center_id).values('disease_condition').annotate(total_cases=Count('disease_condition')).order_by('-total_cases')    
    data = [
        {
            'name': stat['disease_condition'],
            'y': stat['total_cases']
        } for stat in overall_stats_past_7_days
    ]
    return JsonResponse(data, safe=False)

@login_required(login_url="login")
def all_fetch_1D_data(request):
    doctor = Doctor_Information.objects.get(user=request.user)
    
    health_center_id = doctor.health_center.healthcenter_id
    
    # Disease count for the last 24 hours
    now = datetime.datetime.now().date()
    past_24_hours = now - timedelta(days=1)
    overall_stats_past_24_hours = MedicalRecord.objects.filter(create_date__range=(past_24_hours, now), doctor__health_center__healthcenter_id=health_center_id).values('disease_condition').annotate(total_cases=Count('disease_condition')).order_by('-total_cases')    
    data = [
        {
            'name': stat['disease_condition'],
            'y': stat['total_cases']
        } for stat in overall_stats_past_24_hours
    ]
    return JsonResponse(data, safe=False)

#All Healthcenter
@login_required(login_url="login")
def fetch_alltime_data(request):
    overall_stats_current = MedicalRecord.objects.values('disease_condition').annotate(total_cases=Count('disease_condition')).order_by('-total_cases')
    data = [
        {
            'name': stat['disease_condition'],
            'y': stat['total_cases']
        } for stat in overall_stats_current
    ]
    return JsonResponse(data, safe=False)

@login_required(login_url="login")
def fetch_30D_data(request):
    # Disease count for the last 30 days
    now = datetime.datetime.now().date()
    past_30_days = now - timedelta(days=30)
    overall_stats_past_30_days = MedicalRecord.objects.filter(create_date__range=(past_30_days, now)).values('disease_condition').annotate(total_cases=Count('disease_condition')).order_by('-total_cases')    
    data = [
        {
            'name': stat['disease_condition'],
            'y': stat['total_cases']
        } for stat in overall_stats_past_30_days
    ]
    return JsonResponse(data, safe=False)

@login_required(login_url="login")
def fetch_7D_data(request):
    # Disease count for the last 7 days
    now = datetime.datetime.now().date()
    past_7_days = now - timedelta(days=7)
    overall_stats_past_7_days = MedicalRecord.objects.filter(create_date__range=(past_7_days, now)).values('disease_condition').annotate(total_cases=Count('disease_condition')).order_by('-total_cases')    
    data = [
        {
            'name': stat['disease_condition'],
            'y': stat['total_cases']
        } for stat in overall_stats_past_7_days
    ]
    return JsonResponse(data, safe=False)

@login_required(login_url="login")
def fetch_1D_data(request):
    # Disease count for the last 24 hours
    now = datetime.datetime.now().date()
    past_24_hours = now - timedelta(days=1)
    overall_stats_past_24_hours = MedicalRecord.objects.filter(create_date__range=(past_24_hours, now)).values('disease_condition').annotate(total_cases=Count('disease_condition')).order_by('-total_cases')    
    data = [
        {
            'name': stat['disease_condition'],
            'y': stat['total_cases']
        } for stat in overall_stats_past_24_hours
    ]
    return JsonResponse(data, safe=False)

@login_required(login_url="login")
def my_patients(request):
    if request.user.is_doctor:
        doctor = Doctor_Information.objects.get(user=request.user)
        healthcenter = Healthcenter_Information.objects.get(healthcenter_id=doctor.health_center.healthcenter_id)
        appointment_patients = set(Appointment.objects.filter(healthcenter=healthcenter, appointment_status='confirmed').values_list('patient', flat=True))
        walkin_patients = set(Walkin.objects.filter(healthcenter=healthcenter).values_list('patient', flat=True))
        unique_patients = appointment_patients.union(walkin_patients)
        patients = Patient.objects.filter(patient_id__in=unique_patients)
    else:
        redirect('logout')
    
    context = {'doctor': doctor, 'patients': patients}
    return render(request, 'my-patients.html', context)


# def patient_profile(request):
#     return render(request, 'patient_profile.html')

@login_required(login_url="login")
def patient_profile(request, pk):
    if request.user.is_doctor:
        # doctor = Doctor_Information.objects.get(user_id=pk)
        doctor = Doctor_Information.objects.get(user=request.user)
        healthcenter = Healthcenter_Information.objects.get(healthcenter_id=doctor.health_center.healthcenter_id)
        patient = Patient.objects.get(patient_id=pk)
        appointments = Appointment.objects.filter(healthcenter=healthcenter, patient=patient)
        walkins = Walkin.objects.filter(healthcenter=healthcenter, patient=patient)
        prescription = Prescription.objects.filter(healthcenter=healthcenter, patient=patient)
        record = MedicalRecord.objects.filter(healthcenter=healthcenter, patient=patient)
        brief = MedicalRecord.objects.filter(healthcenter=healthcenter, patient=patient).order_by('-create_date')[:5]        
        context = {'doctor': doctor, 'appointments': appointments, 'walkins': walkins, 'patient': patient, 'prescription': prescription, 'record': record, 'brief': brief} 
        return render(request, 'patient-profile.html', context) 
    elif request.user.is_staff:
        # doctor = Doctor_Information.objects.get(user_id=pk)
        staff = Staff.objects.get(user=request.user)
        healthcenter = Healthcenter_Information.objects.get(healthcenter_id=staff.health_center.healthcenter_id)
        patient = Patient.objects.get(patient_id=pk)
        appointments = Appointment.objects.filter(healthcenter=healthcenter).filter(patient=patient)
        prescription = Prescription.objects.filter(doctor__health_center=healthcenter).filter(patient=patient)
        record = MedicalRecord.objects.filter(doctor__health_center=healthcenter).filter(patient=patient)
        context = {'staff': staff, 'appointments': appointments, 'patient': patient, 'prescription': prescription, 'record': record}   
        return render(request, 'patient-profile.html', context)
    else:
        messages.error(request, 'No permission to view this page')
        return redirect('logout')

@transaction.atomic
@login_required(login_url="login")
def create_prescription(request, type, pk):
        if request.user.is_doctor:
            doctor = Doctor_Information.objects.get(user=request.user)
            create_date = datetime.date.today()
            healthcenter = Healthcenter_Information.objects.get(healthcenter_id=doctor.health_center.healthcenter_id)
            
            if type == 'appointment':
                related_record = Appointment.objects.get(id=pk)
            elif type == 'walkin':
                related_record = Walkin.objects.get(id=pk)
            else:
                messages.error(request, 'Something went wrong, please try again.')
                return render('doctor-dashboard')
            
            if related_record.healthcenter != doctor.health_center:
                messages.info(request, 'Not Authorized')
                return render('doctor-dashboard')

            # Check if a medical record is already associated with the appointment/walk-in
            if related_record.prescription:
                messages.info(request, 'A prescription is already associated with this appointment/walk-in.')
                return redirect('patient-profile', pk=related_record.patient.patient_id)

            patient = related_record.patient

            context = {'doctor': doctor,'patient': patient}  

            if request.method == 'POST':
                prescription = Prescription(doctor=doctor, patient=patient, healthcenter=healthcenter)
                    
                test_name= request.POST.getlist('test_name')
                test_description = request.POST.getlist('description')
                medicine_name = request.POST.getlist('medicine_name')
                medicine_quantity = request.POST.getlist('quantity')
                medecine_frequency = request.POST.getlist('frequency')
                medicine_duration = request.POST.getlist('duration')
                medicine_instruction = request.POST.getlist('instruction')
                extra_information = request.POST.get('extra_information')

                prescription.extra_information = extra_information
                prescription.create_date = create_date
                
                prescription.save()
                
                if type == 'appointment':
                    related_record.prescription = prescription
                elif type == 'walkin':
                    related_record.prescription = prescription
                else:
                    messages.error(request, 'Something went wrong, please try again.')
                    return render(request, 'patient-profile')

                related_record.save()

                for i in range(len(medicine_name)):
                    if not medicine_name[i]:
                        messages.error(request, f'Medicine name for item {i+1} is required.')
                        return render(request, 'create-prescription.html',context)

                    if not medicine_quantity[i]:
                        messages.error(request, f'Medicine quantity for item {i+1} is required.')
                        return render(request, 'create-prescription.html',context)
                    
                    if not medecine_frequency[i]:
                        messages.error(request, f'Medicine frequency for item {i+1} is required.')
                        return render(request, 'create-prescription.html',context)
                    
                    if not medicine_duration[i]:
                        messages.error(request, f'Medicine duration for item {i+1} is required.')
                        return render(request, 'create-prescription.html',context)
                    
                    try:
                        medicine = Prescription_medicine(prescription=prescription)
                        medicine.medicine_name = medicine_name[i]
                        medicine.quantity = medicine_quantity[i]
                        medicine.frequency = medecine_frequency[i]
                        medicine.duration = medicine_duration[i]
                        medicine.instruction = medicine_instruction[i]
                        medicine.save()
                    except Exception as e:
                        messages.error(request, f"An error occurred: {str(e)}")
                        return render(request, 'create-prescription.html',context)


                for i in range(len(test_name)):
                    if not test_name[i]:
                        messages.error(request, f'Test name for item {i+1} is required.')
                        return render(request, 'create-prescription.html',context)
                    
                    try:
                        tests = Prescription_test(prescription=prescription)
                        tests.test_name = test_name[i]
                        tests.test_description = test_description[i]
                    
                        tests.save()
                    except Exception as e:
                        messages.error(request, f"An error occurred: {str(e)}")
                        return render(request, 'create-prescription.html',context)

                # Create a new notification for verification
                notify.send(patient.health_center, recipient=patient.user, verb='Prescription Created', 
                            description=f'You can now view your prescription. Thank you!', 
                            redirect=f'/prescription-view/{prescription.prescription_id}', icon='medical-outline')  

                messages.success(request, 'Prescription Created')
                return redirect('patient-profile', pk=patient.patient_id)
             
        return render(request, 'create-prescription.html',context)

@transaction.atomic
@login_required(login_url="login")
def create_vaccination(request):
    page = 'walkin-registration'
    staff = Staff.objects.get(user=request.user)
    healthcenter = Healthcenter_Information.objects.get(healthcenter_id=staff.health_center.healthcenter_id)
    patients = Patient.objects.filter(health_center=healthcenter)
    patient_form = ExtraInfoForm()
    creationtype = 'vaccination'

    context = {
        'staff': staff,
        'healthcenter': healthcenter,
        'patients': patients,
        'VACCINE_CHOICES': Vaccination.VACCINE_CHOICES,
        'DOSE_NUMBER_CHOICES': Vaccination.DOSE_NUMBER_CHOICES,
        'patient_form': patient_form,
    }

    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        no_account = request.POST.get('check')  # Get the value of the checkbox

        if no_account:  # If the checkbox is checked
            patient_form = ExtraInfoForm(request.POST)

            if patient_form.is_valid():
                email = request.POST.get('email')
                # Check if another patient with the same email already exists
                if Patient.objects.filter(email=email).exists():
                    error_message = "A patient with this email already exists."
                    messages.error(request, error_message)
                    return render(request, 'create-vaccination.html', context)
                else:
                    patient = create_new_user(request, patient_form, email, healthcenter, page, staff, patients, creationtype)
                    if patient is None:
                        messages.error(request, f'An error occurred during registration. Please check the form for errors. {patient_form.errors}')
                        return render(request, 'create-vaccination.html', context)
            else:
                messages.error(request, f'An error occurred during registration. Please check the form for errors. {patient_form.errors}')
        else:
            patient = Patient.objects.get(patient_id=patient_id)

        vaccination = Vaccination(staff=staff, patient=patient, healthcenter=healthcenter)


        vaccine_name = request.POST.get('vaccine_name')
        lot_number = request.POST.get('lot_number')
        expiry_date = request.POST.get('expiry_date')
        date_given = request.POST.get('date_given')
        given_by = request.POST.get('given_by')
        dose_number = int(request.POST.get('dose_number'))
        create_date = request.POST.get('create_date')

        if lot_number is not None:
            if not lot_number.isdigit() or int(lot_number) < 0:
                error_message = "Lot number must be a number."
                messages.error(request, error_message)
                return render(request, 'create-vaccination.html', context)
        
        if given_by is None or vaccine_name is None:
            error_message = "Please fill in the text fields."
            messages.error(request, error_message)
            return render(request, 'create-vaccination.html', context)

        if given_by.isdigit():
            error_message = "Invalid format for given by, must be a name."
            messages.error(request, error_message)
            return render(request, 'create-vaccination.html', context)
        
        vaccination.patient = patient
        vaccination.vaccine_name = vaccine_name
        vaccination.lot_number = lot_number
        vaccination.expiry_date = expiry_date
        vaccination.date_given = date_given
        vaccination.given_by = given_by
        vaccination.dose_number = dose_number
        vaccination.create_date = create_date

        # Your checks and validation rules here.
        # If any check fails, render 'create_vaccination.html' with an error message

        # Check if a vaccination record for the same dose_number already exists
        if Vaccination.objects.filter(patient=patient, dose_number=dose_number).exists():
                messages.error(request, f'Vaccination Record for Dose {dose_number} already exists.')
                return render(request, 'create-vaccination.html', context)
            
            # Check if the 1st dose and second dose are the same brand
        if dose_number > 1:
                last_vaccination = Vaccination.objects.filter(patient=patient, dose_number=dose_number - 1).last()
                if last_vaccination and last_vaccination.vaccine_name != vaccine_name:
                    messages.error(request, f'The 1st dose and 2nd dose should be the same brand.')
                    return render(request, 'create-vaccination.html', context)
            
            # Check if the second dose is after 90 days from the first dose
        if dose_number == 2:
                last_vaccination = Vaccination.objects.filter(patient=patient, dose_number=1).last()
                if last_vaccination and last_vaccination.date_given:
                    date_given_as_date = datetime.datetime.strptime(date_given, "%Y-%m-%d").date()  # Convert to datetime.date
                    days_since_first_dose = (date_given_as_date - last_vaccination.date_given).days
                    if days_since_first_dose < 90:
                        messages.error(request, 'The second dose should be given after 90 days from the first dose.')
                        return render(request, 'create-vaccination.html', context)

            # Check if the expiry date is not less than 90 days
        expiry_date_obj = datetime.datetime.strptime(expiry_date, "%Y-%m-%d")
        if expiry_date_obj < (datetime.datetime.now() + timedelta(days=90)):
                messages.error(request, 'The expiry date should not be less than 90 days.')
                return render(request, 'create-vaccination.html', context)
            
            # Check if the patient has received the previous dose before adding a new dose
        if dose_number > 1:
                previous_dose_number = dose_number - 1
                if not Vaccination.objects.filter(patient=patient, dose_number=previous_dose_number).exists():
                    messages.error(request, f'The patient has not received Dose {previous_dose_number}.')
                    return render(request, 'create-vaccination.html', context)
            # Check if the patient has received the second dose before adding the third dose
        elif dose_number > 2:
                previous_dose_number = dose_number - 1
                if not Vaccination.objects.filter(patient=patient, dose_number=previous_dose_number).exists():
                    messages.error(request, f'The patient has not received Dose {previous_dose_number}.')
                    return render(request, 'create-vaccination.html', context)
            # Check if the patient has received the third dose before adding the fourth dose
        elif dose_number > 3:
                previous_dose_number = dose_number - 1
                if not Vaccination.objects.filter(patient=patient, dose_number=previous_dose_number).exists():
                    messages.error(request, f'The patient has not received Dose {previous_dose_number}.')
                    return render(request, 'create-vaccination.html', context)

        try:
            vaccination.save()
            messages.success(request, 'Vaccination Record Created')
            return redirect('staff-dashboard')
        except Exception as e:
            messages.error(request, 'Something went wrong, please try again.')
            return render(request, 'create-vaccination.html', context)
        
    return render(request, 'create-vaccination.html', context)

@transaction.atomic
@login_required(login_url="login")
def create_immunization(request):
    page = 'walkin-registration'
    staff = Staff.objects.get(user=request.user)
    healthcenter = Healthcenter_Information.objects.get(healthcenter_id=staff.health_center.healthcenter_id)
    patients = Patient.objects.filter(health_center=healthcenter)
    patient_form = ExtraInfoForm()
    creationtype = 'immunization'

    context = {
        'staff': staff,
        'healthcenter': healthcenter,
        'patients': patients,
        'IMMUNIZATION_RECORD_CHOICES': Immunization.IMMUNIZATION_RECORD_CHOICES,
        'IMMUNE_CHOICES': Immunization.IMMUNE_CHOICES,
        'VISIT_NUMBER_CHOICES': Immunization.VISIT_NUMBER_CHOICES,
        'DOSE_NUMBER_CHOICES': Immunization.DOSE_NUMBER_CHOICES,
        'patient_form': patient_form,
    }

    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        no_account = request.POST.get('check')  # Get the value of the checkbox

        if no_account:  # If the checkbox is checked
            patient_form = ExtraInfoForm(request.POST)

            if patient_form.is_valid():
                email = request.POST.get('email')
                # Check if another patient with the same email already exists
                if Patient.objects.filter(email=email).exists():
                    error_message = "A patient with this email already exists."
                    messages.error(request, error_message)
                    return render(request, 'create-immunization.html', context)
                else:
                    patient = create_new_user(request, patient_form, email, healthcenter, page, staff, patients, creationtype)
                    if patient is None:
                        messages.error(request, 'An error occurred during registration. Please check the form for errors.')
                        return render(request, 'create-immunization.html', context)
            else:
                messages.error(request, 'An error occurred during registration. Please check the form for errors.')
                return render(request, 'create-immunization.html', context)
        else:
            patient = Patient.objects.get(patient_id=patient_id)

        immunization = Immunization(staff=staff, patient=patient, healthcenter=healthcenter)

        immune_record = request.POST.get('immune_record')
        immune_name = request.POST.get('immune_name')
        given_by = request.POST.get('given_by')
        create_date = request.POST.get('create_date')
        date_given = request.POST.get('date_given')
        dose_number = request.POST.get('dose_number')


        if not given_by:
            error_message = "Please fill in the text fields."
            messages.error(request, error_message)
            return render(request, 'create-immunization.html', context)
        
        if given_by.isdigit():
            error_message = "Invalid format for given by, must be a name."
            messages.error(request, error_message)
            return render(request, 'create-immunization.html', context)

        immunization.patient = patient
        immunization.immune_record = immune_record
        immunization.given_by = given_by
        immunization.create_date = create_date
        immunization.date_given = date_given
        immunization.dose_number = dose_number
        

        # Check if the immune_record is not equal to "ADULTS"
        if immune_record == 'Child':
                immune_name = request.POST.get('immune_name')
                othervaccine_name = request.POST.get('othervaccine_name')
                visit_number = int(request.POST.get('visit_number'))
                remarks = request.POST.get('remarks')

                immunization.immune_name = immune_name
                immunization.othervaccine_name = othervaccine_name
                immunization.remarks = remarks
                immunization.visit_number = visit_number
                
               # Check if an immunization record for the same visit_number and immune_name already exists
                if Immunization.objects.filter(patient=patient, visit_number=visit_number, immune_name=immune_name).exists():
                    messages.error(request, f'Immunization Record for {visit_number} and {immune_name} already exists.')
                    return render(request, 'create-immunization.html', context)
                

                if immune_name == 'HEPATITIS B' and Immunization.objects.filter(patient=patient, immune_name='HEPATITIS B', remarks=remarks).exists():
                    messages.error(request, 'The patient has already received HEPATITIS B immunization.')
                    return render(request, 'create-immunization.html', context)
                     
                if immune_name == 'PENTAVALENT VACCINE'and Immunization.objects.filter(patient=patient, immune_name='PENTAVALENT VACCINE').exists():
                    # Check if the patient has received the previous dose of BCG or Hepatitis
                    previous_immunizations = ['BCG', 'HEPATITIS B']
                    for prev_immunization in previous_immunizations:
                        if not Immunization.objects.filter(patient=patient, immune_name=prev_immunization).exists():
                            messages.error(request, f'The patient has not received {prev_immunization} immunization.')
                            return render(request, 'create-immunization.html', context)
                        
                     # Check if the patient has received the previous dose before adding a new dose
                    if visit_number > 1:
                        previous_visit_number = visit_number - 1
                        if not Immunization.objects.filter(patient=patient, visit_number=previous_visit_number).exists():
                            messages.error(request, f'The patient has not received {previous_visit_number}.')
                            return render(request, 'create-immunization.html', context)              
                        
                    # Check if the patient has received the second dose before adding the third dose
                    elif visit_number > 2:
                        previous_visit_number = visit_number - 1
                        if not Immunization.objects.filter(patient=patient, visit_number=previous_visit_number, remarks=remarks).exists():
                            messages.error(request, f'The patient has not received {previous_visit_number}.')
                            return render(request, 'create-immunization.html', context)
                    

                if immune_name == 'ORAL POLIO VACCINE':
                    oralpolio_count = Immunization.objects.filter(patient=patient, immune_name='ORAL POLIO VACCINE').count()
                    if oralpolio_count > 3:
                        messages.error(request, 'The patient has already received 3 doses of ORAL POLIO VACCINE.')
                        return render(request, 'create-immunization.html', context)
                    
                    # Check if the patient has received the previous dose of BCG or Hepatitis
                    previous_immunizations = ['PENTAVALENT VACCINE']
                    for prev_immunization in previous_immunizations:
                        if not Immunization.objects.filter(patient=patient, immune_name=prev_immunization).exists():
                            messages.error(request, f'The patient has not received {prev_immunization} immunization.')
                            return render(request, 'create-immunization.html', context)    

                    # Check if the patient has received the previous dose before adding a new dose
                    if visit_number > 1:
                        previous_visit_number = visit_number - 1
                        if not Immunization.objects.filter(patient=patient, visit_number=previous_visit_number).exists():
                            messages.error(request, f'The patient has not received {previous_visit_number}.')
                            return render(request, 'create-immunization.html', context)

                    # Check if the patient has received the second dose before adding the third dose
                    elif visit_number > 2:
                        previous_visit_number = visit_number - 1
                        if not Immunization.objects.filter(patient=patient, visit_number=previous_visit_number, remarks=remarks).exists():
                            messages.error(request, f'The patient has not received {previous_visit_number}.')
                            return render(request, 'create-immunization.html', context)
      
                        
                if immune_name == 'INACTIVATED POLIO VACCINE' and Immunization.objects.filter(patient=patient, immune_name='INACTIVATED POLIO VACCINE', remarks=remarks).exists():
                     # Check if the patient has received the previous dose of BCG or Hepatitis
                    previous_immunizations = ['ORAL POLIO VACCINE']
                    for prev_immunization in previous_immunizations:
                        if not Immunization.objects.filter(patient=patient, immune_name=prev_immunization).exists():
                            messages.error(request, f'The patient has not received {prev_immunization} immunization.')
                            return render(request, 'create-immunization.html', context)
                        
                
                if immune_name == 'PNEUMOCOCCAL CONJUGATE VACCINE':
                    pneumococcal_count = Immunization.objects.filter(patient=patient, immune_name='PNEUMOCOCCAL CONJUGATE VACCINE').count()
                    if pneumococcal_count > 3:
                        messages.error(request, 'The patient has already received 3 doses of PNEUMOCOCCAL CONJUGATE VACCINE.')
                        return render(request, 'create-immunization.html', context)

                    # Check if the patient has received the previous dose of BCG or Hepatitis
                    previous_immunizations = ['INACTIVATED POLIO VACCINE']
                    for prev_immunization in previous_immunizations:
                        if not Immunization.objects.filter(patient=patient, immune_name=prev_immunization).exists():
                            messages.error(request, f'The patient has not received {prev_immunization} immunization.')
                            return render(request, 'create-immunization.html', context)

                    # Check if the patient has received the previous dose before adding a new dose
                    if visit_number > 1:
                        previous_visit_number = visit_number - 1
                        if not Immunization.objects.filter(patient=patient, visit_number=previous_visit_number).exists():
                            messages.error(request, f'The patient has not received {previous_visit_number}.')
                            return render(request, 'create-immunization.html', context)

                    # Check if the patient has received the second dose before adding the third dose
                    elif visit_number > 2:
                        previous_visit_number = visit_number - 1
                        if not Immunization.objects.filter(patient=patient, visit_number=previous_visit_number, remarks=remarks).exists():
                            messages.error(request, f'The patient has not received {previous_visit_number}.')
                            return render(request, 'create-immunization.html', context)

                if immune_name == 'MEASLES, MUMPS, RUBELLA':
                    mmr_count = Immunization.objects.filter(patient=patient, immune_name='MEASLES, MUMPS, RUBELLA').count()
                    if mmr_count > 3:
                        messages.error(request, 'The patient has already received 3 doses of MEASLES, MUMPS, RUBELLA.')
                        return render(request, 'create-immunization.html', context)

                    # Check if the patient has received the previous dose of BCG or Hepatitis
                    previous_immunizations = ['BCG', 'HEPATITIS B', 'PNEUMOCOCCAL CONJUGATE VACCINE', 'INACTIVATED POLIO VACCINE', 'ORAL POLIO VACCINE', 'PENTAVALENT VACCINE']
                    for prev_immunization in previous_immunizations:
                        if not Immunization.objects.filter(patient=patient, immune_name=prev_immunization).exists():
                            messages.error(request, f'The patient has not received {prev_immunization} immunization.')
                            return render(request, 'create-immunization.html', context)

                    # Check if the patient has received the previous dose before adding a new dose
                    if visit_number > 1:
                        previous_visit_number = visit_number - 1
                        if not Immunization.objects.filter(patient=patient, visit_number=previous_visit_number, remarks=remarks).exists():
                            messages.error(request, f'The patient has not received {previous_visit_number}.')
                            return render(request, 'create-immunization.html', context)
                            
                elif immune_name == 'Others':
                    if Immunization.objects.filter(patient=patient, othervaccine_name=othervaccine_name).exists():
                        messages.error(request, f'Immunization Record for {othervaccine_name} already exists.')
                        return render(request, 'create-immunization.html', context)
 

                else:
                    if Immunization.objects.filter(patient=patient, dose_number=dose_number).exists():
                                    messages.error(request, f'Immunization Record for {dose_number} already exists.')
                                    return render(request, 'create-immunization.html', context)  
                    
        elif immune_record =='Adult':
            other_vaccine = request.POST.get('other_vaccine')
            hfacility_name= request.POST.get('hfacility_name')
            dose_number = request.POST.get('dose_number')

            if not other_vaccine or not hfacility_name:
                error_message = "Please fill in the text fields."
                messages.error(request, error_message)
                return render(request, 'create-immunization.html', context)

            immunization.other_vaccine = other_vaccine
            immunization.dose_number = dose_number
            immunization.hfacility_name = hfacility_name
            immunization.visit_number = 0

            if Immunization.objects.filter(patient=patient, other_vaccine=other_vaccine, dose_number=dose_number).exists():
                    messages.error(request, f'Immunization Record for {other_vaccine} already exists.')
                    return render(request, 'create-immunization.html', context)
        try:
            immunization.save()
            messages.success(request, 'Immunization Record Created')
            return redirect('staff-dashboard')
        except Exception as e:
            messages.error(request, 'Something went wrong, please try again.')
            return render(request, 'create-immunization.html', context)
        
    return render(request, 'create-immunization.html', context)

@transaction.atomic
@login_required(login_url="login")
def create_medical(request, type, pk):
    if request.user.is_doctor:
        doctor = Doctor_Information.objects.get(user=request.user)
        healthcenter = Healthcenter_Information.objects.get(healthcenter_id=doctor.health_center.healthcenter_id)
        create_date = datetime.date.today() 

        if type == 'appointment':
            related_record = Appointment.objects.get(id=pk)
        elif type == 'walkin':
            related_record = Walkin.objects.get(id=pk)
        else:
            messages.error(request, 'Something went wrong, please try again.')
            return render('doctor-dashboard')

        if related_record.healthcenter != doctor.health_center:
            messages.info(request, 'Not Authorized')
            return render('doctor-dashboard')
        
        # Check if a medical record is already associated with the appointment/walk-in
        if related_record.medical_record:
            messages.info(request, 'A medical record is already associated with this appointment/walk-in.')
            return redirect('patient-profile', pk=related_record.patient.patient_id)
        
        patient = related_record.patient

        context = {'doctor': doctor,'patient': patient, 'DISEASE_CHOICES': MedicalRecord.DISEASE_CHOICES}  

        if request.method == 'POST':
            # Add an instance of the MedicalRecord model to the context
            medical_record = MedicalRecord(doctor=doctor, patient=patient, healthcenter=healthcenter)
                
            lab_name = request.POST.get('lab_name')
            test_date = request.POST.get('test_date')
            tests_conducted = request.POST.get('tests_conducted')
            results_summary = request.POST.get('results_summary')
            blood_pressure = request.POST.get('blood_pressure')
            heart_rate = request.POST.get('heart_rate')
            respiratory_rate = request.POST.get('respiratory_rate')
            temperature = request.POST.get('temperature')
            physical_examination = request.POST.get('physical_examination')
            diagnostic_tests = request.POST.get('diagnostic_tests')
            disease_condition = request.POST.get('disease_condition')
            severity = request.POST.get('severity')
            additional_notes = request.POST.get('additional_notes')

            if not lab_name:
                messages.error(request, 'Lab name is required.')
                return render(request, 'create-medical.html',context)

            if not test_date:
                messages.error(request, 'Test date is required.')
                return render(request, 'create-medical.html',context)
            
            if not tests_conducted:
                messages.error(request, 'Tests conducted field is required.')
                return render(request, 'create-medical.html',context)

            if not blood_pressure:
                messages.error(request, 'Blood pressure is required.')
                return render(request, 'create-medical.html',context)

            if not heart_rate:
                messages.error(request, 'Heart rate is required.')
                return render(request, 'create-medical.html',context)

            if not respiratory_rate:
                messages.error(request, 'Respiratory rate is required.')
                return render(request, 'create-medical.html',context)

            if not temperature:
                messages.error(request, 'Temperature is required.')
                return render(request, 'create-medical.html',context)

            if not disease_condition:
                messages.error(request, 'Disease condition is required.')
                return render(request, 'create-medical.html',context)

            if not severity:
                messages.error(request, 'Severity is required.')
                return render(request, 'create-medical.html',context)
            try:
                medical_record.lab_name = lab_name
                medical_record.test_date = test_date
                medical_record.tests_conducted = tests_conducted
                medical_record.results_summary = results_summary
                medical_record.blood_pressure = blood_pressure
                medical_record.heart_rate = heart_rate
                medical_record.respiratory_rate = respiratory_rate
                medical_record.temperature = temperature
                medical_record.physical_examination = physical_examination
                medical_record.diagnostic_tests = diagnostic_tests
                medical_record.disease_condition = disease_condition
                medical_record.severity = severity
                medical_record.additional_notes = additional_notes
                medical_record.create_date = create_date
                
                medical_record.save()

                if type == 'appointment':
                    related_record.medical_record = medical_record
                elif type == 'walkin':
                    related_record.medical_record = medical_record
                else:
                    messages.error(request, 'Something went wrong, please try again.')
                    return redirect('patient-profile', pk=patient.patient_id)

                related_record.save()

                # Create a new notification for verification
                notify.send(patient.health_center, recipient=patient.user, verb='Medical Record Created', 
                            description=f'You can now view your medical record by requesting for it. Thank you!', 
                            redirect=f'/patient-dashboard/', icon='medical-outline') 

                messages.success(request, 'Medical Record Created')
                return redirect('patient-profile', pk=patient.patient_id)
            
            except IntegrityError as e:
                messages.error(request, f"An integrity error occurred: {str(e)}")
                return render(request, 'create-medical.html',context)

            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
                return render(request, 'create-medical.html',context)

    return render(request, 'create-medical.html',context)

@transaction.atomic
@login_required(login_url="login")
def edit_prescription(request, pk):
    if request.user.is_doctor:
        doctor = Doctor_Information.objects.get(user=request.user)

        try:
            prescription = Prescription.objects.get(pk=pk)
        except Prescription.DoesNotExist:
            messages.error(request, 'Prescription does not exist.')
            return redirect('dashboard')

        if prescription.healthcenter != doctor.health_center:
            messages.info(request, 'Not Authorized')
            return render('doctor-dashboard')

        patient = prescription.patient

        test = Prescription_test.objects.filter(prescription=prescription)
        medicine = Prescription_medicine.objects.filter(prescription=prescription)

        context = {'prescription': prescription, 'doctor': doctor, 'patient': patient, 'test': test, 'medicine': medicine}
        
        if request.method == 'POST':
            prescription.extra_information = request.POST.get('extra_information')
            prescription.save()
            medicine.all().delete()  # delete existing associated medicines and tests
            test.all().delete()  # before creating new ones

            medicine_name = request.POST.getlist('medicine_name')
            medicine_quantity = request.POST.getlist('quantity')
            medecine_frequency = request.POST.getlist('frequency')
            medicine_duration = request.POST.getlist('duration')
            medicine_instruction = request.POST.getlist('instruction')

            for i in range(len(medicine_name)):
                if not medicine_name[i]:
                    messages.error(request, f'Medicine name for item {i+1} is required.')
                    return render(request, 'edit-prescription.html', context)

                if not medicine_quantity[i]:
                    messages.error(request, f'Medicine quantity for item {i+1} is required.')
                    return render(request, 'edit-prescription.html', context)
                
                if not medecine_frequency[i]:
                    messages.error(request, f'Medicine frequency for item {i+1} is required.')
                    return render(request, 'edit-prescription.html', context)
                
                if not medicine_duration[i]:
                    messages.error(request, f'Medicine duration for item {i+1} is required.')
                    return render(request, 'edit-prescription.html', context)
                
                try:
                    medicine = Prescription_medicine(prescription=prescription)
                    medicine.medicine_name = medicine_name[i]
                    medicine.quantity = medicine_quantity[i]
                    medicine.frequency = medecine_frequency[i]
                    medicine.duration = medicine_duration[i]
                    medicine.instruction = medicine_instruction[i]
                    medicine.save()
                except Exception as e:
                    messages.error(request, f"An error occurred: {str(e)}")
                    return render(request, 'edit-prescription.html', context)

            test_name= request.POST.getlist('test_name')
            test_description = request.POST.getlist('description')
            test_info_id = request.POST.getlist('id')

            for i in range(len(test_name)):
                if not test_name[i]:
                    messages.error(request, f'Test name for item {i+1} is required.')
                    return render(request, 'edit-prescription.html', context)
                
                if not test_info_id[i]:
                    messages.error(request, f'Test id for item {i+1} is required.')
                    return render(request, 'edit-prescription.html', context)
                
                try:
                    tests = Prescription_test(prescription=prescription)
                    tests.test_name = test_name[i]
                    tests.test_description = test_description[i]
                    tests.test_info_id = test_info_id[i]
                
                    tests.save()
                except Exception as e:
                    messages.error(request, f"An error occurred: {str(e)}")
                    return render(request, 'edit-prescription.html', context)
            
            # Create a new notification for verification
            notify.send(patient.health_center, recipient=patient.user, verb='Prescription has been Modified', 
                        description=f'Your prescription has been modified, please check the changes made. Thank you!', 
                        redirect=f'/prescription-view/{prescription.prescription_id}', icon='medical-outline')  

            messages.success(request, 'Prescription Updated')
            return redirect('patient-profile', pk=prescription.patient.patient_id)
        
    else:
        logout(request)
        messages.info(request, 'Not Authorized')
        return render(request, 'login.html')

    return render(request, 'edit-prescription.html', context)


@transaction.atomic
@login_required(login_url="login")
def edit_medical(request, pk):
    if request.user.is_doctor:
        doctor = Doctor_Information.objects.get(user=request.user)

        try:
            medical_record = MedicalRecord.objects.get(pk=pk)
        except MedicalRecord.DoesNotExist:
            messages.error(request, 'Medical Record does not exist.')
            return redirect('doctor-dashboard')
        
        if medical_record.healthcenter != doctor.health_center:
            messages.info(request, 'Not Authorized')
            return render('doctor-dashboard')
        
        create_datetime = datetime.datetime.combine(medical_record.create_date, datetime.datetime.min.time())
        create_datetime_aware = timezone.make_aware(create_datetime, timezone.get_current_timezone())

        if (timezone.localtime(timezone.now()) - create_datetime_aware) > timedelta(hours=24):
            messages.info(request, 'Time limit for editing this medical record has expired.')
            return redirect('patient-profile', pk=medical_record.patient.patient_id)

        patient = medical_record.patient

        context = {'medical_record': medical_record, 'DISEASE_CHOICES': MedicalRecord.DISEASE_CHOICES, 'doctor': doctor, 'patient': patient}

        if request.method == 'POST':
            lab_name = request.POST.get('lab_name')
            test_date = request.POST.get('test_date')
            tests_conducted = request.POST.get('tests_conducted')
            results_summary = request.POST.get('results_summary')
            blood_pressure = request.POST.get('blood_pressure')
            heart_rate = request.POST.get('heart_rate')
            respiratory_rate = request.POST.get('respiratory_rate')
            temperature = request.POST.get('temperature')
            physical_examination = request.POST.get('physical_examination')
            diagnostic_tests = request.POST.get('diagnostic_tests')
            disease_condition = request.POST.get('disease_condition')
            severity = request.POST.get('severity')
            additional_notes = request.POST.get('additional_notes')

            if not lab_name:
                messages.error(request, 'Lab name is required.')
                return render(request, 'edit-medical.html', context)

            if not test_date:
                messages.error(request, 'Test date is required.')
                return render(request, 'edit-medical.html', context)
            
            if not tests_conducted:
                messages.error(request, 'Tests conducted field is required.')
                return render(request, 'edit-medical.html', context)

            if not blood_pressure:
                messages.error(request, 'Blood pressure is required.')
                return render(request, 'edit-medical.html', context)

            if not heart_rate:
                messages.error(request, 'Heart rate is required.')
                return render(request, 'edit-medical.html', context)

            if not respiratory_rate:
                messages.error(request, 'Respiratory rate is required.')
                return render(request, 'edit-medical.html', context)

            if not temperature:
                messages.error(request, 'Temperature is required.')
                return render(request, 'edit-medical.html', context)

            if not disease_condition:
                messages.error(request, 'Disease condition is required.')
                return render(request, 'edit-medical.html', context)

            if not severity:
                messages.error(request, 'Severity is required.')
                return render(request, 'edit-medical.html', context)
            try:
                medical_record.lab_name = lab_name
                medical_record.test_date = test_date
                medical_record.tests_conducted = tests_conducted
                medical_record.results_summary = results_summary
                medical_record.blood_pressure = blood_pressure
                medical_record.heart_rate = heart_rate
                medical_record.respiratory_rate = respiratory_rate
                medical_record.temperature = temperature
                medical_record.physical_examination = physical_examination
                medical_record.diagnostic_tests = diagnostic_tests
                medical_record.disease_condition = disease_condition
                medical_record.severity = severity
                medical_record.additional_notes = additional_notes
                
                medical_record.save()

            except IntegrityError as e:
                messages.error(request, f"An integrity error occurred: {str(e)}")
                return render(request, 'edit-medical.html', context)

            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
                return render(request, 'edit-medical.html', context)

            # Create a new notification for verification
            notify.send(patient.health_center, recipient=patient.user, verb='Medical Record has been Modified', 
                        description=f'Your medical record has been modified, please check the changes made. Thank you!', 
                        redirect=f'/patient-dashboard/', icon='medical-outline')  

            messages.success(request, 'Medical Record Updated')
            return redirect('patient-profile', pk=medical_record.patient.patient_id)
    else:
        logout(request)
        messages.info(request, 'Not Authorized')
        return render(request, 'login.html')

    return render(request, 'edit-medical.html', context)

@csrf_exempt
def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)  # Changed encoding to UTF-8
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type="application/pdf")  # Fixed content_type
    return None

@csrf_exempt
def record_pdf(request, pk):
    if request.user.is_patient:
        patient = Patient.objects.get(user=request.user)

        patient = Patient.objects.get(user=request.user)

        try:
            record = MedicalRecord.objects.get(medical_id=pk)
        except MedicalRecord.DoesNotExist:
            messages.error(request, 'Medical Record does not exist.')
            return redirect('patient-dashboard')

        try:
            existing_request = MedicalRecordRequest.objects.get(patient=patient, record=record, status='A')
        except MedicalRecordRequest.DoesNotExist:
            messages.info(request, 'Not Authorized')
            return redirect('patient-dashboard')

        if record.patient != patient:
            messages.info(request, 'Not Authorized')
            return redirect('patient-dashboard')

        # Check if there is an approved request from this patient for this record
        if existing_request and existing_request.status != 'A':
            messages.info(request, 'You need to request to view this medical record.')
            return redirect('patient-dashboard')

        # current_date = datetime.date.today()  # Commented out since not used
        context = {'patient': patient, 'record': record}
        pdf = render_to_pdf('record_pdf.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            # Uncomment next line if you want to download the PDF instead of viewing it
            #response['Content-Disposition'] = 'attachment; filename=record.pdf'
            return response
    return HttpResponse("Not Found")


# def testing(request):
#     doctor = Doctor_Information.objects.get(user=request.user)
#     degree = doctor.degree
#     degree = re.sub("'", "", degree)
#     degree = degree.replace("[", "")
#     degree = degree.replace("]", "")
#     degree = degree.replace(",", "")
#     degree_array = degree.split()
    
#     education = zip(degree_array, institute_array)
    
#     context = {'doctor': doctor, 'degree': institute, 'institute_array': institute_array, 'education': education}
#     # test range, len, and loop to show variables before moving on to doctor profile
    
#     return render(request, 'testing.html', context)

@login_required(login_url="login")
def patient_search(request, pk):
    if request.user.is_authenticated and request.user.is_doctor:
        doctor = Doctor_Information.objects.get(doctor_id=pk)
        try:
            id = int(request.GET['search_query'])
        except ValueError:
            messages.error(request, 'Please input patient id.')
            return redirect('my-patients')
        patient = Patient.objects.get(patient_id=id)
        prescription = Prescription.objects.filter(doctor=doctor).filter(patient=patient)
        context = {'patient': patient, 'doctor': doctor, 'prescription': prescription}
        return render(request, 'patient-profile.html', context)
    else:
        logout(request)
        messages.info(request, 'Not Authorized')
        return render(request, 'login.html')

@csrf_exempt
@login_required(login_url="login")
def doctor_test_list(request):
    if request.user.is_authenticated and request.user.is_doctor:
        doctor = Doctor_Information.objects.get(user=request.user)
        tests = Test_Information.objects.all
        context = {'doctor': doctor, 'tests': tests}
        return render(request, 'doctor-test-list.html', context)
    
    elif request.user.is_authenticated and request.user.is_patient:
        patient = Patient.objects.get(user=request.user)
        tests = Test_Information.objects.all
        context = {'patient': patient, 'tests': tests}
        return render(request, 'doctor-test-list.html', context)
        
    else:
        logout(request)
        messages.info(request, 'Not Authorized')
        return render(request, 'login.html')


@login_required(login_url="login")
def doctor_view_prescription(request, pk):
    if request.user.is_authenticated and request.user.is_doctor:
        doctor = Doctor_Information.objects.get(user=request.user)

        try:
            prescriptions = Prescription.objects.get(prescription_id=pk)
        except Prescription.DoesNotExist:
            messages.error(request, 'Prescription does not exist.')
            return redirect('doctor-dashboard')
        
        if prescriptions.doctor == doctor:
                medicines = Prescription_medicine.objects.filter(prescription=prescriptions)
                tests = Prescription_test.objects.filter(prescription=prescriptions)
                context = {'prescription': prescriptions, 'medicines': medicines, 'tests': tests, 'doctor': doctor}
                return render(request, 'doctor-view-prescription.html', context)
        else:
            record_request = DoctorRecordRequest.objects.filter(doctor=doctor, patient=prescriptions.patient).order_by('-request_date').first()

            if record_request is None:
                messages.error(request, 'No record request found')
                return redirect('doctor-dashboard')
            
            if record_request.status == 'A':
                    medicines = Prescription_medicine.objects.filter(prescription=prescriptions)
                    tests = Prescription_test.objects.filter(prescription=prescriptions)
                    context = {'prescription': prescriptions, 'medicines': medicines, 'tests': tests, 'doctor': doctor}
                    return render(request, 'doctor-view-prescription.html', context)
            else:
                messages.info(request, 'Not Authorized')
                return redirect('doctor-dashboard')
    else:
        logout(request)
        messages.info(request, 'Not Authorized')
        return render(request, 'login.html')

@login_required(login_url="login")
def doctor_view_medical(request, pk):
    if request.user.is_authenticated and request.user.is_doctor:
        doctor = Doctor_Information.objects.get(user=request.user)

        try:
            record = MedicalRecord.objects.get(medical_id=pk)
        except MedicalRecord.DoesNotExist:
            messages.error(request, 'Medical Record does not exist.')
            return redirect('doctor-dashboard')
        
        if record.doctor == doctor:
                context = {'record': record, 'doctor': doctor}
                return render(request, 'doctor-view-record.html', context)
        else:
            record_request = DoctorRecordRequest.objects.filter(doctor=doctor, patient=record.patient).order_by('-request_date').first()

            if record_request is None:
                messages.error(request, 'No record request found')
                return redirect('doctor-dashboard')
            
            if record_request.status == 'A':
                    context = {'record': record, 'doctor': doctor}
                    return render(request, 'doctor-view-record.html', context)
            else:
                messages.info(request, 'Not Authorized')
                return redirect('doctor-dashboard')
            
    else:
        logout(request)
        messages.info(request, 'Not Authorized')
        return render(request, 'login.html')

@login_required(login_url="login")
def doctor_view_history(request, pk):
    if request.user.is_authenticated and request.user.is_doctor:
        doctor = Doctor_Information.objects.get(user=request.user)
        healthcenter = Healthcenter_Information.objects.get(healthcenter_id=doctor.health_center.healthcenter_id)
        patient = Patient.objects.get(patient_id=pk)

        try:
            record = MedicalRecord.objects.filter(healthcenter=healthcenter, patient=patient)
        except MedicalRecord.DoesNotExist:
            messages.error(request, 'Patient medical history does not exist.')
            return redirect('doctor-dashboard')
        
        context = {'record': record, 'doctor': doctor, 'patient': patient}
        return render(request, 'doctor-view-history.html', context)        
    else:
        logout(request)
        messages.info(request, 'Not Authorized')
        return render(request, 'login.html')
    
@login_required(login_url="login")
def doctor_view_other_record(request, pk):
    if request.user.is_doctor:
        doctor = Doctor_Information.objects.get(user=request.user)
        patient = Patient.objects.get(patient_id=pk)
        healthcenter = Healthcenter_Information.objects.get(healthcenter_id=patient.health_center.healthcenter_id)
        record_request = DoctorRecordRequest.objects.filter(doctor=doctor, patient=patient).order_by('-request_date').first()

        if record_request is None:
            messages.error(request, 'No record request found')
            return redirect('doctor-dashboard')
        elif record_request.status != 'A':
            messages.error(request, 'Your record request has not been approved')
            return redirect('doctor-dashboard')

        prescription = Prescription.objects.filter(healthcenter=healthcenter).filter(patient=patient)
        record = MedicalRecord.objects.filter(healthcenter=healthcenter).filter(patient=patient) 

        context = {'patient': patient, 'doctor': doctor, 'healthcenter':healthcenter,'record': record, 'prescription': prescription}
        return render(request, 'patient-records.html', context)
    else:
        messages.error(request, 'Not authorized')
        redirect('logout')



@csrf_exempt
@receiver(user_logged_in)
def got_online(sender, user, request, **kwargs):    
    user.login_status = True
    user.save()

@csrf_exempt
@receiver(user_logged_out)
def got_offline(sender, user, request, **kwargs):   
    user.login_status = False
    user.save()

@transaction.atomic
@login_required(login_url="login")
def doctor_review(request, pk):
    if request.user.is_doctor:
        # doctor = Doctor_Information.objects.get(user_id=pk)
        doctor = Doctor_Information.objects.get(user=request.user)
            
        doctor_review = Doctor_review.objects.filter(doctor=doctor)
        
        context = {'doctor': doctor, 'doctor_review': doctor_review}  
        return render(request, 'doctor-profile.html', context)

    if request.user.is_patient:
        patient = Patient.objects.get(user=request.user)
        if(patient.is_verified):
            doctor = Doctor_Information.objects.get(doctor_id=pk)

            if request.method == 'POST':
                title = request.POST.get('title')
                message = request.POST.get('message')

                if not title or not message:
                    messages.error(request, 'Please fill in the fields for review.')
                    return redirect('doctor-profile', pk)
                
                doctor_review = Doctor_review(doctor=doctor, patient=patient, title=title, message=message)
                doctor_review.save()

            context = {'doctor': doctor, 'patient': patient, 'doctor_review': doctor_review}  
            return render(request, 'doctor-profile.html', context)
        else:
            messages.error(request, 'Please get verified first.')
            redirect('patient-verification')

    else:
        messages.error(request, 'Not authorized')
        redirect('logout')
 
 
   
 


