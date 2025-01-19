from django.contrib.auth import authenticate, login
import logging
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
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
from hotel_management.models import HotelEmployees, Hotel
import sweetify
from utils.funcs import hash_password

# Configura o logger para o módulo atual
logger = logging.getLogger(__name__)

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

                sweetify.success(request, f"{'Utilizador adicionado com sucesso!' if operation == 'adicionar' else 'Utilizador atualizado com sucesso!'}")
                return redirect('../../')

            except Exception as e:
                
                sweetify.error(request, f"Ocorreu um erro: {str(e)}")
        else:
            sweetify.error(request, "Por favor, corrija os erros abaixo.")
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

                sweetify.success(request, f"{'Utilizador adicionado com sucesso!' if operation == 'adicionar' else 'Utilizador atualizado com sucesso!'}")
                return redirect('users_list')

            except Exception as e:
                sweetify.error(request, f"Ocorreu um erro: {str(e)}")
        else:
            sweetify.error(request, "Por favor, corrija os erros abaixo.")
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
    redirect_authenticated_user = False
    next_page = reverse_lazy('index')

    def form_valid(self, form):
        email = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')

        user = authenticate(request=self.request, username=email, password=password)
        if user is None:
            sweetify.error(self.request, 'Credenciais inválidas')
            return self.form_invalid(form)

        user_from_db = User.objects.filter(pk=user.pk).values('last_login').first()
        first_login = user_from_db['last_login'] is None

        # Salva o estado de primeiro login na sessão para o template
        self.request.session['first_login'] = first_login

        login(self.request, user)

        # Exibir a modal se for o primeiro login
        if first_login:
            return self.render_to_response(self.get_context_data(first_login=first_login))

        # Redirecionar para a página principal após logins subsequentes
        sweetify.success(self.request, "Login efetuado com sucesso!")
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['first_login'] = self.request.session.pop('first_login', False)
        return context

    def get_success_url(self):
        sweetify.success(self.request, "Login efetuado com sucesso!")
        return self.next_page

