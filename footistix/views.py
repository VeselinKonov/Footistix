from calendar import day_abbr
from collections import namedtuple
from threading import local

# from bunch import bunchify
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
from django.utils import timezone
import datetime   

from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework import views
from . import serializers
import ujson
now = datetime.datetime.now()
now_user = timezone.now()

@csrf_exempt
def firstRate(request):
   user_id = request.user.id
  
   if request.POST.get("logout"):
      logout(request)
 

   if request.POST.get("ratings"):
      #if request.user.is_authenticated:
      ratings = parse.parse_qs(request.POST.get("ratings"))
      timer = parse.parse_qs(request.POST.get("timer"))
      rate1 = (ratings["1"])[0]
      rate4 = (ratings["4"])[0]
      rate5 = (ratings["5"])[0]
      print(f'''Rate 1: {rate1} and Rate 4: {rate4} and Rate 5: {rate5} by user: {request.user}''')
   return render(request, 'BasicScoring.html', locals())
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
   API_TOKEN = 'ZD1pc28BlB0liaOUXKLvTFdGKcXBqHmYK8wu6QRaYR47zjfp7CYb08V1euyx'
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

class PlayerViewClass(APIView):
   serializer_class = PlayerSkillsSerializer
   def get(self, request, slug):
      name = slugToName(slug)
      qparam = self.request.GET.get('details')
      if qparam == 'api':
         API_TOKEN = 'ZD1pc28BlB0liaOUXKLvTFdGKcXBqHmYK8wu6QRaYR47zjfp7CYb08V1euyx'
         url = f"https://soccer.sportmonks.com/api/v2.0/players/search/"+ name +f"?api_token={API_TOKEN}&include=position,team, country, stats"
         response = requests.get(url.replace (" ","%20"))
         # data_json = response.json() // check whitch is fast
         data_json = ujson.loads(response.text)
         player=data_json['data'][0]
         player_info = {
            'fullname':player['fullname'],
            'birthdate':player['birthdate'],
            "height": player['height'],
            "weight": player['weight'],
            "image_path": player['image_path'],
            'team':{
               'name':player['team']['data']['name'],
               'logo':player['team']['data']['logo_path']
               } 

            }
         return Response({'details':player_info})
      
      playerObj = Player.objects.get(name=name)
      playerDefs = PlayerDefaults.objects.filter(player_id= playerObj.id).values_list('skill', 'value')
      # skills = Skill.objects.all()
      playerDefautsView = dict()
      playerDefauts = dict()
      for enum, each in enumerate(playerDefs):
         playerDefauts[each[0]]=each[1]
      for enum, each in enumerate(Skill.objects.all()):
         playerDefautsView[each.skill] = playerDefs[enum][1]
      avrDefaults = getAvrDefault(playerDefs)
      playerOVRValue = playerOVR(playerObj.position, playerDefs)
      
      
      defaults = PlayerSerializer(playerDefauts)
      serializer = PlayerSerializer(playerObj)
      context = {'details':serializer.data, 'playerDefauts':playerDefautsView, 'avrDefaults': avrDefaults,  'playerOVR':playerOVRValue, 'prefoot':playerObj.preferred_foot}
      return Response(context)

   def post(self, request, slug):
      if request.user.is_authenticated:
         player = get_player_object(slug)
         playerDefs = PlayerDefaults.objects.filter(player_id= player.id)
         playerDefauts = dict()
         for each in playerDefs:
            playerDefauts[(each.skill.id)]=each.value
         
         ratingData = [{"user":request.user.id, "player":player.id, "accuracy":0}]

         serializerRating = PlayerRatingsSeraializer(data = ratingData, many = True)
         if serializerRating.is_valid():
            rating = serializerRating.save()
            #its list because if 'many = True'
            rating_id = rating[0].id
            #creating new rating instance on every rate
            request_data = list()
            for i, each in enumerate(request.data):
               new = each
               new['rating'] = rating_id
               new['accuracy'] = get_accuracy(new['rate'], new['skill'], playerDefauts)
               request_data.append(new)
            #//
            print(request_data)
            serializerSkill = PlayerSkillsSerializer(data = request_data, many = True)
            if serializerSkill.is_valid() and type(request.data) == list:
               # try:
               serializerSkill.save()
               # except:
               #    return Response(serializerSkill.errors, status=status.HTTP_406_NOT_ACCEPTABLE)
               return Response(serializerSkill.data, status=status.HTTP_201_CREATED)
            else:
               return Response(serializerSkill.errors, status=status.HTTP_400_BAD_REQUEST)
         else:
            return Response("Cant seri rating", status=status.HTTP_400_BAD_REQUEST)      
      return Response("Log in required!", status=status.HTTP_401_UNAUTHORIZED)
         

