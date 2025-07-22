import email
from multiprocessing import context
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
# from django.contrib.auth.models import User
# from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm, PatientForm, PasswordResetForm
from healthcenter.models import Healthcenter_Information, User, Patient, MedicalRecordRequest
from healthcenter_admin.models import service, Test_Information,Admin_Information
from django.views.decorators.cache import cache_control
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime
import datetime
import json
import re
from django.utils import timezone
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.template.loader import get_template
from xhtml2pdf import pisa
from .utils import searchDoctors, searchHealthcenters, searchHealthcenterDoctors, paginateHealthcenters
from .models import Patient, User, VerificationRequest
from doctor.models import Doctor_Information, Appointment, Walkin,Report, Specimen, Test, Prescription, Prescription_medicine, Prescription_test, MedicalRecord, DoctorRecordRequest,Vaccination, Immunization, Waitlist
from doctor.views import reschedule
from django.db.models import Q, Count
from io import BytesIO
from urllib import response
from django.core.mail import BadHeaderError, send_mail
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from datetime import datetime, timedelta
from itertools import product
from PIL import Image, UnidentifiedImageError
from verify_email.email_handler import send_verification_email
from django.core.exceptions import ValidationError
from django.db import transaction
from notifications.signals import notify
from notifications.models import Notification

# Create your views here.
@login_required(login_url="login")
def get_waitlist_count(request):
    date = request.GET.get('date')
    time = request.GET.get('time')
    patient = request.user.patient
    healthcenter = request.user.patient.health_center

    count = Waitlist.objects.filter(desired_date=date, desired_time=time).count()

    # Check if the current user is in the waitlist
    user_in_waitlist = Waitlist.objects.filter(healthcenter=healthcenter, desired_date=date, desired_time=time, patient=patient).exists()

    return JsonResponse({'count': count, 'user_in_waitlist': user_in_waitlist})

@login_required(login_url="login")
def get_appointments_data(request, pk):
    healthcenter = Healthcenter_Information.objects.get(healthcenter_id=pk)
    date_filter = request.GET.get('date')
    times = ['8:00 am - 9:00 am', '10:00 am - 11:00 am', '1:00 pm - 2:00 pm', '3:00 pm - 4:00 pm']
    if date_filter:
        appointments = Appointment.objects.filter(date=date_filter, healthcenter=healthcenter).values('date', 'time').annotate(total=Count('id'))
    else:
        appointments = Appointment.objects.filter(healthcenter=healthcenter).values('date', 'time').annotate(total=Count('id'))

    # Create a dictionary with date and time as key and total appointments as value
    appointment_dict = {(appointment['date'], appointment['time']): appointment['total'] for appointment in appointments}

    # Get the date range for your calendar
    start_date = datetime.today().date()
    end_date = start_date + timedelta(days=60)  # Adjust the number of days as needed

    date_range = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]

    # Get all date and time combinations
    date_time_combinations = list(product(date_range, times))

    # Fill in the dates with no appointments
    for dt in date_time_combinations:
        if dt not in appointment_dict:
            appointment_dict[dt] = 0

    # Convert the dictionary to a list of dictionaries
    appointment_list = [{'date': k[0], 'time': k[1], 'total': v} for k, v in appointment_dict.items()]

    return JsonResponse(appointment_list, safe=False)

@transaction.atomic
@login_required(login_url="login")
def cancel_appointment(request, pk):
    appointment = Appointment.objects.get(id=pk)
    patient = appointment.patient
    appointment_patient = Patient.objects.get(user=request.user)
    if appointment_patient == patient:
        appointment_time_str = appointment.time.split('-')[0].strip()  # Get the start time of the time slot
        appointment_date_str = str(appointment.date)

        # Merge date and time into a single string and convert it to datetime
        appointment_datetime_str = f"{appointment_date_str} {appointment_time_str}"
        appointment_datetime = datetime.strptime(appointment_datetime_str, "%Y-%m-%d %I:%M %p")

        # Get current datetime
        now = datetime.now()

        # Allow cancellation if the appointment is at least 15 minutes away
        if now <= appointment_datetime - timedelta(minutes=15):
            appointment.appointment_status = 'cancelled'
            appointment.save()

            # Increment the patient's cancellations count
            patient.cancellations += 1
            patient.save()

            # Delete the old notification
            notifications = Notification.objects.filter(recipient=patient.user)
            for notification in notifications:
                notification_data = json.loads(notification.data)
                if 'appointment' in notification_data and notification_data['appointment'] == appointment.id:
                    # If it matches, delete the notification
                    notification.delete()

            # Create a new notification for cancelled appointment
            notify.send(patient.health_center, recipient=patient.user, verb='Appointment Cancelled!', 
                        description=f'Your appointment on {appointment.date} at {appointment.time} has been cancelled.', 
                        redirect=f'/patient-dashboard/', icon='calendar')

            #fill up the spot
            reschedule(appointment)

            messages.error(request, 'Your appointment has been cancelled.')
            return redirect('patient-dashboard')
        else:
            messages.error(request, 'Too late to cancel appointment. Please contact the healthcare facility directly.')
            return redirect('patient-dashboard')
    else:
        messages.error(request, 'Something went wrong. Please try again.')
        return redirect('patient-dashboard')

