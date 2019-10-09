from django.core.management.base import BaseCommand, CommandError
from poker.models import Players, Room

class Command(BaseCommand):
    help = 'Clears Room and Players from DB'

    def handle(self, *args, **kwargs):
        Players.objects.all().delete()
        Room.objects.all().delete()
        print('Tables cleared')