from django.db.models import Q
from .models import Patient, User, Healthcenter_Information
from doctor.models import Doctor_Information, Appointment
from healthcenter_admin.models import service
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


def searchDoctors(request):
    
    search_query = ''
    
    if request.GET.get('search_query'):
        search_query = request.GET.get('search_query')
        
    #skills = Skill.objects.filter(name__icontains=search_query)
    
    doctors = Doctor_Information.objects.all().distinct().filter(
        Q(name__icontains=search_query) |
        Q(health_center__name__icontains=search_query) |  
        Q(department__icontains=search_query))
    
    return doctors, search_query



def searchHealthcenters(request):
    
    search_query = ''
    
    if request.GET.get('search_query'):
        search_query = request.GET.get('search_query')
        
    
    healthcenters = Healthcenter_Information.objects.distinct().filter(Q(name__icontains=search_query))
    
    return healthcenters, search_query


def paginateHealthcenters(request, healthcenters, results):

    page = request.GET.get('page')
    paginator = Paginator(healthcenters, results)

    try:
        healthcenters = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        healthcenters = paginator.page(page)
    except EmptyPage:
        # display last page if page is out of range
        page = paginator.num_pages
        healthcenters = paginator.page(page)
        
    
    # if there are many pages, we will see some at a time in the pagination bar (range window)
    # leftIndex(left button) = current page no. - 4 
    leftIndex = (int(page) - 4)
    if leftIndex < 1:
        # if leftIndex is less than 1, we will start from 1
        leftIndex = 1

    rightIndex = (int(page) + 5)
    if rightIndex > paginator.num_pages:
        rightIndex = paginator.num_pages + 1

    custom_range = range(leftIndex, rightIndex)
    # return custom_range, projects, paginator
    return custom_range, healthcenters


# def searchHealthcenterDoctors(request, pk):
    
#     search_query = ''
    
#     if request.GET.get('search_query'):
#         search_query = request.GET.get('search_query')
        
    
#     departments = healthcenter_department.object.filter(healthcenter_department_id=pk).filter(
#         Q(doctor__name__icontains=search_query) |  
#         Q(doctor__department__icontains=search_query))
    
#     return departments, search_query

def searchHealthcenterDoctors(request, pk):
    
    search_query = ''
    
    if request.GET.get('search_query'):
        search_query = request.GET.get('search_query')
            
    doctors = Doctor_Information.objects.filter(health_center=pk).filter(
        Q(name__icontains=search_query))
    
    # doctors = Doctor_Information.objects.filter(department_name=departments).filter(
    #     Q(name__icontains=search_query) |
    #     Q(specialization_name__name__icontains=search_query))
    
    return doctors, search_query



# products = Products.objects.filter(price__range=[10, 100])
