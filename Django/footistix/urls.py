from django.urls import path
from django.urls.conf import include
from . import views
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('players', views.PlayerViewSet)
urlpatterns = [
    path('', include(router.urls)),
    path('', views.firstRate),
    # path('playersMethod/', views.PlayerList.as_view()),
    path('search/', views.searchPlayer),
    path('playerAPI/<int:pk>', views.playerViewAPI, name='player-api'),
    path('team/<slug:slug>', views.TeamView, name='team-profile'),
    path('send_rate/', views.saveRating),
    path('player/<slug:slug>', views.PlayerView, name='player-profile'),
    path('league/<slug:slug>', views.LeagueView, name='league-profile'),
    path('avrCompare/<slug:slug>', views.playerAverage, name='average-player'),
    path('getTeamById/<int:local_id>/<int:visitor_id>', views.getTeamById, name='getTeambyId')
    # path('playerInfo/<slug:slug>', views.PlayerDetails.as_view())
]