from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .forms import UserRegistrationForm
from django.contrib.auth.models import User
from django.shortcuts import render
from django.core.serializers import serialize
from rest_framework.response import Response
from rest_framework.decorators import api_view

@csrf_exempt
def get_email(request):
    # Assuming the user's email is stored in the user's profile or similar
    # You may need to adjust this to fit your data model
    user = request.user  # Assuming you're using Django's authentication system
    if user.is_authenticated:
        email = user.email
        return JsonResponse({'email': email})
    else:
        return JsonResponse({'error': 'User is not authenticated'}, status=401)

@csrf_exempt
def get_nickname(request):
    user = request.user
    if user.is_authenticated:
        nickname = user.nickname  # Assuming your user model has a field named 'nickname'
        return JsonResponse({'nickname': nickname})
    else:
        return JsonResponse({'error': 'User is not authenticated'}, status=401)

@csrf_exempt 
@api_view(['POST'])
def upload_avatar(request):
    if request.method == 'POST' and request.FILES['avatar']:
        avatar_file = request.FILES['avatar']
        user_profile = UserProfile.objects.get_or_create(user=request.user)  # Assuming you have a user associated with the profile
        
        # Save the avatar file to a desired location
        user_profile.avatar = avatar_file
        user_profile.save()

        return Response({"message": "Avatar uploaded successfully."})
    else:
        return Response({"message": "No avatar file provided."}, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
def get_score(request):
    # Retrieve user info from the database
    users = User.objects.all()
    
    # Serialize user info
    user_data = serialize('json', users)
    
    # Example score
    score = 100  
    
    # Return user info along with score
    response_data = {
        'score': score,
        'users': user_data
    }
    
    return JsonResponse(response_data)

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

