"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from myapp import views
#from socketio import views as socketio_views



urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login_view, name='login'),
    path('ping/', views.login_view, name='ping'),
    path('register/', views.register, name='register'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('tournaments/', views.get_tournament_data, name='tournaments'),
    path('get-csrf-token/', views.get_csrf_token, name='get_csrf_token'),
    path('api/fetch-messages/', views.fetch_messages, name='fetch_messages'),
    path('api/send-message/', views.send_message, name='send_message'),
    path('upload-avatar/', views.upload_avatar, name='upload_avatar'),
    path('get-email/', views.upload_avatar, name='get_email'),
    path('get-nickname/', views.get_nickname, name='get_nickname'),
    #path("socket.io/", socketio_views.SocketIOView.as_view(), name="socketio"),
]
