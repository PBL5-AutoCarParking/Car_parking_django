from django.forms.utils import ValidationError
from .models import Customer, Car, ParkingRecord, ParkingSlot, Invoice
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Customer
from bootstrap_modal_forms.forms import BSModalModelForm, BSModalForm
from bootstrap_modal_forms.mixins import PopRequestMixin, CreateUpdateAjaxMixin
from django.contrib.auth import get_user_model
from django.core.signals import setting_changed
from django.dispatch import receiver
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import re

User = get_user_model()  # QUan trọng


class MyRegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True,
                             help_text='Required. Enter a valid email address.')
    first_name = forms.CharField(
        max_length=30, required=True, help_text='Required. Enter your first name.')

    last_name = forms.CharField(max_length=30, required=True, help_text='Required. Enter your last name.')

    phone_number = forms.CharField(
        max_length=30, required=True, help_text='Required. Enter your phone number.')
    card_number = forms.CharField(
        max_length=100, required=True, help_text='Required. Enter your card number.')

    class Meta:
        model = User  # 'confirm_password',
        fields = ['email', 'password1', 'password2',
                  'first_name', 'last_name', 'phone_number', 'card_number']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'This email address is already in use.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already in use.')
        return username

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if len(password1) < 8:
            raise forms.ValidationError('Password must be at least 8 characters long.')
        if not re.search('[A-Z]', password1):
            raise forms.ValidationError('Password must contain at least one uppercase letter.')
        if not re.search('[0-9]', password1):
            raise forms.ValidationError('Password must contain at least one number.')
        # if not re.search('[^A-Za-z0-9]', password1):
        #     raise forms.ValidationError('Password must contain at least one special character.')
        return password1

    def clean_confirm_password(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 != password2:
            raise forms.ValidationError('Mật khẩu nhập lại không trùng khớp ')
        return password2


class EmailVerificationForm(forms.Form):
    token = forms.UUIDField()


class CustomerForm(BSModalModelForm):
    def __init__(self, *args, **kwargs):
        super(CustomerForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs = {
            'class': 'form-control col-md-6'
        }
        self.fields['last_name'].widget.attrs = {
            'class': 'form-control col-md-6'
        }
        self.fields['phone_number'].widget.attrs = {
            'class': 'form-control col-md-6'
        }
        self.fields['location'].widget.attrs = {
            'class': 'form-control col-md-6'
        }

    class Meta:
        model = Customer
        fields = ('first_name', 'last_name', 'phone_number', 'card_number', 'location')


class UserForm(BSModalModelForm):
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs = {
            'class': 'form-control col-md-6'
        }
        self.fields['first_name'].widget.attrs = {
            'class': 'form-control col-md-6'
        }
        self.fields['last_name'].widget.attrs = {
            'class': 'form-control col-md-6'
        }
        self.fields['email'].widget.attrs = {
            'class': 'form-control col-md-6'
        }
        self.fields['password'].widget.attrs = {
            'class': 'form-control col-md-6'
        }

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password')


# class UserActiveForm(Mode)
class CarFormMixin(forms.ModelForm):
    def clean_license_plate(self):
        license_plate = self.cleaned_data['license_plate']
        existing_car = Car.objects.filter(license_plate=license_plate).exists()
        if existing_car:
            raise forms.ValidationError('This license plate is already in use.')
        if not license_plate[:2].isdigit():
            raise forms.ValidationError('License plate must start with two digits.')
        if len(license_plate) > 12:
            raise forms.ValidationError('License plate must be a maximum of 12 characters.')
        return license_plate

class CarForm(CarFormMixin, BSModalModelForm):
    # Loi tham so nay forms.ModelForm
    owner = forms.ModelChoiceField(queryset=Customer.objects.all(), label='Owner', widget=forms.Select(attrs={'class': 'form-control col-md-6'}),to_field_name='__str__')
    def __init__(self, *args, **kwargs):
        super(CarForm, self).__init__(*args, **kwargs)
        self.fields['license_plate'].widget.attrs = {
            'class': 'form-control col-md-6'
        }
        self.fields['car_model'].widget.attrs = {
            'class': 'form-control col-md-6'
        }
        self.fields['car_color'].widget.attrs = {
            'class': 'form-control col-md-6'
        }
    class Meta:
        model = Car
        exclude = ['timestamp']
        fields = ['license_plate',
                  'car_model', 'car_color', 'owner' , 'image']

class CreateCarForm(BSModalModelForm):
    owner = forms.ModelChoiceField(queryset=Customer.objects.all(), label='Owner', widget=forms.Select(attrs={'class': 'form-control col-md-6'}),to_field_name='__str__')
    def __init__(self, *args, **kwargs):
        super(CreateCarForm, self).__init__(*args, **kwargs)
        self.fields['license_plate'].widget.attrs = {
            'class': 'form-control col-md-6'
        }
        self.fields['car_model'].widget.attrs = {
            'class': 'form-control col-md-6'
        }
        self.fields['car_color'].widget.attrs = {
            'class': 'form-control col-md-6'
        }
    def clean_license_plate(self):
        license_plate = self.cleaned_data['license_plate']
        existing_car = Car.objects.filter(license_plate=license_plate).first()
        if existing_car:
            raise forms.ValidationError('This license plate is already in use.')
        if not license_plate[:2].isdigit():
            raise forms.ValidationError('License plate must start with two digits.')
        if len(license_plate) > 12:
            raise forms.ValidationError('License plate must be a maximum of 12 characters.')
        return license_plate
    class Meta:
        model = Car
        exclude = ['timestamp']
        fields = ['license_plate',
                  'car_model', 'car_color', 'owner' , 'image']

class CarUpdateForm(forms.ModelForm):
    owner = forms.ModelChoiceField(queryset=Customer.objects.all())

    class Meta:
        model = Car
        fields = ['license_plate', 'owner', 'car_model', 'car_color']


class CreateParkingRecordForm(forms.ModelForm):
    class Meta:
        model = ParkingRecord
        fields = ['car', 'parking_slot']
        widgets = {
            'car': forms.Select(attrs={'class': 'form-control col-md-6'}),
            'parking_slot': forms.Select(attrs={'class': 'form-control col-md-6'})
        }


class UpdateParkingRecordForm(BSModalModelForm):
    class Meta:
        model = ParkingRecord
        fields = ['car', 'parking_slot', 'total_cost', 'is_paid', 'exit_time']
        widgets = {
            'car': forms.Select(attrs={'class': 'form-control col-md-6'}),
            'parking_slot': forms.Select(attrs={'class': 'form-control col-md-6'}),
            'total_cost': forms.NumberInput(attrs={'class': 'form-control col-md-6'}),
            'is_paid': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'exit_time': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }


class ParkingRecordDetailForm(BSModalModelForm):
    class Meta:
        model = ParkingRecord
        fields = ('car', 'parking_slot',
                  'exit_time', 'total_cost', 'is_paid')

        def __init__(self, *args, **kwargs):
            super(CarForm, self).__init__(*args, **kwargs)
            self.fields['car'].widget.attrs = {
                'class': 'form-control col-md-6'
            }
            self.fields['parking_slot'].widget.attrs = {
                'class': 'form-control col-md-6'
            }
            self.fields['exit_time'].widget.attrs = {
                'class': 'form-control col-md-6'
            }
            self.fields['total_cost'].widget.attrs = {
                'class': 'form-control col-md-6'
            }
            self.fields['is_paid'].widget.attrs = {
                'class': 'form-control col-md-6'
            }


class CreateUserCarForm(BSModalModelForm):
    class Meta:
        model = Car
        fields = ['license_plate', 'car_model', 'car_color', 'image']
        widgets = {
            'license_plate': forms.TextInput(attrs={'class': 'form-control col-md-6'}),
            'car_model': forms.TextInput(attrs={'class': 'form-control col-md-6'}),
            'car_color': forms.TextInput(attrs={'class': 'form-control col-md-6'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'})
        }

class UpdateUserCarForm(BSModalModelForm):
    class Meta:
        model = Car
        fields = ['license_plate', 'car_model', 'car_color', 'image']
        widgets = {
            'license_plate': forms.TextInput(attrs={'class': 'form-control col-md-6'}),
            'car_model': forms.TextInput(attrs={'class': 'form-control col-md-6'}),
            'car_color': forms.TextInput(attrs={'class': 'form-control col-md-6'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'})
        }


class UserCarModelForm(BSModalModelForm):
    class Meta:
        model = Car
        fields = ['license_plate', 'car_model', 'car_color','owner']


class UpdateInvoiceForm(forms.Form):
    class Meta:
        model = Invoice
        PAYMENT_METHOD_CHOICES = (
            ('direct', 'Direct'),
            ('online', 'Online'),
        )
        payment_method = forms.ChoiceField(choices=PAYMENT_METHOD_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
        fields = ['invoice_date', 'due_date', 'payment_date', 'payment_method', 'payment_status']
        widgets = {
            'invoice_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
        }