@transaction.atomic
@login_required(login_url="login")
def confirm_appointment(request, pk):
    try:
        appointment = Appointment.objects.get(id=pk)
        appointment_patient = Patient.objects.get(user=request.user)
        patient = appointment.patient
        if appointment_patient == patient:
            if request.method == 'POST':
                if 'confirm' in request.POST:
                    # User has confirmed the appointment
                    appointment.confirmed = True
                    appointment.save()

                    # Delete the old notification
                    notifications = Notification.objects.filter(recipient=patient.user)
                    for notification in notifications:
                        notification_data = json.loads(notification.data)
                        if 'appointment' in notification_data and notification_data['appointment'] == appointment.id:
                            # If it matches, delete the notification
                            notification.delete()

                    # Create a new notification for confirmed appointment
                    notify.send(patient.health_center, recipient=patient.user, verb='Appointment Confirmed!', 
                                description=f'Your appointment on {appointment.date} at {appointment.time} has been confirmed. See you then at {appointment.healthcenter.name}!', 
                                redirect=f'/patient-dashboard/', icon='calendar')

                    messages.success(request, 'Your appointment has been confirmed. Please go to the appointment as scheduled.')
                    return redirect('patient-dashboard')
                elif 'cancel' in request.POST:
                    # User has cancelled the appointment
                    return redirect('cancel_appointment', pk=pk)
                else:
                    messages.error(request, 'Invalid confirmation. Please try again.')
                    return redirect('patient-dashboard')
        else:
            messages.error(request, 'Something went wrong. Please try again.')
            return redirect('patient-dashboard')
            
        context = {'appointment': appointment, 'patient': patient}
        return render(request, 'confirm_appointment.html', context)
    except Exception as e:
        messages.error(request, 'Invalid appointment. Please try again.')
        return redirect('patient-dashboard')

@csrf_exempt
def healthcenter_home(request):
    # .order_by('-created_at')[:6]
    healthcenters = Healthcenter_Information.objects.all()
    context = {'healthcenters': healthcenters} 
    return render(request, 'index.html', context)

def file_size(value):
    limit = 2 * 1024 * 1024
    if value.size > limit:
        raise ValidationError('File size must be less than 2MB')

@transaction.atomic
@login_required(login_url="login")
def submit_verification(request):
    if request.user.is_patient:
        patient = Patient.objects.get(user=request.user)
        if patient.is_verified == True:
            messages.error(request, 'You are already verified.')
            return redirect('patient-dashboard')

        # Check if a verification request already exists for the patient
        try:
            existing_request = VerificationRequest.objects.get(patient=patient)
            if existing_request.status == VerificationRequest.PENDING:
                messages.error(request, 'You have already submitted a verification request.')
                return redirect('patient-dashboard')
        except VerificationRequest.DoesNotExist:
            existing_request = None

        if request.method == 'POST':
            proof_of_billing = request.FILES['proof_of_billing']
            id_proof_front = request.FILES['id_proof_front']
            id_proof_back = request.FILES['id_proof_back']        
            selfie_with_id = request.FILES['selfie_with_id']       

            for file in [proof_of_billing, id_proof_front, id_proof_back, selfie_with_id]:
                file_size(file)

            if existing_request and existing_request.status == VerificationRequest.REJECTED:
                try:
                    existing_request_again = VerificationRequest.objects.get(patient=patient)
                    # If a verification request was previously rejected, update it
                    existing_request_again.proof_of_billing = proof_of_billing
                    existing_request_again.id_proof_front = id_proof_front
                    existing_request_again.id_proof_back = id_proof_back
                    existing_request_again.selfie_with_id = selfie_with_id
                    existing_request_again.status = VerificationRequest.PENDING
                    existing_request_again.request_date = datetime.today()
                    existing_request_again.save()
                except VerificationRequest.DoesNotExist:
                    existing_request = None

                    messages.error(request, 'Somethin went wrong! Please try again.')
                    return redirect('patient-dashboard')

                # Create a new notification for verification
                notify.send(patient.health_center, recipient=patient.user, verb='Verification Request Submitted!', 
                            description=f'Your verification request for {patient.health_center.name} has been submitted and is now under review. Thank you for your patience.', 
                            redirect=f'/patient-dashboard/', icon='checkmark-circle-outline')  
                
                messages.success(request, 'Your verification request has been resubmitted successfully and is now under review. Thank you for your patience.')
                return redirect('patient-dashboard')
            else:
                # Create new VerificationRequest
                verification_request = VerificationRequest(
                    patient=patient,
                    proof_of_billing=proof_of_billing,
                    id_proof_front=id_proof_front,
                    id_proof_back=id_proof_back,
                    selfie_with_id=selfie_with_id,
                    status=VerificationRequest.PENDING,
                    request_date= datetime.today()
                )
                verification_request.save()

                # Create a new notification for verification
                notify.send(patient.health_center, recipient=patient.user, verb='Verification Request Submitted!', 
                            description=f'Your verification request for {patient.health_center.name} has been submitted and is now under review. Thank you for your patience.', 
                            redirect=f'/patient-dashboard/', icon='checkmark-circle-outline')   

                messages.success(request, 'Verification request submitted successfully and is now under review. Thank you for your patience.')
                return redirect('patient-dashboard')

    else:
        messages.error(request, 'No permission to view this page')
        return redirect('logout')

    return render(request, 'patient-verification.html', {'patient': patient})

