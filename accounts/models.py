from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    money = models.PositiveSmallIntegerField(default=1000)

    #def __str__(self):
        #return self.username