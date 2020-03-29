from django.contrib import admin

from .models import Channel, ChannelPermissions
# Register your models here.

admin.site.register(Channel)
admin.site.register(ChannelPermissions)