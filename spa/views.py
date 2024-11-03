from django.shortcuts import render

from django.views.generic import View

from django.contrib.auth import logout
from django.shortcuts import redirect

from django.contrib.auth import authenticate, login

from django.contrib.auth import get_user_model

from .forms import LoginForm, SignUpForm, EditProfileForm
from .models import Sound, Album, Upload
from .models import ProfilePictureMapping

from django.templatetags.static import static

# Create your views here.

class HTMXView(View) :
    def html_name(self):
        return "index"
    
    def pre_get(self, request):
        return ""
    
    def get(self, request, *args, **kwargs):
        redirect_url = self.pre_get(request)
        if redirect_url != "":
            return redirect(redirect_url)

        if request.htmx:
            return render(request, f"{self.html_name()}.html", self.get_context())
        else :
            return render(request, f"{self.html_name()}_f.html", self.get_context())
        
    def get_context(self) -> dict:
        return {
            "profile_picture": get_profile_picture(self.request.user) if self.request.user.is_authenticated else static('images/none.png')
        }

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

def get_profile_picture(user):
    if user is None :
        return static('images/none.png')
    
    pro = ProfilePictureMapping.objects.filter(user=user).first()
    if pro is None:
        return static('images/none.png')
    
    return pro.upload.file.url
    
class ProfileView(HTMXView) :
    def html_name(self):
        return "profile"
    
    def get_user_from_request(self):
        return self.request.GET.get('username', None)
    
    def get_context(self) -> dict:
        user = self.get_user_from_request()
        if user is None:
            return {}
        
        eform = EditProfileForm()
        # put data in the form
        eform.fields['username'].initial = user.username
        eform.fields['email'].initial = user.email

        return {
            "profile_picture": get_profile_picture(user),
            "profile_user": user,

            "sounds": Sound.objects.filter(user=user),
            "albums": Album.objects.filter(user=user),

            "edit_form": eform
        }
    
class MeView(ProfileView) :
    def html_name(self):
        return "profile"
    
    def get_user_from_request(self):
        return self.request.user
    
    def pre_get(self, request):
        if request.user.is_anonymous:
            return 'login'
        return ""
    
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
    
class EditProfileView(View) :
    def post(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return redirect('login')
        
        # update user profile and upload a new profile picture
        form = EditProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user = request.user
            user.username = form.cleaned_data['username']
            user.email = form.cleaned_data['email']
            user.save()
            
            new_pic = form.cleaned_data['new_pic']
            print(form.cleaned_data)
            print(new_pic)
            if new_pic is not None:
                # create a new upload
                up = Upload.objects.create(user=user, file=new_pic)
                # create a new profile picture mapping
                p = ProfilePictureMapping.objects.create(user=user, upload=up)
                print(p)
            
            return redirect('me')
        
        return render(request, 'profile_f.html', {
            "edit_form": form
        })