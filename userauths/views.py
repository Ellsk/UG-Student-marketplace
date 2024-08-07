from django.shortcuts import render, redirect
from userauths.forms import UserRegisterForm
from django.contrib.auth import login, authenticate
from django.contrib import messages

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