import email
from email.mime import image
from multiprocessing import context
from unicodedata import name
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from healthcenter.models import Healthcenter_Information, User, Patient
from django.db.models import Q
from inventory.models import Medicine, MedicineAdjustment, MedicalEquipment,MedicalEquipmentAdjustment, MedicalSupply, MedicalSupplyAdjustment, InventoryManager
from doctor.models import Doctor_Information, Prescription, Prescription_test, Report, Appointment, Experience , Education,Specimen,Test, Staff
from .forms import AdminUserCreationForm, LabWorkerCreationForm, EditHealthcenterForm, EditEmergencyForm,AdminForm , InventoryManagerCreationForm, DoctorUserCreationForm, StaffUserCreationForm
from .models import Admin_Information,service, Clinical_Laboratory_Technician, Test_Information, OperationHour
import random,re
import string
from django.db.models import  Count
from datetime import datetime
import datetime
from django.views.decorators.csrf import csrf_exempt

from django.core.mail import BadHeaderError, send_mail
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.utils.html import strip_tags
from .utils import searchMedicines, searchMedicalEquipment, searchMedicalSupply

from django.core.exceptions import ValidationError
import re
from django.db import transaction

# Create your views here.

@csrf_exempt
@login_required(login_url='login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_dashboard(request):
    # admin = Admin_Information.objects.get(user_id=pk)
    if request.user.is_healthcenter_admin:
        user = Admin_Information.objects.get(user=request.user)
        total_patient_count = Patient.objects.annotate(count=Count('patient_id'))
        total_doctor_count = Doctor_Information.objects.annotate(count=Count('doctor_id'))
        total_inventorymanager_count = InventoryManager.objects.annotate(count=Count('inventorymanager_id'))
        total_staff_count = Staff.objects.annotate(count=Count('staff_id'))
        total_healthcenter_count = Healthcenter_Information.objects.annotate(count=Count('healthcenter_id'))
        total_labworker_count = Clinical_Laboratory_Technician.objects.annotate(count=Count('technician_id'))
        pending_appointment = Appointment.objects.filter(appointment_status='pending').count()
        doctors = Doctor_Information.objects.all()
        patients = Patient.objects.all()
        staff = Staff.objects.all()
        healthcenters = Healthcenter_Information.objects.all()
        lab_workers = Clinical_Laboratory_Technician.objects.all()
        inventorymanager = InventoryManager.objects.all()
        
        sat_date = datetime.date.today()
        sat_date_str = str(sat_date)
        sat = sat_date.strftime("%A")

        sun_date = sat_date + datetime.timedelta(days=1) 
        sun_date_str = str(sun_date)
        sun = sun_date.strftime("%A")
        
        mon_date = sat_date + datetime.timedelta(days=2) 
        mon_date_str = str(mon_date)
        mon = mon_date.strftime("%A")
        
        tues_date = sat_date + datetime.timedelta(days=3) 
        tues_date_str = str(tues_date)
        tues = tues_date.strftime("%A")
        
        wed_date = sat_date + datetime.timedelta(days=4) 
        wed_date_str = str(wed_date)
        wed = wed_date.strftime("%A")
        
        thurs_date = sat_date + datetime.timedelta(days=5) 
        thurs_date_str = str(thurs_date)
        thurs = thurs_date.strftime("%A")
        
        fri_date = sat_date + datetime.timedelta(days=6) 
        fri_date_str = str(fri_date)
        fri = fri_date.strftime("%A")
        
        sat_count = Appointment.objects.filter(date=sat_date_str).filter(Q(appointment_status='pending') | Q(appointment_status='confirmed')).count()
        sun_count = Appointment.objects.filter(date=sun_date_str).filter(Q(appointment_status='pending') | Q(appointment_status='confirmed')).count()
        mon_count = Appointment.objects.filter(date=mon_date_str).filter(Q(appointment_status='pending') | Q(appointment_status='confirmed')).count()
        tues_count = Appointment.objects.filter(date=tues_date_str).filter(Q(appointment_status='pending') | Q(appointment_status='confirmed')).count()
        wed_count = Appointment.objects.filter(date=wed_date_str).filter(Q(appointment_status='pending') | Q(appointment_status='confirmed')).count()
        thurs_count = Appointment.objects.filter(date=thurs_date_str).filter(Q(appointment_status='pending') | Q(appointment_status='confirmed')).count()
        fri_count = Appointment.objects.filter(date=fri_date_str).filter(Q(appointment_status='pending') | Q(appointment_status='confirmed')).count()

        context = {'admin': user,'total_patient_count': total_patient_count,'total_doctor_count':total_doctor_count,'pending_appointment':pending_appointment,'doctors':doctors,'staff':staff,'patients':patients,'healthcenters':healthcenters,'lab_workers':lab_workers,'total_inventorymanager_count':total_inventorymanager_count,'total_healthcenter_count':total_healthcenter_count,'total_labworker_count':total_labworker_count,'sat_count': sat_count, 'sun_count': sun_count, 'mon_count': mon_count, 'tues_count': tues_count, 'wed_count': wed_count, 'thurs_count': thurs_count, 'fri_count': fri_count, 'sat': sat, 'sun': sun, 'mon': mon, 'tues': tues, 'wed': wed, 'thurs': thurs, 'fri': fri, 'inventorymanager': inventorymanager,'total_staff_count':total_staff_count}
        return render(request, 'healthcenter_admin/admin-dashboard.html', context)
    elif request.user.is_labworker:
        # messages.error(request, 'You are not authorized to access this page')
        return redirect('labworker-dashboard')
    # return render(request, 'healthcenter_admin/admin-dashboard.html', context)

@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logoutAdmin(request):
    logout(request)
    messages.error(request, 'User Logged out')
    return redirect('login')

#Admin Login       
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_login(request):
    if request.method == 'GET':
        return render(request, 'healthcenter_admin/login.html')
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
            if user.is_healthcenter_admin:
                messages.success(request, 'User logged in')
                return redirect('admin-dashboard')
            else:
                return redirect('logout')
        else:
            messages.error(request, 'Invalid username or password')
        

    return render(request, 'healthcenter_admin/login.html')

#Inventory Login
@csrf_exempt
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def inventorymanager_login(request):
    if request.method == 'GET':
        return render(request, 'healthcenter_admin/inventorymanager_login.html')
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
            if user.is_inventorymanager:
                messages.success(request, 'User logged in')
                return redirect('inventorymanager-dashboard')
            else:
                return redirect('inventorymanager_login.html')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'healthcenter_admin/inventorymanager_login.html')

def clean_fname(fname):
    errors = []
    if not fname:
        errors.append('Please provide your first name.')
    
    if re.search(r'[^A-Za-z.\s]', fname):
        errors.append('First name should only contain letters.')
    
    if len(fname) > 40:
        errors.append('First name should not exceed 40 characters.')

    if errors:
        raise ValidationError(errors)
    
def clean_lname(lname):
    errors = []
    if not lname:
        errors.append('Please provide your last name.')
    
    if re.search(r'[^A-Za-z.\s]', lname):
        errors.append('Last name should only contain letters.')
    
    if len(lname) > 70:
        errors.append('Last name should not exceed 40 characters.')

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

def clean_state(state):
    errors = []
    if not state.isalpha():
        errors.append('State should contain only alphabetic characters.')
    if errors:
        raise ValidationError(errors)

