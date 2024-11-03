from django.shortcuts import render

from django.views.generic import View

from django.contrib.auth import logout
from django.shortcuts import redirect

from django.contrib.auth import authenticate, login

from django.contrib.auth import get_user_model

from .forms import LoginForm, SignUpForm, EditProfileForm
from .forms import SoundUploadForm, SoundEditForm
from .forms import PlaylistCreateEditForm, AlbumCreateEditForm
from .models import Sound, Album, Upload
from .models import ProfilePictureMapping
from .models import History, Playlist

from django.http import FileResponse

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
        
        default_context = self.get_context(*args, **kwargs) | {
            "profile_picture_me": get_profile_picture(self.request.user) if self.request.user.is_authenticated else static('images/none.png')
        }

        if request.htmx:
            return render(request, f"{self.html_name()}.html", default_context)
        else :
            return render(request, f"{self.html_name()}_f.html", default_context)
        
    def get_context(self, *args, **kwargs) -> dict:
        return {}

class IndexView(HTMXView):
    def get_context(self, *args, **kwargs) -> dict:
        if self.request.user.is_authenticated:
            histories = History.objects.filter(user=self.request.user).order_by('-id')[:9]
            return {
                "histories": histories
            }
        return {}

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
    
    def get_context(self, *args, **kwargs) -> dict:
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
    
    def get_context(self, *args, **kwargs) -> dict:
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
    
    def get_user_from_request(self, *args, **kwargs):
        user = kwargs.get('username', None)
        if user is None:
            return None
        
        user = get_user_model().objects.filter(username=user).first()
        if user is None:
            return None
        
        return user
    
    def get_context(self, *args, **kwargs) -> dict:
        user = self.get_user_from_request(*args, **kwargs)

        if user is None:
            return {}
        
        eform = EditProfileForm()
        # put data in the form
        eform.fields['username'].initial = user.username
        eform.fields['email'].initial = user.email

        sounds = Sound.objects.filter(user=user)
        albums = Album.objects.filter(user=user)
        playlists = Playlist.objects.filter(user=user)

        return {
            "profile_picture": get_profile_picture(user),
            "profile_user": user,

            "sounds": sounds,
            "albums": albums,
            "playlists": playlists,

            "edit_form": eform,

            "sound_count": len(sounds),
            "album_count": len(albums),
            "playlist_count": len(playlists)
            
        }
    
class MeView(ProfileView) :
    def html_name(self):
        return "profile"
    
    def get_user_from_request(self, *args, **kwargs):
        return self.request.user
    
    def pre_get(self, request):
        if request.user.is_anonymous:
            return 'login'
        return ""
    
#############

