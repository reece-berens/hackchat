from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse

from mlhAuth.models import MLHUser


class AccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        url = super(AccountAdapter, self).get_login_redirect_url(request)
        if 'login/callback' in request.path:
            try:
                profile = MLHUser.objects.get(user=request.user)
            except MLHUser.DoesNotExist:
                profile = None
            if profile is None:
                url = reverse('registration:register')

        return url
