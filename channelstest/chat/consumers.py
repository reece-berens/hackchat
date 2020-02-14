from channels.generic.websocket import WebsocketConsumer
import json

class ChatConsumer(WebsocketConsumer):
	def connect(self):
		self.accept()

	def disconnect(self, closeCode):
		pass

	def receive(self, text_data):
		textDataJson = json.loads(text_data)
		message = textDataJson['message']
		self.send(text_data = json.dumps({
			'message': message
		}))