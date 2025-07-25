from django.db.models import Q
from .models import Patient, User, Healthcenter_Information
from doctor.models import Doctor_Information, Appointment
from healthcenter_admin.models import specialization, service


def searchPatients(request):
    
    search_query = ''
    
    if request.GET.get('search_query'):
        search_query = request.GET.get('search_query')
        
    #skills = Skill.objects.filter(name__icontains=search_query)
    
    patient = Patient.objects.filter(
        Q(patient_id__icontains=search_query))
    
    return patient, search_query