@login_required(login_url='inventorymanager_login')
def manager_profile(request, pk):
    # profile = request.user.profile
    # get user id of logged in user, and get all info from table
    manager = InventoryManager.objects.get(inventorymanager_id=pk)
    context = {'inventorymanager': manager}
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        if form_type == 'update_personal_details':
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            date_of_birth = request.POST.get('date_of_birth')
            phone_number = request.POST.get('phone_number')
            address = request.POST.get('address')
            city = request.POST.get('city')
            state = request.POST.get('state')
            zip_code = request.POST.get('zip_code')
            country = request.POST.get('country')

            try:
                if first_name != manager.first_name:
                    clean_fname(first_name)
                    manager.first_name = first_name

                if last_name != manager.last_name:
                    clean_lname(last_name)
                    manager.last_name = last_name

                if date_of_birth != manager.date_of_birth:
                    clean_dob(date_of_birth)
                    manager.date_of_birth = date_of_birth

                if phone_number != manager.phone_number:
                    clean_phone_number(phone_number)
                    manager.phone_number = phone_number
                
                if address != manager.address:
                    manager.address = address
                
                if city != manager.city:
                    manager.city = city
                
                if state != manager.state:
                    clean_state(state)
                    manager.state = state
                
                if zip_code != manager.zip_code:
                    clean_zip_code(zip_code)
                    manager.zip_code = zip_code
                
                if country != manager.country:
                    clean_barangay_num(country)
                    manager.country = country

                
                manager.save()
                messages.success(request, 'Personal details updated successfully')
                return redirect("manager-profile", pk)
            except ValidationError as e:
                errors = e.args[0]
                error_msg = ' '.join(errors)
                messages.error(request, error_msg)
                return redirect("manager-profile", pk)

        elif form_type == 'change_password':
            prev_password = request.POST.get("old_password_input")
            new_password = request.POST.get("new_password_input")
            confirm_password = request.POST.get("confirm_password_input")
            if prev_password and new_password and confirm_password:
                # Check if the old password is correct
                if not request.user.check_password(prev_password):
                    messages.error(request, "Current password is incorrect")
                    return redirect("manager-profile", pk)

                # Check if the new password and confirm password match
                if new_password == confirm_password:
                    request.user.set_password(new_password)
                    request.user.save()
                    messages.success(request, "Password Changed Successfully")
                    return redirect("login")
                else:
                    messages.error(request, "New Password and Confirm Password do not match")
                    return redirect("manager-profile", pk)
            else:
                messages.error(request, "Please fill in all the fields")
                return redirect("manager-profile", pk)

    return render(request, 'healthcenter_admin/pharmacist-profile.html', context)

#ADMIN INVENTORY MANAGER PROFILE VIEW
@login_required(login_url='login')
def admin_invmanager_profile(request, pk):
    invmanager = InventoryManager.objects.get(inventorymanager_id=pk)
    healthcenter = Healthcenter_Information.objects.get(healthcenter_id=invmanager.health_center.healthcenter_id)
    admin = Admin_Information.objects.get(user=request.user)

    context = {'invmanager': invmanager, 'admin': admin, 'healthcenter': healthcenter}
    return render(request, 'healthcenter_admin/admin-manager-profile.html', context)

#Midwife Login
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def midwife_login(request):
    if request.method == 'GET':
        return render(request, 'healthcenter_admin/midwife_login.html')
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
            if user.is_labworker:
                messages.success(request, 'User logged in')
                return redirect('labworker-dashboard')
            else:
                return redirect('midwife_login.html')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'healthcenter_admin/midwife_login.html')



def admin_register(request):
    page = 'healthcenter_admin/register'
    form = AdminUserCreationForm()

    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            # form.save()
            # commit=False --> don't save to database yet (we have a chance to modify object)
            user = form.save(commit=False)
            user.is_healthcenter_admin = True
            user.save()

            messages.success(request, 'User account was created!')
            
            # After user is created, we can log them in
            #login(request, user)
            return redirect('login')

        else:
            messages.error(request, 'An error has occurred during registration')

    context = {'page': page, 'form': form}
    return render(request, 'healthcenter_admin/register.html', context)

@csrf_exempt
@login_required(login_url='login')
def admin_forgot_password(request):
    return render(request, 'healthcenter_admin/forgot-password.html')

@csrf_exempt
@login_required(login_url='login')
def invoice(request):
    return render(request, 'healthcenter_admin/invoice.html')

@csrf_exempt
@login_required(login_url='login')
def invoice_report(request):
    return render(request, 'healthcenter_admin/invoice-report.html')

@login_required(login_url='login')
def lock_screen(request):
    return render(request, 'healthcenter_admin/lock-screen.html')

@csrf_exempt
@login_required(login_url='login')
def patient_list(request):
    if request.user.is_healthcenter_admin:
        user = Admin_Information.objects.get(user=request.user)
    patients = Patient.objects.all()
    return render(request, 'healthcenter_admin/patient-list.html', {'all': patients, 'admin': user})

@csrf_exempt
@login_required(login_url='login')
def specialitites(request):
    return render(request, 'healthcenter_admin/specialities.html')

@csrf_exempt
@login_required(login_url='login')
def appointment_list(request):
    return render(request, 'healthcenter_admin/appointment-list.html')

@login_required(login_url='login')
def transactions_list(request):
    return render(request, 'healthcenter_admin/transactions-list.html')

@login_required(login_url='login')
def emergency_details(request):
    user = Admin_Information.objects.get(user=request.user)
    healthcenters = Healthcenter_Information.objects.all()
    context = { 'admin': user, 'all': healthcenters}
    return render(request, 'healthcenter_admin/emergency.html', context)

@login_required(login_url='login')
def healthcenter_list(request):
    user = Admin_Information.objects.get(user=request.user)
    healthcenters = Healthcenter_Information.objects.all()
    context = { 'admin': user, 'healthcenters': healthcenters}
    return render(request, 'healthcenter_admin/healthcenter-list.html', context)

@login_required(login_url='login')
def appointment_list(request):
    return render(request, 'healthcenter_admin/appointment-list.html')

@login_required(login_url='login')
def healthcenter_profile(request):
    return render(request, 'healthcenter-profile.html')

@login_required(login_url='login')
def admin_healthcenter_profile(request):
    return render(request, 'healthcenter_admin/admin-healthcenter-profile.html')

@transaction.atomic
@login_required(login_url='login')
def healthcenter_admin_profile(request, pk):
    # profile = request.user.profile
    # get user id of logged in user, and get all info from table
    admin = Admin_Information.objects.get(user_id=pk)
    context={'admin':admin}
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        if form_type == 'update_personal_details':
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            date_of_birth = request.POST.get('date_of_birth')
            phone_number = request.POST.get('phone_number')
            address = request.POST.get('address')
            city = request.POST.get('city')
            state = request.POST.get('state')
            zip_code = request.POST.get('zip_code')
            country = request.POST.get('country')

            try:
                if first_name != admin.first_name:
                    clean_fname(first_name)
                    admin.first_name = first_name

                if last_name != admin.last_name:
                    clean_lname(last_name)
                    admin.last_name = last_name

                if date_of_birth != admin.date_of_birth:
                    clean_dob(date_of_birth)
                    admin.date_of_birth = date_of_birth

                if phone_number != admin.phone_number:
                    clean_phone_number(phone_number)
                    admin.phone_number = phone_number
                
                if address != admin.address:
                    admin.address = address
                
                if city != admin.city:
                    admin.city = city
                
                if state != admin.state:
                    clean_state(state)
                    admin.state = state
                
                if zip_code != admin.zip_code:
                    clean_zip_code(zip_code)
                    admin.zip_code = zip_code
                
                if country != admin.country:
                    clean_barangay_num(country)
                    admin.country = country

                
                admin.save()
                messages.success(request, 'Personal details updated successfully') 
                return redirect("healthcenter-admin-profile", pk)
            except ValidationError as e:
                errors = e.args[0]
                error_msg = ' '.join(errors)
                messages.error(request, error_msg)
                return redirect("healthcenter-admin-profile", pk)

        elif form_type == 'change_password':
            prev_password = request.POST.get("old_password_input")
            new_password = request.POST.get("new_password_input")
            confirm_password = request.POST.get("confirm_password_input")
            if prev_password and new_password and confirm_password:
                # Check if the old password is correct
                if not request.user.check_password(prev_password):
                    messages.error(request, "Current password is incorrect")
                    return redirect("healthcenter-admin-profile", pk)

                # Check if the new password and confirm password match
                if new_password == confirm_password:
                    request.user.set_password(new_password)
                    request.user.save()
                    messages.success(request, "Password Changed Successfully")
                    return redirect("login")
                else:
                    messages.error(request, "New Password and Confirm Password do not match")
                    return redirect("healthcenter-admin-profile", pk)
            else:
                messages.error(request, "Please fill in all the fields")
                return redirect("healthcenter-admin-profile", pk)

    return render(request, 'healthcenter_admin/healthcenter-admin-profile.html', context)

def validate_not_empty(value, field_name):
    if not value:
        raise ValidationError(field_name + " cannot be empty.")
    
def clean_name(name):
    validate_not_empty(name, "Health Center Name")

    errors = []
    if not name:
        errors.append('Please provide the health center\'s name.')
    else:
        if re.search(r'[^A-Za-z.\s]', name):
            errors.append('Health center\'s name should only contain letters.')
        
        if len(name) > 40:
            errors.append('Health center\'s name should not exceed 40 characters.')

    if errors:
        raise ValidationError(errors)

def clean_hname(name):
    validate_not_empty(name, "Head Facility")

    errors = []
    if not name:
        errors.append('Please provide the Head of the Facility name.')
    else:
        if re.search(r'[^A-Za-z.\s]', name):
            errors.append('Head of the Facility name should only contain letters.')
        
        if len(name) > 40:
            errors.append('Head of the Facility name should not exceed 40 characters.')

    if errors:
        raise ValidationError(errors)
    
