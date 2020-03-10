from django.db import models
from django.contrib.auth.models import AbstractUser


class MLHUser(AbstractUser):
	updated_at = models.DateTimeField(auto_now=True, help_text='The last time this record was updated.')
	isOrganizer = models.BooleanField(default=False)

	def __str__(self):
		return "{}".format(self.email)