def get_player_object(slug):
   name = slugToName(slug)
   player_object = Player.objects.get(name=name)
   return player_object
def get_accuracy(rate, skill, playerDefs = dict()):
   accuracy = getAccuracyforEach(rate, playerDefs[skill])
   return accuracy
@api_view() 
def searchPlayer(request):
   players = Player.objects.all()
   teams = Team.objects.all()
   NTeams = NationalTeam.objects.all()
   serializer = PlayerSearchSerializer(players, many=True,context={'request' : request})
   teamSerializer = TeamSearchSerializer(teams, many=True, context={'request' : request}) 
   # nateamSerializer = NTeamSearchSerializer(NTeams, many=True, context={'request' : request})
   #teamsSeri = PlayerSerializer(teams)
   return Response({"players":serializer.data,  "teams":teamSerializer.data})
@api_view()
def NTeamView(request):
   nteam = NationalTeam.object.a
   return 1
@api_view() 
def playerViewAPI(request, slug):
   name = slugToName(slug)
   playerObj = Player.objects.get(name=name)
   playerDefs = PlayerDefaults.objects.filter(player_id= playerObj.id)
   playerDefauts = dict()
   for each in playerDefs:
      playerDefauts[(each.skill.skill)]=each.value
   avrDefaults = getAvrDefault(playerDefs)
   playerOVRValue = playerOVR(playerObj.position, playerDefs)
   API_TOKEN = 'ZD1pc28BlB0liaOUXKLvTFdGKcXBqHmYK8wu6QRaYR47zjfp7CYb08V1euyx'
   url = f"https://soccer.sportmonks.com/api/v2.0/players/search/"+ name +f"?api_token={API_TOKEN}&include=position,team, country, stats"
   response = requests.get(url.replace (" ","%20"))
   data_json = response.json()
   player=data_json['data'][0]
   player_info = {
      'fullname':player['fullname'],
      'birthdate':player['birthdate'],
      "height": player['height'],
      "weight": player['weight'],
      "image_path": player['image_path'],
      'team':{
         'name':player['team']['data']['name'],
         'logo':player['team']['data']['logo_path']
         } 

      }
   context = {'avrDefaults': avrDefaults, 'player':player, 'playerDefauts':playerDefauts, 'playerOVR':playerOVRValue, 'prefoot':playerObj.preferred_foot}
   # defaults = PlayerSerializer(playerDefauts)
   serializer = PlayerSerializer(playerObj)
   return Response({'details':serializer.data,'player':player_info, 'defaults':playerDefauts, 'avrDefaults':avrDefaults, 'playerOVR':playerOVRValue})

