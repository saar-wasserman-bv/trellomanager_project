from django.contrib.auth.models import AbstractUser
from django.db import models


class TrelloUser(AbstractUser):
    """ A user that is able to set and get notifications of trello cards status """

    def __str__(self):
        return '{id}: {email}'.format(id=self.pk, email=self.email)
