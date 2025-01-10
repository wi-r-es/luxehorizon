from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegisterForm, CustomLoginForm
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from .models import User, Client, Employee, AccPermission, UserPasswordsDictionary
from django.shortcuts import render, get_object_or_404, redirect
from .models import User
from django.db.models import Q, Count, Sum, OuterRef, Subquery
from .forms import UserForm
from django.db import connection
from django.contrib.auth.hashers import make_password
from django import forms

def hash_password(password):
    return make_password(password)

class RegisterForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)
    nif = forms.CharField(max_length=20)
    phone = forms.CharField(max_length=20)
    full_address = forms.CharField(max_length=160, required=False)
    postal_code = forms.CharField(max_length=8, required=False)
    city = forms.CharField(max_length=100, required=False)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Passwords do not match.")

        return cleaned_data
    
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                # Collect form data
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']
                nif = form.cleaned_data['nif']
                phone = form.cleaned_data['phone']
                address = form.cleaned_data.get('full_address', '')
                postal_code = form.cleaned_data.get('postal_code', '')
                city = form.cleaned_data.get('city', '')
                hashed_password = hash_password(password)  # Custom hashing function
                utp = 'C'  # Default user type
                social_sec = None  # Default as None

                # Call the PostgreSQL procedure
                with connection.cursor() as cursor:
                    cursor.execute("""
                        CALL sp_register_user(
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """, [
                        first_name, last_name, email, hashed_password, nif, phone, 
                        address, postal_code, city, utp, social_sec, True, False, False
                    ])
                
                messages.success(request, "Registration successful!")
                return redirect('login')

            except Exception as e:
                # Log the error if needed
                messages.error(request, f"An error occurred: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below.")
    
    else:
        form = RegisterForm()

    return render(request, 'users/register.html', {'form': form})


class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'users/login.html'   
    redirect_authenticated_user = True
    next_page = reverse_lazy('index')  # Default redirection for other users

    def form_valid(self, form):
        user = form.cleaned_data.get('user')
        password = form.cleaned_data.get('password')
        
        # Validate password and user existence
        if user and check_password(password, user.hashed_password):
            login(self.request, user)

            # Redirect based on roles: Admin & Employee
            if user.utp != User.CLIENT: 
                return redirect('admin_dashboard') 
            
            # Redirect to default next page
            return redirect(self.get_success_url())
        else:
            # Handle invalid credentials
            messages.error(self.request, "Invalid credentials")
            return redirect('login')

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('index')

def profile_view(request):
    # Retrieve the user and check if they're a client or an employee
    user = request.user
    user_type = "Client" if user.utp == User.CLIENT else "Employee"
    
    # Fetch related employee/client and role information
    role = None
    social_security = None
    if user_type == "Employee":
        employee = Employee.objects.get(pk=user.pk)
        role = employee.role.perm_description
        social_security = employee.social_security
    
    # Retrieve password history
    password_history = UserPasswordsDictionary.objects.filter(user=user).order_by('-valid_from')

    context = {
        'user': user,
        'user_type': user_type,
        'role': role,
        'social_security': social_security,
        'password_history': password_history,
    }
    return render(request, 'users/profile.html', context)

def update_profile(request):
    if request.method == 'POST':
        user = request.user

        # Update basic information
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.nif = request.POST.get('nif')
        user.phone = request.POST.get('phone')
        user.full_address = request.POST.get('full_address')
        user.postal_code = request.POST.get('postal_code')
        user.city = request.POST.get('city')

        # Update switches (is_staff and is_active)
        user.is_staff = 'flexSwitchCheckChecked' in request.POST  # Switch checked = True
        user.is_active = 'flexSwitchCheckDefault' in request.POST  # Switch checked = True

        # If employee, update additional fields
        if hasattr(user, 'employee'):
            user.employee.social_security = request.POST.get('social_security')

        user.save()  # Save changes
        messages.success(request, "Profile updated successfully.")
        return redirect('/')

    return render(request, 'users/profile.html', {'user': request.user})

def users_list(request):
    query = request.GET.get('q', '')
    sort = request.GET.get('sort', 'first_name')  
    order = request.GET.get('order', 'asc')  

    # Campo de ordenação e ordem
    sort_field = sort if order == 'asc' else f'-{sort}'

    # Filtrar usuários
    users = User.objects.filter(
        Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(email__icontains=query)
    ).order_by(sort_field) if query else User.objects.all().order_by(sort_field)

    return render(request, 'users/users_list.html', {
        'users': users,
        'query': query,
        'sort': sort,
        'order': order,
    })

def users_form(request, user_id=None):
    if user_id:
        user = get_object_or_404(User, id=user_id)
        operation = "editar"
    else:
        user = None
        operation = "adicionar"

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            new_user = form.save(commit=False)

            # Atualizar os campos is_staff e is_active
            new_user.is_staff = 'is_staff_switch' in request.POST
            new_user.is_active = 'is_active_switch' in request.POST

            new_user.save()
            messages.success(request, f"{'Utilizador adicionado' if user is None else 'Utilizador atualizado'} com sucesso!")
            return redirect('users_list')
        else:
            messages.error(request, "Erro ao processar o formulário.")
    else:
        form = UserForm(instance=user)

    return render(request, 'users/users_form.html', {
        'form': form,
        'operation': operation,
        'user': user or {},
    })


# Apagar utilizador
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        user.delete()
        messages.success(request, "Utilizador apagado com sucesso!")
        return redirect('users_list')
    else:
        return render(request, 'users/confirm_delete.html', {'user': user})