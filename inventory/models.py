from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.conf import settings
import uuid
from doctor.models import Prescription
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone

from healthcenter.models import User, Patient, Healthcenter_Information


# Create your models here.
def validate_time_not_in_future(value):
    now_time = timezone.now().time()
    if value > now_time:
        raise ValidationError("The time cannot be in the future.")

class InventoryManager(models.Model):
    inventorymanager_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='inventorymanager')
    name = models.CharField(max_length=200, null=True, blank=True)
    username = models.CharField(max_length=200, null=True, blank=True)
    degree = models.CharField(max_length=200, null=True, blank=True)
    featured_image = models.ImageField(upload_to='doctors/', default='pharmacist/user-default.png', null=True, blank=True)
    email = models.EmailField(max_length=200, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True) # Adjust max_length as needed
    age = models.IntegerField(null=True, blank=True)
    health_center = models.ForeignKey(Healthcenter_Information, on_delete=models.CASCADE, null=True, blank=True)

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
 
class Medicine(models.Model):
    MEDICINE_TYPE = (
        ('tablets', 'tablets'),
        ('syrup', 'syrup'),
        ('capsule', 'capsule'),
        ('general', 'general'),
    )

    
    MEDICINE_CATEGORY = (
        ('fever', 'fever'),
        ('pain', 'pain'),
        ('cough', 'cough'),
        ('cold', 'cold'),
        ('flu', 'flu'),
        ('diabetes', 'diabetes'),
        ('eye', 'eye'),
        ('ear', 'ear'),
        ('allergy', 'allergy'),
        ('asthma', 'asthma'),
        ('bloodpressure', 'bloodpressure'),
        ('heartdisease', 'heartdisease'),
        ('vitamins', 'vitamins'),
        ('digestivehealth', 'digestivehealth'),
        ('skin', 'skin'),
        ('infection', 'infection'),
        ('nurological', 'nurological'),
    )
    
    serial_number = models.AutoField(primary_key=True)
    item_code = models.CharField(max_length=200, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    weight = models.CharField(max_length=200, null=True, blank=True)
    featured_image = models.ImageField(upload_to='medicines/', default='medicines/Medicine.png', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    medicine_type = models.CharField(max_length=200, choices=MEDICINE_TYPE, null=True, blank=True)
    medicine_category = models.CharField(max_length=200, choices=MEDICINE_CATEGORY, null=True, blank=True)
    manufacturer = models.CharField(max_length=200, null=True, blank=True)
    expiration_date = models.DateField(validators=[MinValueValidator(limit_value=timezone.now().date())])
    health_center = models.ForeignKey(Healthcenter_Information, on_delete=models.CASCADE, null=True, blank=True)

    location = models.CharField(max_length=200, null=True, blank=True)
    sponsoredby = models.CharField(max_length=200, null=True, blank=True)
    receivedby = models.CharField(max_length=200, null=True, blank=True)
    dor = models.DateField(validators=[MinValueValidator(limit_value=timezone.now().date())])
    tor = models.TimeField(validators=[validate_time_not_in_future])
    remarks= models.CharField(max_length=200, null=True, blank=True)


    @property
    def stock_quantity(self):
        adjustments = MedicineAdjustment.objects.filter(medicine=self, medicine__health_center=self.health_center)
        total_in = adjustments.filter(adjustment_type='in').aggregate(total_in=Coalesce(Sum('quantity'), 0))['total_in']
        total_out = adjustments.filter(adjustment_type='out').aggregate(total_out=Coalesce(Sum('quantity'), 0))['total_out']
        return total_in - total_out
    def __str__(self):
        return str(self.name)
    
class MedicineAdjustment(models.Model):
    ADJUSTMENT_TYPE = (
        ('in', 'In'),
        ('out', 'Out'),
    )
    
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    adjustment_type = models.CharField(max_length=3, choices=ADJUSTMENT_TYPE)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    inventory_manager = models.ForeignKey(InventoryManager, on_delete=models.CASCADE)
    sponsored_by = models.CharField(max_length=200, null=True, blank=True)
    
    def __str__(self):
        return f"{self.medicine.name} ({self.adjustment_type} {self.quantity})"
    
class MedicalEquipment(models.Model):
    EQUIPMENT_SUBCATEGORY = (
        ('diagnostic', 'Diagnostic Equipments'),
        ('monitoring', 'Monitoring Equipments'),
        ('surgical', 'Surgical Instruments'),
        ('imaging', 'Medical Imaging Equipment'),
        ('rehabilitation', 'Rehabilitation and Mobility Aids'),
    )

    serial_number = models.AutoField(primary_key=True)
    model_number = models.CharField(max_length=200, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    subcategory = models.CharField(max_length=200, choices=EQUIPMENT_SUBCATEGORY, null=True, blank=True)
    manufacturer = models.CharField(max_length=200, null=True, blank=True)
    supplier = models.CharField(max_length=200, null=True, blank=True)
    date_of_purchase = models.DateField()
    warranty = models.DateField(validators=[MinValueValidator(limit_value=timezone.now().date())])
    featured_image = models.ImageField(upload_to='medicines/', default='medicines/Medical Equipment.png', null=True, blank=True)
    health_center = models.ForeignKey(Healthcenter_Information, on_delete=models.CASCADE, null=True, blank=True)

    location = models.CharField(max_length=200, null=True, blank=True)
    sponsoredby = models.CharField(max_length=200, null=True, blank=True)
    receivedby = models.CharField(max_length=200, null=True, blank=True)
    dor = models.DateField(validators=[MinValueValidator(limit_value=timezone.now().date())])
    tor = models.TimeField(validators=[validate_time_not_in_future])
    remarks= models.CharField(max_length=200, null=True, blank=True)

    def clean(self):
        if self.date_of_purchase > self.warranty:
            raise ValidationError('Date of purchase must be earlier than warranty date')
        elif self.warranty < self.date_of_purchase:
            raise ValidationError('Warranty date must be later than date of purchase')
        
    @property
    def stock_quantity(self):
        adjustments = MedicalEquipmentAdjustment.objects.filter(medicalequipment=self, medicalequipment__health_center=self.health_center)
        total_in = adjustments.filter(adjustment_type='in').aggregate(total_in=Coalesce(Sum('quantity'), 0))['total_in']
        total_out = adjustments.filter(adjustment_type='out').aggregate(total_out=Coalesce(Sum('quantity'), 0))['total_out']
        return total_in - total_out

    def __str__(self):
        return str(self.name)
    
class MedicalEquipmentAdjustment(models.Model):
    ADJUSTMENT_TYPE = (
        ('in', 'In'),
        ('out', 'Out'),
    )
    
    medicalequipment = models.ForeignKey(MedicalEquipment, on_delete=models.CASCADE)
    adjustment_type = models.CharField(max_length=3, choices=ADJUSTMENT_TYPE)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    inventory_manager = models.ForeignKey(InventoryManager, on_delete=models.CASCADE)
    sponsored_by = models.CharField(max_length=200, null=True, blank=True)
    
    def __str__(self):
        return f"{self.medicalequipment.name} ({self.adjustment_type} {self.quantity})"

class MedicalSupply(models.Model):
    SUPPLY_SUBCATEGORY = (
        ('ppe', 'Personal Protective Equipments (PPEs)'),
        ('consumables', 'Medical Consumables'),
        ('wound_care', 'Wound Care Supplies'),
        ('surgical', 'Surgical Supplies'),
        ('diagnostic', 'Diagnostic Test Kits'),
    )
    
    serial_number = models.AutoField(primary_key=True)
    item_code = models.CharField(max_length=200, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    subcategory = models.CharField(max_length=200, choices=SUPPLY_SUBCATEGORY, null=True, blank=True)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    supplier = models.CharField(max_length=200, null=True, blank=True)
    expiration_date = models.DateField(validators=[MinValueValidator(limit_value=timezone.now().date())])
    description = models.TextField(null=True, blank=True)
    featured_image = models.ImageField(upload_to='medicines/', default='medicines/Medical Supply.png', null=True, blank=True)
    health_center = models.ForeignKey(Healthcenter_Information, on_delete=models.CASCADE, null=True, blank=True)

    location = models.CharField(max_length=200, null=True, blank=True)
    sponsoredby = models.CharField(max_length=200, null=True, blank=True)
    receivedby = models.CharField(max_length=200, null=True, blank=True)
    dor = models.DateField(validators=[MinValueValidator(limit_value=timezone.now().date())])
    tor = models.TimeField(validators=[validate_time_not_in_future])
    remarks= models.CharField(max_length=200, null=True, blank=True)

    @property
    def stock_quantity(self):
        adjustments = MedicalSupplyAdjustment.objects.filter(medicalsupply=self, medicalsupply__health_center=self.health_center)
        total_in = adjustments.filter(adjustment_type='in').aggregate(total_in=Coalesce(Sum('quantity'), 0))['total_in']
        total_out = adjustments.filter(adjustment_type='out').aggregate(total_out=Coalesce(Sum('quantity'), 0))['total_out']
        return total_in - total_out

    def __str__(self):
        return str(self.name)

class MedicalSupplyAdjustment(models.Model):
    ADJUSTMENT_TYPE = (
        ('in', 'In'),
        ('out', 'Out'),
    )
    
    medicalsupply = models.ForeignKey(MedicalSupply, on_delete=models.CASCADE)
    adjustment_type = models.CharField(max_length=3, choices=ADJUSTMENT_TYPE)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    inventory_manager = models.ForeignKey(InventoryManager, on_delete=models.CASCADE)
    sponsored_by = models.CharField(max_length=200, null=True, blank=True)
    
    def __str__(self):
        return f"{self.medicalsupply.name} ({self.adjustment_type} {self.quantity})"