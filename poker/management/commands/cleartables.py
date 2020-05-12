from django.core.management.base import BaseCommand, CommandError
from poker.models import Players, Room
import time
from datetime import datetime, timezone

class Command(BaseCommand):
    help = 'Clears Room and Players from DB'

    def handle(self, *args, **kwargs):
        Players.objects.all().delete()
        Room.objects.all().delete()
        print('Tables cleared')

        while True:
            tables = Table.objects.all()
            for table in tables:
                timeDiff = datetime.now(timezone.utc) - table.lastUsed
                timeDiff = timeDiff.total_seconds()/60
                if timeDiff > 15 and table.getNoOfPlayers() == 0:
                    print('deleting %s, not used for: %d minutes' % (table.name, timeDiff))
                    table.delete()
            time.sleep(10)
