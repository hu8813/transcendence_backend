from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .forms import UserRegistrationForm
from django.contrib.auth.models import User
from django.shortcuts import render

@csrf_exempt
def ping(request):
    return JsonResponse({'message': 'Server is awake!'})

@csrf_exempt
def leaderboard(request):
    leaderboard_users = User.objects.order_by('-date_joined')[:10]  # Order by date joined
    leaderboard_data = [{'username': user.username, 'date_joined': user.date_joined} for user in leaderboard_users]
    return JsonResponse(leaderboard_data, safe=False)

@csrf_exempt
def fetch_messages(request):
    # Logic to fetch old chat messages
    messages = [...]  # Fetch messages from database
    return JsonResponse(messages, safe=False)

@csrf_exempt
def send_message(request):
    # Logic to save new chat message
    # Extract message data from request
    message_data = json.loads(request.body)
    message = message_data['message']

    # Save message to database
    # ...

    return JsonResponse({'status': 'success'})

@csrf_exempt
def get_csrf_token(request):
    # Get the CSRF token from the request's CSRF middleware
    csrf_token = request.COOKIES.get('csrftoken', '')

    # Return the CSRF token in a JSON response
    return JsonResponse({'csrfToken': csrf_token})

@csrf_exempt
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Hash password
            user.save()
            return redirect('login')
        else:
            # Return form errors if the form is invalid
            errors = form.errors.as_text()
            return HttpResponse(f"Error occurred: {errors}", status=400)  # Bad Request status code
    else:
        form = UserRegistrationForm()  # Move form initialization here
        return render(request, 'registration/register.html', {'form': form})  # Render the registration form template


@csrf_exempt
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

