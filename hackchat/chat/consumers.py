from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
import json
from asgiref.sync import async_to_sync
#from channels.db import database_sync_to_async
from .models import Message, Channel, ChannelPermissions
from mlhAuth.models import MLHUser


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
		dbMsg = Message()
		dbMsg.author = MLHUser.objects.filter(email=author)[0]
		dbMsg.messageText = message
		dbMsg.channelID = Channel.objects.filter(channelName=roomName)[0]
		print(type(Channel.objects.filter(channelName=roomName)[0]))
		print(Channel.objects.filter(channelName=roomName)[0].channelName)
		print(MLHUser.objects.filter(email=author)[0])
		#dbMsg.save()

		#Send message to room group
		async_to_sync(self.channel_layer.group_send)(
			self.room_group_name,
			{
				'type': 'chat_message',
				'message': message,
				'author': author
			}
		)
		
		#self.send(text_data = json.dumps({
		#	'message': message
		#}))
		

	#Receive message from room group
	def chat_message(self, event):
		message = event['message']
		author = event['author']
		print("In chat_message")
		#Send message to WebSocket
		self.send(text_data=json.dumps({
			'message': message,
			'author': author
		}))