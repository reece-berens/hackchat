from django.views.generic import TemplateView
from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings

def index(request):
	context = settings.DEFAULT_CONTEXT
	return render(request, 'index.html', context)