@transaction.atomic
@login_required(login_url="login")
def change_password(request, pk):
    patient = Patient.objects.get(user_id=pk)
    context = {"patient": patient}
    if request.method == "POST":
        prev_password = request.POST.get("prev_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if prev_password and new_password and confirm_password:
            # Check if the old password is correct
            if not request.user.check_password(prev_password):
                messages.error(request, "Current password is incorrect")
                return redirect("change-password", pk)

            # Check if the new password and confirm password match
            if new_password == confirm_password:
                request.user.set_password(new_password)
                request.user.save()
                messages.success(request, "Password Changed Successfully")
                return redirect("patient-dashboard")
            else:
                messages.error(request, "New Password and Confirm Password do not match")
                return redirect("change-password", pk)
        else:
            messages.error(request, "Please fill in all the fields")
            return redirect("change-password", pk)

    return render(request, "change-password.html", context)

def appointments(request):
    return render(request, 'appointments.html')

def edit_prescription(request):
    return render(request, 'edit-prescription.html')

# def forgot_password(request):
#     return render(request, 'forgot-password.html')

def resetPassword(request):
    form = PasswordResetForm()

    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user_email = user.email
       
            subject = "Password Reset Requested"
            # email_template_name = "password_reset_email.txt"
            values = {
				"email":user.email,
				'domain':'mediqs-production.up.railway.app',
				'site_name': 'Mediqs',
				"uid": urlsafe_base64_encode(force_bytes(user.pk)),
				"user": user,
				'token': default_token_generator.make_token(user),
				'protocol': 'https',
			}

            html_message = render_to_string('mail_template.html', {'values': values})
            plain_message = strip_tags(html_message)
            
            try:
                send_mail(subject, plain_message, 'admin@example.com',  [user.email], html_message=html_message, fail_silently=False)
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect ("password_reset_done")

    context = {'form': form}
    return render(request, 'reset_password.html', context)
    
    
def privacy_policy(request):
    return render(request, 'privacy-policy.html')

def about_us(request):
    return render(request, 'about-us.html')

@login_required(login_url="login")
def chat(request, pk):
    patient = Patient.objects.get(user_id=pk)
    doctors = Doctor_Information.objects.all()

    context = {'patient': patient, 'doctors': doctors}
    return render(request, 'chat.html', context)

@login_required(login_url="login")
def chat_doctor(request):
    if request.user.is_doctor:
        doctor = Doctor_Information.objects.get(user=request.user)
        patients = Patient.objects.all()
        
    context = {'patients': patients, 'doctor': doctor}
    return render(request, 'chat-doctor.html', context)

@csrf_exempt     
@login_required(login_url="login")
def inventory(request):
    return render(request, 'Pharmacy/shop.html')

def login_user(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        if password.strip() == "" or username.strip() == "":
            messages.error(request, 'Please fill up all the required fields.')
            return render(request, 'login.html')

        user = authenticate(username=username, password=password)

        if user is not None:
            user = User.objects.get(username=username)
            if not user.is_active:
                messages.error(request, 'This account is not active. Please check your email to activate your account.')
                return render(request, 'login.html')
            
            if user.is_patient:
                login(request, user)
                messages.success(request, 'User Logged in Successfully')
                return redirect('patient-dashboard')
            elif user.is_doctor:
                login(request, user)
                messages.success(request, 'User Logged in Successfully')
                return redirect('doctor-dashboard')
            elif user.is_healthcenter_admin:
                login(request, user)
                messages.success(request, 'User Logged in Successfully')
                return redirect('admin-dashboard')
            elif user.is_inventorymanager:
                login(request, user)
                messages.success(request, 'User Logged in Successfully')
                return redirect('inventorymanager-dashboard')
            elif user.is_staff:
                login(request, user)
                messages.success(request, 'User Logged in Successfully')
                return redirect('staff-dashboard')
            else:
                messages.error(request, 'Invalid credentials, contact an admin for support.')
                return redirect('logout')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'login.html')

#roles
@csrf_exempt
def roles_new(request):
     return render(request, 'roles-new.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logoutUser(request):
    if request.user.is_authenticated:
        if request.user.is_patient:
            logout(request)
            messages.error(request, 'User Logged out')
            return redirect('login')
        elif request.user.is_doctor:
            user = User.objects.get(id=request.user.id)

            user.login_status == "offline"
            user.save()
            logout(request)
            
            messages.error(request, 'User Logged out')
            return render(request,'login.html')
        elif request.user.is_healthcenter_admin:
            logout(request)
            messages.error(request, 'User Logged out')
            return redirect('login')
        elif request.user.is_inventorymanager:
            logout(request)
            messages.error(request, 'User Logged out')
            return redirect('login')
        elif request.user.is_staff:
            logout(request)
            messages.error(request, 'User Logged out')
            return redirect('login')
        else:
            logout(request)
            messages.error(request, 'You are already logged out')
            return redirect('login')
    else:
        messages.error(request, 'You are already logged out')
        return redirect('login')

def patient_register(request):
    page = 'patient-register'
    user_form = CustomUserCreationForm()
    patient_form = PatientForm()

    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        patient_form = PatientForm(request.POST)
        terms = request.POST.get('check')  # Get the value of the checkbox

        if terms:  # If the checkbox is checked
            if user_form.is_valid() and patient_form.is_valid():
                username = user_form.cleaned_data['username']
                email = user_form.cleaned_data['email']

                # Check if a user with the same username or email already exists
                if User.objects.filter(username=username).exists():
                    error_message = "A user with this username already exists."
                    messages.error(request, error_message)
                    return render(request, 'patient-register.html', {'page': page, 'user_form': user_form, 'patient_form': patient_form})
                elif Patient.objects.filter(email=email).exists():
                    error_message = "A patient with this email already exists."
                    messages.error(request, error_message)
                    return render(request, 'patient-register.html', {'page': page, 'user_form': user_form, 'patient_form': patient_form})
                else:
                    try:
                        user = user_form.save()
                        patient, created = Patient.objects.get_or_create(user=user)
                        patient.name = patient_form.cleaned_data['name']
                        patient.age = patient_form.cleaned_data['age']
                        patient.dob = patient_form.cleaned_data['dob']
                        patient.gender = patient_form.cleaned_data['gender']
                        patient.blood_group = patient_form.cleaned_data['blood_group']
                        patient.phone_number = patient_form.cleaned_data['phone_number']
                        patient.address = patient_form.cleaned_data['address']
                        patient.terms_confirmed = True

                        patient.save()
                    except Exception as e:
                        messages.error(request, e)
                        return render(request, 'patient-register.html', {'page': page, 'user_form': user_form, 'patient_form': patient_form})
                    
                    inactive_user = send_verification_email(request, user_form)

                    if inactive_user is None:
                        messages.error(request, 'Failed to send the verification email.')
                        return render(request, 'patient-register.html', {'page': page, 'user_form': user_form, 'patient_form': patient_form})
                    
                    messages.success(request, 'Patient account was created! Please check your email for verification.')
                    return redirect('login')
            else:
                # Form is not valid, display error messages
                for field_errors in user_form.errors.values():
                    for error in field_errors:
                        messages.error(request, error)
                for field_errors in patient_form.errors.values():
                    for error in field_errors:
                        messages.error(request, error)
        else:
            messages.error(request, 'Please check the terms and condition to register.')
            return redirect('patient-register')
    
    context = {'page': page, 'user_form': user_form, 'patient_form': patient_form}
    return render(request, 'patient-register.html', context)

@login_required(login_url="login")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def patient_dashboard(request): 
    if request.user.is_patient:
        patient = Patient.objects.get(user=request.user)
        prescription = Prescription.objects.filter(patient=patient).order_by('-prescription_id')
        walkin = Walkin.objects.filter(patient=patient).order_by('-date')
        appointments = Appointment.objects.filter(patient=patient).filter(Q(appointment_status='pending') | Q(appointment_status='confirmed')).order_by('-date')
        now = timezone.now().date()

        # Calculate time difference in minutes for each appointment
        for appointment in appointments:
            appointment.time_diff = (appointment.date - now) / timedelta(minutes=1)

        context = {'patient': patient, 'appointments': appointments,'prescription':prescription, 'walkin': walkin, 'now': now}
    else:
        return redirect('logout')
        
    return render(request, 'patient-dashboard.html', context)

@login_required(login_url="login")
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def patient_record(request): 
    if request.user.is_patient:
        patient = Patient.objects.get(user=request.user)
        record = MedicalRecord.objects.filter(patient=patient)
        vaccination = Vaccination.objects.filter(patient=patient)
        immunization = Immunization.objects.filter(patient=patient)

        context = {'patient': patient, 'record':record, 'vaccinations': vaccination, 'immunizations': immunization}
    else:
        return redirect('logout')
        
    return render(request, 'patient-record.html', context)

# def profile_settings(request):
#     if request.user.is_patient:
#         # patient = Patient.objects.get(user_id=pk)
#         patient = Patient.objects.get(user=request.user)
#         form = PatientForm(instance=patient)  

#         if request.method == 'POST':
#             form = PatientForm(request.POST, request.FILES,instance=patient)  
#             if form.is_valid():
#                 form.save()
#                 return redirect('patient-dashboard')
#             else:
#                 form = PatientForm()
#     else:
#         redirect('logout')

#     context = {'patient': patient, 'form': form}
#     return render(request, 'profile-settings.html', context)

def clean_name(name):
    errors = []
    if not name:
        errors.append('Please provide a name.')
    
    if re.search(r'[^A-Za-z.\s]', name):
        errors.append('Name should only contain letters.')
    
    if len(name) > 70:
        errors.append('Name should not exceed 70 characters.')

    if errors:
        raise ValidationError(errors)
def clean_age(age):
    errors = []
    if not age or int(age) < 0:
        errors.append('Please provide a valid age.')
    if not str(age).isnumeric():
        errors.append('Age should only contain numeric characters.')
    if errors:
        raise ValidationError(errors)

def clean_dob(dob):
    errors = []
    if not dob:
        errors.append('Please provide your date of birth.')
    
    dob_date = datetime.strptime(dob, '%Y-%m-%d').date()
    today_date = datetime.today().date()
    
    if dob_date > today_date:
        errors.append('Please provide a valid date of birth.')
    
    if errors:
        raise ValidationError(errors)

def clean_gender(gender):
    errors = []
    if not gender:
        errors.append('Please select a gender.')
    if errors:
        raise ValidationError(errors)
    

def clean_phone_number(phone_number):
    errors = []
    if not phone_number:
        errors.append('Please provide a phone number.')
    
    if not re.match(r'^(\+639|0)\d{10}$', phone_number):
        errors.append('Invalid phone number format: Must start with +639 or 0 and be followed by a 10-digit number')
    if errors:
        raise ValidationError(errors)

def clean_address(address):
    errors = []
    if not address:
        errors.append('Please provide an address.')
    if errors:
        raise ValidationError(errors)

def clean_father_name(father_name):
    errors = []
    if not father_name:
        errors.append('Please provide your father\'s name.')
    
    if re.search(r'[^A-Za-z\s]', father_name):
        errors.append('Father\'s name should only contain letters and spaces.')
    
    if len(father_name) > 70:
        errors.append('Father\'s name should not exceed 70 characters.')
    
    if errors:
        raise ValidationError(errors)

def clean_mother_name(mother_name):
    errors = []
    if not mother_name:
        errors.append('Please provide your mother\'s name.')
    
    if re.search(r'[^A-Za-z\s]', mother_name):
        errors.append('Mother\'s name should only contain letters and spaces.')
    
    if len(mother_name) > 70:
        errors.append('Mother\'s name should not exceed 70 characters.')
    
    if errors:
        raise ValidationError(errors)

def clean_fam_num(fam_num):
    errors = []
    if not fam_num:
        errors.append('Please provide a valid family number.')
    try:
        fam_num = int(fam_num)
        if fam_num < 0:
            errors.append('Please provide a valid family number.')
    except ValueError:
        errors.append('Please provide a valid family number.')
    if errors:
        raise ValidationError(errors)

def clean_barangay_num(barangay_num):
    errors = []
    if not barangay_num:
        errors.append('Please provide a valid barangay number.')
    try:
        barangay_num = int(barangay_num)
        if barangay_num < 0:
            errors.append('Please provide a valid barangay number.')
    except ValueError:
        errors.append('Please provide a valid barangay number.')
    if errors:
        raise ValidationError(errors)

def clean_birth_weight(birth_weight):
    errors = []
    if not birth_weight:
        errors.append('Please provide a valid birth weight.')
    try:
        birth_weight = int(birth_weight)
        if birth_weight < 0:
            errors.append('Please provide a valid birth weight.')
    except ValueError:
        errors.append('Please provide a valid birth weight.')
    if errors:
        raise ValidationError(errors)

def clean_birth_height(birth_height):
    errors = []
    if not birth_height:
        errors.append('Please provide a valid birth height.')
    try:
        birth_height = int(birth_height)
        if birth_height < 0:
            errors.append('Please provide a valid birth height.')
    except ValueError:
        errors.append('Please provide a valid birth height.')
    if errors:
        raise ValidationError(errors)

def clean_place_birth(place_birth):
    errors = []
    if not place_birth:
        errors.append('Please provide your place of birth.')
    if errors:
        raise ValidationError(errors)

@login_required(login_url="login")
def profile_settings(request):
    if request.user.is_patient:
        # patient = Patient.objects.get(user_id=pk)
        patient = Patient.objects.get(user=request.user)
        old_featured_image = patient.featured_image
        
        if request.method == 'GET':
            context = {'patient': patient}
            return render(request, 'profile-settings.html', context)
        elif request.method == 'POST':
            if 'featured_image' in request.FILES:
                featured_image = request.FILES['featured_image']

                # Verify that the uploaded file is an image
                try:
                    img = Image.open(featured_image)
                except UnidentifiedImageError:
                    messages.error(request, 'Invalid file type. Please upload an image.')
                    return redirect('profile-settings')

                # Reset the file pointer to the beginning of the file
                featured_image.seek(0)

            else:
                featured_image = old_featured_image
                
            name = request.POST.get('name')
            father_name=request.POST.get('father_name')
            dob = request.POST.get('dob')
            age = request.POST.get('age')
            gender = request.POST.get('gender')
            blood_group = request.POST.get('blood_group')
            phone_number = request.POST.get('phone_number')
            address = request.POST.get('address')
            nid = request.POST.get('nid')
            history = request.POST.get('history')
            mother_name = request.POST.get('mother_name')
            fam_num = request.POST.get('fam_num')
            barangay_num = request.POST.get('barangay_num')
            birth_weight = request.POST.get('birth_weight')
            birth_height = request.POST.get('birth_height')
            place_birth = request.POST.get('place_birth')
            try:
                if name != patient.name:
                    clean_name(name)
                    patient.name = name

                if age != patient.age:
                    clean_age(age)
                    patient.age = age

                if gender != patient.gender:
                    clean_gender(gender)
                    patient.gender = gender

                if phone_number != patient.phone_number:
                    clean_phone_number(phone_number)
                    patient.phone_number = phone_number

                if father_name != patient.father_name:
                    clean_father_name(father_name)
                    patient.father_name = father_name

                if address != patient.address:
                    clean_address(address)
                    patient.address = address

                if blood_group != patient.blood_group:
                    patient.blood_group = blood_group

                if history != patient.history:
                    patient.history = history

                if dob != patient.dob:
                    clean_dob(dob)
                    patient.dob = dob

                if nid != patient.nid:
                    patient.nid = nid

                if featured_image != patient.featured_image:
                    patient.featured_image = featured_image

                if mother_name != patient.mother_name:
                    clean_mother_name(mother_name)
                    patient.mother_name = mother_name

                if fam_num != patient.fam_num:
                    clean_fam_num(fam_num)
                    patient.fam_num = fam_num

                if barangay_num != patient.barangay_num:
                    clean_barangay_num(barangay_num)
                    patient.barangay_num = barangay_num

                if birth_weight != patient.birth_weight:
                    clean_birth_weight(birth_weight)
                    patient.birth_weight = birth_weight

                if birth_height != patient.birth_height:
                    clean_birth_height(birth_height)
                    patient.birth_height = birth_height

                if place_birth != patient.place_birth:
                    clean_place_birth(place_birth)
                    patient.place_birth = place_birth
            
                patient.save()
                
                messages.success(request, 'Profile Settings Changed!')
                
                return redirect('profile-settings')
            
            except ValidationError as e:
                errors = e.args[0]
                error_msg = ' '.join(errors)
                messages.error(request, error_msg)
                return redirect('profile-settings')
    else:
        redirect('logout')  
        
@csrf_exempt
@login_required(login_url="login")
def search(request):
    if request.user.is_authenticated and request.user.is_patient:
        # patient = Patient.objects.get(user_id=pk)
        patient = Patient.objects.get(user=request.user)
        doctors = Doctor_Information.objects.all()
        
        doctors, search_query = searchDoctors(request)
        context = {'patient': patient, 'doctors': doctors, 'search_query': search_query}
        return render(request, 'search.html', context)
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'login.html')    

@csrf_exempt
@login_required(login_url="login")
def multiple_healthcenter(request):
    
    if request.user.is_authenticated: 
        
        if request.user.is_patient:
            # patient = Patient.objects.get(user_id=pk)
            patient = Patient.objects.get(user=request.user)
            doctors = Doctor_Information.objects.all()
            healthcenters = Healthcenter_Information.objects.order_by('name').distinct('name')
            healthcenters, search_query = searchHealthcenters(request)
            
            # PAGINATION ADDED TO MULTIPLE HOSPITALS
            #custom_range, healthcenters = paginateHealthcenters(request, healthcenters, 3)
        
            context = {'patient': patient, 'doctors': doctors, 'healthcenters': healthcenters, 'search_query': search_query,}
            return render(request, 'multiple-healthcenter.html', context)
        
        elif request.user.is_doctor:
            doctor = Doctor_Information.objects.get(user=request.user)
            healthcenters = Healthcenter_Information.objects.all()
            
            healthcenters, search_query = searchHealthcenters(request)
            
            context = {'doctor': doctor, 'healthcenters': healthcenters, 'search_query': search_query,}
            return render(request, 'multiple-healthcenter.html', context)
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'login.html') 
    
