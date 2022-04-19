from calendar import day_abbr
from collections import namedtuple
from threading import local

from bunch import bunchify
import collections
from email.policy import default
from itertools import product
from multiprocessing import context
from unicodedata import name
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.db import connection
from django.core.exceptions import ObjectDoesNotExist
from footistix.models import *
from account.models import *
from django.views.decorators.csrf import csrf_exempt
from urllib import parse
import datetime
from footistix.forms import *
from account.forms import *
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.db.models import F
from django.shortcuts import HttpResponseRedirect
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from django.views.generic import TemplateView
from django.conf import settings
from urllib.request import urlopen
import json
import requests


def firstRate(request):
   user_id = request.user.id
  
   if request.POST.get("logout"):
      logout(request)
 

   if request.POST.get("ratings"):
     pass 

   return render(request, 'BasicScoring.html')

class PlayerViewSet(ModelViewSet):
   queryset = Player.objects.all()
   serializer_class = PlayerSerializer
   #because of filter 
   def get_queryset(self):
       queryset = Player.objects.all()
       team_id = self.request.query_params.get('team_id')
       if team_id is not None:
          queryset = queryset.filter(team = team_id)
       return queryset
   def get_serializer_context(self):
       return {'request': self.request}



def TeamView(request, slug):
   name = slugToName(slug)
   API_TOKEN = '****'
   raw_url = f"https://soccer.sportmonks.com/api/v2.0/teams/search/"+ name +f"?api_token={API_TOKEN}&include=stats, rivals, league.season, squad.player,venue,coach,latest, upcoming"
   url = raw_url.replace(" ","%20")
   latest_url_raw = f"https://soccer.sportmonks.com/api/v2.0/teams/search/"+ name +f"?api_token={API_TOKEN}&include=latest.lineup"
   latest_url = latest_url_raw.replace(" ","%20")
  
   payload={}
   headers = {}
   # here need to use async for latest.lineup becasuse they are to big to wait
   response = requests.request("GET", url, headers=headers, data=payload)
   team_json = response.json()
   team = team_json['data'][0]
   nextGames = list()
   for count, each in enumerate(team['upcoming']['data']):
      if count <=5:
         game = dict()
         teams =  getTeamById(each['localteam_id'],each['visitorteam_id'])
         game['localTeam'] = teams['localTeam']
         game['visitorTeam'] = teams['visitorTeam']
         game['time'] = each['time']['starting_at']['date_time']
         game['timezone'] = each['time']['starting_at']['timezone']
         nextGames.append(game)
   lastGames = list()
   for count, each in enumerate(reversed(team['latest']['data'])):
      if count <=5:
         game = dict()
         teams =  getTeamById(each['localteam_id'],each['visitorteam_id'])
         game['localTeam'] = teams['localTeam']
         game['visitorTeam'] = teams['visitorTeam']
         game['localScores'] = each['scores']['localteam_score']
         game['visitorScores'] = each['scores']['visitorteam_score']
         lastGames.append(game)
   season_id = team['league']['data']['season']['data']['id']
   standings_url = f"https://soccer.sportmonks.com/api/v2.0/standings/season/"+ str(season_id) +f"?api_token={API_TOKEN}&include="
   payload={}
   headers = {}
   # here need to use async for latest.lineup becasuse they are to big to wait
   response_standings = requests.request("GET", standings_url, headers=headers, data=payload)
   standings_json = response_standings.json()
   all_standings = standings_json['data'][0]['standings']['data']
   standings = {}
   for each in all_standings:
      if each['team_name']==team['name']:
         standings=each
   return render(request, 'Team.html', locals())


class PlayerList(APIView):
   def get(self, request):
      players = Player.objects.all() 
      parameter = self.request.query_params.get('name')
      if parameter is not None:
         players = players.filter(name__contains=parameter)
      
      serializer = PlayerSerializer(players, many=True)
      return Response(serializer.data)
   
   def post(self, request):
      serializer = PlayerSerializer(data=request.data)
      serializer.is_valid(raise_exception=True)
      serializer.save()
      return Response(serializer.data, status=status.HTTP_201_CREATED)
      
