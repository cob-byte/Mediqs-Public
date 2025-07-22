from django.db import models
from django.forms import ValidationError

import healthcenter
from healthcenter.models import User, Healthcenter_Information
# from doctor.models import Doctor_Information


# Create your models here.

class Admin_Information(models.Model):
    ADMIN_TYPE = (
        ('healthcenter', 'healthcenter'),
        ('laboratory', 'laboratory'),
        ('inventory', 'inventory'),
    )

    admin_id = models.AutoField(primary_key=True, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='healthcenter_admin')
    username = models.CharField(null=True, blank=True, max_length=200)
    name = models.CharField(max_length=200, null=True, blank=True)
    featured_image = models.ImageField(upload_to='admin/', default='admin/user-default.png', null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True) # Adjust max_length as needed
    email = models.CharField(max_length=200, null=True, blank=True)
    role = models.CharField(max_length=200, choices=ADMIN_TYPE, null=True, blank=True)
    healthcenter = models.ForeignKey(Healthcenter_Information, on_delete=models.SET_NULL, null=True, blank=True)

    #New Info
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    zip_code = models.CharField(max_length=12, null=True, blank=True)

    def __str__(self):
        return str(self.user.username)


class Clinical_Laboratory_Technician(models.Model):
    technician_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='technician')
    name = models.CharField(max_length=200, null=True, blank=True)
    username = models.CharField(max_length=200, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    email = models.EmailField(max_length=200, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True) # Adjust max_length as needed
    featured_image = models.ImageField(upload_to='technician/', default='technician/user-default.png', null=True, blank=True)
    healthcenter = models.ForeignKey(Healthcenter_Information, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return str(self.user.username)

class OperationHour(models.Model):
    DAY_CHOICES = (
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
        ('SAT', 'Saturday'),
        ('SUN', 'Sunday')
    )

    healthcenter = models.ForeignKey(Healthcenter_Information, on_delete=models.CASCADE, null=True, blank=True)
    day = models.CharField(max_length=3, choices=DAY_CHOICES, default='MON')
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.healthcenter} - {self.day} - {self.start_time} to {self.end_time}"
    
    def validate_time_range(self):
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError("Start time must be before end time.")
        
    class Meta:
        unique_together = ('healthcenter', 'day',)


class service(models.Model):
    service_id = models.AutoField(primary_key=True)
    service_name = models.CharField(max_length=200, null=True, blank=True)
    # doctor = models.ForeignKey(Doctor_Information, on_delete=models.CASCADE, null=True, blank=True)
    healthcenter = models.ForeignKey(Healthcenter_Information, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        val1 = str(self.service_name)
        val2 = str(self.healthcenter)
        val3 = val1 + ' - ' + val2
        return str(val3)

class Test_Information(models.Model):
    test_id = models.AutoField(primary_key=True)
    test_name = models.CharField(max_length=200, null=True, blank=True)
    test_price = models.CharField(max_length=200, null=True, blank=True)


    def __str__(self):
        return str(self.test_name)

    

