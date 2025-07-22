from django.db import models
import uuid
from django.conf import settings
import datetime
from django.utils import timezone

# import django user model
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


# Create your models here.

"""
null=True --> don't require a value when inserting into the database
blank=True --> allow blank value when submitting a form
auto_now_add --> automatically set the value to the current date and time
unique=True --> prevent duplicate values
primary_key=True --> set this field as the primary key
editable=False --> prevent the user from editing this field

django field types --> google it  # every field types has field options
Django automatically creates id field for each model class which will be a PK # primary_key=True --> if u want to set manual
"""

class User(AbstractUser):
    is_patient = models.BooleanField(default=False)
    is_doctor = models.BooleanField(default=False)
    is_healthcenter_admin = models.BooleanField(default=False)
    is_labworker = models.BooleanField(default=False)
    is_inventorymanager = models.BooleanField(default=False)
    #login_status = models.CharField(max_length=200, null=True, blank=True, default="offline")
    login_status = models.BooleanField(default=False)
    
class Healthcenter_Information(models.Model):
    healthcenter_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    featured_image = models.ImageField(upload_to='healthcenters/', default='healthcenters/default.png', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    email = models.EmailField(max_length=200, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True) # Adjust max_length as needed
    general_bed_no = models.IntegerField(null=True, blank=True)
    available_icu_no = models.IntegerField(null=True, blank=True)
    regular_cabin_no = models.IntegerField(null=True, blank=True)
    emergency_cabin_no = models.IntegerField(null=True, blank=True)
    vip_cabin_no = models.IntegerField(null=True, blank=True)

    # New fields
    street = models.CharField(max_length=200, null=True, blank=True)
    zip_code = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=200, null=True, blank=True)
    barangay = models.CharField(max_length=200, null=True, blank=True)
    head_facility = models.CharField(max_length=200, null=True, blank=True)
   

    # String representation of object
    def __str__(self):
        return str(self.name)

class Patient(models.Model):
    GENDER_CHOICES = [
        ("Female", "Female"),
        ("Male", "Male")
    ]
    patient_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='patient')
    name = models.CharField(max_length=200, null=True, blank=True)
    username = models.CharField(max_length=200, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    email = models.EmailField(max_length=200, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True) # Adjust max_length as needed
    gender = models.CharField(max_length=200, choices=GENDER_CHOICES, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    serial_number = models.CharField(max_length=200, null=True, blank=True)
    featured_image = models.ImageField(upload_to='patients/', default='patients/user-default.png', null=True, blank=True)
    blood_group = models.CharField(max_length=200, null=True, blank=True)
    history = models.CharField(max_length=200, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    nid = models.CharField(max_length=200, null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    father_name = models.CharField(max_length=200, null=True, blank=True)
    mother_name = models.CharField(max_length=200, null=True, blank=True)
    fam_num = models.CharField(max_length=200, null=True, blank=True)
    barangay_num = models.CharField(max_length=200, null=True, blank=True)
    birth_weight = models.CharField(max_length=200, null=True, blank=True)
    birth_height = models.CharField(max_length=200, null=True, blank=True)
    place_birth = models.CharField(max_length=200, null=True, blank=True)
    
    health_center = models.ForeignKey(Healthcenter_Information, on_delete=models.SET_NULL, null=True, blank=True)

    #penalties
    cancellations = models.IntegerField(default=0, null=True, blank=True)
    no_shows = models.IntegerField(default=0, null=True, blank=True)

    terms_confirmed = models.BooleanField(default=False)

    # Chat
    login_status = models.CharField(max_length=200, null=True, blank=True, default="offline")

    def __str__(self):
        return str(self.user.username)

class VerificationRequest(models.Model):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (APPROVED, "Approved"),
        (REJECTED, "Rejected"),
    ]
    
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE)
    proof_of_billing = models.ImageField(upload_to='verification/')
    id_proof_front = models.ImageField(upload_to='verification/', default='doctors_certificate/default.png', null=True, blank=True)
    id_proof_back = models.ImageField(upload_to='verification/', default='doctors_certificate/default.png', null=True, blank=True)
    selfie_with_id = models.ImageField(upload_to='verification/', default='doctors/user-default.png', null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    request_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.patient} - {self.status}'
    
class MedicalRecordRequest(models.Model):
    STATUS_CHOICES = (
        ('P', 'Pending'),
        ('A', 'Approved'),
        ('D', 'Denied'),
    )
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    record = models.ForeignKey('doctor.MedicalRecord', on_delete=models.CASCADE)
    purpose_of_request = models.TextField()
    request_date = models.DateTimeField(default=timezone.now)
    supporting_documentation = models.FileField(upload_to='support_docs/', null=True, blank=True)
    date_needed = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')

    def __str__(self):
        return f"Request from {self.patient} - {self.request_date}"
    