from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
import json, pytz
from asgiref.sync import async_to_sync
#from channels.db import database_sync_to_async
from .models import Message, Channel, ChannelPermissions
from mlhAuth.models import MLHUser
from django.utils import timezone
from datetime import datetime, timedelta
from django.conf import settings

import threading, time

utc = pytz.UTC

#SYNCHRONOUS VERSION
class ChatConsumer(WebsocketConsumer):
	def connect(self):
		self.room_name = self.scope['url_route']['kwargs']['roomName']
		self.room_group_name = 'chat_%s' % self.room_name
		#Join room group
		async_to_sync(self.channel_layer.group_add)(
			self.room_group_name,
			self.channel_name
		)
		self.accept()

	def disconnect(self, closeCode):
		async_to_sync(self.channel_layer.group_discard)(
			self.room_group_name,
			self.channel_name
		)

	#Receive message from WebSocket
	def receive(self, text_data):
		textDataJson = json.loads(text_data)
		typeOfMessage = textDataJson['messageType']
		if (typeOfMessage == 'message'):
			message = textDataJson['message']
			author = textDataJson['authorEmail']
			roomName = textDataJson['roomName']
			#print("In receive")
			#We need to store the message in the database here since this is where it comes in from the websocket
			authorObject = MLHUser.objects.filter(email=author)[0]
			tzMuteUntilTime = timezone.localtime(authorObject.muteUntilTime, pytz.timezone(settings.TIME_ZONE))
			nowDate = timezone.localtime(timezone.now(), pytz.timezone(settings.TIME_ZONE))

			if (nowDate < tzMuteUntilTime):
				#The user is currently muted, so we should not let them send the message
				print("The user is currently muted until {}".format(tzMuteUntilTime))
				return
			
			channelObject = Channel.objects.filter(channelName=roomName)[0]
			dbMsg = Message()
			dbMsg.author = authorObject
			dbMsg.messageText = message
			dbMsg.channelID = channelObject

			#Check to make sure the user has permission to send message in group
			cPerm = ChannelPermissions.objects.filter(channelID=channelObject).filter(participantID=authorObject)[0]
			if (cPerm.permissionStatus < 2):
				#The user does not have permission to send a message, so get out of the method
				print("The user does not have enough permissions to send a message here")
				print(cPerm)
				return

			#print(type(Channel.objects.filter(channelName=roomName)[0]))
			#print(Channel.objects.filter(channelName=roomName)[0].channelName)
			#print(MLHUser.objects.filter(email=author)[0])
			dbMsg.save()

			tempDateTime = dbMsg.messageTimestamp
			localDT = timezone.localtime(dbMsg.messageTimestamp, pytz.timezone(settings.TIME_ZONE))

			#Send message to room group
			async_to_sync(self.channel_layer.group_send)(
				self.room_group_name,
				{
					'type': 'chat_message',
					'messageType': 'chatMessage',
					'contents': message,
					'email': author,
					'firstName': authorObject.first_name,
					'lastName': authorObject.last_name,
					'time': localDT.strftime("%a %I:%M %p"),
					'fromOrg': authorObject.isOrganizer
				}
			)
		elif (typeOfMessage == 'muteUser'):
			emailToMute = textDataJson['mutingEmail']
			requestEmail = textDataJson['requestingEmail']
			muteMinutes = int(textDataJson['muteMinutes'])
			requestUser = MLHUser.objects.get(email=requestEmail)
			print("emailToMute is {}".format(emailToMute))
			print("requestEmail is {}".format(requestEmail))
			if (requestUser.isOrganizer == False):
				return
			user = MLHUser.objects.get(email=emailToMute)
			if (muteMinutes == -1):
				#permanent mute
				user.permanentMute = True
			else:
				user.muteUntilTime = timezone.localtime(timezone.now() + timedelta(minutes=muteMinutes), pytz.timezone(settings.TIME_ZONE))
				#self.notify_unmute(user.email, schedule=timedelta(minutes=muteMinutes))

				####################### HERE'S THE THREADING TEST #################################
				unmuteThread = threading.Thread(target=self.notify_unmute, args=(user.email, muteMinutes))
				unmuteThread.start()
			user.muteInstances += 1
			user.save()
			for c in ChannelPermissions.objects.filter(participantID=user):
				#Set all permissions to 1 (read-only) for the channels we have access to
				cChannel = c.channelID
				if (cChannel.organizerOnly == False and cChannel.defaultPermissionStatus > 0):
					c.permissionStatus = 1
					c.save()
			async_to_sync(self.channel_layer.group_send)(
				self.room_group_name,
				{
					'type': 'user_muted',
					'email': user.email,
					'muteMinutes': muteMinutes
				}
			)
		
		#self.send(text_data = json.dumps({
		#	'message': message
		#}))
		

	#Receive message from room group
	def chat_message(self, event):
		print("In chat_message")
		#Send message to WebSocket
		self.send(text_data=json.dumps({
			'messageType': 'chatMessage',
			'contents': event['contents'],
			'email': event['email'],
			'firstName': event['firstName'],
			'lastName': event['lastName'],
			'time': event['time'],
			'fromOrg': event['fromOrg']
		}))

	def user_muted(self, event):
		self.send(text_data=json.dumps({
			'messageType': 'userMuted',
			'email': event['email'],
			'muteMinutes': event['muteMinutes']
		}))

	def user_unmuted(self, event):
		self.send(text_data=json.dumps({
			'messageType': 'userUnmuted',
			'email': event['email']
		}))

	#@background(schedule=15)
	def notify_unmute(self, userEmail, timeToMute):
		print("Inside background task notify_unmute")
		print("Sleeping for {} minutes".format(timeToMute))
		time.sleep(60 * int(timeToMute))
		print("Resetting channel permissions and notifying everyone")
		for c in ChannelPermissions.objects.filter(participantID=MLHUser.objects.get(email=userEmail)):
			#Set all permissions to 2 (read and write) that we have access to
			if (c.permissionStatus == 1 and c.channelID.defaultPermissionStatus == 2):
				c.permissionStatus = 2
				c.save()
		async_to_sync(self.channel_layer.group_send)(
					self.room_group_name,
					{
						'type': 'user_unmuted',
						'email': userEmail
					}
				)

