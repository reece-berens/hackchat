from django.views.generic import TemplateView
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.conf import settings

def index(request):
	context = settings.DEFAULT_CONTEXT
	print(request.user) #Will return AnonymousUser if not logged in, will show email address otherwise
	return render(request, 'index.html', context)

def callback(request):
	context = settings.DEFAULT_CONTEXT
	print(request.user) #This shows the e-mail address of the user that is currently logged in
	return redirect('../chat/general')
	#return render(request, 'callback.html', context)