@api_view() 
def leagueViewAPI(request, slug):
   name = slugToName(slug)
   league_db = League.objects.get(name=name)
   API_TOKEN = 'ZD1pc28BlB0liaOUXKLvTFdGKcXBqHmYK8wu6QRaYR47zjfp7CYb08V1euyx'
   url = f'https://soccer.sportmonks.com/api/v2.0/leagues/search/{name}?api_token={API_TOKEN}&include=country,season.stats.topscorer,season.upcoming'
   payload={}
   headers = {}
   print(url)
   response = requests.request("GET", url, headers=headers, data=payload)
   league_json = response.json()
   league = league_json['data'][0]
   # Need to be async
   # nextGames = list()
   # for count, each in enumerate(league['season']['data']['upcoming']['data']):
   #    if count <=5:
   #       game = dict()
   #       teams =  getTeamById(each['localteam_id'],each['visitorteam_id'])
   #       game['localTeam'] = teams['localTeam']
   #       game['visitorTeam'] = teams['visitorTeam']
   #       game['time'] = each['time']['starting_at']['date_time']
   #       game['timezone'] = each['time']['starting_at']['timezone']
   #       nextGames.append(game)   
   # season_id = league['season']['data']['id']
   # standings_url = f'https://soccer.sportmonks.com/api/v2.0/standings/season/{season_id}?api_token={API_TOKEN}&include='
   # payload1={}
   # headers1 = {}
   # response = requests.request("GET", standings_url, headers=headers1, data=payload1)
   # standings_json = response.json()
   # standings = standings_json['data'][0]['standings']['data']
   # league_info = {
   #    'name': league['name'],
   #    'logo': league['logo_path'],
   #    'num_of_clubs': league['season']['data']['stats']['data']['number_of_clubs'],
   #    'num_of_matches': league['season']['data']['stats']['data']['number_of_matches'],
   #    'num_of_played_matches': league['season']['data']['stats']['data']['number_of_matches_played'],
   #    'num_of_goals_scorred': league['season']['data']['stats']['data']['number_of_goals'],
   #    'avg_goals_per_match': league['season']['data']['stats']['data']['avg_goals_per_match']
   # }
   # league_next_matches = dict()
   # for x, each in enumerate(nextGames):
   #    league_next_matches[x+1] = each

   # league_most_cleansheets = league['season']['data']['stats']['data']['goalkeeper_most_cleansheets_number']

   
   # api_content = {'details': league_info, 'next matches': league_next_matches,'most cleansheets':league_most_cleansheets, 'standings': standings}
   
   return Response(league)

@api_view()
def teamViewAPI(request, slug):
   name = slugToName(slug)
   API_TOKEN = 'ZD1pc28BlB0liaOUXKLvTFdGKcXBqHmYK8wu6QRaYR47zjfp7CYb08V1euyx'
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
   # nextGames = list()
   # for count, each in enumerate(team['upcoming']['data']):
   #    if count <=5:
   #       game = dict()
   #       teams =  getTeamById(each['localteam_id'],each['visitorteam_id'])
   #       game['localTeam'] = teams['localTeam']
   #       game['visitorTeam'] = teams['visitorTeam']
   #       game['time'] = each['time']['starting_at']['date_time']
   #       game['timezone'] = each['time']['starting_at']['timezone']
   #       nextGames.append(game)
   # lastGames = list()
   # for count, each in enumerate(reversed(team['latest']['data'])):
   #    if count <=5:
   #       game = dict()
   #       teams =  getTeamById(each['localteam_id'],each['visitorteam_id'])
   #       game['localTeam'] = teams['localTeam']
   #       game['visitorTeam'] = teams['visitorTeam']
   #       game['localScores'] = each['scores']['localteam_score']
   #       game['visitorScores'] = each['scores']['visitorteam_score']
   #       lastGames.append(game)
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
   team_info = {'name': team['name'], 'logo' : team['logo_path'], 'rival_teams': team['rivals']['data'], 'league': team['league']['data']['name'], 'coach': team['coach']['data']['fullname'],
                'staduim' : {
                  'capacity': team['venue']['data']['capacity'],
                   'location': team['venue']['data']['coordinates']
                }}
   
   api_content = {'details': team_info,  'standings':standings}
   return Response(api_content)  

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
   return float("{:.1f}".format(accuracy))

