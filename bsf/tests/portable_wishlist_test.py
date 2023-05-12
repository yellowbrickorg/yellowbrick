from django.test import TestCase, Client
from django.conf import settings
from django.urls import URLPattern, URLResolver

from ..urls import urlpatterns

URLCONF = __import__(settings.ROOT_URLCONF, {}, {}, [""])


def list_urls(patterns, path=None):
    """recursive"""
    if not path:
        path = []
    result = []
    for pattern in patterns:
        if isinstance(pattern, URLPattern):
            result.append("".join(path) + str(pattern.pattern))
        elif isinstance(pattern, URLResolver):
            result += list_urls(pattern.url_patterns, path + [str(pattern.pattern)])
    return result


class PortableWishlistTest(TestCase):
    def test_wishlist_should_be_accessible_from_every_page(self):
        urls = list_urls(urlpatterns)

        c = Client()
        response = c.post(
            "/auth/signup/",
            {
                "username": "janusz",
                "email": "janusz@mimuw.edu.pl",
                "password1": "kimloan1",
                "password2": "kimloan1",
            },
        )

        self.assertEqual(response.status_code, 302)

        for url in urls:
            if "auth" not in url:
                response = c.get(f"/{url}")

                if response.status_code is 200:
                    print(f"Checking {url}")
                    self.assertIn("user_sets_wishlist", response.context)
                    self.assertIn("user_bricks_wishlist", response.context)
                    self.assertIn("user_sets_offers", response.context)
                    self.assertIn("user_bricks_offers", response.context)
