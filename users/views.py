from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegisterForm, CustomLoginForm
from django.contrib.auth.hashers import check_password

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the user
            messages.success(request, "Registration successful!")
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})


class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'users/login.html'   
    redirect_authenticated_user = True
    next_page = reverse_lazy('index')

    def form_valid(self, form):
        user = form.cleaned_data.get('user')
        
        # Check if the password is correct
        if user and check_password(form.cleaned_data['password'], user.hashed_password):
            login(self.request, user)
            return redirect(self.get_success_url())
        else:
            messages.error(self.request, "Invalid credentials")
            return redirect('login')

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('index')