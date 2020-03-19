from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse
from django.db.models.query import QuerySet, EmptyQuerySet

from mlhAuth.models import MLHUser
from chat.models import Channel, ChannelPermissions


class AccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        url = '/callback'
        print('inside get_login_redirect_url in AccountAdapter')
        print(request.path)
        if 'login/callback' in request.path:
            print(request)
            #print(request.user)
            profile = MLHUser.objects.get(email=request.user)
            #print(profile)
            allChannels = Channel.objects.all()
            #print(type(allChannels))
            for i in allChannels:
                try:
                    cpObject = ChannelPermissions.objects.filter(channelID=i.id).filter(participantID=profile.id)
                    #print("Type of cpObject is {}".format(type(cpObject)))
                    #print(cpObject)
                    if not cpObject:
                        #We need to create a ChannelPermission object
                        print("Empty query set")
                        newPermission = ChannelPermissions()
                        newPermission.channelID = i
                        newPermission.participantID = profile
                        if (profile.isOrganizer == True):
                            newPermission.permissionStatus = 3
                        else:
                            #Normal user
                            if (i.organizerOnly == True):
                                newPermission.permissionStatus = 0
                            else:
                                newPermission.permissionStatus = 2
                        newPermission.save()
                    else:
                        print("Not empty query set")
                        #Update the current one
                        newPermission = cpObject[0]
                        newPermission.channelID = i
                        newPermission.participantID = profile
                        if (profile.isOrganizer == True):
                            newPermission.permissionStatus = 3
                        else:
                            #Normal user
                            if (i.organizerOnly == True):
                                newPermission.permissionStatus = 0
                            else:
                                newPermission.permissionStatus = 2
                        newPermission.save()
                except Exception as e:
                    print(e)
        print('callback-' + url)
        return url
