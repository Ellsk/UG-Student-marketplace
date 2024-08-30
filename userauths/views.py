from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from userauths.forms import UserRegisterForm, ProfileForm
from .models import CustomUser, Profile

def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            messages.success(request, f"Hey {new_user.id}, Your account was created successfully!")
            new_user = authenticate(request, id=form.cleaned_data['id'], password=form.cleaned_data['pin'])
            if new_user is not None:
                login(request, new_user)
                return redirect('api:index')
            else:
                messages.error(request, "Authentication failed. Please check your credentials.")
        else:
            messages.error(request, form.errors)
    else:
        form = UserRegisterForm()

    context = {
        'form': form,
    }
    return render(request, 'userauths/sign-up.html', context)

def login_view(request):
    if request.user.is_authenticated:
        messages.error(request,f"Hey, You are already logged in!")
        return redirect("api:index")
    
    if request.method == "POST":
        id = request.POST.get("id")
        pin = request.POST.get("pin")
        
        print(f"ID: {id}, PIN: {pin}")  # Debugging line

        if not id or not pin:
            messages.error(request, "Both ID and PIN are required.")
            return redirect("userauths:sign-in")

        user = authenticate(request, id=id, password=pin)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.full_name}!")
            return redirect("api:index")
        else:
            messages.warning(request, "Invalid credentials. Please try again.")
            return redirect("userauths:sign-in")
    
    context = {}
    return render(request, "userauths/sign-in.html", context)

def logout_view(request):
    
    logout(request)
    messages.success(request, "User logged out successfully")
    return redirect("userauths:sign-in")

def profile_update(request):
    profile = Profile.objects.get(user=request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.user = request.user
            new_form.save()
            messages.success(request, "Profile Updated Successfully.")
            return redirect("api:dashboard")
    else:
        form = ProfileForm(instance=profile)

    context = {
        "form": form,
        "profile": profile,
    }

    return render(request, "userauths/profile-edit.html", context)

