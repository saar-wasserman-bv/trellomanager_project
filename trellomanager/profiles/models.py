from django.db import models


class User(models.Model):
    """ a model to represent a user that will be involved in the trello manager tasks """

    ROLES = (
        ('TL', 'Team Leader'),
        ('PM', 'Product Manager'),
        ('DV', 'Developer')
    )

    # TODO: add email validator to allow only bluevine.com emails
    email = models.EmailField()
    username = models.CharField(max_length=50)
    role = models.CharField(max_length=2, choices=ROLES)

    def __str__(self):
        """ string representation of a profile object """

        return self.email
