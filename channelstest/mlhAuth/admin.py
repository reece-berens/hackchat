from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import MLHUser

# Register your models here.

class MLHUserAdmin(BaseUserAdmin):
	model = MLHUser
	verbose_name_plural = 'MLH_Users'

admin.site.register(MLHUser, MLHUserAdmin)