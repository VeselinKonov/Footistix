from dataclasses import field, fields
from pyexpat import model
from rest_framework import serializers

from account.models import MAX_LENGTH
from footistix.models import Player, PlayerDefaults, RatingSkill, Skill, Team, NationalTeam, Rating
from account.models import User
from rest_framework.reverse import reverse
from slugify import slugify
from django.db import IntegrityError
from django.core.exceptions import ValidationError


class PlayerSearchSerializer(serializers.ModelSerializer):
    hyperlink = serializers.SerializerMethodField()
    # hyperlinkToApi = serializers.HyperlinkedIdentityField(view_name='player-api')
    class Meta:
        model = Player
        fields = ['name', 'hyperlink']

    def get_hyperlink(self, obj):
        result = '{}'.format(
            reverse('player-api', args=[slugify(obj.name)], request=self.context['request']),
            'param=foo'
        )
        return result

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = '__all__'

class  PlayerSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["skill"]
class PlayerSkillsSerializer(serializers.ModelSerializer):
    # player_skill_set = PlayerSkillSerializer(many=True)
    class Meta:
        model = RatingSkill
        fields = '__all__'
        def create(self, validated_data):
            try:
                return super().create(validated_data)
            except IntegrityError as e:
                raise serializers.ValidationError(str(e))
        # fields = '__all__'
    # rate = serializers.IntegerField(read_only=True)
    # def create(self, validated_data):
        
    #     # rating = Rating()
    #     # rating.user = User.objects.get(id=request.user.id)
    #     # rating.player = Player.objects.get(pk=playerID) 
    #     # rating.accuracy = getAccuracy(playerID, ratings)
    #     # rating.save()

    #     # user = User.objects.create(**attrs)
    #     # Profile.objects.create(user=user)
    #     # print(validated_data)
        
    #     return RatingSkill.objects.create(**validated_data)


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'

class NationalTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = NationalTeam
        fields = '__all__'

class TeamSearchSerializer(serializers.ModelSerializer):
    # hyperlink = serializers.HyperlinkedIdentityField(view_name='team-api')
    hyperlink = serializers.SerializerMethodField()
    class Meta:
        model = Team
        fields = ['name', 'hyperlink']
    
    def get_hyperlink(self, obj):
        result = '{}'.format(
            reverse('team-profile', args=[slugify(obj.name)], request=self.context['request'])
        )
        return result
class NTeamSearchSerializer(serializers.ModelSerializer):
    hyperlink = serializers.HyperlinkedIdentityField(view_name='nteam-api')
    class Meta:
        model = NationalTeam
        fields = ['name', 'hyperlink']


class PlayerRatingsSeraializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'
    def create(self, validated_data):
        return Rating.objects.create(**validated_data)
class PlayerAverages(serializers.Serializer):
    skillCategory = serializers.CharField(max_length = 50)
    value = serializers.IntegerField()