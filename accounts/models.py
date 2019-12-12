from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class CustomUser(AbstractUser):
    alphanumeric = RegexValidator(r'^[0-9a-zA-Z_]*$', 'Only alphanumeric characters and _ allowed.')
    
    username = model.CharField(max_length=25, validators=[alphanumeric])
    money = models.PositiveSmallIntegerField(default=1000)

    def __str__(self):
        return self.username
