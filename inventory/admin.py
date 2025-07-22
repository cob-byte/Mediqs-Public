from django.contrib import admin

# Register your models here.
from .models import Medicine, MedicineAdjustment, MedicalEquipment,MedicalEquipmentAdjustment, MedicalSupply, MedicalSupplyAdjustment, InventoryManager

admin.site.register(Medicine)
admin.site.register(MedicineAdjustment)
admin.site.register(MedicalEquipment)
admin.site.register(MedicalEquipmentAdjustment)
admin.site.register(MedicalSupply)
admin.site.register(MedicalSupplyAdjustment)
admin.site.register(InventoryManager)

