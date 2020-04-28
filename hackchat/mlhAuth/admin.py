from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import MLHUser
from chat.models import Channel, ChannelPermissions

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

	def save_model(self, request, user, form, change):
		super().save_model(request, user, form, change)
		cpList = ChannelPermissions.objects.filter(participantID=user)
		if (user.isOrganizer == True):
			#Give the user organizer permissions on all channels
			for cp in cpList:
				cp.permissionStatus = 3
				cp.save()
		else:
			for cp in cpList:
				cp.permissionStatus = cp.channelID.defaultPermissionStatus
				cp.save()

admin.site.register(MLHUser, MLHUserAdmin)