from django.shortcuts import render,redirect
from .forms import CustomUserCreationForm

def SignUp(request):
    if request.method=="POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    data={
        'form':form
    }
    return render(request,'accounts/signup.html',data)

# Create your views here.
