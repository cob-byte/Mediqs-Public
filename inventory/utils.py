from django.contrib import messages
from django.db.models import Q
from .models import Medicine, MedicalEquipment, MedicalSupply,InventoryManager
from doctor.models import Doctor_Information,Staff
from healthcenter.models import Healthcenter_Information


#def searchMedicines(request):
#   if request.user.is_authenticated and request.user.is_doctor:
#      doctor = Doctor_Information.objects.get(user=request.user)
#        health_center = Healthcenter_Information.objects.get(health_center=doctor.health_center)
#       search_query = ''
#       
#       if request.GET.get('search_query'):
#           search_query = request.GET.get('search_query')
                
 #      medicines = set(Medicine.objects.filter(Q(name__icontains=search_query)).filter(health_center=health_center))
 #       medical_equipment = set(MedicalEquipment.objects.filter(Q(name__icontains=search_query)).filter(health_center=health_center))
#     medical_supply = set(MedicalSupply.objects.filter(Q(name__icontains=search_query)).filter(health_center=health_center))

#       medicine = medicines.union(medical_equipment.union(medical_supply))
        
def searchMedicines(request):
    if request.user.is_authenticated:
        if request.user.is_doctor:
            doctor = Doctor_Information.objects.get(user=request.user)
            health_center = Healthcenter_Information.objects.get(healthcenter_id=doctor.health_center.healthcenter_id)
        elif request.user.is_inventorymanager:
            inventory_manager = InventoryManager.objects.get(user=request.user)
            health_center = Healthcenter_Information.objects.get(healthcenter_id=inventory_manager.health_center.healthcenter_id)
        elif request.user.is_staff:
            staff = Staff.objects.get(user=request.user)
            health_center = Healthcenter_Information.objects.get(healthcenter_id=staff.health_center.healthcenter_id)
        else:
            messages.error(request, "No Authorized Access")

        search_query = ''

        if request.GET.get('search_query'):
            search_query = request.GET.get('search_query')

        medicines = Medicine.objects.filter(Q(name__icontains=search_query), health_center=health_center)
        medical_equipment = MedicalEquipment.objects.filter(Q(name__icontains=search_query), health_center=health_center)
        medical_supply = MedicalSupply.objects.filter(Q(name__icontains=search_query), health_center=health_center)

        return medicines, medical_equipment, medical_supply, search_query






