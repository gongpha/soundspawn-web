from django.contrib import admin
from django.urls import path

from django.urls import include

from .views import IndexView, DiscoverView, LoginView, LogoutView, SignupView, MeView
from .views import ProfileView, PlaylistView, AlbumView, SoundView, SearchView
from .views import PlaylistCreateView, AlbumCreateView, SoundCreateView, AlbumTrackView
from .views import EditProfileView, UploadSoundView, SoundDownloadStreamView, PlaylistTrackView
from .views import NewAlbumView, NewPlaylistView, PostCommentView, SearchAddTracksView
from .views import PlaylistViewSoundsJSON, AlbumViewSoundsJSON

from django.conf import settings
from django.conf.urls.static import static

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

     # rest
    path('playlist/<str:uuid>/sounds', PlaylistViewSoundsJSON.as_view(), name='playlist'),
    path('album/<str:uuid>/sounds', AlbumViewSoundsJSON.as_view(), name='album'),

    path('playlist/<str:uuid>/<str:sound_uuid>', PlaylistTrackView.as_view(), name='playlist_track'),
    path('album/<str:uuid>/<str:sound_uuid>', AlbumTrackView.as_view(), name='album_track'),

    path('playlist/<str:uuid>/', PlaylistView.as_view(), name='playlist'),
    path('album/<str:uuid>/', AlbumView.as_view(), name='album'),
    path('sound/<str:uuid>/', SoundView.as_view(), name='sound'),

    path('soundf/<str:uuid>/', SoundDownloadStreamView.as_view(), name='soundf'),

    path('me/edit/', EditProfileView.as_view(), name='edit_profile'),
    path('uploadsound/', UploadSoundView.as_view(), name='upload_sound'),
    path('newalbum/', NewAlbumView.as_view(), name='new_album'),
    path('newplaylist/', NewPlaylistView.as_view(), name='new_playlist'),
    
    path('search/', SearchView.as_view(), name='search'),
    path('searchaddtracks/<str:obj_uuid>', SearchAddTracksView.as_view(), name='search_add_tracks'),

    path('comment/<str:sound_uuid>/', PostCommentView.as_view(), name='post_comment'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)