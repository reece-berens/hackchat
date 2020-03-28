from django.shortcuts import render, redirect
from django.conf import settings
from django.urls import reverse

from .models import Message, Channel
from mlhAuth.models import MLHUser
import json, pytz
from django.utils import timezone

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
	context['selfIsOrganizer'] = json.dumps(loggedInUser.isOrganizer)

	#We want to make sure the channel exists in the database
	#If not, just go back to the chat landing page that will have all available channels on it
	roomsInDB = Channel.objects.filter(channelName = roomName).count()
	if (roomsInDB == 0):
		return redirect('../')

	lastMessages = Message.objects.filter(channelID=Channel.objects.get(channelName=roomName)).order_by('-messageTimestamp')[:settings.PREV_CHAT_MSGS_TO_LOAD][::-1]

	"""
	msgsForSend = [
		{
			'firstName': 'Organizer',
			'lastName': 'User',
			'contents': 'This is a test of the emergency broadcast system to see what the box will do with a whole heck of a lot of text dang we need even more text when we dont have the console window open my goodness',
			'email': 'rberens123@yahoo.com',
			'time': '10:00',
			'fromOrg': True,
		},
		{
			'firstName': 'Reece',
			'lastName': 'Berens',
			'contents': 'This is another long piece of text to see what the box for the current user will do when there is a lot of text in the box lorem ipsum stuff to make the text longer and see what the box does',
			'email': 'rberens@ksu.edu',
			'time': '10:05',
			'fromOrg': False,
		}
	]
	"""
	msgsForSend = []
	for i in lastMessages:
		msgsForSend.append({
			'firstName': i.author.first_name,
			'lastName': i.author.last_name,
			'email': i.author.email,
			'contents': i.messageText,
			'time': timezone.localtime(i.messageTimestamp, pytz.timezone('America/Chicago')).strftime("%a %I:%M %p"),
			'fromOrg': i.author.isOrganizer
		})
	print(type(msgsForSend))
	context['room_name'] = roomName
	context['previous_messages'] = msgsForSend
	context['channelList'] = getChannelList()
	context['participantList'] = getParticipantList()
	context['self_email'] = email
	return render(request,'room.html', context)

#This will get the lists of all organizers and normal users for the participant column
#Organizer list comes first, followed by normal user list
def getParticipantList():
	users = MLHUser.objects.order_by('last_name').order_by('first_name')
	userList = []
	for i in users:
		userList.append({
			'first_name': i.first_name,
			'last_name': i.last_name,
			'email': i.email,
			'isOrganizer': i.isOrganizer,
			})
	return userList

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