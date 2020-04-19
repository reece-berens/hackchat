from django.shortcuts import render, redirect
from django.conf import settings
from django.urls import reverse

from .models import Message, Channel, ChannelPermissions
from mlhAuth.models import MLHUser
import json, pytz, secrets
from django.utils import timezone

# Create your views here.
def index(request):
	context = settings.DEFAULT_CONTEXT
	#https://stackoverflow.com/questions/4642596/how-do-i-check-whether-this-user-is-anonymous-or-actually-a-user-on-my-system/4642607
	if (request.user.is_anonymous):
		#The user is not logged in, so we want to send them back to the login page
		return redirect('../accounts/login/')
	print(request.user.is_anonymous)
	context['user'] = {'loggedIn': True}
	email = request.user
	loggedInUser = MLHUser.objects.get(email=email)
	context['user']['firstName'] = loggedInUser.first_name
	context['user']['lastName'] = loggedInUser.last_name

	#Build list of channels to send to landing page
	context['channelList'] = getChannelList(loggedInUser)

	return render(request, 'chatIndex.html', context)

def room(request, roomName):
	context = settings.DEFAULT_CONTEXT
	#https://stackoverflow.com/questions/4642596/how-do-i-check-whether-this-user-is-anonymous-or-actually-a-user-on-my-system/4642607
	if (request.user.is_anonymous):
		#The user is not logged in, so we want to send them back to the login page
		return redirect('../accounts/login/')
	context['user'] = {'loggedIn': True}
	email = request.user
	loggedInUser = MLHUser.objects.get(email=email)
	context['user']['firstName'] = loggedInUser.first_name
	context['user']['lastName'] = loggedInUser.last_name
	#print(loggedInUser)
	#print(type(loggedInUser))
	#print(loggedInUser.isOrganizer)
	context['selfIsOrganizer'] = json.dumps(loggedInUser.isOrganizer)

	#We want to make sure the channel exists in the database
	#If not, just go back to the chat landing page that will have all available channels on it
	roomsInDB = Channel.objects.filter(channelName = roomName).count()
	if (roomsInDB == 0):
		return redirect('../')
	currentChannel = Channel.objects.get(channelName = roomName)

	#See if the user is currently muted
	tzMuteUntilTime = timezone.localtime(loggedInUser.muteUntilTime, pytz.timezone(settings.TIME_ZONE))
	nowDate = timezone.localtime(timezone.now(), pytz.timezone(settings.TIME_ZONE))

	if (nowDate < tzMuteUntilTime):
		#The user is currently muted, so we should not let them send the message
		#print("The user is currently muted until {}".format(tzMuteUntilTime))
		context['startMuted'] = True
	else:
		context['startMuted'] = False

	#Generate new token for the user
	# https://docs.python.org/3/library/secrets.html
	newToken = secrets.token_urlsafe(5)
	loggedInUser.token = newToken
	loggedInUser.save()

	#Load all unread messages for the user in this channel
	cp = ChannelPermissions.objects.filter(participantID=loggedInUser).get(channelID=currentChannel)
	lastReadMessageID = cp.lastReadMessage
	lastMessages = Message.objects.filter(channelID=currentChannel).filter(id__gt=lastReadMessageID).order_by('-id')[::-1]
	#If we have read all of the messages, show the last few
	if (len(lastMessages) == 0):
		lastMessages = Message.objects.filter(channelID=currentChannel).order_by('-messageTimestamp')[:settings.PREV_CHAT_MSGS_TO_LOAD][::-1]

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
			'id': i.id,
			'firstName': i.author.first_name,
			'lastName': i.author.last_name,
			'email': i.author.email,
			'contents': i.messageText,
			'time': timezone.localtime(i.messageTimestamp, pytz.timezone('America/Chicago')).strftime("%a %I:%M %p"),
			'fromOrg': i.author.isOrganizer
		})
	context['room_name'] = roomName
	context['previous_messages'] = msgsForSend
	context['channelList'] = getChannelList(loggedInUser)
	context['participantList'] = getParticipantList()
	context['self_email'] = email
	context['self_name'] = "{} {}".format(loggedInUser.first_name, loggedInUser.last_name)
	context['token'] = loggedInUser.token
	context['currentRoom'] = roomName
	return render(request,'room.html', context)

#This will get the lists of all organizers and normal users for the participant column
#Organizer list comes first, followed by normal user list
def getParticipantList():
	users = MLHUser.objects.order_by('last_name').order_by('first_name')
	userList = []
	for i in users:
		userList.append({
			'id': i.id,
			'firstName': i.first_name,
			'lastName': i.last_name,
			'email': i.email,
			'isOrganizer': i.isOrganizer,
			})
	return userList

#This will get the list of all channels registered to the chat server
#It will be used for the chat landing page and channel column of the main chat page
def getChannelList(loggedInUser):
	"""
	channels = Channel.objects.order_by('channelName')
	channelList = []
	for i in channels:
		channelList.append({
			'id': i.id,
			'channelName': i.channelName,
			'organizerOnly': i.organizerOnly
		})
	return channelList
	"""
	CPfromDB = ChannelPermissions.objects.filter(participantID=loggedInUser)
	CfromDB = Channel.objects.all().order_by('channelName')
	channelsList = []
	for c in CfromDB:
		#Find the channels that we have a valid CP for
		cp = CPfromDB.get(channelID=c)
		print(cp)
		if (cp.permissionStatus > 0):
			channelsList.append({
				'id': c.id,
				'channelName': c.channelName,
			})
	return channelsList