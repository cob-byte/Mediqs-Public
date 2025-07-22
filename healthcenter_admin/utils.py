from django.db.models import Q
from inventory.models import Medicine, MedicalSupply, MedicalEquipment


def searchMedicines(request):
    
    search_query = ''
    
    if request.GET.get('search_query'):
        search_query = request.GET.get('search_query')
            
    medicine = Medicine.objects.filter(Q(name__icontains=search_query))
    
    return medicine, search_query

def searchMedicalEquipment(request):
    
    search_query = ''
    
    if request.GET.get('search_query'):
        search_query = request.GET.get('search_query')
            
    medicalequipment = MedicalEquipment.objects.filter(Q(name__icontains=search_query))
    
    return medicalequipment, search_query

def searchMedicalSupply(request):
    
    search_query = ''
    
    if request.GET.get('search_query'):
        search_query = request.GET.get('search_query')
            
    medicalsupply = MedicalSupply.objects.filter(Q(name__icontains=search_query))
    
    return medicalsupply, search_query