def validate_email_format(email):
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        raise ValidationError('Invalid email format.')

def clean_phone_number(phone_number):
    validate_not_empty(phone_number, 'Phone number')
    
    if not re.match(r'^(\+639|0)\d{10}$', phone_number):
        raise ValidationError('Invalid phone number format: Must start with +639 or 0 and be followed by a 10-digit number')

def clean_barangay_num(barangay_num):
    validate_not_empty(barangay_num, 'Barangay number')
    
    try:
        barangay_num = int(barangay_num)
        if barangay_num < 0:
            raise ValidationError('Please provide a valid barangay number.')
    except ValueError:
        raise ValidationError('Please provide a valid barangay number.')

def clean_zip_code(zip_code):
    validate_not_empty(zip_code, 'Zip code')
    
    try:
        zip_code = int(zip_code)
        if zip_code < 0:
            raise ValidationError('Please provide a valid zip code number.')
    except ValueError:
        raise ValidationError('Please provide a valid zip code number.')

def clean_email(email):
    validate_not_empty(email, 'Email address')
    validate_email_format(email)

@transaction.atomic
@login_required(login_url='login')
def add_healthcenter(request):
    if  request.user.is_healthcenter_admin:
        user = Admin_Information.objects.get(user=request.user)

        if request.method == 'POST':
            healthcenter = Healthcenter_Information()
            
            if 'featured_image' in request.FILES:
                featured_image = request.FILES['featured_image']
            else:
                featured_image = "departments/default.png"
            
            healthcenter_name = request.POST.get('healthcenter_name')
            street = request.POST.get('street')
            zip_code = request.POST.get('zip_code')
            city = request.POST.get('city')
            barangay = request.POST.get('barangay')
            description = request.POST.get('description')
            email = request.POST.get('email')
            phone_number = request.POST.get('phone_number') 
            service_name = request.POST.getlist('service')
            op_days = request.POST.getlist('day')
            op_starts = request.POST.getlist('start_time')
            op_ends = request.POST.getlist('end_time')
            head_facility= request.POST.get('head_facility')
            
            try:
                # Validate that all fields are not empty
                validate_not_empty(street, "Street")
                validate_not_empty(city, "City")
                validate_not_empty(description, "Description")

                # Additional validations for specific fields
                clean_phone_number(phone_number)
                clean_barangay_num(barangay)
                clean_zip_code(zip_code)
                clean_email(email)
                clean_name(healthcenter_name)
                clean_hname(head_facility)

                healthcenter.name = healthcenter_name
                healthcenter.description = description
                healthcenter.street = street
                healthcenter.zip_code = zip_code
                healthcenter.city = city
                healthcenter.barangay = barangay
                healthcenter.email = email
                healthcenter.phone_number =phone_number
                healthcenter.featured_image=featured_image
                healthcenter.head_facility=head_facility
                
                # print(department_name[0])
            
                healthcenter.save()
                
                for op_day, op_start, op_end in zip(op_days, op_starts, op_ends):
                    operation_hour = OperationHour(healthcenter=healthcenter)
                    operation_hour.day = op_day
                    operation_hour.save()
                    # update the start_time and end_time fields separately
                    operation_hour.start_time = datetime.datetime.strptime(op_start, '%H:%M').time()
                    operation_hour.end_time = datetime.datetime.strptime(op_end, '%H:%M').time()
                    operation_hour.save()

                for i in range(len(service_name)):
                    services = service(healthcenter=healthcenter)
                    services.service_name = service_name[i]
                    services.save()
                
                messages.success(request, 'Healthcenter Added')
                return redirect('healthcenter-list')
            except ValidationError as e:
                errors = e.args[0]
                error_msg = ' '.join(errors)
                messages.error(request, error_msg)
                return redirect('add-healthcenter')
        context = { 'admin': user }
        return render(request, 'healthcenter_admin/add-healthcenter.html',context)


# def edit_healthcenter(request, pk):
#     healthcenter = Healthcenter_Information.objects.get(healthcenter_id=pk)
#     return render(request, 'healthcenter_admin/edit-healthcenter.html')

@transaction.atomic
@login_required(login_url='login')
def edit_healthcenter(request, pk):
    if  request.user.is_healthcenter_admin:
        user = Admin_Information.objects.get(user=request.user)
        healthcenter = Healthcenter_Information.objects.get(healthcenter_id=pk)
        old_featured_image = healthcenter.featured_image

        if request.method == 'GET':
            operation_hour = OperationHour.objects.filter(healthcenter=healthcenter)
            services = service.objects.filter(healthcenter=healthcenter)
            context = {'healthcenter': healthcenter, 'services': services, 'admin': user, 'operation_hour': operation_hour}
            return render(request, 'healthcenter_admin/edit-healthcenter.html',context)

        elif request.method == 'POST':
            if 'featured_image' in request.FILES:
                featured_image = request.FILES['featured_image']
            else:
                featured_image = old_featured_image
                               
            healthcenter_name = request.POST.get('healthcenter_name')
            street = request.POST.get('street')
            zip_code = request.POST.get('zip_code')
            city = request.POST.get('city')
            barangay = request.POST.get('barangay')
            description = request.POST.get('description')
            email = request.POST.get('email')
            phone_number = request.POST.get('phone_number') 
            service_name = request.POST.getlist('service')
            op_day = request.POST.getlist('day')
            op_start = request.POST.getlist('start_time')
            op_end = request.POST.getlist('end_time')
            head_facility= request.POST.get('head_facility')

            try:
                if healthcenter_name != healthcenter.name:
                    clean_name(healthcenter_name)
                    healthcenter.name = healthcenter_name
                
                if description != healthcenter.description:
                    validate_not_empty(description, "Description")
                    healthcenter.description = description
                
                if street != healthcenter.street:
                    validate_not_empty(street, "Street")
                    healthcenter.street = street
                
                if zip_code != healthcenter.zip_code:
                    clean_zip_code(zip_code)
                    healthcenter.zip_code = zip_code
                
                if city != healthcenter.city:
                    validate_not_empty(city, "City")
                    healthcenter.city = city

                if barangay != healthcenter.barangay:
                    clean_barangay_num(barangay)
                    healthcenter.barangay = barangay

                if email != healthcenter.email:
                    clean_email(email)
                    healthcenter.email = email
                
                if phone_number != healthcenter.phone_number:
                    clean_phone_number(phone_number)
                    healthcenter.phone_number =phone_number

                if featured_image != healthcenter.featured_image:
                    healthcenter.featured_image=featured_image
                
                if head_facility != healthcenter.head_facility:
                    clean_hname(head_facility)
                    healthcenter.head_facility=head_facility
            
                # specializations.specialization_name=specialization_name
                # services.service_name = service_name
                # departments.healthcenter_department_name = department_name 

                healthcenter.save()

                OperationHour.objects.filter(healthcenter=healthcenter).delete()
                
                # operation hours
                for op_day, op_start, op_end in zip(op_day, op_start, op_end):
                    operation_hour = OperationHour(healthcenter=healthcenter)
                    operation_hour.day = op_day
                    operation_hour.start_time = datetime.datetime.strptime(op_start, '%H:%M').time()
                    operation_hour.end_time = datetime.datetime.strptime(op_end, '%H:%M').time()
                    operation_hour.save()

                
                # Services
                for i in range(len(service_name)):
                    services = service(healthcenter=healthcenter)
                    services.service_name = service_name[i]
                    services.save()

                messages.success(request, 'Healthcenter Updated')
                return redirect('healthcenter-list')
            except ValidationError as e:
                errors = e.args[0]
                error_msg = ' '.join(errors)
                messages.error(request, error_msg)
                return redirect('edit-healthcenter')

@transaction.atomic
@login_required(login_url='login')
def delete_operation_hour(request, pk, pk2):
    operation_hour = OperationHour.objects.get(pk=pk)
    operation_hour.delete()
    messages.success(request,  'Operation Hour Deleted Successfully')
    return redirect('edit-healthcenter', pk2)   

@transaction.atomic
@login_required(login_url='login')
def delete_service(request, pk, pk2):
    services = service.objects.get(service_id=pk)
    services.delete()
    messages.success(request, 'Service Deleted Successfully')
    return redirect('edit-healthcenter', pk2)

