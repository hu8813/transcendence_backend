from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import HttpResponse

def login_view(request):
    # Handle login form submission and authentication logic here
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponse('Login successful')
        else:
            return HttpResponse('Invalid login credentials')
    else:
        return render(request, 'login.html')  # Render the login form template

