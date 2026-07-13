from django import forms
from .models import Location
from django.core.validators import MinValueValidator, MaxValueValidator
import datetime
from django.utils.timezone import make_aware
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class TripPredictionForm(forms.Form):
    #! ModelChoiceField, veri tabanındaki lokasyonları seçilebilir forma getirir.
    location = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        label="Choose a location",
        empty_label="Please select a Location!"
    )

    target_datetime = forms.DateTimeField(
        label="Date and Hour",

        validators=[
            MinValueValidator(make_aware(datetime.datetime(2015, 1, 1, 0, 0))),
            MaxValueValidator(make_aware(datetime.datetime(2016, 12, 31, 23, 59)))
        ],

        widget=forms.DateTimeInput( # HTML görünüm değiştirir.
            attrs={
                'type': 'datetime-local',
                'min': '2015-01-01T00:00',
                'max': '2016-12-31T23:59'
            }
        )
    )

    predictor_name = forms.CharField(
        label="Name and Surname",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Örn: Taha Soylu'
        })
    )

class ShowLocationsBasedOnDate(forms.Form):
    """User belli bir andaki taxi count karşilaştirmasi isterse dolduracagi form."""
    target_datetime = forms.DateTimeField(
        label="Date and Hour",

        validators=[
            MinValueValidator(make_aware(datetime.datetime(2015, 1, 1, 0, 0))),
            MaxValueValidator(make_aware(datetime.datetime(2016, 12, 31, 23, 59)))
        ],

        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'min': '2015-01-01T00:00',
                'max': '2016-12-31T23:59'
            }
        )
    )

class DriverForm(forms.Form):
    """Taxi sürücüsü tarafindan girilen veriler"""
    driver_name = forms.CharField(
        label="Name and Surname",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Örn: Taha Soylu'
        })
    )

    passenger_count = forms.IntegerField(
        label="Passenger Count",
        min_value=0
    )

    location = forms.ModelChoiceField(
        queryset=Location.objects.all(),
        label="Choose a location",
        empty_label="Please select a location"
    )

    datetime = forms.DateTimeField(
        label="Date and Hour",

        validators=[
            MinValueValidator(make_aware(datetime.datetime(2015, 1, 1, 0, 0))),
            MaxValueValidator(make_aware(datetime.datetime(2016, 12, 31, 23, 59)))
        ],

        widget=forms.DateTimeInput( # HTML görünüm değiştirir.
            attrs={
                'type': 'datetime-local',
                'min': '2015-01-01T00:00',
                'max': '2016-12-31T23:59'
            }
        )
    )

class RegisterForm(forms.Form):
    """User Registeriation Form"""
    username = forms.CharField(
        label="Username",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Örn: tahasoylu'
        })
    )

    name = forms.CharField(
        label="Name",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Örn: Taha'
        })
    )

    surname = forms.CharField(
        label="Surname",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Örn: Soylu'
        })
    )

    mail = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control'
        })
    )

    password = forms.CharField(
        label="Password",
        max_length=100,
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control'
        })
    )

    def clean_mail(self):   
        """clean_<fieldname> fonksiyonu otomatik çalişarak email doğrulamasi yapar."""
        mail = self.cleaned_data["mail"]

        if User.objects.filter(email=mail).exists():
            raise ValidationError("A User with this email already exists!")
        return mail
    
    def clean_username(self):
        """clean_<fieldname> fonksiyonu otomatik çalişarak username doğrulamasi yapar."""
        username = self.cleaned_data["username"]

        if User.objects.filter(username=username).exists():
            raise ValidationError("A user with this nick already exists!")
        return username
    

class DeleteUserForm(forms.Form):
        """User Registeriation Form"""
        username = forms.CharField(
            label="Username",
            max_length=100,
            required=True,
            widget=forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Örn: tahasoylu'
            })
        )

        name = forms.CharField(
            label="Name",
            max_length=100,
            required=True,
            widget=forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Örn: Taha'
            })
        )

        surname = forms.CharField(
            label="Surname",
            max_length=100,
            required=True,
            widget=forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Örn: Soylu'
            })
        )

        mail = forms.EmailField(
            label="Email",
            required=True,
            widget=forms.EmailInput(attrs={
                'class': 'form-control'
            })
        )

        password = forms.CharField(
            label="Password",
            max_length=100,
            required=True,
            widget=forms.PasswordInput(attrs={
                'class': 'form-control'
            })
        )

        def clean_mail(self):   
            """clean_<fieldname> fonksiyonu otomatik çalişarak email doğrulamasi yapar."""
            mail = self.cleaned_data["mail"]

            if User.objects.filter(email=mail).exists():
                return mail
            raise ValidationError("A user having this email cannot be found!")
        
        def clean_username(self):
            """clean_<fieldname> fonksiyonu otomatik çalişarak username doğrulamasi yapar."""
            username = self.cleaned_data["username"]

            if User.objects.filter(username=username).exists():
                return username
            raise ValidationError("A user having this name cannot be found!")