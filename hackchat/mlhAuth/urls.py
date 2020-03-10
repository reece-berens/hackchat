from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from .provider import MLHProvider


urlpatterns = default_urlpatterns(MLHProvider)