from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
import json, pytz
from asgiref.sync import async_to_sync
#from channels.db import database_sync_to_async
from .models import Message, Channel, ChannelPermissions
from mlhAuth.models import MLHUser
from django.utils import timezone


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
		message = textDataJson['message']
		author = textDataJson['authorEmail']
		roomName = textDataJson['roomName']
		print("In receive")
		#We need to store the message in the database here since this is where it comes in from the websocket
		authorObject = MLHUser.objects.filter(email=author)[0]
		channelObject = Channel.objects.filter(channelName=roomName)[0]
		dbMsg = Message()
		dbMsg.author = authorObject
		dbMsg.messageText = message
		dbMsg.channelID = channelObject

		#Check to make sure the user has permission to send message in group
		cPerm = ChannelPermissions.objects.filter(channelID=channelObject).filter(participantID=authorObject)[0]
		print(cPerm)
		if (cPerm.permissionStatus < 2):
			#The user does not have permission to send a message, so get out of the method
			return

		print(type(Channel.objects.filter(channelName=roomName)[0]))
		print(Channel.objects.filter(channelName=roomName)[0].channelName)
		print(MLHUser.objects.filter(email=author)[0])
		dbMsg.save()

		tempDateTime = dbMsg.messageTimestamp
		localDT = timezone.localtime(dbMsg.messageTimestamp, pytz.timezone('America/Chicago'))
		print(localDT)
		print(type(localDT))

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