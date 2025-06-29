from django.urls import path
from . import views


urlpatterns = [
    path('my_fish_status/', views.get_my_fish_status, name='get_my_fish_status'),
    path('all_fish_status/', views.get_all_fish_status, name='get_all_fish_status'),
    path('fish_list/', views.get_fish_list, name='get_fish_list'),
    path('all_fish_list/', views.get_all_fish_list, name='get_all_fish_list'),
    path('upload_fish_csv/', views.upload_fish_csv, name='upload_fish_csv'),
    path('download_fish_csv/', views.download_fish_csv, name='download_fish_csv'),
    path('download_all_fish_csv/', views.download_all_fish_csv, name='download_all_fish_csv')
]