@csrf_exempt    
@login_required(login_url="login")
def healthcenter_profile(request, pk):
    
    if request.user.is_authenticated: 
        
        if request.user.is_patient:
            patient = Patient.objects.get(user=request.user)
            doctors = Doctor_Information.objects.all()
            healthcenters = Healthcenter_Information.objects.get(healthcenter_id=pk)
        
            services = service.objects.filter(healthcenter=healthcenters)
            
            # department_list = None
            # for d in departments:
            #     vald = d.healthcenter_department_name
            #     vald = re.sub("'", "", vald)
            #     vald = vald.replace("[", "")
            #     vald = vald.replace("]", "")
            #     vald = vald.replace(",", "")
            #     department_list = vald.split()
            
            context = {'patient': patient, 'doctors': doctors, 'healthcenters': healthcenters, 'services': services}
            return render(request, 'healthcenter-profile.html', context)
        
        elif request.user.is_doctor:
           
            doctor = Doctor_Information.objects.get(user=request.user)
            healthcenters = Healthcenter_Information.objects.get(healthcenter_id=pk)
            appointment_patients = set(Appointment.objects.filter(healthcenter=healthcenters, appointment_status='confirmed').values_list('patient', flat=True))
            walkin_patients = set(Walkin.objects.filter(healthcenter=healthcenters).values_list('patient', flat=True))
            unique_patients = appointment_patients.union(walkin_patients)
            patients = Patient.objects.filter(patient_id__in=unique_patients)

            services = service.objects.filter(healthcenter=healthcenters)

            record_requests = DoctorRecordRequest.objects.filter(doctor=doctor).order_by('-request_date').first()
            
            context = {'doctor': doctor, 'healthcenters': healthcenters, 'services': services, 'patients': patients, 'record_requests': record_requests}
            return render(request, 'healthcenter-profile.html', context)
        
        elif request.user.is_healthcenter_admin:
            # Code for admin view
            
            admin = Admin_Information.objects.get(user=request.user)
            healthcenters = Healthcenter_Information.objects.get(healthcenter_id=pk)
            services = service.objects.filter(healthcenter=healthcenters)
            context = {'admin':admin,'healthcenters': healthcenters, 'services': services}
            return render(request, 'admin-healthcenter-profile.html', context)

    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'login.html') 

