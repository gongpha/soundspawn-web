from django.contrib import admin
from django.urls import path

from django.urls import include

from .views import IndexView
from .views import DiscoverView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('discover/', DiscoverView.as_view(), name='discover'),
]