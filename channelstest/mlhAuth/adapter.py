from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse

from mlhAuth.models import MLHUser


class AccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        url = super(AccountAdapter, self).get_login_redirect_url(request)
        url = '/callback'
        print('hi')
        if 'login/callback' in request.path:
            try:
                print(request)
                print(request.user)
                profile = MLHUser.objects.get(email=request.user)
            except MLHUser.DoesNotExist:
                print("Does not exist")
                profile = None
            if profile is None:
                url = reverse('registration:register')
        print('callback-' + url)
        return url
