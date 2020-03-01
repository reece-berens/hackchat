from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    name = 'mlhAuth'
    WEB_URL = 'https://my.mlh.io'
    API_URL = '{0}/api/v2'.format(WEB_URL)