@transaction.atomic
@login_required(login_url='login')
def edit_emergency_information(request, pk):

    healthcenter = Healthcenter_Information.objects.get(healthcenter_id=pk)
    form = EditEmergencyForm(instance=healthcenter)  

    if request.method == 'POST':
        form = EditEmergencyForm(request.POST, request.FILES,
                           instance=healthcenter)  
        if form.is_valid():
            form.save()
            messages.success(request, 'Emergency information added')
            return redirect('emergency')
        else:
            messages.error(request, 'Input value is invalid, numbers only.')
            return redirect('edit-emergency-information', pk)

    context = {'healthcenter': healthcenter, 'form': form}
    return render(request, 'healthcenter_admin/edit-emergency-information.html', context)

@transaction.atomic
@login_required(login_url='login')
def delete_healthcenter(request, pk):
	healthcenter = Healthcenter_Information.objects.get(healthcenter_id=pk)
	healthcenter.delete()
	return redirect('healthcenter-list')


@login_required(login_url='login')
def generate_random_invoice():
    N = 4
    string_var = ""
    string_var = ''.join(random.choices(string.digits, k=N))
    string_var = "#INV-" + string_var
    return string_var


@login_required(login_url='login')
def generate_random_specimen():
    N = 4
    string_var = ""
    string_var = ''.join(random.choices(string.digits, k=N))
    string_var = "#INV-" + string_var
    return string_var

@transaction.atomic
@login_required(login_url='login')
def create_report(request, pk):
    if request.user.is_labworker:
        lab_workers = Clinical_Laboratory_Technician.objects.get(user=request.user)
        prescription =Prescription.objects.get(prescription_id=pk)
        patient = Patient.objects.get(patient_id=prescription.patient_id)
        doctor = Doctor_Information.objects.get(doctor_id=prescription.doctor_id)
        tests = Prescription_test.objects.filter(prescription=prescription)
        

        if request.method == 'POST':
            report = Report(doctor=doctor, patient=patient)
            
            specimen_type = request.POST.getlist('specimen_type')
            collection_date  = request.POST.getlist('collection_date')
            receiving_date = request.POST.getlist('receiving_date')
            test_name = request.POST.getlist('test_name')
            result = request.POST.getlist('result')
            unit = request.POST.getlist('unit')
            referred_value = request.POST.getlist('referred_value')
            delivery_date = request.POST.get('delivery_date')
            other_information= request.POST.get('other_information')

            # # Save to report table
            # report.test_name = test_name
            # report.result = result
            report.delivery_date = delivery_date
            report.other_information = other_information
            # #report.specimen_id =generate_random_specimen()
            # report.specimen_type = specimen_type
            # report.collection_date  = collection_date 
            # report.receiving_date = receiving_date
            # report.unit = unit
            # report.referred_value = referred_value

            report.save()

            for i in range(len(specimen_type)):
                specimens = Specimen(report=report)
                specimens.specimen_type = specimen_type[i]
                specimens.collection_date = collection_date[i]
                specimens.receiving_date = receiving_date[i]
                specimens.save()
                
            for i in range(len(test_name)):
                tests = Test(report=report)
                tests.test_name=test_name[i]
                tests.result=result[i]
                tests.unit=unit[i]
                tests.referred_value=referred_value[i]
                tests.save()
            
            # mail
            doctor_name = doctor.name
            doctor_email = doctor.email
            patient_name = patient.name
            patient_email = patient.email
            report_id = report.report_id
            delivery_date = report.delivery_date
            
            subject = "Report Delivery"

            values = {
                    "doctor_name":doctor_name,
                    "doctor_email":doctor_email,
                    "patient_name":patient_name,
                    "report_id":report_id,
                    "delivery_date":delivery_date,
                }

            html_message = render_to_string('healthcenter_admin/report-mail-delivery.html', {'values': values})
            plain_message = strip_tags(html_message)

            try:
                send_mail(subject, plain_message, 'healthcenter_admin@gmail.com',  [patient_email], html_message=html_message, fail_silently=False)
            except BadHeaderError:
                return HttpResponse('Invalid header found') 

            return redirect('mypatient-list')

        context = {'prescription':prescription,'lab_workers':lab_workers,'tests':tests}
        return render(request, 'healthcenter_admin/create-report.html',context)

@transaction.atomic
@login_required(login_url='login')
def doctor_register(request):
    if request.user.is_healthcenter_admin:
        user = Admin_Information.objects.get(user=request.user)
        form = DoctorUserCreationForm()

        if request.method == 'POST':
            form = DoctorUserCreationForm(request.POST)
            if form.is_valid():
                form.save()

                messages.success(request, 'Doctor account was created!')

                # After user is created, we can log them in
                #login(request, user)
                return redirect('doctor-list')
            else:
                for field_errors in form.errors.values():
                    for error in field_errors:
                        messages.error(request, error)

    context = {'form': form, 'admin': user}
    return render(request, 'healthcenter_admin/add-doctor.html', context)

@transaction.atomic
@login_required(login_url='login')
def delete_doctor(request, pk):
    if request.user.is_authenticated:
        if request.user.is_healthcenter_admin:
            doctor = Doctor_Information.objects.get(doctor_id=pk)
            user = doctor.user
            doctor.delete()
            user.delete()
            messages.success(request, 'Successfully deleted doctor account!') 
            return redirect('doctor-list')
    
@login_required(login_url='login')
def view_doctor(request):
    if request.user.is_healthcenter_admin:
        user = Admin_Information.objects.get(user=request.user)
        doctor = Doctor_Information.objects.all()
        
    return render(request, 'healthcenter_admin/doctor-list.html', {'doctor': doctor, 'admin': user})

@transaction.atomic
@login_required(login_url='login')
def staff_register(request):
    if request.user.is_healthcenter_admin:
        user = Admin_Information.objects.get(user=request.user)
        form = StaffUserCreationForm()

        if request.method == 'POST':
            form = StaffUserCreationForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Staff account was created!')
                return redirect('staff-list')
            else:
                for field_errors in form.errors.values():
                    for error in field_errors:
                        messages.error(request, error)

    context = {'form': form, 'admin': user}
    return render(request, 'healthcenter_admin/add-staff.html', context)

@transaction.atomic
@login_required(login_url='login')
def delete_staff(request, pk):
    if request.user.is_authenticated:
        if request.user.is_healthcenter_admin:
            staff = Staff.objects.get(staff_id=pk)
            user = staff.user
            staff.delete()
            user.delete()
            return redirect('staff-list')

@transaction.atomic
@login_required(login_url='admin-login')
def delete_inventorymanager(request, pk):
    if request.user.is_authenticated:
        if request.user.is_healthcenter_admin:
            inventorymanager = InventoryManager.objects.get(inventorymanager_id=pk)
            user = inventorymanager.user
            inventorymanager.delete()
            user.delete()
            return redirect('inventorymanager-list')
    
@login_required(login_url='login')
def view_staff(request):
    if request.user.is_healthcenter_admin:
        user = Admin_Information.objects.get(user=request.user)
        staff = Staff.objects.all()
        
    return render(request, 'healthcenter_admin/staff-list.html', {'staff': staff, 'admin': user})

@transaction.atomic
@login_required(login_url='login')
def add_inventorymanager(request):
    if request.user.is_healthcenter_admin:
        user = Admin_Information.objects.get(user=request.user)
        form = InventoryManagerCreationForm()
     
        if request.method == 'POST':
            form = InventoryManagerCreationForm(request.POST)
            if form.is_valid():
                form.save()
            
                messages.success(request, 'Inventory Manager account was created!')

                # After user is created, we can log them in
                #login(request, user)
                return redirect('inventorymanager-list')
            else:
                for field_errors in form.errors.values():
                    for error in field_errors:
                        messages.error(request, error)
    
    context = {'form': form, 'admin': user}
    return render(request, 'healthcenter_admin/add-pharmacist.html', context)

#medicine
@login_required(login_url='login')
def medicine_list(request):
    if request.user.is_authenticated:
        if request.user.is_inventorymanager:
            inventorymanager = InventoryManager.objects.get(user=request.user)
            health_center = inventorymanager.health_center

            
            # Get the list of medicines that belong to the user's health center
            medicine = Medicine.objects.filter(health_center=health_center)
            
            medicine, search_query = searchMedicines(request)
            context = {'medicine':medicine,
                        'inventorymanager':inventorymanager,
                        'search_query': search_query}
            return render(request, 'healthcenter_admin/medicine-list.html',context)
        
