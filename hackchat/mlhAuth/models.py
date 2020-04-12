from django.db import models
from django.contrib.auth.models import AbstractUser


class MLHUser(AbstractUser):
	updated_at = models.DateTimeField(auto_now=True, help_text='The last time this record was updated.')
	isOrganizer = models.BooleanField(default=False)
	muteUntilTime = models.DateTimeField()
	permanentMute = models.BooleanField(default=False)
	muteInstances = models.IntegerField(default=0)
	token = models.CharField(default="", max_length=10)

	def __str__(self):
		return "{}".format(self.email)