@login_required
def change_password(request):
    if request.method == "POST":
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        user_id = request.user.id

        if new_password != confirm_password:
            sweetify.error(request, "As passwords não coincidem.")
            return redirect('check_login')

        new_hashed_password = make_password(new_password)

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    CALL sp_change_password(%s, %s)
                """, [user_id, new_hashed_password])
            sweetify.success(request, "Password alterada com sucesso. Por favor, faça login novamente.")
            print("Password alterada com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao alterar senha: {str(e)}")
            sweetify.error(request, "Ocorreu um erro ao alterar a senha. Por favor, tente novamente.")
            print("Erro ao alterar senha:", e)
        return redirect('login')
    
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('index')

def profile_view(request):
    # Retrieve the user and check if they're a client or an employee
    user = request.user
    user_type = "Client" if user.utp == User.CLIENT else "Employee"

    # Fetch related employee/client and role information
    role = AccPermission.objects.get(id=user.role_id, perm_description=user.role.perm_description ,perm_level=user.role.perm_level)
    print("id", user.role_id)
    print("perm level", role.perm_level)
    print("perm_desc", role.perm_description)

    # Retrieve password history
    password_history = UserPasswordsDictionary.objects.filter(user=user).order_by('-valid_from')

    context = {
        'user': user,
        'user_type': user_type,
        'role': role,
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
                sweetify.error(request, "A password antiga está incorreta.")
                return render(request, 'users/profile.html', {'user': user})
            if old_password == new_password:
                sweetify.error(request, "A nova password não pode ser igual à antiga.")
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
        user.social_security = request.POST.get('social_security')

        # user.is_active = 'flexSwitchCheckDefault' in request.POST  # Switch checked = True

        # Atualizar informações de Employee
        if hasattr(user, 'employee'):
            user.employee.social_security = request.POST.get('social_security')

        user.save()  # Salvar alterações
        sweetify.success(request, f"Utilizador {'adicionado' if not user else 'atualizado'} com sucesso!")
        return redirect('/')

    return render(request, 'users/profile.html', {'user': request.user})

def users_list(request):
    query = request.GET.get('q', '')
    sort = request.GET.get('sort', 'first_name')  
    order = request.GET.get('order', 'asc')  

    # Campo de ordenação e ordem
    sort_field = sort if order == 'asc' else f'-{sort}'

    # Obter o perm_level do usuário atual
    user_perm_level = request.user.role.perm_level

    # Filtrar usuários com base no perm_level
    if user_perm_level == 1:  # Administrador
        users = User.objects.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(email__icontains=query)
        ).order_by(sort_field) if query else User.objects.all().order_by(sort_field)
    elif user_perm_level == 2:  # Manager
        # Exibir apenas usuários com permissão de "Employee" ou "None"
        users = User.objects.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(email__icontains=query),
            role__perm_description__in=["Employee", "None"]
        ).order_by(sort_field) if query else User.objects.filter(role__perm_description__in=["Employee", "None"]).order_by(sort_field)
    elif user_perm_level == 3:  # Employee
        # Exibir apenas usuários com permissão de "None"
        users = User.objects.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(email__icontains=query),
            role__perm_description="None"
        ).order_by(sort_field) if query else User.objects.filter(role__perm_description="None").order_by(sort_field)
    else:
        users = User.objects.none()  # Nenhum usuário se o perm_level não for reconhecido

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

        # Handle role selection for dynamic field validation
        role_id = request.POST.get('role')
        role = None
        if role_id:
            try:
                role = AccPermission.objects.get(id=role_id)
            except AccPermission.DoesNotExist:
                sweetify.error(request, "Permissão selecionada é inválida.")
                return render_form(request, form, operation, user)

        # Adjust `social_security` field requirement dynamically
        if role and role.perm_level == 444:
            form.fields['social_security'].required = False

        if form.is_valid():
            new_user = form.save(commit=False)

            # Atualizar role
            if role:
                new_user.role = role
                new_user.utp = 'F' if role.perm_level <= 3 else 'C'

            # Handle `social_security` field
            if role and role.perm_level == 444:
                new_user.social_security = None  # Clear social_security for roles with perm_level 444

            # Definir senha padrão ao adicionar um novo usuário
            if operation == "adicionar":
                default_password = "12345"
                hashed_password = hash_password(default_password)
                new_user.password = default_password
                new_user.hashed_password = hashed_password

            # Atualizar status ativo
            new_user.is_active = 'is_active_switch' in request.POST
            new_user.save()

            # Atualizar hotel_employee, se necessário
            hotel_id = request.POST.get('hotel')
            if role and role.perm_level != 444 and hotel_id:
                try:
                    hotel = Hotel.objects.get(id=hotel_id)
                    HotelEmployees.objects.get_or_create(hotel=hotel, employee=new_user)
                except Hotel.DoesNotExist:
                    sweetify.error(request, "Hotel selecionado é inválido.")
                    return render_form(request, form, operation, user)

            # Exibir mensagem de sucesso com Sweetify
            sweetify.success(
                request,
                f"{'Utilizador adicionado' if user is None else 'Utilizador atualizado'} com sucesso!",
                text="Os dados foram salvos corretamente.",
                button="Fechar"
            )
            return redirect('users_list')
        else:
            print("Erros no formulário:", form.errors)
            sweetify.error(request, "Erro ao processar o formulário.")
    else:
        form = UserForm(instance=user)

    return render_form(request, form, operation, user)

def render_form(request, form, operation, user):
    # Obter roles e hotéis de acordo com o perm_level do usuário atual
    user_perm_level = request.user.role.perm_level

    # Lógica para determinar as roles baseadas no perm_level
    if user_perm_level == 1:  # Administrador
        roles = AccPermission.objects.all()
    elif user_perm_level == 2:  # Gestor
        roles = AccPermission.objects.filter(perm_description__in=["Employee", "None"])
    elif user_perm_level == 3:  # Cliente
        roles = AccPermission.objects.filter(perm_description="None")
    else:
        roles = AccPermission.objects.none()  # Caso não exista perm_level

    # Obter hotéis e hotel_employee
    hotels = Hotel.objects.all()
    hotel_employee = HotelEmployees.objects.filter(employee=request.user)

    return render(request, 'users/users_form.html', {
        'form': form,
        'operation': operation,
        'user': user or {},
        'roles': roles,
        'hotels': hotels,
        'hotel_employee': hotel_employee
    })

# Apagar utilizador
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        user.delete()
        sweetify.success(request, "Utilizador apagado com sucesso!")
        return redirect('users_list')
    else:
        return render(request, 'users/confirm_delete.html', {'user': user})