@api_view() 
def searchPlayer(request):
   players = Player.objects.all()
   teams = Team.objects.all()
   NTeams = NationalTeam.objects.all()
   serializer = PlayerSearchSerializer(players, many=True,context={'request': request})
   teamSerializer = TeamSearchSerializer(teams, many=True, context={'request':request}) 
   nateamSerializer = NTeamSearchSerializer(NTeams, many=True, context={'request': request})
   #teamsSeri = PlayerSerializer(teams)
   return Response({"players":serializer.data, "nationals_teams":nateamSerializer.data, "teams":teamSerializer.data})

@api_view() 
def playerViewAPI(request, pk):
   player = Player.objects.get(pk = pk)
   serializer = PlayerSerializer(player)
   return Response(serializer.data)


@csrf_exempt
def saveRating(request):
   print(request.user.id)
   if request.POST.get("ratings"):
   #if request.user.is_authenticated:
      ratingsPOST = parse.parse_qs(request.POST.get("ratings"))
      playerIDPOST = parse.parse_qs(request.POST.get("player"))
      playerID = int((playerIDPOST['0'])[0])
      ratings={}
      for rate in ratingsPOST:
         key = (int(rate))
         value = int(ratingsPOST[rate][0])
         ratings[key] = value

   rating = Rating()
   rating.user = User.objects.get(id=request.user.id)
   rating.player = Player.objects.get(pk=playerID) 
   rating.accuracy = getAccuracy(playerID, ratings)
   rating.save()
 
   saveEachRate(request, playerID, ratings, rating)
   return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def getAccuracy(player_id, ratings):
   defaults = PlayerDefaults.objects.filter(player=player_id)
   ratesList = []
   for rate in ratings:
      default_value=defaults[rate].value
      accuracy = getAccuracyforEach(ratings[rate], default_value)
      ratesList.append(accuracy)
   sum = 0
   count = len(ratesList) 
   for each in ratesList:
      sum += each
   accuracy = sum/count
   return accuracy

def saveEachRate(request, player_id, ratings, rating):
   defaults = PlayerDefaults.objects.filter(player=player_id)
   points = 0
   for rate in ratings:
      default_value=defaults[rate].value         
      points +=100
      accuracy = getAccuracyforEach(ratings[rate], default_value)
      rating_skill = RatingSkill()
      rating_skill.rating = rating  
      rating_skill.accuracy = accuracy
      rating_skill.skill = Skill.objects.get(id=rate)
      rating_skill.rate = ratings[rate]
      rating_skill.save()
   Profile.objects.filter(user_id=request.user.id).update(points = F('points')+points)
   

def getAccuracyforEach(rate, default):
   accuracy = 0#% in percenteges%
   accuracy = 100-(abs(default-rate))/default*100
   return accuracy

def slugToName(slug):
   names = slug.split('-')
   name = ""
   for each in names:
      name += each.capitalize() 
      name += " "
   name  = name[0: -1]
   return name

def PlayerView(request, slug):
   name = slugToName(slug)
   playerObj = Player.objects.get(name=name)
   playerDefs = PlayerDefaults.objects.filter(player_id= playerObj.id)
   playerDefauts = []
   for each in playerDefs:
      playerDefauts.append(each.value)
   avrDefaults = getAvrDefault(playerDefs)
   API_TOKEN = '****'
   url = f"https://soccer.sportmonks.com/api/v2.0/players/search/"+ name +f"?api_token={API_TOKEN}&include=position,team, country, stats"
   response = requests.get(url.replace (" ","%20"))
   data_json = response.json()
   player=data_json['data'][0]
   playerOVRValue = playerOVR(playerObj.position, playerDefs)
   context = {'avrDefaults': avrDefaults, 'player':player, 'playerDefauts':playerDefauts, 'playerOVR':playerOVRValue, 'prefoot':playerObj.preferred_foot}
   
   return render(request, 'player_main.html', context)

