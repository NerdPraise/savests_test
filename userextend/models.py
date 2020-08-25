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


class UserMetrics(models.Model):
    pass
