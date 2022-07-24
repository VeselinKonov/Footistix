import imp
from urllib import request
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth import get_user_model
from .models import *
from footistix.models import *
from .forms import *
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import HttpResponseRedirect

from rest_framework import permissions
from rest_framework import views
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework import generics
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import redirect, render, get_object_or_404

# from . import 
from account.serializers import *

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from rest_framework.generics import GenericAPIView


# Create your views here.
def activateAccout(request, pk):
    
    User.objects.filter(pk=pk).update(is_active=True)
    print(pk)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'profile/'))

def profile(request):
    name = request.user
    id = request.user.id
    profile_only_points = Profile.objects.filter(user_id=id).only('points')[0]
    return render(request, 'Profile.html', locals())

# def loginView(request):
#     form = UserLogin(request.POST or None)
#     if form.is_valid():
#       username = form.cleaned_data.get("username")
#       password = form.cleaned_data.get("password")
#       user = authenticate(request, username=username, password=password)
#       # if user is.active=false cant authenticate
#       if user != None:
#          login(request, user)
#          if not user.is_active:
#             print("user not activated")            
#       else:
#             print("user not valid")
#     return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'first/'))

def RegistrationView(request):
    form = UserRegister(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get("username")
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password1")
        password2 = form.cleaned_data.get("password2")
        try:
            new_user = User.objects.create_user(username, email, password)
            profile = Profile.objects.create(user_id = new_user.id, points = 0)
            try:
                new_user = authenticate(username=username,password=password)
                login(request, new_user)
            except:
                print('cant login')
        except:
           user = None
           print("Cant register")
    else:
      print("RegFormNotValid")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'first/'))


class LoginView(views.APIView):
    # This view should be accessible also for unauthenticated users.
    permission_classes = (permissions.AllowAny,)
    serializer_class = LoginSerializer
    # def get(self, request):
    #     logout(request)
    #     return Response("Log in", status=status.HTTP_401_UNAUTHORIZED)
    def post(self, request, format=None):
        serializer = LoginSerializer(data=self.request.data,
            context={ 'request': self.request })
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return Response("Logged in succesfuly", status=status.HTTP_202_ACCEPTED)


class RegistrationView(generics.RetrieveAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegistrationSerializer
    def get(self, request):
        return Response("Hello")
    def post(self, request, format=None):
        serializer = RegistrationSerializer(data=self.request.data,
            context={ 'request': self.request })
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        link = "https://www.footistix.com/activation"
        return Response({
            "activational-link": link + str(user.id),
        } , status=status.HTTP_201_CREATED)

@method_decorator(login_required, name='dispatch')
class ProfileView(generics.RetrieveAPIView, generics.UpdateAPIView):

    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user
    
   

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
    def patch(request, pk):
        User.objects.filter(pk=pk).update(is_active=True)
        print(pk)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'profile/'))
