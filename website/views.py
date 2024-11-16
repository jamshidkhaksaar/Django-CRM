from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SignUpForm, AddRecordForm
from .models import Record

def home(request):
    records = Record.objects.all()
    form = AddRecordForm()

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You have been logged in!")
            return redirect('home')
        else:
            messages.error(request, "There was an error logging in. Please check your username and password and try again.")
            return redirect('home')
    else:     
        return render(request, 'home.html', {'records': records, 'form': form})

def register_user(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'register.html', {'form': form})

def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('home')

def customer_record(request, pk):
    if request.user.is_authenticated:
        customer_record = Record.objects.get(id=pk)
        return render(request, 'record.html', {'customer_record': customer_record})
    else: 
        messages.error(request, "You must be logged in to view this page.")
        return redirect('home')

def delete_record(request, pk):
    if request.user.is_authenticated:
        delete_it = Record.objects.get(id=pk)
        delete_it.delete()
        messages.success(request, "Record deleted successfully.")
        return redirect('home')
    else:
        messages.error(request, "You must be logged in to do that.")
        return redirect('home')

def add_record(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = AddRecordForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Record added.")
                return redirect('home')
            else:
                messages.error(request, "There was an error with your form submission.")
                return redirect('home')
        return redirect('home')
    else: 
        messages.error(request, "You must be logged in to add a record.")
        return redirect('home')

def update_record(request, pk):
    if request.user.is_authenticated:
        current_record = Record.objects.get(id=pk)
        form = AddRecordForm(request.POST or None, instance=current_record)
        if request.method == "POST":
            if form.is_valid():
                form.save()
                messages.success(request, "Record has been updated!")
                return redirect('home')
            else:
                messages.error(request, "There was an error with your form submission.")
        return render(request, 'update_record.html', {'form': form})
    else:
        messages.error(request, "You must be logged in to update a record.")
        return redirect('home')