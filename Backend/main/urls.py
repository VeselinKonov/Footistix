from django.urls import path
from .views import get_team

urlpatterns = [
    path('getTeam/<slug:slug>/', get_team, name='checkserver'),
]