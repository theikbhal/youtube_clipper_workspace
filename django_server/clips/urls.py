from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/clip/', views.api_clip, name='api_clip'),
    path('downloads/<str:filename>/', views.download_file, name='download_file'),
]
