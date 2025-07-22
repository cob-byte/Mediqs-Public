from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User
from healthcenter.models import User
from .models import Doctor_Information, Staff
# # Create a custom form that inherits from user form (reason --> for modify and customize)


class DoctorForm(ModelForm):
    class Meta:
        model = Doctor_Information
        fields = ['name', 'email', 'phone_number', 'degree', 'department',
                  'featured_image', 'visiting_hour', 'dob', 'health_center']

    def __init__(self, *args, **kwargs):
        super(DoctorForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

class StaffForm(ModelForm):
    class Meta:
        model = Staff
        fields = ['name', 'email', 'phone_number', 'health_center']

    def __init__(self, *args, **kwargs):
        super(StaffForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})