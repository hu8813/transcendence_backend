from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers import serialize
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core.files.images import ImageFile
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
import uuid
import os
from django.conf import settings
import requests
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
import json
from .forms import UserRegistrationForm
from .models import Tournament, User  # Change import here
from .serializers import TournamentSerializer

token_obtain_pair_view = TokenObtainPairView.as_view()
token_refresh_view = TokenRefreshView.as_view()


@csrf_exempt
def proxy_userinfo(request):
    # Get the code parameter from the request
    code = request.GET.get('code')
    
    # Check if code parameter is provided
    if not code:
        return JsonResponse({'error': 'Code parameter is missing'}, status=400)
    
    # Query the database for a user with the given code
    try:
        user = User.objects.get(authorization_code=code)  # Assuming 'code' is a field in your User model
        user_info = {
            'nickname': user.nickname,
            'login': user.username,
            'image_link': user.image_link,
            'score': user.score,
            'email': user.email,
            # Add other user information fields as needed
        }
        return JsonResponse({'user': user_info})
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def proxy_view(request):
    # Get the authorization code from the request parameters
    code = request.GET.get('code')
    if not code:
        return JsonResponse({'error': 'Code parameter is missing'}, status=400)

    # Retrieve environment variables
    client_id = os.getenv('REACT_APP_CLIENT_ID')
    client_secret = os.getenv('REACT_APP_CLIENT_SECRET')
    redirect_uri = os.getenv('REACT_APP_REDIRECT_URI')

    # Check if environment variables are set
    if not client_id or not client_secret or not redirect_uri:
        return JsonResponse({'error': 'Environment variables are not set correctly'}, status=500)

    # Prepare the data for token exchange
    data = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'client_secret': client_secret,
        'code': code,
        'redirect_uri': redirect_uri,
    }

    try:
        # Exchange the authorization code for an access token
        response = requests.post('https://api.intra.42.fr/oauth/token', data=data)
        response.raise_for_status()  # Raise an exception for non-2xx responses

        # Extract the access token from the response
        access_token = response.json().get('access_token')

        # Make a request to get user data using the access token
        user_data_response = requests.get('https://api.intra.42.fr/v2/me', headers={'Authorization': f'Bearer {access_token}'})
        user_data_response.raise_for_status()  # Raise an exception for non-2xx responses

        # Extract required user data
        user_data = user_data_response.json()
        login = user_data.get('login')
        email = user_data.get('email')
        image_data = user_data.get('image', {})
        image_link = image_data.get('versions', {}).get('medium', image_data.get('link'))


        # Check if the user already exists in the database
        user, created = User.objects.get_or_create(username=login, email=email)

        # Update user fields
        user.nickname = user_data.get('nickname', user.username)  # Set nickname to login name if not provided
        user.score += 0 
        user.image_link = image_link
        user.access_token = access_token
        user.authorization_code = code
        user.save()

        # Return a redirect response to the frontend with the code included in the URL
        return redirect(f'https://transcendence-beige.vercel.app/login/return?code={code}')
    except requests.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@api_view(['POST'])
def obtain_token(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')
        user = User.objects.filter(username=username).first()
        if user is not None and user.check_password(password):
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        else:
            return Response({'error': 'Invalid credentials'}, status=400)


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
def update_nickname(request):
    if request.method == 'POST':
        new_nickname = request.data.get('nickname')  # Assuming the nickname is sent in the request data
        user = request.user
        if user.is_authenticated:
            user.nickname = new_nickname
            user.save()
            return JsonResponse({"message": "Nickname updated successfully."})
        else:
            return JsonResponse({'error': 'User is not authenticated'}, status=401)
    else:
        return JsonResponse({"message": "Invalid request method."}, status=400)
       
@csrf_exempt
@api_view(['POST'])
def upload_avatar(request):
    if request.method == 'POST' and request.FILES.get('avatar'):
        avatar_file = request.FILES['avatar']
        
        # Check if the uploaded file is an image file by the file extension
        if not avatar_file.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            return Response({"message": "Only image files (PNG, JPG, JPEG, GIF) are allowed."}, status=status.HTTP_400_BAD_REQUEST)
        
        user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
        
        # Generate a unique filename using UUID
        unique_filename = str(uuid.uuid4()) + avatar_file.name[avatar_file.name.rfind('.'):]
        # Save the avatar file to the desired location with the unique filename
        file_path = os.path.join(settings.MEDIA_ROOT, unique_filename)
        with open(file_path, 'wb') as f:
            for chunk in avatar_file.chunks():
                f.write(chunk)
        # Save the file path to the user profile
        user_profile.avatar = unique_filename
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
def get_games(request):
    return JsonResponse({'message': 'Server is awake!'})


@csrf_exempt
def tournaments(request):
    tournaments = Tournament.objects.all()
    serializer = TournamentSerializer(tournaments, many=True)
    return JsonResponse(serializer.data, safe=False)

@csrf_exempt
def leaderboard(request):
    leaderboard_users = User.objects.order_by('-score')[:100]  # Order by date joined
    leaderboard_data = [{'username': user.username, 'date_joined': user.date_joined, 'image_link': user.image_link, 'score': user.score} for user in leaderboard_users]
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

