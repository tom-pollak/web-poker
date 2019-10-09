from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

class Table(models.Model):
    def getNoOfPlayers(self):
        try:
            noOfPlayers = self.room.noOfPlayers
        except:
            noOfPlayers = 0
        return noOfPlayers
        
    name = models.CharField(max_length=24, unique=True)
    buyIn = models.IntegerField(validators=[MinValueValidator(100), MaxValueValidator(100000000)])
    maxNoOfPlayers = models.IntegerField(validators=[MinValueValidator(2), MaxValueValidator(8)])
    createdAt = models.DateTimeField(auto_now_add=True)
    lastUsed = models.DateTimeField(auto_now_add=True)