from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import MLHUser

# Register your models here.

class MLHUserAdmin(BaseUserAdmin):
	model = MLHUser
	verbose_name_plural = 'MLH_Users'
	# https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#custom-users-and-django-contrib-admin
	fieldsets = BaseUserAdmin.fieldsets + (
		(None, {'fields': ('isOrganizer',)}),
		(None, {'fields': ('muteUntilTime',)}),
		(None, {'fields': ('permanentMute',)}),
		(None, {'fields': ('muteInstances',)}),
	)

admin.site.register(MLHUser, MLHUserAdmin)