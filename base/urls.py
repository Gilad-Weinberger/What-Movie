from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home, name='home'),
    path('movie/', views.Movie, name='movie')
]