@login_required(login_url="login")
def admin_healthcenter_profile(request, pk):
    
    if request.user.is_authenticated: 
        
        if request.user.is_healthcenter_admin:
            # Code for admin view
            
            admin = Admin_Information.objects.get(user=request.user)
            healthcenters = Healthcenter_Information.objects.get(healthcenter_id=pk)
            services = service.objects.filter(healthcenter=healthcenters)
            context = {'admin':admin,'healthcenters': healthcenters, 'services': services}
            return render(request, 'admin-healthcenter-profile.html', context)

    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'login.html') 
    
    
def data_table(request):
    return render(request, 'data-table.html')

@login_required(login_url="login")
def healthcenter_doctor_list(request, pk):
    if request.user.is_authenticated and request.user.is_patient:
        # patient = Patient.objects.get(user_id=pk)
        patient = Patient.objects.get(user=request.user)
        doctors = Doctor_Information.objects.filter(health_center=pk)
        
        doctors, search_query = searchHealthcenterDoctors(request, pk)
        
        context = {'patient': patient, 'doctors': doctors, 'search_query': search_query, 'pk_id': pk}
        return render(request, 'healthcenter-doctor-list.html', context)

    elif request.user.is_authenticated and request.user.is_doctor:
        # patient = Patient.objects.get(user_id=pk)
        
        doctor = Doctor_Information.objects.get(user=request.user)
        
        doctors = Doctor_Information.objects.filter(health_center=pk)
        doctors, search_query = searchHealthcenterDoctors(request, pk)
        
        context = {'doctor':doctor, 'doctors': doctors, 'search_query': search_query, 'pk_id': pk}
        return render(request, 'healthcenter-doctor-list.html', context)
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'login.html')   
    
    
def testing(request):
    # healthcenters = Healthcenter_Information.objects.get(healthcenter_id=1)
    test = "test"
    context = {'test': test}
    return render(request, 'testing.html', context)