@login_required(login_url='login')
def medicine_list_view(request):
    if request.user.is_authenticated:
        if request.user.is_inventorymanager:
            inventorymanager = InventoryManager.objects.get(user=request.user)
            health_center = inventorymanager.health_center

            
            # Get the list of medicines that belong to the user's health center
            medicine = Medicine.objects.filter(health_center=health_center)
            
            medicine, search_query = searchMedicines(request)
            context = {'medicine':medicine,
                        'inventorymanager':inventorymanager,
                        'search_query': search_query}
            return render(request, 'healthcenter_admin/medicine-list-view.html',context)
        
@transaction.atomic
@login_required(login_url='login')
def medicine_list_manage(request, pk):
    if request.user.is_authenticated:
        if request.user.is_inventorymanager:
            inventorymanager = InventoryManager.objects.get(user=request.user)
    
            medicine = Medicine.objects.get(serial_number=pk)
            
            history = MedicineAdjustment.objects.filter(medicine__serial_number=pk).order_by('-created_at')

            # Handle medicine adjustments
            if request.method == 'POST':
                adjustment_type = request.POST.get('adjustment_type')
                quantity = request.POST.get('quantity')
                sponsored_by = request.POST.get('sponsored_by')
                adjustment = MedicineAdjustment(medicine=medicine, adjustment_type=adjustment_type, quantity=quantity, inventory_manager=inventorymanager,sponsored_by=sponsored_by,)
                adjustment.save()
                
                if adjustment_type == 'in':
                    message = f"{quantity} {medicine.name} has been added to stock."
                else:
                    message = f"{quantity} {medicine.name} has been subtracted from stock."
                
                return redirect('medicine-list')
            
            context = {
                'medicine':medicine,
                'inventorymanager':inventorymanager,
                'history': history
            }
            return render(request, 'healthcenter_admin/medicine-list-manage.html', context)
        

@transaction.atomic
@login_required(login_url='login')
def add_medicine(request):
    if request.user.is_inventorymanager:
        user = InventoryManager.objects.get(user=request.user)
        health_center = user.health_center
     
    if request.method == 'POST':
        medicine = Medicine()
       
        if 'featured_image' in request.FILES:
            featured_image = request.FILES['featured_image']
        else:
            featured_image = "medicines/default.png"
       
        name = request.POST.get('name')
        item_code = request.POST.get('itemcode')
        weight = request.POST.get('weight') 
        medicine_category = request.POST.get('category_type')
        medicine_type = request.POST.get('medicine_type')
        description = request.POST.get('description')
        manufacturer = request.POST.get('manufacturer')
        expiration_date = request.POST.get('expiration')
        location = request.POST.get('location')
        sponsoredby = request.POST.get('sponsoredby')
        receivedby = request.POST.get('receivedby')
        dor = request.POST.get('dor')
        tor = request.POST.get('tor')
        remarks = request.POST.get('remarks')

        if not name:
            messages.error(request, 'Please provide a name for the medicine.')
            return redirect('add-medicine')
        
        if not item_code:
            messages.error(request, 'Please provide an item code for the medicine.')
            return redirect('add-medicine')
        
        if not weight:
            messages.error(request, 'Please provide the weight of the medicine.')
            return redirect('add-medicine')
        
        if not medicine_category:
            messages.error(request, 'Please select a category for the medicine.')
            return redirect('add-medicine')
        
        if not medicine_type:
            messages.error(request, 'Please select a type for the medicine.')
            return redirect('add-medicine')
        
        if not description:
            messages.error(request, 'Please provide a description for the medicine.')
            return redirect('add-medicine')
        
        if not manufacturer:
            messages.error(request, 'Please provide the manufacturer of the medicine.')
            return redirect('add-medicine')
        
        if not expiration_date:
            messages.error(request, 'Please provide the expiration date of the medicine.')
            return redirect('add-medicine')
        
        if not location:
            messages.error(request, 'Please provide the location of the medicine.')
            return redirect('add-medicine')
        
        if not sponsoredby:
            messages.error(request, 'Please provide the sponsor of the medicine.')
            return redirect('add-medicine')
        
        if not receivedby:
            messages.error(request, 'Please provide the recipient of the medicine.')
            return redirect('add-medicine')
        
        if not dor:
            messages.error(request, 'Please provide the date of receipt of the medicine.')
            return redirect('add-medicine')
        
        if not tor:
            messages.error(request, 'Please provide the time of receipt of the medicine.')
            return redirect('add-medicine')
        
        try:
            weight = float(weight)
            if weight <= 0:
                messages.error(request, 'Weight must be a positive number.')
                return redirect('add-medicine')
        except ValueError:
            messages.error(request, 'Weight must be a numeric value.')
            return redirect('add-medicine')

        try:
            stock_quantity = int(request.POST.get('stock_quantity'))
            if stock_quantity < 0:
                messages.error(request, 'Stock quantity must be a non-negative number.')
                return redirect('add-medicine')
        except ValueError:
            messages.error(request, 'Stock quantity must be an number value.')
            return redirect('add-medicine')
       
        medicine.name = name
        medicine.weight = weight
        medicine.medicine_category = medicine_category
        medicine.medicine_type = medicine_type
        medicine.description = description
        medicine.featured_image = featured_image
        medicine.item_code = item_code
        medicine.manufacturer = manufacturer
        medicine.expiration_date = expiration_date
        medicine.health_center = health_center
        medicine.stock_quantity = stock_quantity 

        medicine.location = location
        medicine.sponsoredby = sponsoredby
        medicine.receivedby = receivedby
        medicine.dor = dor
        medicine.tor = tor
        medicine.remarks = remarks

        medicine.save()

        # create a new MedicineAdjustment object with the stock_quantity as the initial quantity
        quantity = request.POST.get('stock_quantity')
        adjustment_type = 'in'
        adjustment = MedicineAdjustment(medicine=medicine, quantity=quantity, adjustment_type=adjustment_type, inventory_manager=user)
        adjustment.save()

        return redirect('medicine-list')
   
    return render(request, 'healthcenter_admin/add-medicine.html',{'inventorymanager': user})


@transaction.atomic
@login_required(login_url='login')
def edit_medicine(request, pk):
    if request.user.is_inventorymanager:
        user = InventoryManager.objects.get(user=request.user)
        
        medicine = Medicine.objects.get(serial_number=pk)
        old_medicine_image = medicine.featured_image
        
        if request.method == 'POST':
            if 'featured_image' in request.FILES:
                featured_image = request.FILES['featured_image']
            else:
                featured_image = old_medicine_image
            name = request.POST.get('name')
            item_code = request.POST.get('itemcode')
            weight = request.POST.get('weight')
            medicine_category = request.POST.get('category_type')
            medicine_type = request.POST.get('medicine_type')
            description = request.POST.get('description')
            manufacturer = request.POST.get('manufacturer')
            expiration_date = request.POST.get('expiration')
            location = request.POST.get('location')
            sponsoredby = request.POST.get('sponsoredby')
            receivedby = request.POST.get('receivedby')
            dor = request.POST.get('dor')
            tor = request.POST.get('tor')
            remarks = request.POST.get('remarks')
       
                
            medicine.name = name
            medicine.weight = weight
            medicine.medicine_category = medicine_category
            medicine.medicine_type = medicine_type
            medicine.description = description
            medicine.item_code = item_code
            medicine.manufacturer = manufacturer
            medicine.expiration_date = expiration_date
            medicine.featured_image = featured_image
            medicine.location = location
            medicine.sponsoredby = sponsoredby
            medicine.receivedby = receivedby
            medicine.dor = dor
            medicine.tor = tor
            medicine.remarks = remarks
            
            medicine.save()
            
            return redirect('medicine-list')
   
    return render(request, 'healthcenter_admin/edit-medicine.html',{'medicine': medicine,'inventorymanager': user})


@transaction.atomic
@login_required(login_url='login')
def delete_medicine(request, pk):
    if request.user.is_inventorymanager:
        user = InventoryManager.objects.get(user=request.user)
        medicine = Medicine.objects.get(serial_number=pk)
        medicine.delete()
        return redirect('medicine-list')

#medical equipment
@login_required(login_url='login')
def medical_equipment_list(request):
    if request.user.is_authenticated:
        if request.user.is_inventorymanager:
            inventorymanager = InventoryManager.objects.get(user=request.user)
            health_center = inventorymanager.health_center

            
            # Get the list of medical equipment that belong to the user's health center
            medical_equipment= MedicalEquipment.objects.filter(health_center=health_center)
            
            medical_equipment, search_query = searchMedicalEquipment(request)
            context = {'medical_equipment':medical_equipment,
                        'inventorymanager':inventorymanager,
                        'search_query': search_query}
            return render(request, 'healthcenter_admin/medical-equipment-list.html',context)
        
