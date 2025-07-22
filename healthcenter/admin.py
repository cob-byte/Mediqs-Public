from django.contrib import admin

# Register your models here.
# # we are in same file path --> .models

from .models import Healthcenter_Information, Patient, User

admin.site.register(User)
admin.site.register(Healthcenter_Information)
admin.site.register(Patient)

