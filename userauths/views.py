from django.shortcuts import render, redirect
from userauths.forms import UserRegisterForm
from django.contrib.auth import login, authenticate
from django.contrib import messages

def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid(): 
            new_user = form.save()
            id = form.cleaned_data.get("id")
            messages.success(request, f"Hey {id}, Your account was created successfully ")
            new_user = authenticate(username =form.cleaned_data['pin'],
                                    password=form.cleaned_data['password1']
            ) 
            login(request, new_user)
            return redirect('api:index')  # Redirect to a success page or login page
    else:
        form = UserRegisterForm() 

    context = {
        'form': form,
    }
    return render(request, 'userauths/sign-up.html', context)
