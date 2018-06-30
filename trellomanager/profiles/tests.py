from django.test import TestCase

from django.core.validators import ValidationError

from .models import User


class ProfileModelTests(TestCase):

    def test_only_bluevine_email_allowed(self):
        """ validate that a profile can be created only with bluevine email """

        bluevine_email = 'abcefg@bluevine.com'
        foreign_email = 'bluevine_test18@gmail.com'

        # create foreign email profile
        with self.assertRaises(ValidationError):
            User(email=foreign_email)

        # create bluevine email profile
        User(email=bluevine_email)