@login_required(login_url="login")
def view_medical(request, pk):
    if request.user.is_patient:
        patient = Patient.objects.get(user=request.user)

        try:
            records = MedicalRecord.objects.get(medical_id=pk)
        except MedicalRecord.DoesNotExist:
            messages.error(request, 'Medical Record does not exist.')
            return redirect('patient-dashboard')

        try:
            existing_request = MedicalRecordRequest.objects.get(patient=patient, record=records, status='A')
        except MedicalRecordRequest.DoesNotExist:
            messages.info(request, 'Not Authorized')
            return redirect('patient-dashboard')

        if records.patient != patient:
            messages.info(request, 'Not Authorized')
            return redirect('patient-dashboard')

        # Check if there is an approved request from this patient for this record
        if existing_request and existing_request.status != 'A':
            messages.info(request, 'You need to request to view this medical record.')
            return redirect('patient-dashboard')

        # current_date = datetime.date.today()
        context = {'patient': patient, 'record': records}
        return render(request, 'view-medical.html', context)

    else:
        redirect('logout')

@transaction.atomic
@login_required(login_url="login")
def create_medical_record_request(request, medical_id):
    if request.user.is_patient:
        patient = Patient.objects.get(user=request.user)
        purpose_of_request = request.POST.get('purpose_of_request', None)
        supporting_documentation = request.FILES.get('supporting_documentation', None) 
        date_needed_str = request.POST.get('date_needed', None)
        date_needed = datetime.strptime(date_needed_str, '%Y-%m-%d').date() if date_needed_str else None
        
        if not purpose_of_request:
            messages.error(request, 'Purpose of request is required.')
            return redirect('patient-records')
        
        if date_needed and date_needed <= datetime.today().date():
            messages.error(request, 'Date needed must be in the future.')
            return redirect('patient-records')
        
        try:
            record = MedicalRecord.objects.get(medical_id=medical_id)
            existing_request = MedicalRecordRequest.objects.filter(patient=patient, record=record).order_by('-request_date').first()
            
            if existing_request and existing_request.status == 'P':
                messages.error(request, 'You already have a pending request.')
                return redirect('patient-records')
            elif existing_request and existing_request.status == 'A':
                messages.error(request, 'Your previous request was already approved.')
                return redirect('patient-records')
        except MedicalRecord.DoesNotExist:
            messages.error(request, 'Medical Record does not exist.')
            return redirect('patient-records')
        
        if record.patient != patient:
            messages.info(request, 'Not Authorized')
            return redirect('patient-records')
        
        # Create the request
        try:
            MedicalRecordRequest.objects.create(
                patient=patient, 
                record=record,
                purpose_of_request=purpose_of_request, 
                supporting_documentation=supporting_documentation,
                date_needed=date_needed,
                status='P'
            )
        except Exception as e:
            messages.error(request, f'Failed to create request. Error: {str(e)}')
            return redirect('patient-records')
        
        # Create a new notification for verification
        notify.send(patient.health_center, recipient=patient.user, verb='Medical Record Request Submitted!', 
                    description=f'Your medical record request has been submitted to {patient.health_center.name}.', 
                    redirect=f'/patient-records/', icon='medical-outline')   
        messages.success(request, f'Medical record request sent!')
        return redirect('patient-records')
    else:
        return redirect('logout') 

