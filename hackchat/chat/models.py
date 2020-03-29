from django.db import models
from mlhAuth.models import MLHUser

# Create your models here.

class Channel(models.Model):
	channelName = models.CharField(max_length=128, default='general')
	organizerOnly = models.BooleanField(default=False)
	newUserPermissionStatus = models.IntegerField(default=2)

	def __str__(self):
		return self.channelName

class ChannelPermissions(models.Model):
	channelID = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='channel_id_for_permission')
	participantID = models.ForeignKey(MLHUser, on_delete=models.CASCADE, related_name='participant_id_for_permission')
	permissionStatus = models.IntegerField(default=0)
	"""
		Permission status values:
			0 - cannot read or write to channel
			1 - can read messages, but not write (will receive notifications)
			2 - can read and write messages, can mention any single user
			3 - can read and write messages, no limit on mentions and has access to mentioning everyone and can remove messages from being viewed
			Permission 3 is reserved for organizers only
	"""
	def __str__(self):
		return "User {} and Channel {} - {}".format(self.participantID, self.channelID, self.permissionStatus)

class Message(models.Model):
	channelID = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='channel_id_for_message')
	author = models.ForeignKey(MLHUser, on_delete=models.CASCADE, related_name='participant_id_for_message_author')
	messageText = models.CharField(max_length=2048, default="")
	messageTimestamp = models.DateTimeField(auto_now=True) #automatically sets to time of creation in database