@login_required(login_url='login')
def medical_equipment_list_view(request):
    if request.user.is_authenticated:
        if request.user.is_inventorymanager:
            inventorymanager = InventoryManager.objects.get(user=request.user)
            health_center = inventorymanager.health_center

            # Get the list of medical equipment that belong to the user's health center
            medical_equipment = MedicalEquipment.objects.filter(health_center=health_center)
            
            medical_equipment, search_query = searchMedicalEquipment(request)
            context = {'medical_equipment':medical_equipment,
                        'inventorymanager':inventorymanager,
                        'search_query': search_query}
            return render(request, 'healthcenter_admin/medical-equipment-list-view.html',context)

@transaction.atomic
@login_required(login_url='login')
def medical_equipment_list_manage(request, pk):
    if request.user.is_authenticated:
        if request.user.is_inventorymanager:
            inventorymanager = InventoryManager.objects.get(user=request.user)
    
            medical_equipment = MedicalEquipment.objects.get(serial_number=pk)
            
            history = MedicalEquipmentAdjustment.objects.filter(medicalequipment__serial_number=pk).order_by('-created_at')

            # Handle equipment adjustments
            if request.method == 'POST':
                adjustment_type = request.POST.get('adjustment_type')
                quantity = request.POST.get('quantity')
                sponsored_by = request.POST.get('sponsored_by')
                adjustment = MedicalEquipmentAdjustment(medicalequipment=medical_equipment, adjustment_type=adjustment_type, quantity=quantity, inventory_manager=inventorymanager,sponsored_by=sponsored_by)
                adjustment.save()
                
                if adjustment_type == 'in':
                    message = f"{quantity} {medical_equipment.name} has been added to stock."
                else:
                    message = f"{quantity} {medical_equipment.name} has been subtracted from stock."
                
                return redirect('medical-equipment-list')
            
            context = {
                'medical_equipment':medical_equipment,
                'inventorymanager':inventorymanager,
                'history': history
            }
            return render(request, 'healthcenter_admin/medical-equipment-list-manage.html', context)       

@transaction.atomic
@login_required(login_url='login')
def add_medical_equipment(request):
    if request.user.is_inventorymanager:
        user = InventoryManager.objects.get(user=request.user)
        health_center = user.health_center
     
    if request.method == 'POST':
        medical_equipment = MedicalEquipment()
       
        if 'featured_image' in request.FILES:
            featured_image = request.FILES['featured_image']
        else:
            featured_image = "medicines/default.png"

        name = request.POST.get('name')
        model_number = request.POST.get('modelnumber')
        supplier = request.POST.get('supplier') 
        subcategory = request.POST.get('subcategory')
        warranty = request.POST.get('warranty')
        description = request.POST.get('description')
        manufacturer = request.POST.get('manufacturer')
        date_of_purchase = request.POST.get('dateofpurchase')

        location = request.POST.get('location')
        sponsoredby = request.POST.get('sponsoredby')
        receivedby = request.POST.get('receivedby')
        dor = request.POST.get('dor')
        tor = request.POST.get('tor')
        remarks = request.POST.get('remarks')

        if not name:
            messages.error(request, 'Please provide a name for the medical equipment.')
            return redirect('add-medical-equipment')
        
        if not model_number:
            messages.error(request, 'Please provide a model number for the medical equipment.')
            return redirect('add-medical-equipment')
        
        if not supplier:
            messages.error(request, 'Please provide a supplier for the medical equipment.')
            return redirect('add-medical-equipment')
        
        if not subcategory:
            messages.error(request, 'Please provide a subcategory for the medical equipment.')
            return redirect('add-medical-equipment')
        
        if not warranty:
            messages.error(request, 'Please provide the warranty information for the medical equipment.')
            return redirect('add-medical-equipment')
        
        if not manufacturer:
            messages.error(request, 'Please provide the manufacturer of the medical equipment.')
            return redirect('add-medical-equipment')
        
        if not date_of_purchase:
            messages.error(request, 'Please provide the date of purchase for the medical equipment.')
            return redirect('add-medical-equipment')
        
        if not location:
            messages.error(request, 'Please provide the location of the medical equipment.')
            return redirect('add-medical-equipment')
        
        if not sponsoredby:
            messages.error(request, 'Please provide the sponsor of the medical equipment.')
            return redirect('add-medical-equipment')
        
        if not receivedby:
            messages.error(request, 'Please provide the recipient of the medical equipment.')
            return redirect('add-medical-equipment')
        
        if not dor:
            messages.error(request, 'Please provide the date of receipt of the medical equipment.')
            return redirect('add-medical-equipment')
        
        if not tor:
            messages.error(request, 'Please provide the time of receipt of the medical equipment.')
            return redirect('add-medical-equipment')
       
        medical_equipment.name = name
        medical_equipment.model_number = model_number
        medical_equipment.supplier = supplier
        medical_equipment.subcategory = subcategory
        medical_equipment.description = description
        medical_equipment.warranty = warranty
        medical_equipment.manufacturer = manufacturer
        medical_equipment.date_of_purchase = date_of_purchase
        medical_equipment.featured_image = featured_image
        medical_equipment.health_center = health_center
        medical_equipment.location = location
        medical_equipment.sponsoredby = sponsoredby
        medical_equipment.receivedby = receivedby
        medical_equipment.dor = dor
        medical_equipment.tor = tor
        medical_equipment.remarks = remarks


        medical_equipment.save()

        return redirect('medical-equipment-list')
   
    return render(request, 'healthcenter_admin/add-medical-equipment.html',{'inventorymanager': user})


@transaction.atomic
@login_required(login_url='login')
def edit_medical_equipment(request, pk):
    if request.user.is_inventorymanager:
        user = InventoryManager.objects.get(user=request.user)
        
        medical_equipment = MedicalEquipment.objects.get(serial_number=pk)
        old_mequipment_image = medical_equipment.featured_image
        
        if request.method == 'POST':
            if 'featured_image' in request.FILES:
                featured_image = request.FILES['featured_image']
            else:
                featured_image = old_mequipment_image
            
            name = request.POST.get('name')
            model_number = request.POST.get('modelnumber')
            supplier = request.POST.get('supplier') 
            subcategory = request.POST.get('subcategory')
            warranty = request.POST.get('warranty')
            description = request.POST.get('description')
            manufacturer = request.POST.get('manufacturer')
            date_of_purchase = request.POST.get('dateofpurchase')
            location = request.POST.get('location')
            sponsoredby = request.POST.get('sponsoredby')
            receivedby = request.POST.get('receivedby')
            dor = request.POST.get('dor')
            tor = request.POST.get('tor')
            remarks = request.POST.get('remarks')
        
            medical_equipment.name = name
            medical_equipment.model_number = model_number
            medical_equipment.supplier = supplier
            medical_equipment.subcategory = subcategory
            medical_equipment.description = description
            medical_equipment.warranty = warranty
            medical_equipment.manufacturer = manufacturer
            medical_equipment.date_of_purchase = date_of_purchase
            medical_equipment.featured_image = featured_image
            medical_equipment.location = location
            medical_equipment.sponsoredby = sponsoredby
            medical_equipment.receivedby = receivedby
            medical_equipment.dor = dor
            medical_equipment.tor = tor
            medical_equipment.remarks = remarks
            
            medical_equipment.save()
            
            return redirect('medical-equipment-list')
   
    return render(request, 'healthcenter_admin/edit-medical-equipment.html',{'medical_equipment': medical_equipment,'inventorymanager': user})


@transaction.atomic
@login_required(login_url='login')
def delete_medical_equipment(request, pk):
    if request.user.is_inventorymanager:
        user = InventoryManager.objects.get(user=request.user)
        medical_equipment = MedicalEquipment.objects.get(serial_number=pk)
        medical_equipment.delete()
        return redirect('medical-equipment-list')
    
        
#medical supply
@login_required(login_url='login')
def medical_supply_list(request):
    if request.user.is_authenticated:
        if request.user.is_inventorymanager:
            inventorymanager = InventoryManager.objects.get(user=request.user)
            health_center = inventorymanager.health_center

            
            # Get the list of medical supply that belong to the user's health center
            medical_supply = MedicalSupply.objects.filter(health_center=health_center)
            
            medical_supply, search_query = searchMedicalSupply(request)
            context = {'medical_supply':medical_supply,
                        'inventorymanager':inventorymanager,
                        'search_query': search_query}
            return render(request, 'healthcenter_admin/medical-supply-list.html',context)
        
