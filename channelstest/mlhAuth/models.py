from django.db import models
from django.contrib.auth.models import AbstractUser
# from allauth.socialaccount.models import SocialApp


# Create your models here.

# class SocialAppExtended(SocialApp):
#     icon = models.ImageField()

class MLHUser(AbstractUser):
	updated_at = models.DateTimeField(auto_now=True,
		help_text='The last time this record was updated.')
	
	def __str__(self):
		return "{}".format(self.email)
