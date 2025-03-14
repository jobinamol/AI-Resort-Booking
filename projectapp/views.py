from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm
from .models import UserDB

# Create your views here.
def index(request):
    return render(request, 'index.html')

def resortindex(request):
    return render(request, 'Resortindex.html')

def guestindex(request):
    return render(request, 'guestindex.html')

def about(request):
    return render(request, 'about.html')

def blog(request):
    return render(request, 'blog.html')

def blog_single(request):
    return render(request, 'blog-single.html')

def contact(request):
    return render(request, 'contact.html')

def main(request):
    return render(request, 'main.html')

def restaurants(request):
    return render(request, 'restaurant.html')

def rooms(request):
    return render(request, 'rooms.html')

def rooms_single(request):
    return render(request, 'rooms-single.html')

def ResortDashboard(request):
    return render(request, 'ResortDashboard.html')

def user_signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful! Welcome to LuxAI Resorts!")
            return redirect("resortindex")
        else:
            messages.error(request, "Invalid form submission. Please check your data.")
    else:
        form = CustomUserCreationForm()
    return render(request, "signup.html", {"form": form})

def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('resortindex')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})

def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully!")
    return redirect('index')


