from django.contrib import admin
from django.urls import path

from django.urls import include

from .views import IndexView, DiscoverView, LoginView, LogoutView, SignupView, MeView
from .views import ProfileView, PlaylistView, AlbumView, SoundView
from .views import PlaylistCreateView, AlbumCreateView, SoundCreateView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('discover/', DiscoverView.as_view(), name='discover'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('signup/', SignupView.as_view(), name='signup'),

    path('me/', MeView.as_view(), name='me'),
    path('profile/<str:username>/', ProfileView.as_view(), name='profile'),

    path('playlist/create', PlaylistCreateView.as_view(), name='playlist_create'),
    path('album/create', AlbumCreateView.as_view(), name='album_create'),
    path('sound/create', SoundCreateView.as_view(), name='sound_create'),

    path('playlist/<str:uuid>/', PlaylistView.as_view(), name='playlist'),
    path('album/<str:uuid>/', AlbumView.as_view(), name='album'),
    path('sound/<str:uuid>/', SoundView.as_view(), name='sound'),
]