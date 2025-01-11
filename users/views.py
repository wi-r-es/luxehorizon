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
from .models import AccPermission
from hotel_management.models import HotelEmployees

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
    
def register_user(request, user_id=None):
    if user_id:
        user = get_object_or_404(User, id=user_id)
        operation = "editar"
    else:
        user = None
        operation = "adicionar"

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                # Dados do formulário
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                email = form.cleaned_data['email']
                nif = form.cleaned_data['nif']
                phone = form.cleaned_data['phone']
                address = form.cleaned_data.get('full_address', '')
                postal_code = form.cleaned_data.get('postal_code', '')
                city = form.cleaned_data.get('city', '')

                if operation == "adicionar":
                    password = form.cleaned_data['password']
                    hashed_password = hash_password(password)

                    # Criar novo utilizador
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            CALL sp_register_user(
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                            )
                        """, [
                            first_name, last_name, email, hashed_password, nif, phone, 
                            address, postal_code, city, 'C', None, True, False, False
                        ])

                else:
                    # Atualizar utilizador existente
                    user.first_name = first_name
                    user.last_name = last_name
                    user.email = email
                    user.nif = nif
                    user.phone = phone
                    user.full_address = address
                    user.postal_code = postal_code
                    user.city = city
                    user.save()

                messages.success(
                    request,
                    f"{'Utilizador adicionado com sucesso!' if operation == 'adicionar' else 'Utilizador atualizado com sucesso!'}"
                )
                return redirect('../../')

            except Exception as e:
                messages.error(request, f"Ocorreu um erro: {str(e)}")
        else:
            messages.error(request, "Por favor, corrija os erros abaixo.")
    else:
        # Pré-popular o formulário no modo de edição
        initial_data = {
            'first_name': user.first_name if user else '',
            'last_name': user.last_name if user else '',
            'email': user.email if user else '',
            'nif': user.nif if user else '',
            'phone': user.phone if user else '',
            'full_address': user.full_address if user else '',
            'postal_code': user.postal_code if user else '',
            'city': user.city if user else '',
        }
        form = RegisterForm(initial=initial_data)

    return render(request, 'users/register.html', {
        'form': form,
        'operation': operation,
        'user': user,
    })

def edit_user(request, user_id=None):
    if user_id:
        user = get_object_or_404(User, id=user_id)
        operation = "editar"
    else:
        user = None
        operation = "adicionar"

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                # Dados do formulário
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                email = form.cleaned_data['email']
                nif = form.cleaned_data['nif']
                phone = form.cleaned_data['phone']
                address = form.cleaned_data.get('full_address', '')
                postal_code = form.cleaned_data.get('postal_code', '')
                city = form.cleaned_data.get('city', '')

                if operation == "adicionar":
                    password = form.cleaned_data['password']
                    hashed_password = hash_password(password)

                    # Criar novo utilizador
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            CALL sp_register_user(
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                            )
                        """, [
                            first_name, last_name, email, hashed_password, nif, phone, 
                            address, postal_code, city, 'C', None, True, False, False
                        ])
                else:
                    # Atualizar utilizador existente
                    user.first_name = first_name
                    user.last_name = last_name
                    user.email = email
                    user.nif = nif
                    user.phone = phone
                    user.full_address = address
                    user.postal_code = postal_code
                    user.city = city
                    user.save()

                messages.success(
                    request,
                    f"{'Utilizador adicionado com sucesso!' if operation == 'adicionar' else 'Utilizador atualizado com sucesso!'}"
                )
                return redirect('users_list')

            except Exception as e:
                messages.error(request, f"Ocorreu um erro: {str(e)}")
        else:
            messages.error(request, "Por favor, corrija os erros abaixo.")
    else:
        # Pré-popular o formulário no modo de edição
        initial_data = {
            'first_name': user.first_name if user else '',
            'last_name': user.last_name if user else '',
            'email': user.email if user else '',
            'nif': user.nif if user else '',
            'phone': user.phone if user else '',
            'full_address': user.full_address if user else '',
            'postal_code': user.postal_code if user else '',
            'city': user.city if user else '',
        }
        form = RegisterForm(initial=initial_data)

    return render(request, 'users/users_form.html', {
        'form': form,
        'operation': operation,
        'user': user,
    })

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

        # Validação da Password Antiga
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('password')
        if old_password and new_password:  # Se o utilizador pretende mudar a password
            if not user.check_password(old_password):
                messages.error(request, "A password antiga está incorreta.")
                return render(request, 'users/profile.html', {'user': user})
            if old_password == new_password:
                messages.error(request, "A nova password não pode ser igual à antiga.")
                return render(request, 'users/profile.html', {'user': user})
            user.set_password(new_password)  # Define a nova password

        # Atualizar informações básicas do utilizador
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.nif = request.POST.get('nif')
        user.phone = request.POST.get('phone')
        user.full_address = request.POST.get('full_address')
        user.postal_code = request.POST.get('postal_code')
        user.city = request.POST.get('city')

        # Atualizar switches (is_staff e is_active)
        # user.is_staff = 'flexSwitchCheckChecked' in request.POST  # Switch checked = True
        # user.is_active = 'flexSwitchCheckDefault' in request.POST  # Switch checked = True

        # Atualizar informações de Employee
        if hasattr(user, 'employee'):
            user.employee.social_security = request.POST.get('social_security')

        user.save()  # Salvar alterações
        messages.success(request, "Perfil atualizado com sucesso.")
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

import sweetify

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

            # Atualizar o role do usuário com base na combobox
            role_id = request.POST.get('role')
            if role_id:
                try:
                    role = AccPermission.objects.get(id=role_id)
                    new_user.role = role
                    new_user.is_staff = role.perm_level >= 2  # Defina a lógica para is_staff
                    new_user.utp = 'F' if role.perm_level <= 3 else 'C'
                except AccPermission.DoesNotExist:
                    messages.error(request, "Permissão selecionada é inválida.")
                    return render(request, 'users/users_form.html', {
                        'form': form,
                        'operation': operation,
                        'user': user or {},
                        'roles': AccPermission.objects.all(),
                    })

            new_user.is_active = 'is_active_switch' in request.POST
            new_user.save()

            # Retrieve the ID of the newly created or updated user
            new_user_id = new_user.id

            # Additional logic for staff users
            #if new_user.is_staff:
                #new_entry = HotelEmployees.create(form.hotel_id, new_user_id) #TODO

            # Exibir alerta Sweetify
            sweetify.success(
                request,
                f"{'Utilizador adicionado' if user is None else 'Utilizador atualizado'} com sucesso!",
                text="Os dados foram salvos corretamente.",
                button="Fechar" # persistent nao fecha o alerta
            )
            return redirect('users_list')
        else:
            messages.error(request, "Erro ao processar o formulário.")
    else:
        form = UserForm(instance=user)

    roles = AccPermission.objects.all()

    return render(request, 'users/users_form.html', {
        'form': form,
        'operation': operation,
        'user': user or {},
        'roles': roles,
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