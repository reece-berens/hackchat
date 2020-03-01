from allauth.socialaccount.providers.oauth2.urls import default_urlpatterns

from authentication.provider import MLHProvider


urlpatterns = default_urlpatterns(MLHProvider)