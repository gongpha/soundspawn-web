from django.shortcuts import render

from django.views.generic import View

from django.contrib.auth import logout
from django.shortcuts import redirect

from django.contrib.auth import authenticate, login

from django.contrib.auth import get_user_model

from .forms import LoginForm, SignUpForm
from .models import Sound, Album
# Create your views here.

class HTMXView(View) :
    def html_name(self):
        return "index"
    
    def get(self, request, *args, **kwargs):
        if request.htmx:
            return render(request, f"{self.html_name()}.html", self.get_context())
        else :
            return render(request, f"{self.html_name()}_f.html", self.get_context())
        
    def get_context(self) -> dict:
        return {}

class IndexView(HTMXView):
    pass

class DiscoverView(HTMXView):
    def html_name(self):
        return "discover"
    
class LogoutView(View):
    def get(self, request, *args, **kwargs):
        # logout from the session
        logout(request)
        return redirect('index')
    
class LoginView(HTMXView):
    def html_name(self):
        return "signin"
    
    def get_context(self) -> dict:
        return {
            "form": LoginForm()
        }
    
    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if form.is_valid():
            # login the user
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                form.add_error(None, 'Invalid username or password')
        return render(request, 'signin_f.html', {
            "form": form
        })
    
class SignupView(HTMXView):
    def html_name(self):
        return "signup"
    
    def get_context(self) -> dict:
        return {
            "form": SignUpForm()
        }
    
    def post(self, request, *args, **kwargs):
        form = SignUpForm(request.POST)
        if form.is_valid():
            # create user
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = get_user_model().objects.create_user(username, email, password)
            login(request, user)
            return redirect('index')
        return render(request, 'signup_f.html', {
            "form": form
        })
    
#############
    
class ProfileView(HTMXView) :
    def html_name(self):
        return "profile"
    
    def get_user_from_request(self):
        return self.request.GET.get('username', None)
    
    def get_context(self) -> dict:
        user = self.get_user_from_request()
        if user is None:
            return {}
        return {
            "sounds": Sound.objects.filter(user=user),
            "albums": Album.objects.filter(user=user)
        }
    
class MeView(HTMXView) :
    def html_name(self):
        return "profile"
    
    def get_user_from_request(self):
        return self.request.user
    
#############

class PlaylistView(HTMXView) :
    def html_name(self):
        return "playlist"
    
    def get_playlist_from_request(self):
        return self.request.GET.get('uuid', None)
    
    def get_context(self) -> dict:
        playlist = self.get_playlist_from_request()
        if playlist is None:
            return {}
        return {
            "playlist": playlist
        }
    
class AlbumView(HTMXView) :
    def html_name(self):
        return "album"
    
    def get_album_from_request(self):
        return self.request.GET.get('uuid', None)
    
    def get_context(self) -> dict:
        album = self.get_album_from_request()
        if album is None:
            return {}
        return {
            "album": album
        }
    
class SoundView(HTMXView) :
    def html_name(self):
        return "sound"
    
    def get_sound_from_request(self):
        return self.request.GET.get('uuid', None)
    
    def get_context(self) -> dict:
        sound = self.get_sound_from_request()
        if sound is None:
            return {}
        return {
            "sound": sound
        }
    
class PlaylistCreateView(HTMXView) :
    def html_name(self):
        return "playlist_create"
    
    def get_context(self) -> dict:
        return {}
    
class AlbumCreateView(HTMXView) :
    def html_name(self):
        return "album_create"
    
    def get_context(self) -> dict:
        return {}
    
class SoundCreateView(HTMXView) :
    def html_name(self):
        return "sound_create"
    
    def get_context(self) -> dict:
        return {}