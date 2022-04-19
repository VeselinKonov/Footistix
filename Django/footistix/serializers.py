from dataclasses import field, fields
from rest_framework import serializers

from account.models import MAX_LENGTH
from footistix.models import Player, PlayerDefaults, RatingSkill, Team, NationalTeam
from rest_framework.reverse import reverse
from slugify import slugify

class PlayerSearchSerializer(serializers.ModelSerializer):
    hyperlink = serializers.SerializerMethodField()
    # hyperlinkToApi = serializers.HyperlinkedIdentityField(view_name='player-api')
    class Meta:
        model = Player
        fields = ['name', 'hyperlink']

    def get_hyperlink(self, obj):
        result = '{}'.format(
            reverse('player-profile', args=[slugify(obj.name)], request=self.context['request']),
            'param=foo'
        )
        return result

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = '__all__'

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
        model = RatingSkill
        fields = '__all__'

class PlayerAverages(serializers.Serializer):
    skillCategory = serializers.CharField(max_length = 50)
    value = serializers.IntegerField()