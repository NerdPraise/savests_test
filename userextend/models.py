# Future modules

# Standard Library

# Third party libraries

# Django imports
from django.db import models
from django.contrib.auth.models import AbstractUser

# Local imports


class User(AbstractUser):
    """
    To allow for possible future user configuration
    """
    pass


class Email(models.Model):
    """"
    To ensure safekeeping of mails sent, can be ignored
    """
    subject = models.CharField(max_length=30)
    body = models.TextField()

    def __str__(self):
        return self.subject
