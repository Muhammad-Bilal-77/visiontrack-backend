from django.shortcuts import render, redirect
from .forms import EmployeeForm

def upload_employee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('upload_success')
    else:
        form = EmployeeForm()
    return render(request, 'core/upload.html', {'form': form})

def upload_success(request):
    return render(request, 'core/upload_success.html')
