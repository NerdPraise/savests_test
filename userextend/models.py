# Django imports
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    To allow for possible future user configuration
    """
    pass


class UserMetrics(models.Model):
    pass
