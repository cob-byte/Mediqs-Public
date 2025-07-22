import email
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
# from django.contrib.auth.models import User
# from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from healthcenter.models import Patient
from inventory.models import Medicine, MedicalEquipment, MedicalSupply, InventoryManager
from doctor.models import Doctor_Information, Staff
from .utils import searchMedicines
from django.views.decorators.csrf import csrf_exempt


# from django.db.models.signals import post_save, post_delete
# from django.dispatch import receiver


# Create your views here.

# function to return views for the urls
@login_required(login_url="login")
def inventory_single_product(request,pk):
     if request.user.is_authenticated and request.user.is_doctor:
        doctor = Doctor_Information.objects.get(user=request.user)
        medicines = Medicine.objects.get(serial_number=pk)
        context = {'doctor': doctor, 'medicines': medicines}
        return render(request, 'inventory/product-single.html', context)
     
     elif request.user.is_authenticated and request.user.is_staff:
        staff = Staff.objects.get(user=request.user)
        medicines = Medicine.objects.get(serial_number=pk)
        context = {'staff': staff, 'medicines': medicines}
        return render(request, 'inventory/product-single.html', context)
     
     elif request.user.is_authenticated and request.user.is_inventorymanager:
        inventorymanager = InventoryManager.objects.get(user=request.user)
        medicines = Medicine.objects.get(serial_number=pk)
        context = {'inventorymanager': inventorymanager, 'medicines': medicines}
        return render(request, 'inventory/product-single.html', context) 

     else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'doctor-login.html')  
     
# function to return views of medical supply
@login_required(login_url="login")
def inventory_view_equipment(request,pk):
     if request.user.is_authenticated and request.user.is_doctor:
        doctor = Doctor_Information.objects.get(user=request.user)
        equipment = MedicalEquipment.objects.get(serial_number=pk)
        context = {'doctor': doctor, 'equipment': equipment}
        return render(request, 'inventory/medical-equipment-view.html', context)
     
     elif request.user.is_authenticated and request.user.is_staff:
        staff = Staff.objects.get(user=request.user)
        equipment = MedicalEquipment.objects.get(serial_number=pk)
        context = {'staff': staff, 'equipment': equipment}
        return render(request, 'inventory/medical-equipment-view.html', context)
     
     elif request.user.is_authenticated and request.user.is_inventorymanager:
        inventorymanager = InventoryManager.objects.get(user=request.user)
        equipment = MedicalEquipment.objects.get(serial_number=pk)
        context = {'inventorymanager': inventorymanager, 'equipment': equipment}
        return render(request, 'inventory/medical-equipment-view.html', context)  
     
     else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'login.html')  
     
# function to return views of medical equipment
@login_required(login_url="login")
def inventory_view_supply(request,pk):
     if request.user.is_authenticated and request.user.is_doctor:
        doctor = Doctor_Information.objects.get(user=request.user)
        supply = MedicalSupply.objects.get(serial_number=pk)
        context = {'doctor': doctor, 'supply': supply}
        return render(request, 'inventory/medical-supply-view.html', context)
     
     elif request.user.is_authenticated and request.user.is_staff:
        staff = Staff.objects.get(user=request.user)
        supply = MedicalSupply.objects.get(serial_number=pk)
        context = {'staff': staff, 'supply': supply}
        return render(request, 'inventory/medical-supply-view.html', context)
     
     elif request.user.is_authenticated and request.user.is_inventorymanager:
        inventorymanager = InventoryManager.objects.get(user=request.user)
        supply = MedicalSupply.objects.get(serial_number=pk)
        context = {'inventorymanager': inventorymanager, 'supply': supply}
        return render(request, 'inventory/medical-supply-view.html', context) 
        
     else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'doctor-login.html') 
        return render(request, 'login.html')  

@login_required(login_url="login")
def inventory(request):
    if request.user.is_authenticated and request.user.is_doctor: 
        doctor = Doctor_Information.objects.get(user=request.user)
        healthcenter = doctor.health_center
        
        medicines, medical_equipment, medical_supply, search_query = searchMedicines(request)
        
        context = {'medicines': medicines, 'medical_equipment': medical_equipment, 'medical_supply': medical_supply, 'doctor': doctor, 'search_query': search_query}
        return render(request, 'inventory/inventory.html', context)
    
    elif request.user.is_authenticated and request.user.is_staff:
        staff = Staff.objects.get(user=request.user)
        healthcenter = staff.health_center
        
        medicines, medical_equipment, medical_supply, search_query = searchMedicines(request)
        
        context = {'medicines': medicines, 'medical_equipment': medical_equipment, 'medical_supply': medical_supply, 'staff': staff, 'search_query': search_query}
        return render(request, 'inventory/inventory.html', context)
    
    elif request.user.is_authenticated and request.user.is_inventorymanager:
        inventorymanager = InventoryManager.objects.get(user=request.user)
        healthcenter = inventorymanager.health_center
        
        medicines, medical_equipment, medical_supply, search_query = searchMedicines(request)
        
        context = {'medicines': medicines, 'medical_equipment': medical_equipment, 'medical_supply': medical_supply, 'inventorymanager': inventorymanager, 'search_query': search_query}
        return render(request, 'inventory/inventory.html', context)

    else:
        logout(request)
        messages.error(request, 'Not Authorized')
        return render(request, 'login.html')


# Create your views here.
