from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegisterForm
 
 
def register(request):
    if request.user.is_authenticated:
        return redirect('home')
 
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Account created! You can now log in.'
            )
            return redirect('login')
    else:
        form = RegisterForm()
 
    return render(request, 'registration/register.html', {'form': form})