def LeagueView(request,slug):
   name = slugToName(slug)
   league_db = League.objects.get(name = name)
   API_TOKEN = '****'
   url = f'https://soccer.sportmonks.com/api/v2.0/leagues/search/{name}?api_token={API_TOKEN}&include=country,season.stats.topscorer,season.upcoming'
   payload={}
   headers = {}
   response = requests.request("GET", url, headers=headers, data=payload)
   league_json = response.json()
   league = league_json['data'][0]
   # Need to be async
   nextGames = list()
   for count, each in enumerate(league['season']['data']['upcoming']['data']):
      if count <=5:
         game = dict()
         teams =  getTeamById(each['localteam_id'],each['visitorteam_id'])
         game['localTeam'] = teams['localTeam']
         game['visitorTeam'] = teams['visitorTeam']
         game['time'] = each['time']['starting_at']['date_time']
         game['timezone'] = each['time']['starting_at']['timezone']
         nextGames.append(game)
   season_id = league['season']['data']['id']
   standings_url = f'https://soccer.sportmonks.com/api/v2.0/standings/season/{season_id}?api_token={API_TOKEN}&include='
   payload1={}
   headers1 = {}
   response = requests.request("GET", standings_url, headers=headers1, data=payload1)
   standings_json = response.json()
   standings = standings_json['data'][0]['standings']['data']
   
   # This will be changed to rest with js - but for now 
   return render(request, 'league.html', locals())


# @api_view() 
def getTeamById(local_id, visitor_id):
   API_TOKEN = '****'
   teams = dict()
   for i in range(2):
      if i == 0:
         url = f'https://soccer.sportmonks.com/api/v2.0/teams/{local_id}?api_token={API_TOKEN}&include='
         team_json = returnJson(url)
         team_name = team_json['data']['name']
         teams['localTeam'] = team_name
      elif i == 1:
         url = f'https://soccer.sportmonks.com/api/v2.0/teams/{visitor_id}?api_token={API_TOKEN}&include='
         team_json = returnJson(url)
         team_name = team_json['data']['name']
         teams['visitorTeam'] = team_name
   return (teams)


def returnJson(url):
   payload={}
   headers = {}
   response = requests.request("GET", url, headers=headers, data=payload)
   json_data = response.json()
   return json_data
@api_view() 
def playerAverage(request, slug):
   name = slugToName(slug)
   playerObj = Player.objects.get(name=name)
   playerDefs = PlayerDefaults.objects.filter(player_id= playerObj.id)
   avrDefaults = getAvrDefault(playerDefs)
 
   return Response(avrDefaults)


def getAvrDefault(playerDefs):
   avrDefaults={}
   passingDefault = 0
   shootingDefault = 0
   physiqueDefault = 0
   defenseDefault = 0
   ballSkillDefault = 0
   counter = 0
   counter1 = 0
   counter2 = 0
   counter3 = 0
   counter4 = 0
   for each in playerDefs:
      if each.skill_id<=5 and each.value!= None:
         counter+=1
         passingDefault += each.value
      if each.skill_id<=12 and each.value!= None:
         counter1+=1
         shootingDefault += each.value
      if each.skill_id<=18 and each.value!= None:
         counter2+=1
         physiqueDefault += each.value
      if each.skill_id<=22 and each.value!= None:
         counter3+=1
         defenseDefault += each.value
      if each.skill_id<=24 and each.value!= None:
         counter4+=1
         ballSkillDefault += each.value   
   avrDefaults['passing'] = int(passingDefault/counter)
   avrDefaults['shooting'] = int(shootingDefault/counter1)
   avrDefaults['physique'] = int(physiqueDefault/counter2)
   avrDefaults['defense'] = int(defenseDefault/counter3)
   avrDefaults['ballSkill'] = int(ballSkillDefault/counter4)
   avrDefaultsList = []
   avrDefaultsList.append(int(passingDefault/counter))
   avrDefaultsList.append(int(shootingDefault/counter1))
   avrDefaultsList.append(int(physiqueDefault/counter2))
   avrDefaultsList.append(int(defenseDefault/counter3))
   avrDefaultsList.append(int(ballSkillDefault/counter4))
   return avrDefaults

def playerOVR(position, defaults):
   OVRTable = {'ST':[None, 0.05, None, None, None, 0.03, 0.19, 0.1, None, None, 0.1, None, 0.05, 0.04, None, None, 0.05, None, None, 0.13, None, None, 0.07, 0.1, None, None, None, None],
               'RW': None,'LT':None, 'LM':None} 
   
   ovr = 0
   ValuesForPosition = OVRTable[position]
   if ValuesForPosition != None:
      for count, each in enumerate(ValuesForPosition):
         if each is not None:
            ovr+= each*defaults[count].value
   pass