from datetime import datetime
import email
from email.policy import default
from operator import mod
from pickle import TRUE
from pyexpat import model
from tkinter import CASCADE
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import json

#GlobalVal
MAX_LENGTH = 255

class Team(models.Model):
    name = models.CharField(max_length = MAX_LENGTH)
    league = models.CharField(max_length = 50)

class NationalTeam(models.Model):
    name = models.CharField(max_length = MAX_LENGTH)

class Player(models.Model):
    
    name = models.CharField(max_length = MAX_LENGTH)
    nationality = models.CharField(max_length = 50)
    #team = models.CharField(max_length=MAX_LENGTH)
    position = models.CharField(max_length=50)
    number = models.SmallIntegerField(null=True)
    height = models.SmallIntegerField(null=True)
    weight = models.SmallIntegerField(null=True)
    team = models.ForeignKey(Team, on_delete=models.PROTECT, null=True)
    national_team = models.ForeignKey(NationalTeam, on_delete=models.PROTECT, null=True)
    birth = models.DateField(null=True)
    age = models.SmallIntegerField(null=True)
    preferred_foot = models.CharField(max_length=5)
    market_value = models.IntegerField(null=True)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)


class Skill(models.Model):
    skill = models.CharField(max_length=MAX_LENGTH)

class PlayerDefaults(models.Model):
    player = models.ForeignKey(Player, on_delete=models.PROTECT)
    skill = models.ForeignKey(Skill, on_delete=models.PROTECT)
    value = models.SmallIntegerField(null=True) 
class PlayerValues(models.Model):
    player = models.ForeignKey(Player, on_delete=models.PROTECT)
    skill = models.ForeignKey(Skill, on_delete=models.PROTECT)
    value = models.SmallIntegerField(null=True)



# class User(AbstractUser):
#     email = models.EmailField(unique=True)
#     username = models.CharField(unique=True, max_length=MAX_LENGTH)

class Rating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    player = models.ForeignKey(Player, on_delete=models.PROTECT)
    # time = models.TimeField(null=True)
    accuracy = models.DecimalField(max_digits=3, decimal_places=1, default=0)
class RatingSkill(models.Model):
    rating = models.ForeignKey(Rating, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.PROTECT)
    rate = models.SmallIntegerField(null=True)
    accuracy = models.DecimalField(max_digits=3, decimal_places=1, default=0)

class League(models.Model):
    name = models.CharField(max_length=MAX_LENGTH)
    tier = models.CharField(max_length=MAX_LENGTH)
    