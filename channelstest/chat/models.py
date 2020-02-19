from django.db import models

class Message(models.Model):
	message_text = models.CharField(max_length=1024, default='')
	author = models.CharField(max_length=256, default='')
	created_timestamp = models.DateTimeField(auto_now_add=True)