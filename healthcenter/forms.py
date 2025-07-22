from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User

from .models import Patient, User, Healthcenter_Information
# Create a custom form that inherits from user form (reason --> for modify and customize)

from django.core.exceptions import ValidationError
from datetime import date
import re

class CustomUserCreationForm(UserCreationForm):
    health_center = forms.ModelChoiceField(queryset=Healthcenter_Information.objects.all(), empty_label="", required=True)

    class Meta:
        model = User
        # password1 and password2 are required fields (django default)
        fields = ['username', 'email', 'password1', 'password2', 'health_center']
        # labels = {
        #     'first_name': 'Name',
        # }

    # create a style for model form
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control floating'})

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise ValidationError('Please provide a username.')
        if len(username) < 6:
            raise ValidationError('Username must be at least 6 characters long.')
        if not username.isalnum():
            raise ValidationError('Username can only contain alphanumeric characters.')
    
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError('Please provide an email.')
        if not re.match(r'^[\w.-]+@[\w.-]+\.\w+$', email):
            raise ValidationError('Invalid email format.')
        return email

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

    def clean_health_center(self):
        health_center = self.cleaned_data.get('health_center')
        if not health_center:
            raise ValidationError('Please select a health center.')
        return health_center

    def save(self, commit=True):
        user = super().save(commit=False)
        user.raw_password = self.cleaned_data.get('password1')
        user.is_patient = True

        # Always save User instance
        user.save()

        # Create or update Patient object for the user
        patient, created = Patient.objects.get_or_create(user=user)
        patient.health_center = self.cleaned_data['health_center']
        patient.save()

        return user

def validate_phone_number(value):
    if not re.match(r'^(\+639|0)\d{10}$', value):
        raise ValidationError('Invalid phone number format: Must start with +639 or 0 and be followed by a 10-digit number')

class PatientForm(forms.ModelForm):
    dob = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True, label="Date of Birth"
    )

    phone_number = forms.CharField(max_length=15, validators=[validate_phone_number])
    
    class Meta:
        model = Patient
        fields = ['name', 'age', 'dob', 'gender', 'blood_group',
                    'phone_number', 'address']


    def __init__(self, *args, **kwargs):
        super(PatientForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise ValidationError('Please provide a name.')
        
        if re.search(r'[^A-Za-z.\s]', name):
            raise ValidationError('Name should only contain letters.')
        
        if len(name) > 70:
            raise ValidationError('Name should not exceed 70 characters.')
        
        return name

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if not age or age < 0:
            raise ValidationError('Please provide a valid age.')
        if not str(age).isnumeric():
            raise ValidationError('Age should only contain numeric characters.')
            
        return age

    def clean_dob(self):
        dob = self.cleaned_data.get('dob')
        if not dob:
            raise ValidationError('Please provide a date of birth.')
        
        if dob > date.today():
            raise ValidationError('Please provide a valid date of birth.')
        
        return dob

    def clean_gender(self):
        gender = self.cleaned_data.get('gender')
        if not gender:
            raise ValidationError('Please select a gender.')
        return gender
        

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number:
            raise ValidationError('Please provide a phone number.')
        return phone_number

    def clean_address(self):
        address = self.cleaned_data.get('address')
        if not address:
            raise ValidationError('Please provide an address.')
        return address

class ExtraInfoForm(forms.ModelForm):
    dob = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True, label="Date of Birth"
    )

    phone_number = forms.CharField(max_length=15, validators=[validate_phone_number])
    
    class Meta:
        model = Patient
        fields = ['name', 'age', 'dob', 'gender', 'blood_group',
                    'phone_number', 'address','father_name','mother_name','fam_num','barangay_num','birth_weight','birth_height','place_birth']


    def __init__(self, *args, **kwargs):
        super(ExtraInfoForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise ValidationError('Please provide a name.')
        
        if re.search(r'[^A-Za-z.\s]', name):
            raise ValidationError('Name should only contain letters.')
        
        if len(name) > 70:
            raise ValidationError('Name should not exceed 70 characters.')
    
        return name

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if not age or age < 0:
            raise ValidationError('Please provide a valid age.')
        if not str(age).isnumeric():
            raise ValidationError('Age should only contain numeric characters.')
        return age

    def clean_dob(self):
        dob = self.cleaned_data.get('dob')
        if not dob:
            raise ValidationError('Please provide a date of birth.')
        
        if dob > date.today():
            raise ValidationError('Please provide a valid date of birth.')
        
        return dob

    def clean_gender(self):
        gender = self.cleaned_data.get('gender')
        if not gender:
            raise ValidationError('Please select a gender.')
        return gender
        

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number:
            raise ValidationError('Please provide a phone number.')
        return phone_number

    def clean_address(self):
        address = self.cleaned_data.get('address')
        if not address:
            raise ValidationError('Please provide an address.')
        return address
    
    def clean_father_name(self):
        father_name = self.cleaned_data.get('father_name')
        if not father_name:
            raise ValidationError('Please provide the father\'s name.')
        
        if re.search(r'[^A-Za-z\s]', father_name):
            raise ValidationError('Father\'s name should only contain letters and spaces.')
        
        if len(father_name) > 70:
            raise ValidationError('Father\'s name should not exceed 70 characters.')
        
        return father_name

    def clean_mother_name(self):
        mother_name = self.cleaned_data.get('mother_name')
        if not mother_name:
            raise ValidationError('Please provide the mother\'s name.')
        
        if re.search(r'[^A-Za-z\s]', mother_name):
            raise ValidationError('Mother\'s name should only contain letters and spaces.')
        
        if len(mother_name) > 70:
            raise ValidationError('Mother\'s name should not exceed 70 characters.')
        
        return mother_name
    
    def clean_fam_num(self):
        fam_num = self.cleaned_data.get('fam_num')
        if not fam_num:
            raise ValidationError('Please provide a valid family number.')
        try:
            fam_num = int(fam_num)
            if fam_num < 0:
                raise ValidationError('Please provide a valid family number.')
        except ValueError:
            raise ValidationError('Please provide a valid family number.')
        return fam_num

    def clean_barangay_num(self):
        barangay_num = self.cleaned_data.get('barangay_num')
        if not barangay_num:
            raise ValidationError('Please provide a valid barangay number.')
        try:
            barangay_num = int(barangay_num)
            if barangay_num < 0:
                raise ValidationError('Please provide a valid barangay number.')
        except ValueError:
            raise ValidationError('Please provide a valid barangay number.')
        return barangay_num

    def clean_birth_weight(self):
        birth_weight = self.cleaned_data.get('birth_weight')
        if not birth_weight:
            raise ValidationError('Please provide a valid birth weight.')
        try:
            birth_weight = int(birth_weight)
            if birth_weight < 0:
                raise ValidationError('Please provide a valid birth weight.')
        except ValueError:
            raise ValidationError('Please provide a valid birth weight.')
        return birth_weight

    def clean_birth_height(self):
        birth_height = self.cleaned_data.get('birth_height')
        if not birth_height:
            raise ValidationError('Please provide a valid birth height.')
        try:
            birth_height = int(birth_height)
            if birth_height < 0:
                raise ValidationError('Please provide a valid birth height.')
        except ValueError:
            raise ValidationError('Please provide a valid birth height.')
        return birth_height

    def clean_place_birth(self):
        place_birth = self.cleaned_data.get('place_birth')
        if not place_birth:
            raise ValidationError('Please provide the place of birth.')
        return place_birth


class PasswordResetForm(ModelForm):
    class Meta:
        model = User
        fields = ['email']

    # create a style for model form
    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control floating]'})