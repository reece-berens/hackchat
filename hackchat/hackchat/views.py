from django.views.generic import TemplateView
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.conf import settings
from mlhAuth.models import MLHUser

def index(request):
	context = settings.DEFAULT_CONTEXT
	print(request.user) #Will return AnonymousUser if not logged in, will show email address otherwise
	if (request.user.is_anonymous):
		context['user'] = {'loggedIn': False}
	else:
		context['user'] = {'loggedIn': True}
		mlhu = MLHUser.objects.get(email=request.user)
		context['user']['firstName'] = mlhu.first_name
		context['user']['lastName'] = mlhu.last_name
	return render(request, 'index.html', context)

def callback(request):
	context = settings.DEFAULT_CONTEXT
	print(request.user) #This shows the e-mail address of the user that is currently logged in
	return redirect('../chat/general')
	#return render(request, 'callback.html', context)
