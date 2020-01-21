from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class CustomUser(AbstractUser):
    alphanumeric = RegexValidator(
        regex=r'^[0-9a-zA-Z_]*$',
        message='Username must consist only of alphanumeric characters and underscores.'
    )
    
    username = models.CharField(max_length=25, validators=[alphanumeric], unique=True)
    money = models.PositiveSmallIntegerField(default=1000)

    def __str__(self):
        return self.username
