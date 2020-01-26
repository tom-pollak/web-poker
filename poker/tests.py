from django.test import TestCase
from tables.models import Table

class PokerTestCase(TestCase):
    @classmethod
    def setup(cls):
        table = Table.objects.create(name='test_table', buyIn=100, maxNoOfPlayers=4)
        #num players
        for a in range(4):
            name = 'test_' + str(a)
            pokerThread = threading.Thread(target=tests, args=(table.pk, name), daemon=True)
            pokerThread.start()
