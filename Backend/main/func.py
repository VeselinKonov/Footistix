from constants import *
import requests
import ujson as json
import urllib

def getTeam(team, include = ""):
    req = urllib.request.urlopen(f'https://api.sportmonks.com/v3/football/teams/search/{team}?api_token={API_KEY}&include={include}')
    data = req.read().decode('utf-8')
    data = json.decode(data)
    data = data['data'][0]
    return data

def slugToName(slug):
   names = slug.split('-')
   name = ""
   for each in names:
      name += each.capitalize() 
      name += " "
   name  = name[0: -1]
   return name