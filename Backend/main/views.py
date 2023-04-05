from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .func import *

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_team(request, slug):
    name = slugToName(slug)
    team = getTeam(name)
    return Response(data=team, status=status.HTTP_200_OK)