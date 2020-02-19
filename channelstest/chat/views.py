from django.shortcuts import render
from django.conf import settings

from .models import Message

# Create your views here.

def index(request):
	return render(request, 'chat/index.html', {})

def room(request, roomName):
	lastTwoMessages = Message.objects.order_by('-created_timestamp')[:settings.PREV_MSGS_TO_DISPLAY_ON_LOAD][::-1]
	msgsForSend = []
	for i in lastTwoMessages:
		msgsForSend.append(i.message_text)
	print(type(msgsForSend))
	return render(request,'chat/room.html', {
		'room_name': roomName,
		'previous_messages': msgsForSend
	})