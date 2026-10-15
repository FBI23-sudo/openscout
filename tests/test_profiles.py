import unittest
from unittest.mock import Mock

import requests

from openscout.profiles import DEFAULT_PLATFORMS, check_profile, validate_username


class UsernameValidationTests(unittest.TestCase):
    def test_valid_username(self):
        self.assertEqual(validate_username("sample_user-1"), "sample_user-1")

    def test_rejects_url_injection(self):
        with self.assertRaises(ValueError):
            validate_username("name/../../example.com")

    def test_rejects_empty_username(self):
        with self.assertRaises(ValueError):
            validate_username(" ")


class ProfileCheckTests(unittest.TestCase):
    def setUp(self):
        self.session = Mock(spec=requests.Session)

    def test_http_200_is_not_claimed_as_confirmed_profile(self):
        response = Mock()
        response.status_code = 200
        response.url = "https://github.com/example"
        self.session.get.return_value = response

        result = check_profile("example", "github", self.session)

        self.assertEqual(result["status"], "http_200_review_needed")
        self.assertEqual(result["http_status"], 200)
        response.close.assert_called_once()

    def test_404_classification(self):
        response = Mock()
        response.status_code = 404
        response.url = "https://github.com/no_such_user"
        self.session.get.return_value = response

        result = check_profile("no_such_user", "github", self.session)

        self.assertEqual(result["status"], "http_404_not_found")

    def test_unknown_platform_rejected(self):
        with self.assertRaises(ValueError):
            check_profile("example", "not-allowed", self.session)


if __name__ == "__main__":
    unittest.main()
