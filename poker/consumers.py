from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Players, Room
from accounts.models import CustomUser
from tables.models import Table
import json
#from .poker import main

class PokerConsumer(WebsocketConsumer):
    def connect(self):
        self.pk = self.scope['url_route']['kwargs']['pk']
        self.pk = str(self.pk)
        self.player = self.scope['user']
        self.username = self.player.username
        p = self.scope['user']
        print('p ID', p.id)
        print('player:', self.username)
        print('player.id', self.player.id)
        self.tableGroup = 'table_' + self.pk

        async_to_sync(self.channel_layer.group_add)(
            self.tableGroup,
            self.channel_name
        )
        
        async_to_sync(self.channel_layer.group_add)(
            str(self.username),
            self.channel_name
        )
        self.accept()

    def disconnect(self, closeCode):
        async_to_sync(self.channel_layer.group_discard)(
            self.tableGroup,
            self.channel_name
        )
        async_to_sync(self.channel_layer.group_discard)(
            str(self.username),
            self.channel_name
        )
        pokerInstance = Room.objects.get(groupName=self.tableGroup)
        pokerInstance.noOfPlayers -= 1
        pokerInstance.save()

        playerInstance = Players.objects.get(user_id=self.player.id) #need the second 1 so money updates
        self.player.money += playerInstance.moneyInTable
        self.player.save()
        playerInstance.delete()
        players = Players.objects.filter(poker_id=self.tableGroup).values()
        print('players in consumers', players)


        if len(players) == 0:
            pokerInstance.delete()

    def receive(self, text_data):
        player = Players.objects.get(user=self.player)
        textDataJson = json.loads(text_data)
        action = textDataJson['action']
        if action == 'message':
            message = textDataJson['message']
            if message != '':
                message = self.username + ': ' + message
                async_to_sync(self.channel_layer.group_send)(
                self.tableGroup,
                {
                    'type': 'chatMessage',
                    'text': message
                }
                )

        elif player.turn:
            player.turn = False
            textDataJson = json.loads(text_data)
            message = textDataJson['action']
            game =  Room.objects.get(groupName=self.tableGroup)

            if message == 'fold':
                action = 'f'

            elif message == 'raise':
                raiseAmount = textDataJson['raiseAmount']
                action = 'r' + raiseAmount

            elif message == 'call':
                action = 'c'

            game.action = action
            game.save()
            player.save()

    def pokerMessage(self, event):
        message = event['message']
        pot = event['pot']

        self.send(text_data=json.dumps({
            'message': message,
            'pot': pot,
        }))


    def playerTurn(self, event):
        message = 'It\'s your turn'
        putIn = event['putIn']
        #moneyInTable = event['moneyInTable']
        self.send(text_data=json.dumps({
            'message': message,
            'putIn': putIn
        }))

    def cards(self, event):
        message = 'cards'
        hand = event['hand']
        comCards = event['comCards']
        dealer = event['dealer']
        moneyInTable = event['moneyInTable']
        self.send(text_data=json.dumps({
            'message': message,
            'hand': hand,
            'comCards': comCards,
            'dealer': dealer,
            'moneyInTable': moneyInTable
        }))

    def showWinner(self, event):
        message = 'winner'
        winner = event['winner']
        showdown = event['showdown']
        log = winner + ' wins'
        self.send(text_data=json.dumps({
            'message': message,
            'showdown': showdown,
            'log': log
        }))

    def chatMessage(self, event):
        text = event['text']
        self.send(text_data=json.dumps({
            'message': 'message',
            'text': text
        }))