from urllib import request
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth import get_user_model
from .models import *
from footistix.models import *
from .forms import *
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import HttpResponseRedirect



def activateAccout(request, pk):
    
    User.objects.filter(pk=pk).update(is_active=True)
    print(pk)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'profile/'))

def profile(request):
    name = request.user
    id = request.user.id
    profile_only_points = Profile.objects.filter(user_id=id).only('points')[0]
    return render(request, 'Profile.html', locals())

def loginView(request):
    form = UserLogin(request.POST or None)
    if form.is_valid():
      username = form.cleaned_data.get("username")
      password = form.cleaned_data.get("password")
      user = authenticate(request, username=username, password=password)
      # if user is.active=false cant authenticate
      if user != None:
         login(request, user)
         if not user.is_active:
            print("user not activated")            
      else:
            print("user not valid")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'first/'))

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
