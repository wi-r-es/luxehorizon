# forms.py
from django import forms
from .models import User
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password

def clean(self):
    cleaned_data = super().clean()
    password = cleaned_data.get("password")
    password_confirm = cleaned_data.get("password_confirm")
    
    if password and password_confirm and password != password_confirm:
        self.add_error("password_confirm", "Passwords do not match")
    
    # Validações adicionais para senha
    if password:
        validate_password(password)
    
    return cleaned_data


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Confirm Password")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'nif', 'phone', 'password', 'password_confirm']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            self.add_error("password_confirm", "Passwords do not match")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])  # Set hashed password
        if commit:
            user.save()
        return user

class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean(self):
        # Não precisamos mais autenticar aqui, pois será feito na CustomLoginView
        cleaned_data = super().clean()
        return cleaned_data

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'nif',
            'full_address', 'postal_code', 'city', 'social_security', 'is_staff', 'is_active',
        ]
        labels = {
            'first_name': 'Primeiro Nome',
            'last_name': 'Último Nome',
            'email': 'E-mail',
            'nif': 'NIF',
            'phone': 'Telefone',
            'full_address': 'Morada',
            'postal_code': 'Código Postal',
            'city': 'Cidade',
            'social_security': 'Segurança Social',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Primeiro Nome'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Último Nome'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'E-mail'}),
            'nif': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'NIF'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Telefone'}),
            'full_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Morada'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código Postal'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cidade'}),
            'social_security': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Segurança Social'}),
        }