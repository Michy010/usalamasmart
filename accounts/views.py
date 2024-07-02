# views.py
from django.shortcuts import render
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm

def signup(request):
    form = UserRegisterForm ()
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
                form.save()
                username = form.cleaned_data.get('username')
                messages.success(request, f'Your account {username} has been created! You can now log in.')
                return redirect('accounts:signin')
    else:
        form = UserRegisterForm()

    return render(request, 'accounts/sign_up.html', {'form': form})

def signin (request):
    if request.method == 'POST':
        username = request.POST.get ('username')
        password = request.POST.get ('password')

        user = authenticate(request, username = username, password = password)
        if user is not None:
            login (request, user)
            return redirect ('usalama_smart:details')
        else:
            messages.error(request, 'password or username is incorrect!')

    return render (request, 'accounts/sign_in.html')