from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Players, Room
from accounts.models import CustomUser
from tables.models import Table
import json
from channels.db import database_sync_to_async


class PokerConsumer(AsyncWebsocketConsumer):
    # adds the player to the poker group to recieve the community cards and bets
    # adds the player to a unique group to recieve his cards
    async def connect(self):
        self.pk = self.scope['url_route']['kwargs']['pk']
        self.player = self.scope['user']
        self.username = self.player.username
        print('player:', self.username)
        self.tableGroup = 'table_' + self.pk
        self.room = await self.get_room()
        #self.censoredList = getCensoredWords()
        # group socket
        await self.channel_layer.group_add(
            self.tableGroup,
            self.channel_name
        )

        # unique socket
        await self.channel_layer.group_add(
            str(self.username),
            self.channel_name
        )
        # accepts all communication with web socket
        await self.accept()

    async def disconnect(self, closeCode):
        # disconnects from group sockets
        await self.channel_layer.group_discard(
            self.tableGroup,
            self.channel_name
        )
        await self.channel_layer.group_discard(
            str(self.username),
            self.channel_name
        )
        # update player money
        playerInstance = await self.get_player()
        self.player.money += playerInstance.moneyInTable
        self.player.save()
        playerInstance.delete()

        # if noone left in table delete table
        self.room.refresh_from_db()
        players = await self.get_players_in_room()
        if len(players) == 0:
            self.room.delete()

    async def receive(self, text_data):
        print('recived message')
        player = self.get_players_in_room()
        textDataJson = json.loads(text_data)
        action = textDataJson['action']
        if action == 'message':
            message = textDataJson['message']
            if message != '':
                message = self.username + ': ' + message
                # message = censor(message, self.censoredList)

                print('sending message')
                print('message:', message)
                await self.channel_layer.group_send(
                    self.tableGroup,
                    {
                        'type': 'chatMessage',
                        'text': message
                    })

        elif player.turn:
            player.turn = False
            textDataJson = json.loads(text_data)
            message = textDataJson['action']

            if message == 'fold':
                action = 'f'

            elif message == 'raise':
                raiseAmount = textDataJson['raiseAmount']
                action = 'r' + raiseAmount

            elif message == 'call':
                action = 'c'

            self.room.action = action
            self.room.save()
            player.save()

    async def pokerMessage(self, event):
        message = event['message']
        pot = event['pot']

        await self.send(text_data=json.dumps({
            'message': message,
            'pot': pot,
        }))

    async def playerTurn(self, event):
        message = 'It\'s your turn'
        putIn = event['putIn']
        await self.send(text_data=json.dumps({
            'message': message,
            'putIn': putIn
        }))

    async def cards(self, event):
        message = 'cards'
        hand = event['hand']
        comCards = event['comCards']
        dealer = event['dealer']
        moneyInTable = event['moneyInTable']
        await self.send(text_data=json.dumps({
            'message': message,
            'hand': hand,
            'comCards': comCards,
            'dealer': dealer,
            'moneyInTable': moneyInTable
        }))

    async def showWinner(self, event):
        message = 'winner'
        winner = event['winner']
        showdown = event['showdown']
        log = winner + ' wins'
        await self.send(text_data=json.dumps({
            'message': message,
            'showdown': showdown,
            'log': log
        }))

    async def chatMessage(self, event):
        text = event['text']
        print('sending message...')
        await self.send(text_data=json.dumps({
            'message': 'message',
            'text': text
        }))
        print('sent')

    @database_sync_to_async
    def get_room(self):
        return Room.objects.get(table_id=self.pk)

    @database_sync_to_async
    def get_player(self):
        Players.objects.get(user=self.player)
    
    @database_sync_to_async
    def get_players_in_room(self):
        Players.objects.filter(room=self.room)

def getCensoredWords():
    censoredList = []
    path = '../censored-words.txt'
    with open(path, 'r') as censoredWords:
        for word in censoredWords:
            w = word.replace('\n', '')
            censoredList.append(w)
    return censoredList


def censor(message, censoredList):
    words = message.split(' ')
    for word in words:
        if word in censoredList:
            message = message.replace(word, '*' * len(word))
    return message
