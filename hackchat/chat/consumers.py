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

def formatEmailForGroup(email):
	return email.replace('@', 'AT')

#SYNCHRONOUS VERSION
class ChatConsumer(WebsocketConsumer):
	def connect(self):
		self.room_name = self.scope['url_route']['kwargs']['roomName']
		print("self.room_name in connect is {}".format(self.room_name))
		self.room_group_name = 'chat_%s' % self.room_name
		print(self.scope['user'].email)
		print(type(self.scope['user']))
		#Join room group
		async_to_sync(self.channel_layer.group_add)(
			self.room_group_name,
			self.channel_name
		)
		#Put the user in their own group for mutes and other things that are only for them
		
		async_to_sync(self.channel_layer.group_add)(
			"user_{}".format(formatEmailForGroup(self.scope['user'].email)),
			self.channel_name
		)
		
		self.accept()

	def disconnect(self, closeCode):
		async_to_sync(self.channel_layer.group_discard)(
			self.room_group_name,
			self.channel_name
		)
		async_to_sync(self.channel_layer.group_discard)(
			"user_{}".format(formatEmailForGroup(self.scope['user'].email)),
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
			token = textDataJson['token']
			#print("In receive")
			#We need to store the message in the database here since this is where it comes in from the websocket
			authorObject = MLHUser.objects.filter(email=author)[0]
			tzMuteUntilTime = timezone.localtime(authorObject.muteUntilTime, pytz.timezone(settings.TIME_ZONE))
			nowDate = timezone.localtime(timezone.now(), pytz.timezone(settings.TIME_ZONE))

			#print("token received {} should be {}".format(token, authorObject.token))
			if (token != authorObject.token):
				print("Author {} has an incorrect token: should be {} is {}".format(authorObject, authorObject.token, token))
				async_to_sync(self.channel_layer.group_send)(
					"user_{}".format(formatEmailForGroup(authorObject.email)),
					{
						'type': 'error',
						'email': author,
					}
				)
				return

			if (nowDate < tzMuteUntilTime):
				#The user is currently muted, so we should not let them send the message
				print("The user is currently muted until {}".format(tzMuteUntilTime))
				return
			
			if ('@everyone' in message and authorObject.isOrganizer == False):
				#The message tries to send a notification to everyone, but the author isn't an organizer
				message = message.replace('@everyone', '')

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
			muteTimeForBannedWord = 3
			#Make sure no banned words are in the message
			for bannedWord in settings.BANNED_WORD_LIST:
				if (bannedWord in message.lower()):
					#Mute the user and don't send the message
					dbMsg.containsBannedPhrase = True
					dbMsg.save()
					authorObject.muteInstances += muteTimeForBannedWord
					authorObject.muteUntilTime = timezone.localtime(timezone.now() + timedelta(minutes=muteTimeForBannedWord), pytz.timezone(settings.TIME_ZONE))
					authorObject.save()
					async_to_sync(self.channel_layer.group_send)(
						"user_{}".format(formatEmailForGroup(authorObject.email)),
						{
							'type': 'user_muted',
							'email': authorObject.email,
							'muteMinutes': muteTimeForBannedWord,
							'forBannedWord': True
						}
					)
					unmuteThread = threading.Thread(target=self.notify_unmute, args=(authorObject.email, muteTimeForBannedWord))
					unmuteThread.start()
					return

			tempDateTime = dbMsg.messageTimestamp
			localDT = timezone.localtime(dbMsg.messageTimestamp, pytz.timezone(settings.TIME_ZONE))

			#Send message to room group
			async_to_sync(self.channel_layer.group_send)(
				self.room_group_name,
				{
					'type': 'chat_message',
					'id': dbMsg.id,
					'messageType': 'chatMessage',
					'contents': message,
					'email': author,
					'firstName': authorObject.first_name,
					'lastName': authorObject.last_name,
					'time': localDT.strftime("%a %I:%M %p"),
					'fromOrg': authorObject.isOrganizer
				}
			)

			if ('@everyone' in message):
				for channelToNotify in Channel.objects.all():
					async_to_sync(self.channel_layer.group_send)(
						'chat_{}'.format(channelToNotify.channelName),
						{
							'type': 'mention_from_other_channel',
							#'messageType': 'chatMessage',
							'contents': message,
							'fromChannel': self.room_name
						}
					)
		elif (typeOfMessage == 'muteUser'):
			emailToMute = textDataJson['mutingEmail']
			requestEmail = textDataJson['requestingEmail']
			muteMinutes = int(textDataJson['muteMinutes'])
			token = textDataJson['token']
			requestUser = MLHUser.objects.get(email=requestEmail)
			print("emailToMute is {}".format(emailToMute))
			print("requestEmail is {}".format(requestEmail))
			if (requestUser.isOrganizer == False):
				return
			user = MLHUser.objects.get(email=emailToMute)
			authorObject = MLHUser.objects.get(email=requestEmail)
			if (token != authorObject.token):
				print("Author {} has an incorrect token: should be {} is {}".format(authorObject, authorObject.token, token))
				async_to_sync(self.channel_layer.group_send)(
					"user_{}".format(formatEmailForGroup(authorObject.email)),
					{
						'type': 'error',
						'email': author,
					}
				)
				return
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
				"user_{}".format(formatEmailForGroup(user.email)),
				{
					'type': 'user_muted',
					'email': user.email,
					'muteMinutes': muteMinutes,
					'forBannedWord': False
				}
			)
		elif (typeOfMessage == 'lastReadMessage'):
			print("GOT LAST MESSAGE ID FOR THIS USER")
			userEmail = textDataJson['email']
			channelName = textDataJson['channelName']
			token = textDataJson['token']
			print(textDataJson)
			print(type(textDataJson['lastMessageID']))
			lastMsgID = int(textDataJson['lastMessageID'])
			authorObject = MLHUser.objects.filter(email=userEmail)[0]
			if (token != authorObject.token):
				print("Author {} has an incorrect token: should be {} is {}".format(authorObject, authorObject.token, token))
				async_to_sync(self.channel_layer.group_send)(
					"user_{}".format(formatEmailForGroup(authorObject.email)),
					{
						'type': 'error',
						'email': author,
					}
				)
				return
			cp = ChannelPermissions.objects.filter(participantID=authorObject).get(channelID=Channel.objects.get(channelName=channelName))
			cp.lastReadMessage = lastMsgID
			cp.save()
		elif (typeOfMessage == 'getPreviousMessages'):
			userEmail = textDataJson['email']
			channelName = textDataJson['channelName']
			token = textDataJson['token']
			print(textDataJson)
			print(type(textDataJson['earliestMessageID']))
			earliestMsgID = int(textDataJson['earliestMessageID'])
			authorObject = MLHUser.objects.get(email=userEmail)
			if (token != authorObject.token):
				print("Author {} has an incorrect token: should be {} is {}".format(authorObject, authorObject.token, token))
				async_to_sync(self.channel_layer.group_send)(
					"user_{}".format(formatEmailForGroup(authorObject.email)),
					{
						'type': 'error',
						'email': author,
					}
				)
				return
			filterChannel = Channel.objects.get(channelName=channelName)
			validMessages = Message.objects.filter(channelID=filterChannel).filter(id__lt=earliestMsgID).filter(containsBannedPhrase=False).order_by('-id')[:settings.PREV_CHAT_MSGS_TO_LOAD][::-1]
			print(validMessages)
			print(type(validMessages))
			msgList = []
			for m in validMessages:
				msgList.append({
					'id': m.id,
					'firstName': m.author.first_name,
					'lastName': m.author.last_name,
					'email': m.author.email,
					'contents': m.messageText,
					'time': timezone.localtime(m.messageTimestamp, pytz.timezone('America/Chicago')).strftime("%a %I:%M %p"),
					'fromOrg': m.author.isOrganizer
				})
			async_to_sync(self.channel_layer.group_send)(
				"user_{}".format(formatEmailForGroup(authorObject.email)),
				{
					'type': 'previous_messages',
					'email': authorObject.email,
					'previousMessages': msgList
				}
			)
		#self.send(text_data = json.dumps({
		#	'message': message
		#}))
	
	def mention_from_other_channel(self, event):
		self.send(text_data=json.dumps({
			'messageType': 'mentionInOtherChannel',
			'contents': event['contents'],
			'fromChannel': event['fromChannel'],
		}))

	#Receive message from room group
	def chat_message(self, event):
		print("In chat_message")
		#Send message to WebSocket
		self.send(text_data=json.dumps({
			'messageType': 'chatMessage',
			'id': event['id'],
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
			'muteMinutes': event['muteMinutes'],
			'forBannedWord': event['forBannedWord']
		}))

	def user_unmuted(self, event):
		self.send(text_data=json.dumps({
			'messageType': 'userUnmuted',
			'email': event['email']
		}))

	def previous_messages(self, event):
		self.send(text_data=json.dumps({
			'messageType': 'previousMessages',
			'email': event['email'],
			'messageList': event['previousMessages']
		}))

	def error(self, event):
		self.send(text_data=json.dumps({
			'messageType': 'error',
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
			"user_{}".format(formatEmailForGroup(userEmail)),
			{
				'type': 'user_unmuted',
				'email': userEmail
			}
		)

