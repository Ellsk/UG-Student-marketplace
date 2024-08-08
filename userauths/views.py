from django.shortcuts import render, redirect
from userauths.forms import UserRegisterForm
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.conf import settings

User = settings.AUTH_USER_MODEL

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
            print(form.errors)
    else:
        form = UserRegisterForm()

    context = {
        'form': form,
    }
    return render(request, 'userauths/sign-up.html', context)

def login_view(request):
    if request.user.is_authenticated:
        return redirect("api:index")
    
    if request.method == "POST":
        id = request.POST.get("id")
        pin = request.POST.get("pin") 
        
    try: 
        user = User.objects.get(id=id)
    except:
        messages.warning(request, f"User with {id} already exists")
    
    user = authenticate(request, id=id, pin=pin)
    
    if user is not None:
        login(request, user)
        messages.success(request, f"You are logged in successfully")
        return redirect("api:index")
    else:
        messages.warning(request, "User Does Not Exist, Create An Account")