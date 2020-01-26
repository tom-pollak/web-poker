from django.db import models

class Players(models.Model):
    user = models.OneToOneField('accounts.CustomUser', max_length=24, primary_key=True, on_delete=models.CASCADE)
    room = models.ForeignKey('Room', on_delete=models.CASCADE, null=True)
    moneyInTable = models.PositiveSmallIntegerField()
    turn = models.BooleanField(default=False)

class Room(models.Model):
    table = models.OneToOneField('tables.Table', primary_key=True, on_delete=models.CASCADE, related_name='room')
    action = models.CharField(max_length=15, default=None, null=True)
    pot = models.PositiveSmallIntegerField(default=0)
