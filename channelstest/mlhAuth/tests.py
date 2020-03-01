from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.tests import OAuth2TestsMixin
from allauth.tests import MockedResponse, TestCase

from authentication.provider import MLHProvider


class GitHubTests(OAuth2TestsMixin, TestCase):
    provider_id = MLHProvider.id

    def get_mocked_response(self):
        return MockedResponse(200, """
        {
            "id": 1,
            "email": "test@example.com",
            "created_at": "2015-07-08T18:52:43Z",
            "updated_at": "2015-07-27T19:52:28Z",
            "first_name": "John",
            "last_name": "Doe",
            "level_of_study": "Undergraduate",
            "major": "Computer Science",
            "shirt_size": "Unisex - L",
            "dietary_restrictions": "None",
            "special_needs": "None",
            "date_of_birth": "1985-10-18",
            "gender": "Male",
            "phone_number": "+1 555 555 5555",
            "school": {
              "id": 1,
              "name": "Rutgers University"
            },
            "scopes": [
              "email", "phone_number", "demographics", "birthday", "education", "event"
            ]
          }""")

    def test_account_name_null(self):
        """String conversion when GitHub responds with empty name"""
        data = """{
            "type": "User",
            "id": 201022,
            "login": "pennersr",
            "name": null
        }"""
        self.login(MockedResponse(200, data))
        socialaccount = SocialAccount.objects.get(uid='201022')
        self.assertIsNone(socialaccount.extra_data.get('name'))
        account = socialaccount.get_provider_account()
        self.assertIsNotNone(account.to_str())
        self.assertEqual(account.to_str(), 'pennersr')
