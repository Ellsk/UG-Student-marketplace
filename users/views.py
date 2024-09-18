from django.shortcuts import render

# Create your views here.
# users/views.py
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm

def custom_admin_login(request):
    form = AuthenticationForm(request, data=request.POST)
    if form.is_valid():
        user = form.get_user()
        if user.is_superuser:
            login(request, user)
            return redirect('admin:index')
    return render(request, 'admin/login.html', {'form': form})