@transaction.atomic
@login_required(login_url="login")
def create_doctor_record_request(request, patient_id):
    if request.user.is_doctor:
        doctor = Doctor_Information.objects.get(user=request.user)
        purpose_of_request = request.POST.get('purpose_of_request', None)
        supporting_documentation = request.FILES.get('supporting_documentation', None) 
        date_needed_str = request.POST.get('date_needed', None)
        date_needed = datetime.strptime(date_needed_str, '%Y-%m-%d').date() if date_needed_str else None
        
        if not purpose_of_request:
            messages.error(request, 'Purpose of request is required.')
            return redirect('doctor-dashboard')
        
        if date_needed and date_needed <= datetime.today().date():
            messages.error(request, 'Date needed must be in the future.')
            return redirect('doctor-dashboard')
        
        patient = get_object_or_404(Patient, patient_id=patient_id)
        
        if doctor.health_center == patient.health_center:
            messages.error(request, 'Failed to create a request.')
            return redirect('doctor-dashboard')

        existing_request = DoctorRecordRequest.objects.filter(doctor=doctor, patient=patient).order_by('-request_date').first()
        
        if existing_request and existing_request.status == 'P':
            messages.error(request, 'You already have a pending request.')
            return redirect('doctor-dashboard')
        elif existing_request and existing_request.status == 'A':
            messages.error(request, 'Your previous request was already approved.')
            return redirect('doctor-dashboard')
        
        # Create the request
        try:
            DoctorRecordRequest.objects.create(
                doctor=doctor, 
                patient=patient,
                purpose_of_request=purpose_of_request, 
                supporting_documentation=supporting_documentation,
                date_needed=date_needed,
                status='P'
            )
        except Exception as e:
            messages.error(request, f'Failed to create request. Error: {str(e)}')
            return redirect('doctor-dashboard')
        
        # Create a new notification for request
        notify.send(patient.health_center, recipient=doctor.user, verb='Record Request has been Submitted!', 
                    description=f'Your record request has been submitted to {patient.health_center.name}.', 
                    redirect=f'/doctor/doctor-dashboard/', icon='medical-outline') 
        messages.success(request, f'Medical record request sent!')
        return redirect('doctor-dashboard')
    else:
        return redirect('logout') 

@login_required(login_url="login")
def prescription_view(request,pk):
      if request.user.is_patient:
        patient = Patient.objects.get(user=request.user)
        
        try:
            prescriptions = Prescription.objects.get(prescription_id=pk)
        except Prescription.DoesNotExist:
            messages.error(request, 'Prescription does not exist.')
            return redirect('patient-dashboard')

        if prescriptions.patient != patient:
            messages.info(request, 'Not Authorized')
            return redirect('patient-dashboard')
        
        prescription_medicine = Prescription_medicine.objects.filter(prescription=prescriptions)
        prescription_test = Prescription_test.objects.filter(prescription=prescriptions)
        
        context = {'patient':patient,'prescription':prescriptions,'prescription_test':prescription_test,'prescription_medicine':prescription_medicine}
        return render(request, 'prescription-view.html',context)
      else:
         redirect('logout') 

@csrf_exempt
def render_to_pdf(template_src, context_dict={}):
    template=get_template(template_src)
    html=template.render(context_dict)
    result=BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)  # Changed encoding to UTF-8
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type="application/pdf")  # Fixed content_type
    return None

#vaccination viewing patient
@login_required(login_url="login")
def vaccination_view(request, pk):
    if request.user.is_patient:
        try:
            patient = Patient.objects.get(user=request.user)
        except Patient.DoesNotExist:
            messages.error(request, 'Patient record does not exist.')
            return redirect('logout')

        required_fields = ['barangay_num', 'birth_height', 'birth_weight', 'fam_num', 'father_name', 'mother_name', 'place_birth']
        for field in required_fields:
            if not getattr(patient, field):
                messages.error(request, f'{field.replace("_", " ").capitalize()} is missing from your profile. Please update it first.')
                return redirect('profile-settings')

        vaccinations = Vaccination.objects.filter(patient=patient)

        if not vaccinations:
            messages.error(request, 'Vaccination record does not exist.')
            return redirect('patient-dashboard')

        context = {'patient': patient, 'vaccinations': vaccinations}
        return render(request, 'vaccination-view.html', context)

    else:
        return redirect('logout')
    
@login_required(login_url="login")
def vaccination_pdf(request):
 if request.user.is_patient:
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        messages.error(request, 'Patient record does not exist.')
        return redirect('logout')
    vaccinations = Vaccination.objects.filter(patient=patient)

    if not vaccinations:
        messages.error(request, 'Vaccination record does not exist.')
        return redirect('patient-dashboard')
    # current_date = datetime.date.today()
    
    context = {'patient': patient, 'vaccinations': vaccinations}

    vac_pdf=render_to_pdf('vaccination-pdf.html', context)
    if vac_pdf:
        response = HttpResponse(vac_pdf, content_type='application/pdf')
        #response['Content-Disposition'] = 'attachment; filename=record.pdf'
        return response
    return HttpResponse("Not Found")