@login_required(login_url='login')
def medical_supply_list_view(request):
    if request.user.is_authenticated:
        if request.user.is_inventorymanager:
            inventorymanager = InventoryManager.objects.get(user=request.user)
            health_center = inventorymanager.health_center

            
            # Get the list of medical supply that belong to the user's health center
            medical_supply = MedicalSupply.objects.filter(health_center=health_center)
            
            medical_supply, search_query = searchMedicalSupply(request)
            context = {'medical_supply':medical_supply,
                        'inventorymanager':inventorymanager,
                        'search_query': search_query}
            return render(request, 'healthcenter_admin/medical-supply-list-view.html',context)
        
@transaction.atomic
@login_required(login_url='login')
def medical_supply_list_manage(request, pk):
    if request.user.is_authenticated:
        if request.user.is_inventorymanager:
            inventorymanager = InventoryManager.objects.get(user=request.user)
    
            medical_supply = MedicalSupply.objects.get(serial_number=pk)
            
            history = MedicalSupplyAdjustment.objects.filter(medicalsupply__serial_number=pk).order_by('-created_at')

            # Handle medicine adjustments
            if request.method == 'POST':
                adjustment_type = request.POST.get('adjustment_type')
                quantity = request.POST.get('quantity')
                sponsored_by = request.POST.get('sponsored_by')
                adjustment = MedicalSupplyAdjustment(medicalsupply=medical_supply, adjustment_type=adjustment_type, quantity=quantity, inventory_manager=inventorymanager,sponsored_by=sponsored_by)
                adjustment.save()
                
                if adjustment_type == 'in':
                    message = f"{quantity} {medical_supply.name} has been added to stock."
                else:
                    message = f"{quantity} {medical_supply.name} has been subtracted from stock."
                
                return redirect('medical-supply-list')
            
            context = {
                'medical_supply':medical_supply,
                'inventorymanager':inventorymanager,
                'history': history
            }
            return render(request, 'healthcenter_admin/medical-supply-list-manage.html', context)
        

@transaction.atomic
@login_required(login_url='login')
def add_medical_supply(request):
    if request.user.is_inventorymanager:
        user = InventoryManager.objects.get(user=request.user)
        health_center = user.health_center
     
    if request.method == 'POST':
        medical_supply = MedicalSupply()
       
        if 'featured_image' in request.FILES:
            featured_image = request.FILES['featured_image']
        else:
            featured_image = "medicines/default.png"

        name = request.POST.get('name')
        item_code = request.POST.get('itemcode')
        subcategory = request.POST.get('subcategory')     
        supplier = request.POST.get('supplier') 
        price_per_unit = request.POST.get('ppunit')
        expiration_date = request.POST.get('expiration')
        description = request.POST.get('description')
        location = request.POST.get('location')
        sponsoredby = request.POST.get('sponsoredby')
        receivedby = request.POST.get('receivedby')
        dor = request.POST.get('dor')
        tor = request.POST.get('tor')
        remarks = request.POST.get('remarks')

        if not name:
            messages.error(request, 'Please provide a name for the medical supply.')
            return redirect('add-medical-supply')
        
        if not item_code:
            messages.error(request, 'Please provide an item code for the medical supply.')
            return redirect('add-medical-supply')
        
        if not subcategory:
            messages.error(request, 'Please provide a subcategory for the medical supply.')
            return redirect('add-medical-supply')
        
        if not supplier:
            messages.error(request, 'Please provide a supplier for the medical supply.')
            return redirect('add-medical-supply')
        
        if not price_per_unit:
            messages.error(request, 'Please provide the price per unit for the medical supply.')
            return redirect('add-medical-supply')
        
        if not expiration_date:
            messages.error(request, 'Please provide the expiration date for the medical supply.')
            return redirect('add-medical-supply')
        
        if not location:
            messages.error(request, 'Please provide the location for the medical supply.')
            return redirect('add-medical-supply')
        
        if not sponsoredby:
            messages.error(request, 'Please provide the sponsor for the medical supply.')
            return redirect('add-medical-supply')
        
        if not receivedby:
            messages.error(request, 'Please provide the recipient for the medical supply.')
            return redirect('add-medical-supply')
        
        if not dor:
            messages.error(request, 'Please provide the date of receipt for the medical supply.')
            return redirect('add-medical-supply')
        
        if not tor:
            messages.error(request, 'Please provide the time of receipt for the medical supply.')
            return redirect('add-medical-supply')

        # Additional field validation

        try:
            price_per_unit = float(price_per_unit)
            if price_per_unit <= 0:
                messages.error(request, 'Price per unit must be a positive number.')
                return redirect('add-medical-supply')
        except ValueError:
            messages.error(request, 'Price per unit must be a numeric value.')
            return redirect('add-medical-supply')
       
        medical_supply.name = name
        medical_supply.item_code = item_code
        medical_supply.subcategory = subcategory
        medical_supply.supplier = supplier
        medical_supply.price_per_unit = price_per_unit
        medical_supply.description = description
        medical_supply.featured_image = featured_image
        medical_supply.expiration_date = expiration_date
        medical_supply.health_center = health_center
        medical_supply.location = location
        medical_supply.sponsoredby = sponsoredby
        medical_supply.receivedby = receivedby
        medical_supply.dor = dor
        medical_supply.tor = tor
        medical_supply.remarks = remarks

        medical_supply.save()

        # create a new MedicalSupplyAdjustment object with the stock_quantity as the initial quantity
        quantity = request.POST.get('stock_quantity')
        adjustment_type = 'in'
        adjustment = MedicalSupplyAdjustment(medicalsupply=medical_supply, quantity=quantity, adjustment_type=adjustment_type, inventory_manager=user)
        adjustment.save()

        return redirect('medical-supply-list')
   
    return render(request, 'healthcenter_admin/add-medical-supply.html',{'inventorymanager': user})


@transaction.atomic
@login_required(login_url='login')
def edit_medical_supply(request, pk):
    if request.user.is_inventorymanager:
        user = InventoryManager.objects.get(user=request.user)
        
        medical_supply = MedicalSupply.objects.get(serial_number=pk)
        old_msupply_image = medical_supply.featured_image
        
        if request.method == 'POST':
            if 'featured_image' in request.FILES:
                featured_image = request.FILES['featured_image']
            else:
                featured_image = old_msupply_image

            name = request.POST.get('name')
            item_code = request.POST.get('itemcode')
            subcategory = request.POST.get('subcategory')     
            supplier = request.POST.get('supplier') 
            price_per_unit = request.POST.get('ppunit')
            expiration_date = request.POST.get('expiration')
            description = request.POST.get('description')
            location = request.POST.get('location')
            sponsoredby = request.POST.get('sponsoredby')
            receivedby = request.POST.get('receivedby')
            dor = request.POST.get('dor')
            tor = request.POST.get('tor')
            remarks = request.POST.get('remarks')
        
            medical_supply.name = name
            medical_supply.item_code = item_code
            medical_supply.subcategory = subcategory
            medical_supply.supplier = supplier
            medical_supply.price_per_unit = price_per_unit
            medical_supply.description = description
            medical_supply.featured_image = featured_image
            medical_supply.expiration_date = expiration_date
            medical_supply.location = location
            medical_supply.sponsoredby = sponsoredby
            medical_supply.receivedby = receivedby
            medical_supply.dor = dor
            medical_supply.tor = tor
            medical_supply.remarks = remarks

            medical_supply.save()
            
            return redirect('medical-supply-list')
   
    return render(request, 'healthcenter_admin/edit-medical-supply.html',{'medical_supply': medical_supply,'inventorymanager': user})


@transaction.atomic
@login_required(login_url='login')
def delete_medical_supply(request, pk):
    if request.user.is_inventorymanager:
        user = InventoryManager.objects.get(user=request.user)
        medical_supply = MedicalSupply.objects.get(serial_number=pk)
        medical_supply.delete()
        return redirect('medical-supply-list')

@transaction.atomic
@login_required(login_url='login')
def add_lab_worker(request): 
    if request.user.is_healthcenter_admin:
        user = Admin_Information.objects.get(user=request.user)
        
        form = LabWorkerCreationForm()
     
        if request.method == 'POST':
            form = LabWorkerCreationForm(request.POST)
            if form.is_valid():
                form.save()

                messages.success(request, 'Clinical Laboratory Technician account was created!')

                # After user is created, we can log them in
                #login(request, user)
                return redirect('lab-worker-list')
            else:
                for field_errors in form.errors.values():
                    for error in field_errors:
                        messages.error(request, error)
    
    context = {'form': form, 'admin': user}
    return render(request, 'healthcenter_admin/add-lab-worker.html', context)


