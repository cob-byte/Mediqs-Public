from django.contrib import admin

# Register your models here.
from .models import Admin_Information, Clinical_Laboratory_Technician, OperationHour, service ,Test_Information

admin.site.register(Admin_Information)

admin.site.register(Clinical_Laboratory_Technician)

admin.site.register(OperationHour)

admin.site.register(service)

admin.site.register(Test_Information)
