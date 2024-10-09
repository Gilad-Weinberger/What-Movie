from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home, name='home'),
    path('movie/<str:movie_name>/', views.Movie, name='movie'),
]