#immunization viewing patient
@login_required(login_url="login")
def immunization_view(request, pk):
    if request.user.is_patient:
        try:
            patient = Patient.objects.get(user=request.user)
        except Patient.DoesNotExist:
            messages.error(request, 'Patient record does not exist.')
            return redirect('logout')

        required_fields = ['barangay_num', 'birth_height', 'birth_weight', 'fam_num', 'father_name', 'mother_name', 'place_birth']
        for field in required_fields:
            if not getattr(patient, field):
                messages.error(request, f'{field.replace("_", " ").capitalize()} is missing from your profile. Please update it first.')
                return redirect('profile-settings')

        immunizations = Immunization.objects.filter(patient=patient)

        if not immunizations:
            messages.error(request, 'Immunization record does not exist.')
            return redirect('patient-dashboard')

        context = {'patient': patient, 'immunizations': immunizations}
        return render(request, 'immunization-view.html', context)

    else:
        return redirect('logout')

# def prescription_pdf(request,pk):
#  if request.user.is_patient:
#     patient = Patient.objects.get(user=request.user)
#     prescription = Prescription.objects.get(prescription_id=pk)
#     perscription_medicine = Perscription_medicine.objects.filter(prescription=prescription)
#     perscription_test = Perscription_test.objects.filter(prescription=prescription)
#     current_date = datetime.date.today()
#     context={'patient':patient,'current_date' : current_date,'prescription':prescription,'perscription_test':perscription_test,'perscription_medicine':perscription_medicine}
#     pdf=render_to_pdf('prescription_pdf.html', context)
#     if pdf:
#         response=HttpResponse(pdf, content_type='application/pdf')
#         content="inline; filename=report.pdf"
#         # response['Content-Disposition']= content
#         return response
#     return HttpResponse("Not Found")

@login_required(login_url="login")
def prescription_pdf(request,pk):
 if request.user.is_patient:
    patient = Patient.objects.get(user=request.user)

    try:
        prescription = Prescription.objects.get(prescription_id=pk)
    except Prescription.DoesNotExist:
        messages.error(request, 'Prescription does not exist.')
        return redirect('patient-dashboard')

    if prescription.patient != patient:
        messages.info(request, 'Not Authorized')
        return redirect('patient-dashboard')
    
    prescription_medicine = Prescription_medicine.objects.filter(prescription=prescription)
    prescription_test = Prescription_test.objects.filter(prescription=prescription)
    # current_date = datetime.date.today()
    context={'patient':patient,'prescription':prescription,'prescription_test':prescription_test,'prescription_medicine':prescription_medicine}
    pres_pdf=render_to_pdf('prescription_pdf.html', context)
    if pres_pdf:
        response = HttpResponse(pres_pdf, content_type='application/pdf')
        #response['Content-Disposition'] = 'attachment; filename=record.pdf'
        return response
    return HttpResponse("Not Found")

@transaction.atomic
@login_required(login_url="login")
def delete_prescription(request,pk):
    if request.user.is_authenticated and request.user.is_patient:
        prescription = Prescription.objects.get(prescription_id=pk)
        prescription.delete()
        messages.success(request, 'Prescription Deleted')
        return redirect('patient-dashboard')
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'login.html')

@transaction.atomic
@login_required(login_url="login")
def delete_report(request,pk):
    if request.user.is_authenticated and request.user.is_patient:
        report = Report.objects.get(report_id=pk)
        report.delete()
        messages.success(request, 'Report Deleted')
        return redirect('patient-dashboard')
    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'login.html')

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

@login_required(login_url="login")
def notifications(request):
    notifications = request.user.notifications.unread()
    for notification in notifications:
        if isinstance(notification.data, str):
            notification.data = json.loads(notification.data)
    return render(request, 'notification/notification_items.html', {'notifications': notifications})

@login_required(login_url="login")
def clear_notification(request):
    try:
        request.user.notifications.unread().delete()
        messages.success(request, _('Unread notifications removed.'))
    except Exception as e:
        messages.error(request, e)
    notifications = request.user.notifications.unread()
    return render(request, 'notification/notification_items.html', {'notifications': notifications})

@login_required(login_url="login")
def delete_notification(request, id):
    try:
        notification = request.user.notifications.get(id=id).delete()
        messages.success(request, ('Notification deleted.'))
    except Exception as e:
        messages.error(request, e)
    notifications = request.user.notifications.all()
    return render(request, 'notification/all_notifications.html', {'notifications': notifications})


@login_required(login_url="login")
def read_notifications(request):
    try:
        request.user.notifications.all().mark_all_as_read()
        messages.info(request, _('Notifications marked as read'))
    except Exception as e:
        messages.error(request, e)
    notifications = request.user.notifications.unread()

    return render(request, 'notification/notification_items.html', {'notifications': notifications})


@login_required(login_url="login")
def all_notifications(request):
    notifications = request.user.notifications.all()
    for notification in notifications:
        if isinstance(notification.data, str):
            notification.data = json.loads(notification.data)
    return render(request, 'notification/all_notifications.html', {'notifications': notifications})

@login_required(login_url="login")
def latest_notification(request):
    notification = request.user.notifications.unread().first()
    if notification is not None:
        if isinstance(notification.data, str):
            notification.data = json.loads(notification.data)  # Parse the data string into a dictionary
        return JsonResponse({
            "id": notification.id,
            "title": notification.verb,
            "message": notification.description,
            "time": notification.timesince(),
            "user": str(notification.actor),
            "image": notification.data.get('icon', ''),  # Now you can safely use the 'get' method
            "timestamp": notification.timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),  # include the timestamp
        })
    else:
        return JsonResponse({})