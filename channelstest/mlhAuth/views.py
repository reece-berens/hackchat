import requests

from allauth.socialaccount import app_settings
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.oauth2.views import (
    OAuth2Adapter,
    OAuth2CallbackView,
    OAuth2LoginView,
)

from django.contrib.auth import get_user_model
from mlhAuth.apps import AuthenticationConfig as auth_settings
from mlhAuth.provider import MLHProvider
from allauth.account.signals import user_signed_up
from django.dispatch import receiver


class MLHOAuth2Adapter(OAuth2Adapter):
    provider_id = MLHProvider.id
    settings = app_settings.PROVIDERS.get(provider_id, {})

    web_url = auth_settings.WEB_URL
    api_url = auth_settings.API_URL

    access_token_url = '{0}/oauth/token'.format(web_url)
    authorize_url = '{0}/oauth/authorize'.format(web_url)
    profile_url = '{0}/user'.format(api_url)
    many_profiles_url = '{0}/users'.format(api_url)

    def complete_login(self, request, app, token, **kwargs):
        params = {'access_token': token.token}
        resp = requests.get(self.profile_url, params=params)
        extra_data = resp.json()
        if extra_data['status'] == 'OK':
            extra_data = extra_data['data']
            return self.get_provider().sociallogin_from_response(
                request, extra_data
            )
        raise Exception("Login Error")

    def get_profile(self, token):
        params = {'access_token': token.token}
        resp = requests.get(self.profile_url, params=params)
        profile = resp.json()
        if resp.status_code == 200 and profile:
            return profile
        return None


@receiver(user_signed_up)
def retrieve_social_data(request, user, **kwargs):
    """Signal, that gets extra data from sociallogin and put it to profile."""

    # in this signal I can retrieve the obj from SocialAccount
    data = SocialAccount.objects.filter(user=user, provider='mlh')
    user.username = user.email
    user.save()


oauth2_login = OAuth2LoginView.adapter_view(MLHOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(MLHOAuth2Adapter)
