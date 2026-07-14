from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

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

        password = forms.CharField(
            label="Password",
            max_length=100,
            required=True,
            widget=forms.PasswordInput(attrs={
                'class': 'form-control'
            })
        )
        
        def clean_username(self):
            """clean_<fieldname> fonksiyonu otomatik çalişarak username doğrulamasi yapar."""
            username = self.cleaned_data["username"]

            if User.objects.filter(username=username).exists():
                return username
            raise ValidationError("A user having this name cannot be found!")