from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def checkserver(request):
    # user = Token.objects.get(request.auth).user
    return Response(data=request.user.email, status=status.HTTP_200_OK)

