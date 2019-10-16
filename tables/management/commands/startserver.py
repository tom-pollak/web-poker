from django.core.management.base import BaseCommand, CommandError
import threading
from django.core.management import call_command
from tables.models import Table
from datetime import datetime, timezone
import time
import os

class Command(BaseCommand):
    help = 'Calls runserver and cleartables, creates and a daemon thread that removes tables that have been inactive \
        for more than 5 minutes'

    def add_arguments(self, parser):
        parser.add_argument('addrport', nargs='?', type=str, default='127.0.0.1:8000', help='ipaddr:port')

    def handle(self, *args, **kwargs):
        #os.system('docker run -p 6379:6379 -d redis:2.8')
        call_command('cleartables')
        addrport = kwargs['addrport']
        thread = threading.Thread(target=self.removeTables, daemon=True)
        thread.start()
        call_command('runserver', addrport)

    def removeTables(self):
        while True:
            tables = Table.objects.all()
            for table in tables:
                timeDiff = datetime.now(timezone.utc) - table.lastUsed
                timeDiff = timeDiff.total_seconds()/60
                if timeDiff > 15 and table.getNoOfPlayers() == 0:
                    print('deleting %s, not used for: %d minutes' % (table.name, timeDiff))
                    table.delete()
            time.sleep(1)