@login_required(login_url='login')
def view_lab_worker(request):
    if request.user.is_healthcenter_admin:
        user = Admin_Information.objects.get(user=request.user)
        lab_workers = Clinical_Laboratory_Technician.objects.all()
        
    return render(request, 'healthcenter_admin/lab-worker-list.html', {'lab_workers': lab_workers, 'admin': user})

@login_required(login_url='login')
def view_inventorymanager(request):
    if request.user.is_healthcenter_admin:
        user = Admin_Information.objects.get(user=request.user)
        inventorymanager = InventoryManager.objects.all()
        
    return render(request, 'healthcenter_admin/pharmacist-list.html', {'inventorymanager': inventorymanager, 'admin': user})

@transaction.atomic
@login_required(login_url='login')
def edit_lab_worker(request, pk):
    if request.user.is_healthcenter_admin:
        user = Admin_Information.objects.get(user=request.user)
        lab_worker = Clinical_Laboratory_Technician.objects.get(technician_id=pk)
        
        if request.method == 'POST':
            if 'featured_image' in request.FILES:
                featured_image = request.FILES['featured_image']
            else:
                featured_image = "technician/user-default.png"
                
            name = request.POST.get('name')
            email = request.POST.get('email')     
            phone_number = request.POST.get('phone_number')
            age = request.POST.get('age')  
    
            lab_worker.name = name
            lab_worker.email = email
            lab_worker.phone_number = phone_number
            lab_worker.age = age
            lab_worker.featured_image = featured_image
    
            lab_worker.save()
            
            messages.success(request, 'Clinical Laboratory Technician account updated!')
            return redirect('lab-worker-list')
        
    return render(request, 'healthcenter_admin/edit-lab-worker.html', {'lab_worker': lab_worker, 'admin': user})

@transaction.atomic
@login_required(login_url='login')
def edit_inventorymanager(request, pk):
    if request.user.is_healthcenter_admin:
        user = Admin_Information.objects.get(user=request.user)
        inventorymanager = InventoryManager.objects.get(inventorymanager_id=pk)
        healthcenters = Healthcenter_Information.objects.all()
        
        if request.method == 'POST':
            if 'featured_image' in request.FILES:
                featured_image = request.FILES['featured_image']
            else:
                featured_image = "technician/user-default.png"
                
            name = request.POST.get('name')
            email = request.POST.get('email')     
            phone_number = request.POST.get('phone_number')
            age = request.POST.get('age')  
            healthcenter_id = request.POST.get('healthcenter')
            healthcenter = Healthcenter_Information.objects.get(healthcenter_id=healthcenter_id)
    
            inventorymanager.name = name
            inventorymanager.email = email
            inventorymanager.phone_number = phone_number
            inventorymanager.age = age
            inventorymanager.featured_image = featured_image
            inventorymanager.health_center = healthcenter
    
            inventorymanager.save()
            messages.success(request, 'Inventory Manager updated!')
            return redirect('inventorymanager-list')
        
        context = {
            'inventorymanager': inventorymanager,
            'admin': user,
            'healthcenters': healthcenters,
        }
        
    return render(request, 'healthcenter_admin/edit-pharmacist.html', context)

@login_required(login_url='login')
def admin_doctor_profile(request,pk):
    doctor = Doctor_Information.objects.get(doctor_id=pk)
    healthcenter = Healthcenter_Information.objects.get(healthcenter_id=doctor.health_center.healthcenter_id)
    admin = Admin_Information.objects.get(user=request.user)
    experience= Experience.objects.filter(doctor_id=pk).order_by('-from_year','-to_year')
    education = Education.objects.filter(doctor_id=pk).order_by('-year_of_completion')
    
    context = {'doctor': doctor, 'admin': admin, 'experiences': experience, 'educations': education, 'healthcenter': healthcenter}
    return render(request, 'healthcenter_admin/doctor-profile.html',context)

@login_required(login_url='admin-login')
def admin_staff_profile(request, pk):
    staff = Staff.objects.get(staff_id=pk)
    healthcenter = Healthcenter_Information.objects.get(healthcenter_id=staff.health_center.healthcenter_id)
    admin = Admin_Information.objects.get(user=request.user)

    context = {'staff': staff, 'admin': admin, 'healthcenter': healthcenter}
    return render(request, 'healthcenter_admin/admin-staff-profile.html', context)

@login_required(login_url='login')
def labworker_dashboard(request):
    if request.user.is_authenticated:
        if request.user.is_labworker:
            
            lab_workers = Clinical_Laboratory_Technician.objects.get(user=request.user)
            doctor = Doctor_Information.objects.all()
            context = {'doctor': doctor,'lab_workers':lab_workers}
            return render(request, 'healthcenter_admin/labworker-dashboard.html',context)

@login_required(login_url='login')
def mypatient_list(request):
    if request.user.is_authenticated:
        if request.user.is_labworker:
            lab_workers = Clinical_Laboratory_Technician.objects.get(user=request.user)
            #report= Report.objects.all()
            patient = Patient.objects.all()
            context = {'patient': patient,'lab_workers':lab_workers}
            return render(request, 'healthcenter_admin/mypatient-list.html',context)

@login_required(login_url='login')
def prescription_list(request,pk):
    if request.user.is_authenticated:
        if request.user.is_labworker:
            lab_workers = Clinical_Laboratory_Technician.objects.get(user=request.user)
            patient = Patient.objects.get(patient_id=pk)
            prescription = Prescription.objects.filter(patient=patient)
            context = {'prescription': prescription,'lab_workers':lab_workers,'patient':patient}
            return render(request, 'healthcenter_admin/prescription-list.html',context)

@transaction.atomic
@login_required(login_url='login')
def add_test(request):
    if request.user.is_labworker:
        lab_workers = Clinical_Laboratory_Technician.objects.get(user=request.user)

    if request.method == 'POST':
        tests=Test_Information()
        test_name = request.POST['test_name']
        test_price = request.POST['test_price']
        tests.test_name = test_name
        tests.test_price = test_price

        tests.save()

        return redirect('test-list')
        
    context = {'lab_workers': lab_workers}
    return render(request, 'healthcenter_admin/add-test.html', context)

@login_required(login_url='login')
def test_list(request):
    if request.user.is_labworker:
        lab_workers = Clinical_Laboratory_Technician.objects.get(user=request.user)
        test = Test_Information.objects.all()
        context = {'test':test,'lab_workers':lab_workers}
    return render(request, 'healthcenter_admin/test-list.html',context)


@transaction.atomic
@login_required(login_url='login')
def delete_test(request,pk):
    if request.user.is_authenticated:
        if request.user.is_labworker:
            test = Test_Information.objects.get(test_id=pk)
            test.delete()
            return redirect('test-list')

@login_required(login_url='login')
def inventorymanager_dashboard(request):
    if request.user.is_authenticated:
        if request.user.is_inventorymanager:
            inventorymanager = InventoryManager.objects.get(user=request.user)
            health_center = inventorymanager.health_center
            total_inventorymanager_count = InventoryManager.objects.filter(health_center=health_center).annotate(count=Count('inventorymanager_id'))
            total_medicine_count = Medicine.objects.filter(health_center=health_center).annotate(count=Count('serial_number'))
            total_medical_equipment_count = MedicalEquipment.objects.filter(health_center=health_center).annotate(count=Count('serial_number'))
            total_medical_supply_count = MedicalSupply.objects.filter(health_center=health_center).annotate(count=Count('serial_number'))

            # Get the list of medicines that belong to the user's health center
            medicine = Medicine.objects.filter(health_center=health_center)
            medical_equipment = MedicalEquipment.objects.filter(health_center=health_center)
            medical_supply = MedicalSupply.objects.filter(health_center=health_center)


            context = {'inventorymanager':inventorymanager, 'medicine':medicine,
                       'medical_equipment':medical_equipment, 'medical_supply':medical_supply,
                       'total_inventorymanager_count':total_inventorymanager_count, 
                       'total_medicine_count':total_medicine_count,
                       'total_medical_equipment_count':total_medical_equipment_count,
                       'total_medical_supply_count':total_medical_supply_count}
            return render(request, 'healthcenter_admin/pharmacist-dashboard.html',context)

@csrf_exempt
def report_history(request):
    if request.user.is_authenticated:
        if request.user.is_labworker:

            lab_workers = Clinical_Laboratory_Technician.objects.get(user=request.user)
            report = Report.objects.all()
            context = {'report':report,'lab_workers':lab_workers}
            return render(request, 'healthcenter_admin/report-list.html',context)

