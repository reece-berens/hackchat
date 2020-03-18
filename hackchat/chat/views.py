from django.shortcuts import render, redirect
from django.conf import settings
from django.urls import reverse

from .models import Message, Channel
from mlhAuth.models import MLHUser

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
	email = request.user
	loggedInUser = MLHUser.objects.get(email=email)
	print(loggedInUser)
	print(type(loggedInUser))
	print(loggedInUser.isOrganizer)
	context['selfIsOrganizer'] = loggedInUser.isOrganizer

	#We want to make sure the channel exists in the database
	#If not, just go back to the chat landing page that will have all available channels on it
	roomsInDB = Channel.objects.filter(channelName = roomName).count()
	if (roomsInDB == 0):
		return index(request)

	lastMessages = [] #Message.objects.order_by('-created_timestamp')[:settings.PREV_CHAT_MSGS_TO_LOAD][::-1]
	msgsForSend = []
	for i in lastMessages:
		msgsForSend.append(i.message_text)
	print(type(msgsForSend))
	context['room_name'] = roomName
	context['previous_messages'] = msgsForSend
	context['channelList'] = getChannelList()
	userLists = getUserLists()
	context['userList'] = userLists[1]
	context['organizerList'] = userLists[0]
	return render(request,'room.html', context)

#This will get the lists of all organizers and normal users for the participant column
#Organizer list comes first, followed by normal user list
def getUserLists():
	users = MLHUser.objects.order_by('last_name').order_by('first_name')
	userList = []
	organizerList = []
	for i in users:
		if (i.isOrganizer == False):
			userList.append({
				'first_name': i.first_name,
				'last_name': i.last_name,
				'email': i.email,
				'isOrganizer': False,
				})
		else:
			organizerList.append({
				'first_name': i.first_name,
				'last_name': i.last_name,
				'email': i.email,
				'isOrganizer': True,
				})
	return (organizerList, userList)

#This will get the list of all channels registered to the chat server
#It will be used for the chat landing page and channel column of the main chat page
def getChannelList():
	channels = Channel.objects.order_by('channelName')
	channelList = []
	for i in channels:
		channelList.append({
			'channelName': i.channelName,
			'organizerOnly': i.organizerOnly
		})
	return channelList