class PlaylistView(HTMXView) :
    def html_name(self):
        return "playlist"
    
    def get_context(self, *args, **kwargs) -> dict:
        uuid = kwargs.get('uuid', None)
        if uuid is None :
            return {}
        playlist = Playlist.objects.get(id=uuid)
        if playlist is None :
            return {}
        
        # PLAYLIST IS PRIVATE
        if playlist.user != self.request.user:
            return {}
        
        eform = PlaylistCreateEditForm()
        # put data in the form
        eform.fields['name'].initial = playlist.name

        return {
            "playlist": playlist,
            "edit_form": eform
        }
    
    def post(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return redirect('login')

        playlist = kwargs.get('uuid', None)
        if playlist is None:
            return redirect('index')
        
        playlist = Playlist.objects.get(id=playlist)
        if playlist is None:
            return redirect('index')
        
        if request.user != playlist.user:
            return redirect('index')
        
        form = PlaylistCreateEditForm(request.POST, request.FILES)
        if form.is_valid():
            playlist.name = form.cleaned_data['name']

            # pic upload
            pic = form.cleaned_data['pic']
            if pic :
                upload = Upload.objects.create(user=request.user, file=pic)
                playlist.picture = upload
            playlist.save()
            
            return redirect('playlist', uuid=playlist.id)
        
        return redirect('playlist', uuid=playlist.id)
    
class AlbumView(HTMXView) :
    def html_name(self):
        return "album"
    
    def get_context(self, *args, **kwargs) -> dict:
        uuid = kwargs.get('uuid', None)
        if uuid is None :
            return {}
        album = Album.objects.get(id=uuid)
        if album is None :
            return {}
        
        eform = AlbumCreateEditForm()
        # put data in the form
        eform.fields['name'].initial = album.name

        return {
            "album": album,
            "edit_form": eform
        }
    
    def post(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return redirect('login')

        album = kwargs.get('uuid', None)
        if album is None:
            return redirect('index')
        
        album = Album.objects.get(id=album)
        if album is None:
            return redirect('index')
        
        if request.user != album.user:
            return redirect('index')
        
        form = AlbumCreateEditForm(request.POST, request.FILES)
        if form.is_valid():
            album.name = form.cleaned_data['name']

            # pic upload
            pic = form.cleaned_data['pic']
            if pic :
                upload = Upload.objects.create(user=request.user, file=pic)
                album.picture = upload
            album.save()
            
            return redirect('album', uuid=album.id)
        
        return redirect('album', uuid=album.id)
    
class SoundView(HTMXView) :
    def html_name(self):
        return "sound"
    
    def get_context(self, *args, **kwargs) -> dict:
        sound = kwargs.get('uuid', None)
        if sound is None:
            return {}
        
        sound = Sound.objects.get(id=sound)

        if sound is None:
            return {}
        
        eform = SoundEditForm()
        # put data in the form
        eform.fields['name'].initial = sound.name

        return {
            "sound": sound,
            "profile_picture_uploader": get_profile_picture(sound.user),
            "edit_form": eform
        }
    
    def post(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return redirect('login')

        sound = kwargs.get('uuid', None)
        if sound is None:
            return redirect('index')
        
        sound = Sound.objects.get(id=sound)
        if sound is None:
            return redirect('index')
        
        if request.user != sound.user:
            return redirect('index')
        
        form = SoundEditForm(request.POST)
        if form.is_valid():
            sound.name = form.cleaned_data['name']
            sound.save()
            
            return redirect('sound', uuid=sound.id)
        
        return redirect('sound', uuid=sound.id)
    
class PlaylistCreateView(HTMXView) :
    def html_name(self):
        return "playlist_create"
    
    def get_context(self) -> dict:
        return {
            'form': PlaylistCreateEditForm()
        }
    
class AlbumCreateView(HTMXView) :
    def html_name(self):
        return "album_create"
    
    def get_context(self) -> dict:
        return {
            'form': AlbumCreateEditForm()
        }
    
class SoundCreateView(HTMXView) :
    def html_name(self):
        return "sound_create"
    
    def get_context(self, *args, **kwargs) -> dict:
        return {
            'form': SoundUploadForm()
        }
    
class EditProfileView(View) :
    def get(self, request, *args, **kwargs):
        return redirect('me')
    
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
            if new_pic is not None:
                # create a new upload
                up = Upload.objects.create(user=user, file=new_pic)

                # assign the new profile picture
                existing = ProfilePictureMapping.objects.filter(user=user).first()
                if existing is not None:
                    existing.upload = up
                    existing.save()
                else:
                    ProfilePictureMapping.objects.create(user=user, upload=up)
            
            return redirect('me')
        
        return render(request, 'profile_f.html', {
            "edit_form": form
        })
    
class UploadSoundView(View) :
    def get(self, request, *args, **kwargs):
        return redirect('sound_create')

    def post(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return redirect('login')
        
        form = SoundUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # create a new sound
            name = form.cleaned_data['name']
            sound = form.cleaned_data['sound']

            upload = Upload.objects.create(user=request.user, file=sound)

            s = Sound.objects.create(user=request.user, name=name, upload=upload)
            return redirect('sound', uuid=s.id)
        
        return render(request, 'sound_create_f.html', {
            'form': form
        })
    
class NewAlbumView(View) :
    def get(self, request, *args, **kwargs):
        return redirect('album_create')
    
    def post(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return redirect('login')
        
        form = AlbumCreateEditForm(request.POST, request.FILES)
        if form.is_valid():
            # create a new album
            name = form.cleaned_data['name']
            pic = form.cleaned_data['pic']

            if pic :
                upload = Upload.objects.create(user=request.user, file=pic)
                album = Album.objects.create(user=request.user, name=name, picture=upload)
            else :
                album = Album.objects.create(user=request.user, name=name)
            return redirect('album', uuid=album.id)
        
        return render(request, 'album_create_f.html', {
            'form': form
        })
    
class NewPlaylistView(View) :
    def get(self, request, *args, **kwargs):
        return redirect('playlist_create')
    
    def post(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return redirect('login')
        
        form = PlaylistCreateEditForm(request.POST, request.FILES)
        if form.is_valid():
            # create a new playlist
            name = form.cleaned_data['name']
            pic = form.cleaned_data['pic']

            if pic :
                upload = Upload.objects.create(user=request.user, file=pic)
                playlist = Playlist.objects.create(user=request.user, name=name, picture=upload)
            else :
                playlist = Playlist.objects.create(user=request.user, name=name)
            return redirect('playlist', uuid=playlist.id)
        
        return render(request, 'playlist_create_f.html', {
            'form': form
        })
    
class SoundDownloadStreamView(View) :
    def get(self, request, *args, **kwargs):
        sound = kwargs.get('uuid', None)
        if sound is None:
            return redirect('index')
        
        sound = Sound.objects.get(id=sound)
        if sound is None:
            return redirect('index')
        
        response = FileResponse(sound.upload.file, as_attachment=True)
        response['Content-Disposition'] = f'attachment; filename="{sound.name}"'

        # add to history
        if request.user.is_authenticated :
            # delete all history that is the same
            History.objects.filter(user=request.user, sound=sound).delete()

            History.objects.create(user=request.user, sound=sound)

        return response

class SearchView(HTMXView) :
    def html_name(self):
        return "search"
    
    def get_context(self, *args, **kwargs) -> dict:
        # search sound matching the query
        query = self.request.GET.get('q', '')
        if query == '':
            return redirect('index')
        
        sounds = Sound.objects.filter(name__icontains=query)

        # serach user matching the query
        users_obj = get_user_model().objects.filter(username__icontains=query)

        users = []
        for user in users_obj:
            users.append({
                'user': user,
                'profile_picture': get_profile_picture(user)
            })

        # search album matching the query
        albums = Album.objects.filter(name__icontains=query)

        return {
            'query': query,
            'sounds': sounds,
            'users': users,
            'albums': albums,

            'empty': len(sounds) == 0 and len(users) == 0 and len(albums) == 0
        }