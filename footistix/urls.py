from django.urls import path
from django.urls.conf import include
from . import views
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('players', views.PlayerViewSet)
# router.register(r'auth', views.ExampleView)
urlpatterns = [
    path('', include(router.urls)),
    path('', views.firstRate),
    path('playersMethod/', views.PlayerList.as_view()),
    path('auth', views.ExampleView.as_view()),
    path('search/', views.searchPlayer),
    path('player/<slug:slug>/', views.PlayerViewClass.as_view(), name='player-api'),
    # path('player_api/<slug:slug>', views.playerViewAPI, name='player-api'),
    # path('player_api/<slug:slug>/<slug:stats>', views.playerViewAPI, name='player-api'),
    path('league_api/<slug:slug>', views.leagueViewAPI, name='player-api'),
    path('team_api/<slug:slug>', views.teamViewAPI, name='team-profile'),
    path('team/<slug:slug>', views.TeamView, name='team-profile'),
    path('nteam/<slug:slug>', views.NTeamView, name='nteam-api'),
    path('send_rate/', views.saveRating),
    # path('player/<slug:slug>', views.PlayerView, name='player-profile'),
    path('league/<slug:slug>', views.LeagueView, name='league-profile'),
    path('avrCompare/<slug:slug>', views.playerAverage, name='average-player'),
    path('getTeamById/<int:local_id>/<int:visitor_id>', views.getTeamById, name='getTeambyId'),
    # path('login', views.LoginView.as_view()),
    # path('playerInfo/<slug:slug>', views.PlayerDetails.as_view())
]