def player(request, pk, slug):
   player = Player.objects.get(pk=pk)
   return render(request, 'Player.html', locals())


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
   API_TOKEN = 'ZD1pc28BlB0liaOUXKLvTFdGKcXBqHmYK8wu6QRaYR47zjfp7CYb08V1euyx'
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
   API_TOKEN = 'ZD1pc28BlB0liaOUXKLvTFdGKcXBqHmYK8wu6QRaYR47zjfp7CYb08V1euyx'
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
   API_TOKEN = 'ZD1pc28BlB0liaOUXKLvTFdGKcXBqHmYK8wu6QRaYR47zjfp7CYb08V1euyx'
   teams = dict()
   
   for i in range(2):
      if i == 0:
         url = f'https://soccer.sportmonks.com/api/v2.0/teams/{local_id}?api_token={API_TOKEN}&include='
         print(url)
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
      if each[0]<=5 and each[1] != None:
         counter+=1
         passingDefault += each[1]
      if each[0]<=12 and each[1] != None:
         counter1+=1
         shootingDefault += each[1]
      if each[0]<=18 and each[1] != None:
         counter2+=1
         physiqueDefault += each[1]
      if each[0]<=22 and each[1] != None:
         counter3+=1
         defenseDefault += each[1]
      if each[0]<=24 and each[1] != None:
         counter4+=1
         ballSkillDefault += each[1]   
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
   OVRTable = {'ST': [None, 0.05, None, 0.04, 0.04, 0.03, 0.19, 0.05, 0.05, 0.06, 0.1, 0.07, 0.05, 0.04, None, None, 0.05, None, None, 0.1, None, None, 0.08, 0.1, None, None, None, None],
               'CAM': [None, 0.18, 0.05, 0.1, 0.15, 0.03, 0.05, None, None, None, None, None, 0.04, 0.05, 0.04, None, None, None, None, 0.09, None, None, 0.12, 0.12, None, None, None, None],
               'CM': [None, 0.17, 0.13, 0.1, 0.13, 0.04, 0.05, None, None, None, None, None, None, None, 0.06, None, None, None, 0.025, 0.06, 0.05, None, 0.07, 0.14, None, None, None, None], 
               'CDM': [None, 0.15, 0.1, 0.07, 0.04, None, None, None, None, None, None, None, None, None, 0.06, None, 0.05, None, 0.1, None, 0.13, 0.17, None, 0.15, None, None, None, None],
               'LW': [0.09, 0.09, None, 0.03, 0.06, 0.05, 0.11, None, None, None, None, None, 0.08, 0.08, None, None, None, None, None, 0.11, None, None, 0.17, 0.15, None, None, None, None],
               'RW': [0.09, 0.09, None, 0.03, 0.06, 0.05, 0.11, None, None, None, None, None, 0.08, 0.08, None, None, None, None, None, 0.11, None, None, 0.17, 0.15, None, None, None, None],
               'LM': [0.1, 0.07, 0.05, 0.04, 0.06, None, 0.06, None, None, None, None, None, 0.1, 0.1, 0.04, None, None, None, None, 0.1, None, None, 0.16, 0.15, None, None, None, None], 
               'RM': [0.1, 0.07, 0.05, 0.04, 0.06, None, 0.06, None, None, None, None, None, 0.1, 0.1, 0.04, None, None, None, None, 0.1, None, None, 0.16, 0.15, None, None, None, None],
               'LB': [0.1, 0.08, 0.03, 0.04, 0.03, None, None, 0.04, None, None, None, 0.03, 0.07, 0.07, 0.1, None, None, None, 0.13, None, 0.11, 0.1, 0.07, 0.05, None, None, None, None],
               'RB': [0.1, 0.08, 0.03, 0.04, 0.03, None, None, 0.04, None, None, None, 0.03, 0.07, 0.07, 0.1, None, None, None, 0.13, None, 0.11, 0.1, 0.07, 0.05, None, None, None, None],
               'CB': [None, 0.05, 0.07, 0.03, None, None, None, 0.14, None, 0.01, None, None, 0.05, None, None, 0.05, 0.13, None, 0.17, None, 0.15, 0.15, None, 0.04, None, None, None, None],
               'GK': [None, 0.05, 0.05, None, None, None, None, None, None, None, None, None, None, None, None, 0.02, 0.08, None, None, None, None, 0.03, 0.02, 0.01, 0.2, 0.22, 0.22, 0.2]
               } 
   
   ovr = 0
   ValuesForPosition = OVRTable[position]
   if ValuesForPosition != None:
      for count, each in enumerate(ValuesForPosition):
         if each is not None and defaults[count][1] is not None:
            ovr+= each*defaults[count][1]
   return ovr



class ExampleView(APIView):
   authentication_classes = [SessionAuthentication, BasicAuthentication]
   permission_classes = [IsAuthenticated]

   def get(self, request, format=None):
        content = {
            'user': str(request.user),  # `django.contrib.auth.User` instance.
            'auth': str(request.auth),  # None
        }
        return Response(content)
   
