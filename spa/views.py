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
from .models import History, Playlist, Comment

from django.http import HttpResponse

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

def _get_album_or_playlist_context(request, is_playlist, *args, **kwargs):
    uuid = kwargs.get('uuid', None)
    if uuid is None :
        return {}
    try :
        if is_playlist :
            obj = Playlist.objects.get(id=uuid)
        else :
            obj = Album.objects.get(id=uuid)
    except :
        return {}
        
    if obj is None :
        return {}
    
    if is_playlist :
        # PLAYLIST IS PRIVATE
        if obj.user != request.user:
            return {}
    
        eform = PlaylistCreateEditForm()
    else :
        eform = AlbumCreateEditForm()
    # put data in the form
    eform.fields['name'].initial = obj.name

    sounds = obj.sounds.all()

    return {
        ("playlist" if is_playlist else "album"): obj,
        "edit_form": eform,
        "tracks": sounds,
        "is_playlist": is_playlist
    }

class PlaylistView(HTMXView) :
    def html_name(self):
        return "playlist"
    
    def get_context(self, *args, **kwargs) -> dict:
        return _get_album_or_playlist_context(self.request, True, *args, **kwargs)
    
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
        return _get_album_or_playlist_context(self.request, False, *args, **kwargs)
    
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
        
        try :
            sound = Sound.objects.get(id=sound)
        except Sound.DoesNotExist:
            return {}

        if sound is None:
            return {}
        
        eform = SoundEditForm()
        # put data in the form
        eform.fields['name'].initial = sound.name

        # comments
        comments = Comment.objects.filter(sound=sound).order_by('-created_at')

        return {
            "sound": sound,
            "profile_picture_uploader": get_profile_picture(sound.user),
            "edit_form": eform,

            "comments": comments
        }
    
    def post(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return redirect('login')

        sound = kwargs.get('uuid', None)
        if sound is None:
            return redirect('index')
        
        try :
            sound = Sound.objects.get(id=sound)
        except Sound.DoesNotExist:
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
        
        try :
            sound = Sound.objects.get(id=sound)
        except Sound.DoesNotExist:
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
    
class SearchAddTracksView(View) :
    def get(self, request, *args, **kwargs):
        if not request.htmx:
            return redirect('index')
        
        query = request.GET.get('q', '')
        is_playlist = int(request.GET.get('p', 0))

        if query == '':
            # set empty list
            sounds = []
        else :
            if is_playlist :
                sounds = Sound.objects.filter(name__icontains=query)
            else :
                # must be from the user and not added to the album
                sounds = Sound.objects.filter(name__icontains=query, user=request.user).filter(album__isnull=True)

        if len(sounds) == 0 :
            return HttpResponse("No sounds found")
        
        obj = kwargs.get('obj_uuid', None)
        if obj is None:
            return render(request, 'add_track_search.html', {
                'sounds': sounds,
                "is_playlist": is_playlist
            })
        
        try :
            if is_playlist :
                obj = Playlist.objects.get(id=obj)
            else :
                obj = Album.objects.get(id=obj)
        except :
            return HttpResponse("Object not found")

        if obj is None:
            return HttpResponse("Object not found")

        return render(request, 'add_track_search.html', {
            'sounds': sounds,
            'object': obj,
            "is_playlist": is_playlist
        })
    
class PostCommentView(HTMXView) :
    def post(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return redirect('login')
        
        sound = kwargs.get('sound_uuid', None)
        if sound is None:
            return redirect('index')
        
        try :
            sound = Sound.objects.get(id=sound)
        except Sound.DoesNotExist:
            return redirect('index')
        
        comment = request.POST.get('comment', '')
        if comment == '':
            return render(request, f"comment_section.html", {
                'comments': Comment.objects.filter(sound=sound).order_by('-created_at'),
                'sound': sound
            })
        
        Comment.objects.create(user=request.user, sound=sound, text=comment)
        return render(request, f"comment_section.html", {
            'comments': Comment.objects.filter(sound=sound).order_by('-created_at'),
            'sound': sound
        })
    
class PlaylistTrackView(View) :
    def get(self, request, *args, **kwargs):
        return redirect('index')
    
    def model_class(self):
        return Playlist
    def model_name(self):
        return "playlist"
    def is_playlist(self):
        return True
    
    def put(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return redirect('login')
        
        mclass = self.model_class()
        
        playlist = kwargs.get('uuid', None)
        if playlist is None:
            return redirect('index')
        
        try :
            playlist = mclass.objects.get(id=playlist)
        except :
            return redirect('index')
        
        sound = kwargs.get('sound_uuid', None)
        if sound is None:
            return redirect('index')
        
        try :
            sound = Sound.objects.get(id=sound)
        except Sound.DoesNotExist:
            return redirect('index')
        
        if not self.is_playlist() :
            # must not inside any album before
            album = Album.objects.filter(sounds=sound).first()
            if album is not None :
                return redirect('index')
        
        playlist.sounds.add(sound)

        return render(request, self.model_name() + '.html',
            _get_album_or_playlist_context(request, self.is_playlist(), uuid=playlist.id)              
        )
    
    def delete(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return redirect('login')
        
        mclass = self.model_class()
        
        playlist = kwargs.get('uuid', None)
        if playlist is None:
            return redirect('index')
            
        try :
            playlist = mclass.objects.get(id=playlist)
        except :
            return redirect('index')
        
        sound = kwargs.get('sound_uuid', None)
        if sound is None:
            return redirect('index')
        
        try :
            sound = Sound.objects.get(id=sound)
        except Sound.DoesNotExist:
            return redirect('index')
        
        playlist.sounds.remove(sound)

        return render(request, self.model_name() + '.html',
            _get_album_or_playlist_context(request, self.is_playlist(), uuid=playlist.id)              
        )
    
# just the same as PlaylistTrackView
class AlbumTrackView(PlaylistTrackView) :
    def model_class(self):
        return Album
    def model_name(self):
        return "album"
    def is_playlist(self):
        return False
    
import json
    
class PlaylistViewSoundsJSON(View) :
    def is_playlist(self):
        return True
    
    def get(self, request, *args, **kwargs):
        obj = kwargs.get('uuid', None)
        if obj is None:
            return redirect('index')
        
        try :
            if self.is_playlist() :
                obj = Playlist.objects.get(id=obj)
            else :
                obj = Album.objects.get(id=obj)
        except :
            return redirect('index')

        if obj is None:
            return HttpResponse("[]", content_type='application/json')
        
        sounds = obj.sounds.all()
        
        # return as JSON
        json_string = json.dumps([{
            'media_url': '/soundf/' + str(sound.id) + '/',
            'uuid': str(sound.id),
            'name': sound.name,
            'cover_url': sound.get_cover(),
            'artist': sound.user.username,
            'name_link': '/sound/' + str(sound.id) + '/',
            'artist_link': '/profile/' + sound.user.username + '/',
        } for sound in sounds])

        return HttpResponse(json_string, content_type='application/json')
    
class AlbumViewSoundsJSON(PlaylistViewSoundsJSON) :
    def is_playlist(self):
        return False