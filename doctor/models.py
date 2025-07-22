from django.db import models

import uuid, datetime
from django.utils import timezone

# import django user model
from healthcenter.models import Healthcenter_Information, User, Patient
from healthcenter_admin.models import service
from django.conf import settings

import random
import string

# # Create your models here.

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
# Create your models here.
def generate_random_string():
    N = 8
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))

class Doctor_Information(models.Model):
    DOCTOR_TYPE = (
        ('Cardiologists', 'Cardiologists'),
        ('Neurologists', 'Neurologists'),
        ('Pediatricians', 'Pediatricians'),
        ('Physiatrists', 'Physiatrists'),
        ('Dermatologists', 'Dermatologists'),
    )
    
    doctor_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='profile')
    name = models.CharField(max_length=200, null=True, blank=True)
    username = models.CharField(max_length=200, null=True, blank=True)
    gender = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(max_length=1000, null=True, blank=True)
    department = models.CharField(max_length=200, choices=DOCTOR_TYPE, null=True, blank=True)

    featured_image = models.ImageField(upload_to='doctors/', default='doctors/user-default.png', null=True, blank=True)
    certificate_image = models.ImageField(upload_to='doctors_certificate/', default='doctors_certificate/default.png', null=True, blank=True)

    email = models.EmailField(max_length=200, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True) # Adjust max_length as needed
    nid = models.CharField(max_length=200, null=True, blank=True)
    visiting_hour = models.CharField(max_length=200, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
     
    # Education
    institute = models.CharField(max_length=200, null=True, blank=True)
    degree = models.CharField(max_length=200, null=True, blank=True)
    completion_year = models.CharField(max_length=200, null=True, blank=True)
    
    # work experience
    work_place = models.CharField(max_length=200, null=True, blank=True)
    designation = models.CharField(max_length=200, null=True, blank=True)
    start_year = models.CharField(max_length=200, null=True, blank=True)
    end_year = models.CharField(max_length=200, null=True, blank=True)
    
    # register_status = models.BooleanField(default=False) default='pending'
    register_status =  models.CharField(max_length=200, null=True, blank=True)
    
    # ForeignKey --> one to one relationship with Healthcenter_Information model.
    health_center = models.ForeignKey(Healthcenter_Information, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return str(self.user.username)

class Staff(models.Model):
    staff_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='staff_profile')
    name = models.CharField(max_length=200, null=True, blank=True)
    username = models.CharField(max_length=200, null=True, blank=True)

    featured_image = models.ImageField(upload_to='doctors/', default='doctors/user-default.png', null=True, blank=True)

    email = models.EmailField(max_length=200, null=True, blank=True)
    gender = models.CharField(max_length=200, null=True, blank=True)
    phone_number = models.CharField(max_length=200, null=True, blank=True)
    date_of_birth = models.CharField(max_length=200, null=True, blank=True)
    health_center = models.ForeignKey(Healthcenter_Information, on_delete=models.SET_NULL, null=True, blank=True)

    address = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    zip_code = models.CharField(max_length=12, null=True, blank=True)

    def __str__(self):
        return str(self.user.username)
    
#Vaccination
class Vaccination(models.Model):
    VACCINE_CHOICES = (
        ('Pfizer-BioNTech', 'Pfizer-BioNTech'),
        ('Moderna', 'Moderna'),
        ('Johnson & Johnson', 'Johnson & Johnson'),
        ('AstraZeneca', 'AstraZeneca'),
        ('Covaxin', 'Covaxin'),
        ('Sinovac', 'Sinovac'),
        ('Sputnik V', 'Sputnik V'),
    )

    DOSE_NUMBER_CHOICES = (
        (1, 'First'),
        (2, 'Second'),
        (3, 'Third (Booster)'),
        (4, 'Fourth (Booster)'),
    )

    vaccination_id = models.AutoField(primary_key=True)
    staff = models.ForeignKey(Staff,on_delete=models.SET_NULL, null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    vaccine_name = models.CharField(max_length=200,choices=VACCINE_CHOICES)
    dose_number = models.IntegerField(choices=DOSE_NUMBER_CHOICES)
    lot_number = models.CharField(max_length=200, null=True, blank=True)
    date_given = models.DateField(null=True, blank=True)
    given_by = models.CharField(max_length=200, null=True, blank=True)
    create_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    healthcenter = models.ForeignKey(Healthcenter_Information, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f'{self.patient.name} - {self.vaccine_name} dose {self.get_dose_number_display()}'
    
#Immunization
class Immunization(models.Model):

    IMMUNIZATION_RECORD_CHOICES = (
       ('Child', 'Child'), 
        ('Adult', 'Adult'), 
       
    )
    IMMUNE_CHOICES = (
        ('BCG', 'BCG'), 
        ('HEPATITIS B', 'HEPATITIS B'), 
        ('PENTAVALENT VACCINE', 'PENTAVALENT VACCINE'), 
        ('ORAL POLIO VACCINE', 'ORAL POLIO VACCINE'), 
        ('INACTIVATED POLIO VACCINE', 'INACTIVATED POLIO VACCINE'), 
        ('PNEUMOCOCCAL CONJUGATE VACCINE', 'PNEUMOCOCCAL CONJUGATE VACCINE'), 
        ('MEASLES, MUMPS, RUBELLA', 'MEASLES, MUMPS, RUBELLA'),
        ('Others', 'Others'),

    )

    VISIT_NUMBER_CHOICES = (
        (0, 'At Birth'),
        (1, '1st Visit'),
        (2, '2nd Visit'),
        (3, '3rd Visit'),
        (4, 'others'),
       
    )

    DOSE_NUMBER_CHOICES = (
        ('1st Dose', '1st Dose'),
        ('2nd Dose', '2nd Dose'),
        ('3rd Dose', '3rd Dose'),
       
    )

    immunization_id = models.AutoField(primary_key=True)
    staff = models.ForeignKey(Staff,on_delete=models.SET_NULL, null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    immune_record = models.CharField(max_length=200,choices=IMMUNIZATION_RECORD_CHOICES)
    immune_name = models.CharField(max_length=200,choices=IMMUNE_CHOICES)
    visit_number = models.IntegerField(choices=VISIT_NUMBER_CHOICES)
    dose_number = models.CharField(max_length=200,choices=DOSE_NUMBER_CHOICES)
    othervaccine_name= models.CharField(max_length=200, null=True, blank=True)
    other_vaccine=models.CharField(max_length=200, null=True, blank=True)
    hfacility_name=models.CharField(max_length=200, null=True, blank=True)
    date_given = models.DateField(null=True, blank=True)
    given_by = models.CharField(max_length=200, null=True, blank=True)
    create_date = models.DateField(null=True, blank=True)
    remarks = models.CharField(max_length=200, null=True, blank=True)
    healthcenter = models.ForeignKey(Healthcenter_Information, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f'{self.patient.name} - {self.immune_name} visit number {self.get_visit_number_display()}'    

class Prescription(models.Model):
    # medicine name, quantity, days, time, description, test, test_descrip
    prescription_id = models.AutoField(primary_key=True)
    doctor = models.ForeignKey(Doctor_Information, on_delete=models.CASCADE, null=True, blank=True)
    serial_number = models.CharField(default=generate_random_string, max_length=8)
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    create_date = models.CharField(max_length=200, null=True, blank=True)
    medicine_name = models.CharField(max_length=200, null=True, blank=True)
    quantity = models.CharField(max_length=200, null=True, blank=True)
    days = models.CharField(max_length=200, null=True, blank=True)
    time = models.CharField(max_length=200, null=True, blank=True)
    relation_with_meal = models.CharField(max_length=200, null=True, blank=True)
    medicine_description = models.TextField(null=True, blank=True)
    test_name = models.CharField(max_length=200, null=True, blank=True)
    test_description = models.TextField(null=True, blank=True)
    extra_information = models.TextField(null=True, blank=True)

    healthcenter = models.ForeignKey(Healthcenter_Information, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return str(self.patient.username)

class MedicalRecord(models.Model):
    # Add disease choices
    DISEASE_CHOICES = (
        ('AFP', 'Acute Flaccid Paralysis'),
        ('Diphtheria', 'Diphtheria'),
        ('Measle', 'Measle'),
        ('Rubella', 'Rubella'),
        ('Neonatal Tetanus', 'Neonatal Tetanus'),
        ('Pertussis', 'Pertussis'),
        ('Chikugunya', 'Chikugunya'),
        ('Dengue', 'Dengue'),
        ('Leptospirosis', 'Leptospirosis'),
        ('Rabies', 'Rabies'),
        ('Acute Bloody Diarrhea', 'Acute Bloody Diarrhea'),
        ('Acute Viral Hepatitis', 'Acute Viral Hepatitis'),
        ('Hepatitis A', 'Hepatitis A'),
        ('Cholera', 'Cholera'),
        ('Rotavirus', 'Rotavirus'),
        ('Typhoid Fever', 'Typhoid Fever'),
        ('Acute Meningitis Encephalitis Syndrome', 'Acute Meningitis Encephalitis Syndrome'),
        ('Influenza-Like Illness', 'Influenza-Like Illness'),
        ('Meningococcal Disease', 'Meningococcal Disease'),
    )

    medical_id = models.AutoField(primary_key=True)
    serial_number = models.CharField(default=generate_random_string, max_length=8)
    doctor = models.ForeignKey(Doctor_Information, on_delete=models.SET_NULL, null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    create_date = models.DateField()
    lab_name = models.CharField(max_length=255)
    test_date = models.DateField()
    tests_conducted = models.TextField()
    results_summary = models.TextField()
    blood_pressure = models.CharField(max_length=255)
    heart_rate = models.CharField(max_length=255)
    respiratory_rate = models.CharField(max_length=255)
    temperature = models.CharField(max_length=255)
    physical_examination = models.TextField()
    diagnostic_tests = models.CharField(max_length=255)
    disease_condition = models.CharField(max_length=255, choices=DISEASE_CHOICES)
    severity = models.CharField(max_length=255)
    additional_notes = models.TextField()

    healthcenter = models.ForeignKey(Healthcenter_Information, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.patient} - {self.create_date}"

class Appointment(models.Model):
    # ('database value', 'display_name')
    APPOINTMENT_TYPE = (
    ('Consultation', 'Consultation'),
    ('Dental', 'Dental'),
    ('Immunization', 'Immunization'),
    ('Animal Bite Treatment', 'Animal Bite Treatment'),
    ('TB Prevention Treatment', 'TB Prevention and Treatment'),
    ('Post Partum Newborn', 'Post-Partum/Newborn'),
    ('Covid Vaccination', 'Covid Vaccination'),
    ('Milk Letting', 'Milk Letting'),
    ('Essential Medicines', 'Provision of Essential Medicines'),
    ('Prenatal Checkup', 'Pre-natal Check-up'),
    ('Syphilis Hepatitis HIV', 'Syphilis/Hepatitis/HIV'),
    )

    APPOINTMENT_STATUS = (
        ('pending', 'pending'),
        ('confirmed', 'confirmed'),
        ('cancelled', 'cancelled'),
    )

    URGENCY_LEVELS = [
    ("low", "Low"),
    ("medium", "Medium"),
    ("high", "High")
    ]

    id = models.AutoField(primary_key=True)
    date = models.DateField(null=True, blank=True)
    time = models.CharField(max_length=200, null=True, blank=True)
    healthcenter = models.ForeignKey(Healthcenter_Information, on_delete=models.SET_NULL, null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True, blank=True)
    appointment_type = models.CharField(max_length=200, choices=APPOINTMENT_TYPE)
    appointment_status = models.CharField(max_length=200, choices=APPOINTMENT_STATUS)
    urgency = models.CharField(max_length=200, choices=URGENCY_LEVELS, null=True, blank=True)
    serial_number = models.CharField(max_length=200, null=True, blank=True)
    symptoms = models.CharField(max_length=155, null=True, blank=True, default="None")
    message = models.CharField(max_length=255, null=True, blank=True, default="None")
    confirmed = models.BooleanField(default=False)

    prescription = models.OneToOneField(Prescription, on_delete=models.SET_NULL, null=True, blank=True)
    medical_record = models.OneToOneField(MedicalRecord, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return str(self.patient.username)
    
class Waitlist(models.Model):
    id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    healthcenter = models.ForeignKey(Healthcenter_Information, on_delete=models.CASCADE)
    desired_date = models.DateField(null=True, blank=True)
    desired_time = models.CharField(max_length=200, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    score = models.FloatField(null=True, blank=True)
    appointment_type = models.CharField(max_length=200, choices=Appointment.APPOINTMENT_TYPE, null=True, blank=True)
    urgency = models.CharField(max_length=200, choices=Appointment.URGENCY_LEVELS, null=True, blank=True)
    message = models.CharField(max_length=255, null=True, blank=True, default="None")
    symptoms = models.CharField(max_length=155, null=True, blank=True, default="None")


class Walkin(models.Model):
    WALK_IN_TYPE = (
    ('Consultation', 'Consultation'),
    ('Dental', 'Dental'),
    ('Immunization', 'Immunization'),
    ('Animal Bite Treatment', 'Animal Bite Treatment'),
    ('TB Prevention Treatment', 'TB Prevention and Treatment'),
    ('Post Partum Newborn', 'Post-Partum/Newborn'),
    ('Covid Vaccination', 'Covid Vaccination'),
    ('Milk Letting', 'Milk Letting'),
    ('Essential Medicines', 'Provision of Essential Medicines'),
    ('Prenatal Checkup', 'Pre-natal Check-up'),
    ('Syphilis Hepatitis HIV', 'Syphilis/Hepatitis/HIV'),
    )

    id = models.AutoField(primary_key=True)
    date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)
    healthcenter = models.ForeignKey(Healthcenter_Information, on_delete=models.SET_NULL, null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True, blank=True)
    reason = models.CharField(max_length=255, null=True, blank=True)
    walk_in_type = models.CharField(max_length=200, choices=WALK_IN_TYPE)
    serial_number = models.CharField(max_length=200, null=True, blank=True)
    symptoms = models.CharField(max_length=155, null=True, blank=True, default="None")

    prescription = models.OneToOneField(Prescription, on_delete=models.SET_NULL, null=True, blank=True)
    medical_record = models.OneToOneField(MedicalRecord, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return str(self.patient.username)

class Education(models.Model):
    education_id = models.AutoField(primary_key=True)
    doctor = models.ForeignKey(Doctor_Information, on_delete=models.CASCADE, null=True, blank=True)
    degree = models.CharField(max_length=200, null=True, blank=True)
    institute = models.CharField(max_length=200, null=True, blank=True)
    year_of_completion = models.CharField(max_length=200, null=True, blank=True)
    
    def __str__(self):
        return str(self.doctor.name)
    
class Experience(models.Model):
    experience_id = models.AutoField(primary_key=True)
    doctor = models.ForeignKey(Doctor_Information, on_delete=models.CASCADE, null=True, blank=True)
    work_place_name = models.CharField(max_length=200, null=True, blank=True)
    from_year = models.CharField(max_length=200, null=True, blank=True)
    to_year = models.CharField(max_length=200, null=True, blank=True)
    designation = models.CharField(max_length=200, null=True, blank=True)
    
    def __str__(self):
        return str(self.doctor.name)


class Report(models.Model):
    report_id = models.AutoField(primary_key=True)
    doctor = models.ForeignKey(Doctor_Information, on_delete=models.SET_NULL, null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True, blank=True)
    specimen_id = models.CharField(max_length=200, null=True, blank=True)
    specimen_type = models.CharField(max_length=200, null=True, blank=True)
    collection_date = models.CharField(max_length=200, null=True, blank=True)
    receiving_date = models.CharField(max_length=200, null=True, blank=True)
    test_name = models.CharField(max_length=200, null=True, blank=True)
    result = models.CharField(max_length=200, null=True, blank=True)
    unit = models.CharField(max_length=200, null=True, blank=True)
    referred_value = models.CharField(max_length=200, null=True, blank=True)
    delivery_date = models.CharField(max_length=200, null=True, blank=True)
    other_information = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return str(self.patient.username)

class Specimen(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, null=True, blank=True)
    specimen_id = models.AutoField(primary_key=True)
    specimen_type = models.CharField(max_length=200, null=True, blank=True)
    collection_date = models.CharField(max_length=200, null=True, blank=True)
    receiving_date = models.CharField(max_length=200, null=True, blank=True)
    
    def __str__(self):
        return str(self.report.report_id)

class Test(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, null=True, blank=True)
    test_id = models.AutoField(primary_key=True)
    test_name = models.CharField(max_length=200, null=True, blank=True)
    result = models.CharField(max_length=200, null=True, blank=True)
    unit = models.CharField(max_length=200, null=True, blank=True)
    referred_value = models.CharField(max_length=200, null=True, blank=True)
    
    def __str__(self):
        return str(self.report.report_id)

class Prescription_medicine(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, null=True, blank=True)
    medicine_id = models.AutoField(primary_key=True)
    medicine_name = models.CharField(max_length=200, null=True, blank=True)
    quantity = models.CharField(max_length=200, null=True, blank=True)
    duration = models.CharField(max_length=200, null=True, blank=True)
    frequency = models.CharField(max_length=200, null=True, blank=True)
    relation_with_meal = models.CharField(max_length=200, null=True, blank=True)
    instruction = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.prescription.prescription_id)

class Prescription_test(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, null=True, blank=True)
    test_id = models.AutoField(primary_key=True)
    test_name = models.CharField(max_length=200, null=True, blank=True)
    test_description = models.TextField(null=True, blank=True)
    test_info_price = models.CharField(max_length=200, null=True, blank=True)
    test_info_pay_status = models.CharField(max_length=200, null=True, blank=True)
    
    """
    (create prescription)
    doctor input --> test_id 
    using test_id --> retrive price
    store price in prescription_test column
    """

    def __str__(self):
        return str(self.prescription.prescription_id)

class Doctor_review(models.Model):
    review_id = models.AutoField(primary_key=True)
    doctor = models.ForeignKey(Doctor_Information, on_delete=models.CASCADE, null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200, null=True, blank=True)
    message = models.CharField(max_length=1000, null=True, blank=True)
    symptoms = models.CharField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return str(self.patient.username)
    
class DoctorRecordRequest(models.Model):
    STATUS_CHOICES = (
        ('P', 'Pending'),
        ('A', 'Approved'),
        ('D', 'Denied'),
    )

    doctor = models.ForeignKey(Doctor_Information, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    purpose_of_request = models.TextField()
    supporting_documentation = models.FileField(upload_to='support_docs/', null=True, blank=True)
    date_needed = models.DateField(null=True, blank=True)
    request_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')

    def __str__(self):
        return f"Request from {self.doctor} - {self.request_date}"
