from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from healthcenter.models import User, Healthcenter_Information
from inventory.models import InventoryManager
from doctor.models import Doctor_Information, Staff
from .models import Admin_Information, Clinical_Laboratory_Technician, OperationHour
from django.core.exceptions import ValidationError
import re


class AdminUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    # create a style for model form
    def __init__(self, *args, **kwargs):
        super(AdminUserCreationForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
            
class DoctorUserCreationForm(UserCreationForm):
    name = forms.CharField(max_length=200, required=True)
    gender = forms.ChoiceField(choices=(('Male', 'Male'), ('Female', 'Female')), required=True)
    health_center = forms.ModelChoiceField(queryset=Healthcenter_Information.objects.all(), empty_label="Select Health Center", required=True)

    class Meta:
        model = User
        # password1 and password2 are required fields (django default)
        fields = ['name', 'gender','username', 'email', 'password1', 'password2']
        # labels = {
        #     'first_name': 'Name',
        # }

    # create a style for model form
    def __init__(self, *args, **kwargs):
        super(DoctorUserCreationForm, self).__init__(*args, **kwargs)
        
        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control floating'})

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name.isalpha():
            raise ValidationError('Name should contain only alphabetic characters.')

        return name

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email is already in use.')

        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('This username is already in use.')

        return username
    
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if not password1:
            raise ValidationError('Please provide a password.')
        if len(password1) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        if not any(char.isdigit() for char in password1):
            raise ValidationError('Password must contain at least one digit.')
        if not any(char.isalpha() for char in password1):
            raise ValidationError('Password must contain at least one letter.')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password1):
            raise ValidationError('Password must contain at least one special character.')
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError('Passwords do not match.')
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.is_doctor = True
            user.save()

        # Create or update Doctor object for the user
        doctor, created = Doctor_Information.objects.get_or_create(user=user)
        doctor.health_center = self.cleaned_data['health_center']
        doctor.name = self.cleaned_data['name']
        doctor.gender = self.cleaned_data['gender']
        doctor.username = self.cleaned_data['username']
        doctor.save()

class StaffUserCreationForm(UserCreationForm):
    name = forms.CharField(max_length=200, required=True)
    gender = forms.ChoiceField(choices=(('Male', 'Male'), ('Female', 'Female')), required=True)
    health_center = forms.ModelChoiceField(queryset=Healthcenter_Information.objects.all(), empty_label="Select Health Center", required=True)

    class Meta:
        model = User
        # password1 and password2 are required fields (django default)
        fields = ['name', 'gender','username', 'email', 'password1', 'password2']

    # create a style for model form
    def __init__(self, *args, **kwargs):
        super(StaffUserCreationForm, self).__init__(*args, **kwargs)
        
        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control floating'})
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if re.search(r'[^A-Za-z.\s]', name):
            raise ValidationError('Name should only contain letters.')
        
        if len(name) > 70:
            raise ValidationError('Name should not exceed 70 characters.')

        return name

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email is already in use.')

        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('This username is already in use.')

        return username
    
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if not password1:
            raise ValidationError('Please provide a password.')
        if len(password1) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        if not any(char.isdigit() for char in password1):
            raise ValidationError('Password must contain at least one digit.')
        if not any(char.isalpha() for char in password1):
            raise ValidationError('Password must contain at least one letter.')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password1):
            raise ValidationError('Password must contain at least one special character.')
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError('Passwords do not match.')
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.is_staff = True
            user.save()

        # Create or update Staff object for the user
        staff, created = Staff.objects.get_or_create(user=user)
        staff.health_center = self.cleaned_data['health_center']
        staff.name = self.cleaned_data['name']
        staff.gender = self.cleaned_data['gender']
        staff.username = self.cleaned_data['username']
        staff.save()

class LabWorkerCreationForm(UserCreationForm):
    healthcenter = forms.ModelChoiceField(queryset=Healthcenter_Information.objects.all(), empty_label="Select Health Center", required=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    # create a style for model form
    def __init__(self, *args, **kwargs):
        super(LabWorkerCreationForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.is_labworker = True
            user.save()

        # Create or update Clinical Laboratory Technician object for the user
        technician, created = Clinical_Laboratory_Technician.objects.get_or_create(user=user)
        technician.healthcenter = self.cleaned_data['healthcenter']
        technician.save()


class InventoryManagerCreationForm(UserCreationForm):
    health_center = forms.ModelChoiceField(queryset=Healthcenter_Information.objects.all(), empty_label="Select Health Center")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    # create a style for model form
    def __init__(self, *args, **kwargs):
        super(InventoryManagerCreationForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email is already in use.')

        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('This username is already in use.')

        return username
    
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if not password1:
            raise ValidationError('Please provide a password.')
        if len(password1) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        if not any(char.isdigit() for char in password1):
            raise ValidationError('Password must contain at least one digit.')
        if not any(char.isalpha() for char in password1):
            raise ValidationError('Password must contain at least one letter.')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password1):
            raise ValidationError('Password must contain at least one special character.')
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError('Passwords do not match.')
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.is_inventorymanager = True
            user.save()

        # Create or update InventoryManager object for the user
        inventory_manager, created = InventoryManager.objects.get_or_create(user=user)
        inventory_manager.health_center = self.cleaned_data['health_center']
        inventory_manager.save()

# class EditLabWorkerForm(forms.ModelForm):
#     class Meta:
#         model = Clinical_Laboratory_Technician
#         fields = ['name', 'age', 'phone_number', 'featured_image']

#     def __init__(self, *args, **kwargs):
#         super(EditLabWorkerForm, self).__init__(*args, **kwargs)

#         for name, field in self.fields.items():
#             field.widget.attrs.update({'class': 'form-control'})



class AddHealthcenterForm(ModelForm):
    class Meta:
        model = Healthcenter_Information
        fields = ['name','street','city','barangay','zip_code','featured_image','phone_number','email','head_facility']

    def __init__(self, *args, **kwargs):
        super(AddHealthcenterForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

class EditHealthcenterForm(forms.ModelForm):
    class Meta:
        model = Healthcenter_Information
        fields = ['name','street','city','barangay','zip_code','featured_image','phone_number','email','head_facility']

    def __init__(self, *args, **kwargs):
        super(EditHealthcenterForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class EditEmergencyForm(forms.ModelForm):
    class Meta:
        model = Healthcenter_Information
        fields = ['general_bed_no','available_icu_no','regular_cabin_no','emergency_cabin_no','vip_cabin_no']

    def __init__(self, *args, **kwargs):
        super(EditEmergencyForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

class AddEmergencyForm(ModelForm):
    class Meta:
        model = Healthcenter_Information
        fields = ['name','general_bed_no','available_icu_no','regular_cabin_no','emergency_cabin_no','vip_cabin_no']

    def __init__(self, *args, **kwargs):
        super(AddEmergencyForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})



class AdminForm(ModelForm):
    class Meta:
        model = Admin_Information
        fields = ['name', 'email', 'phone_number', 'role','featured_image']

    def __init__(self, *args, **kwargs):
         super(AdminForm, self).__init__(*args, **kwargs)

         for name, field in self.fields.items():
             field.widget.attrs.update({'class': 'form-control'})

