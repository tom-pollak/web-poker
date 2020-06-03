from django.core.management.base import BaseCommand
import threading
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Calls runserver and cleartables, creates and a daemon thread that removes tables that have been \
        inactive for more than 15 minutes'

    def add_arguments(self, parser):
        parser.add_argument('addrport', nargs='?', type=str, default='127.0.0.1:8000', help='ipaddr:port')

    def handle(self, *args, **kwargs):
        #os.system('docker run --name channels_app -p 6379:6379 -d redis:2.8')
        call_command('cleartables')
        addrport = kwargs['addrport']
        thread = threading.Thread(target=self.removeTables, daemon=True)
        thread.start()
        call_command('runserver', '--noreload', addrport)
