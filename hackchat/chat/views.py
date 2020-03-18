from django.shortcuts import render, redirect
from django.conf import settings
from django.urls import reverse

from .models import Message

# Create your views here.
def index(request):
	context = settings.DEFAULT_CONTEXT
	#https://stackoverflow.com/questions/4642596/how-do-i-check-whether-this-user-is-anonymous-or-actually-a-user-on-my-system/4642607
	if (request.user.is_anonymous):
		#The user is not logged in, so we want to send them back to the login page
		return redirect('../accounts/login/')
	print(request.user.is_anonymous)
	return render(request, 'chatIndex.html', context)

def room(request, roomName):
	context = settings.DEFAULT_CONTEXT
	#https://stackoverflow.com/questions/4642596/how-do-i-check-whether-this-user-is-anonymous-or-actually-a-user-on-my-system/4642607
	if (request.user.is_anonymous):
		#The user is not logged in, so we want to send them back to the login page
		return redirect('../accounts/login/')

	lastMessages = [] #Message.objects.order_by('-created_timestamp')[:settings.PREV_CHAT_MSGS_TO_LOAD][::-1]
	msgsForSend = []
	for i in lastMessages:
		msgsForSend.append(i.message_text)
	print(type(msgsForSend))
	return render(request,'room.html', {
		'room_name': roomName,
		'previous_messages': msgsForSend
	})