import random
from .models import Players, Room
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from tables.models import Table
import time
from accounts.models import CustomUser
import sys
from datetime import datetime, timezone

#TODO
#somebody posted bb and sb?? unreproducable
#re buy in

class Player:
    def __init__(self, username, money):
        self.__username = username
        self.__money = money
        self.__hand = []
        self.__playerIn = True
        self.__callAmount = self.__putIn = 0
        self.__handStrength = ''
        self.__moneyWon = 0

    @property
    def username(self):
        return self.__username
    
    @property
    def money(self):
        return self.__money
    
    def increaseMoney(self, increaseAmount):
        self.__money += increaseAmount
        self.__moneyWon += increaseAmount
    
    @property
    def callAmount(self):
        return self.__callAmount

    @callAmount.setter
    def callAmount(self, callAmount):
        self.__callAmount = callAmount

    @property
    def hand(self):
        return self.__hand

    @hand.setter
    def hand(self, hand):
        self.__hand = hand

    @property
    def playerIn(self):
        return self.__playerIn

    @property
    def putIn(self):
        return self.__putIn
    
    @property
    def handStrength(self):
        return self.__handStrength
    
    @handStrength.setter
    def handStrength(self, strength):
        self.__handStrength = strength
    
    @property
    def moneyWon(self):
        return self.__moneyWon

    def decreasePutIn(self, amount):
        if amount <= self.__putIn:
            self.__putIn -= amount
        else:
            raise Exception('amount to decrease putIn by was greater than putIn.')

    def fold(self):
        self.__playerIn = False

    def call(self, moneyToPutIn):
        if self.__money > moneyToPutIn:
            self.__money -= moneyToPutIn

        else: #all-in situation
            moneyToPutIn = self.__money
            self.__money = 0

        if moneyToPutIn == 0:
            print('no money put in')

        self.__putIn += moneyToPutIn
        self.__callAmount = 0
        return moneyToPutIn

class Cards:
    def __init__(self, players):
        self.__players = players
        self.__noOfPlayers = len(self.__players)
        self.__playerHands = []
        self.__deck = []
        self.__comCards = []
        self.makeDeck()
        self.hands()

    def makeDeck(self):
        self.__deck = [[k, j] for j in range(4) for k in range(2,15)]

    def hands(self):
        random.shuffle(self.__deck)
        self.__comCards = self.__deck[:5][:]
        del self.__deck[:5]
        for player in self.__players:
            playerHand = []
            playerHand = self.__deck[:2][:]
            del self.__deck[:2]
            player.hand = playerHand

    @property
    def comCards(self):
        return self.__comCards

    def convert(hand):
        numbers = [[11, 'J'], [12, 'Q'], [13, 'K'], [14, 'A'], [1, 'A']]
        suits = ['♥', '♦', '♠', '♣']
        convertHand = ''

        for a in range(len(hand)):
            add = False
            for item in numbers:
                if hand[a][0] == item[0]:
                    convertHand += item[1]
                    add = True

            if not add:
                convertHand += str(hand[a][0])

            for b in range(4):
                if hand[a][1] == b:
                    convertHand += (suits[b] + ' ')
        return convertHand


class Poker:
    def __init__(self, players, C):
        self.players = players
        self.C = C
        self.strengthList = ['High Card', 'Pair', 'Two Pair',\
        'Three of a kind', 'Straight', 'Flush', 'Full House', 'Four of a kind',\
        'Straight Flush', 'Royal Flush']
        self.win = []
        self.__playerWin = []
        self.split = [] #stores name strength of every hand of same value of another hand in 1d list
        self.splitted = [] #stores name of easch user with the same hand in a 2d list (useful 1)
        self.handStrength()
        self.winStack()
    @property
    def playerWin(self):
        return self.__playerWin
    
    @playerWin.setter
    def playerWin(self, playerWin):
        self.__playerWin = playerWin

    def handStrength(self):
        for player in self.players:
            self.orderHand = []
            self.hand = player.hand + self.C.comCards
            self.hand.sort(reverse=True)
            self.pairThree()
            self.straightFlush()
            player.handStrength = self.strengthList[self.strength]
            self.win.append([self.strength, player, self.orderHand[:]])
        self.win.sort(key = lambda x: x[0], reverse=True)
        self.clash()

    def pairThree(self):
        countList = []
        hand = self.hand[:]
        pair = 0
        three = False
        pairIndex = []
        threeIndex = []
        self.strength = 0

        for a in range(7):
            count = 0
            temp = []
            for b in range(7):
                if hand[a][0] == hand[b][0]:
                    count+=1
                    temp.append(hand[a][0])
            countList.append([count, temp])

        for a in range(7):
            if countList[a][0] == 2:
                pair+=1
                pairIndex.append([countList[a][1][0], a])

            elif countList[a][0] == 3:
                three = True
                if self.strength <= 3:
                    self.strength = 3
                    threeIndex.append(hand[a][:])
                    #self.orderHand = [hand[a][:]] + self.orderHand
                    hand[a] = ''

            elif countList[a][0] == 4:
                if self.strength <= 7:
                    self.strength = 7
                    self.orderHand = [hand[a][:]] + self.orderHand
                    hand[a] = ''

        for three in threeIndex:
            self.orderHand.append(three)

        pairIndex.sort(reverse=True)
        for item in pairIndex: #dosent stop at 2 pairs??
            self.orderHand.append(hand[item[1]][:])
            hand[item[1]] = ''

        if pair == 2:
            if three:
                if self.strength < 6:
                    self.strength = 6
            else:
                if self.strength <= 1:
                    self.strength = 1

        elif pair == 4:
            if self.strength < 2:
                self.strength = 2

        while '' in hand:
            hand.remove('')

        for item in hand:
            if len(self.orderHand) < 5:
                self.orderHand.append(item)

    def straightFlush(self):
        count = 0
        for a in range(4):
            count = 0
            for item in self.hand:
                if item[1] == a:
                    count+=1

            if count >= 5 and self.strength < 5:
                self.orderHand = []
                self.strength = 5
                for item in self.hand:
                    if item[1] == a:
                        self.orderHand.append(item[:])
        count = 0

        for item in self.hand:
            if 14 in item:
                self.hand.append([1, item[1]])

        for b in range(len(self.hand)):
            if len(self.hand) > b+1:
                if self.hand[b][0]+1 == self.hand[b+1][0]: #looking for straights
                    count+=1
                else:
                    count = 0

                if count == 4:
                    if self.strength <= 4:
                        self.strength = 4
                        self.orderHand = self.hand[b-4:b+1][:]

                    for c in range(4):
                        count2 = 0
                        for item in self.hand[b-4:b+1]:
                            if item[1] == a:
                                count2+=1

                        if count2 >= 5:
                            self.strength = 8
                            self.orderHand = self.hand[b-4:b+1][:]

        if self.strength == 8 and self.orderHand[0][0] == 14:
            self.strength = 9

    def clash(self): #binary sort with abit of splitting if the values are the same
        repeated = []
        flip = True
        while flip:
            flip = False
            for a in range(len(self.win)):
                if len(self.win) > a+1:
                    if self.win[a][0] == self.win[a+1][0]:
                        flip = self.sorting(self.win[a][2], self.win[a+1][2])

                        if flip == 'split':
                            flip = True
                            repeated.append(self.win[a][1])
                            repeated.append(self.win[a+1][1])

                        elif flip:
                            temp = self.win[a]
                            self.win[a] = self.win[a+1][:]
                            self.win[a+1] = temp[:]
        self.splitWork(repeated)

    def splitWork(self, repeated):
        for a in range(0, len(repeated), 2):
            if a - 1 >= 0:
                if repeated[a] == repeated[a-1]:
                    self.split[-1].append(repeated[a+1])
                else:
                    self.split.append([repeated[a], repeated[a+1]])

    def winStack(self):
        for s, player, h in self.win:
            added = False
            for players in self.split:
                if player in players:
                    self.playerWin.append(players)
                    added = True
                    del players[:]

            if not added:
                self.playerWin.append([player])
        print('playerWin:', self.playerWin)

    def sorting(self, hand1, hand2):
        a = 0
        while hand1[a][0] == hand2[a][0] and a < 4:
            a+=1

        if hand1[a][0] > hand2[a][0]:
            return False

        elif hand1[a][0] < hand2[a][0]:
            return True

        else:
            return 'split'

class Game:
    def __init__(self, minimumBet, dealer, tableGroup, table, playersInGame):
        self.minimumBet = minimumBet
        self.dealer = dealer
        self.tableGroup = tableGroup
        self.table = table
        self.players = playersInGame
        self.winners = []
        self.turnIndex = self.dealer
        self.better = self.dealer
        self.noOfPlayers = len(self.players)
        self.comCount = 0
        self.pot = 0
        self.instantiateCardsPoker()
        self.play()
    
    def instantiateCardsPoker(self):
        self.C = Cards(self.players)
        self.P = Poker(self.players, self.C)

    def makeComCards(self):
        if self.comCount == 0:
            self.comCards = ''
            message = ''

        if self.comCount == 1:
            self.comCards = Cards.convert(self.C.comCards[:3])
            message = 'Flop: '

        elif self.comCount == 2:
            self.comCards = Cards.convert(self.C.comCards[:4])
            message = 'Turn: '

        elif self.comCount == 3:
            self.comCards = Cards.convert(self.C.comCards[:])
            message = 'River: '
        
        message += self.comCards
        if message != '':
            self.sendMessage(message, self.tableGroup)
        self.comCount+=1

    def nextTurn(self):
        self.turnIndex = (self.turnIndex+1)%self.noOfPlayers
        self.turn = self.players[self.turnIndex]

    def getPlayer(self, player):
        try:
            userInstance = CustomUser.objects.get(username=player.username)
            player = Players.objects.get(user_id=userInstance.id)
        except Players.DoesNotExist:
            self.getRoom()
            return (False, '')
        return (True, player)

    def getRoom(self):
        try:
            self.game = Room.objects.get(groupName=self.tableGroup)
        except Room.DoesNotExist:
            print('everyone left')
            self.table.lastUsed = datetime.now(timezone.utc)
            self.table.save()
            sys.exit()

    def blinds(self):
        sb = self.addRaiseAmount(self.minimumBet)
        self.nextTurn()
        bb = self.addRaiseAmount(self.minimumBet)
        self.nextTurn()
        message = self.turn.username + ' posted BB (' + str(bb + sb) + ')\n'
        message += self.turn.username + ' posted SB (' + str(sb) + ')'
        self.sendMessage(message, self.tableGroup)
        
    def sendCards(self):
        for player in self.players:
            if player.playerIn:
                hand = Cards.convert(player.hand)
                print('for simons shitty username***', player.username + '***end of username')
                async_to_sync(get_channel_layer().group_send)(
                    player.username,
                    {
                        'type': 'cards',
                        'hand': hand,
                        'comCards': self.comCards,
                        'dealer': self.dealer,
                        'moneyInTable': str(player.money)

                    }
                )

    def getChoice(self):
        putIn = str(self.turn.callAmount)
        async_to_sync(get_channel_layer().group_send)(
            self.turn.username,
            {
                'type': 'playerTurn',
                'putIn': putIn,
            }
        )

        playerLeft = False
        self.getRoom()
        while self.game.action is None and not playerLeft:
            self.getRoom()
            if self.game.noOfPlayers == 1: #everyone leaves while its your turn
                self.game.action = 'c'
                self.game.save()
                self.choice = 'c'

            elif self.game.action is not None:
                self.choice = self.game.action[0] #the first character is the action the user wants to take after that it is the optional raiseAmount
                if self.choice == 'r':
                    try:
                        self.raiseAmount = self.game.action[1:]
                        if not int(self.raiseAmount) > 0:
                            raise ValueError()
                    except ValueError:
                        self.sendMessage('Raise amount must be a positive integer', self.turn.username)
                        self.makeTurn()

            if not self.getPlayer(self.turn)[0]:
                self.choice = 'f'
                playerLeft = True
                print(self.turn.username, 'left')

        self.game.action = None
        self.game.save()

    def makeTurn(self):
        playerExists, player = self.getPlayer(self.turn)
        if playerExists:
            player.turn = True
            player.save()
            self.getChoice()

        else:
            self.choice = 'f'

    def makeChoice(self):
        money = 0
        if self.choice == 'c':
            money = self.turn.call(self.turn.callAmount)
            self.pot += money

        elif self.choice == 'r':
            money = self.addRaiseAmount(int(self.raiseAmount))

        elif self.choice == 'f':
            self.turn.fold()

        self.makeMessage(money)

    def addRaiseAmount(self, raiseAmount):
        self.better = self.turnIndex
        callAmount = self.turn.call(self.turn.callAmount)
        raiseAmount = self.turn.call(raiseAmount)
        self.pot += (raiseAmount + callAmount)

        for player in self.players:
            if self.turn != player:
                player.callAmount += raiseAmount
        return raiseAmount

    def updateDBMoney(self):
        for user in self.players:
            playerExists, player = self.getPlayer(user)
            if playerExists:
                print(user.username, str(user.money))
                player.moneyInTable = user.money
                player.save()

    def makeMessage(self, money):
        if self.choice == 'f':
            message = self.turn.username + ' folded'

        elif self.choice == 'r':
            if self.turn.money == 0:
                message = self.turn.username + ' went all-in'
            else:
                message = self.turn.username + ' raised ' +  str(money)

        if self.choice == 'c':
            if money == 0:
                message = self.turn.username + ' checked'
            else:
                message = self.turn.username + ' called ' + str(money)

        self.sendMessage(message, self.tableGroup)
    
    def sendMessage(self, message, group):
        async_to_sync(get_channel_layer().group_send)(
            group,
            {
                'type': 'pokerMessage',
                'message': message,
                'pot': str(self.pot),
            }
        )

    def checkMultiplePlayersIn(self):
        count = 0
        for player in self.players:
            if player.playerIn and player.money > 0:
                count+=1
        if count > 1:
            if self.table.getNoOfPlayers() > 1:
                return (True, count)
        return (False, count)

    def makeWinnerMessage(self):
        self.message = '\n------------------------------------------'
        showHands = []
        startIndex = currentIndex = (self.dealer+1)%self.noOfPlayers
        winningIndex = 999
        firstRun = True
        while currentIndex != startIndex or firstRun:
            firstRun = False
            for a in range(len(self.P.playerWin)):
                if self.players[currentIndex] in self.P.playerWin[a]:
                    currentWin = a
            if self.players[currentIndex].playerIn and currentWin <= winningIndex:
                winningIndex = currentWin
                playerStats = {
                    'username': self.players[currentIndex].username,
                    'moneyWon': self.players[currentIndex].moneyWon
                }

                if self.checkMultiplePlayersIn()[1] > 1:
                    playerStats['hand'] = Cards.convert(self.players[currentIndex].hand)
                    playerStats ['strength'] = ': ' + self.players[currentIndex].handStrength + ' '
                else:
                    playerStats['hand'] = ''
                    playerStats ['strength'] =  ''

                showHands.append(playerStats)
            currentIndex = (currentIndex+1)%self.noOfPlayers

        for player in showHands:
            winnings = ''
            if player['moneyWon'] != 0:
                winnings = ' won ' + str(player['moneyWon'])

            self.message += '\n' + player['username'] + winnings + player['strength'] + player['hand']

        self.message += '\n------------------------------------------\n'

    def distributeMoney(self, players, winners, pot):
        players.sort(key = lambda x: x.putIn)
        winners.sort(key = lambda x: x.putIn)
        if len(winners) != 0:
            money = players[0].putIn
            moneyMade = money * len(players)
            if moneyMade % len(winners) != 0: #need to return odd
                oddMoney = moneyMade % len(winners)
                print('odd money in pot:', str(oddMoney))
                pot = self.distributeMoney(players, winners, oddMoney)

            moneyWon = moneyMade // len(winners)
            for player in players:
                print(player.username, str(player.money))
                if player.putIn != 0:
                    player.decreasePutIn(money)
                    if player in winners:
                        player.increaseMoney(moneyWon)
                print(player.username, str(player.money))
            pot -= moneyMade
            if winners[0] == players[0]:
                del winners[0]
            pot = self.distributeMoney(players[1:][:], winners, pot)
        return pot

    def winner(self):
        a = 0
        print('playerWin', self.P.playerWin)
        while self.pot != 0:
            for player in self.P.playerWin[a]:
                if player.playerIn:
                    self.winners.append(player)
            print('winners', self.winners)
            self.pot = self.distributeMoney(self.players[:], self.winners[:], self.pot)
            print(self.pot)
            print(self.winners)
            self.updateDBMoney()
            a+=1
        self.makeWinnerMessage()
        self.sendMessage(self.message, self.tableGroup)


    def play(self):
        self.nextTurn()
        for a in range(4):
            self.better = (self.dealer+1)%self.noOfPlayers
            firstRun = True
            if a == 0:
                self.blinds()
            self.makeComCards()
            if self.checkMultiplePlayersIn()[0]:
                print('turnIndex:', self.turnIndex, end="")
                print(' |  better:', self.better)
                while (self.turnIndex != self.better or firstRun):
                    self.updateDBMoney()
                    self.sendCards()
                    firstRun = False
                    if self.turn.money != 0 and self.turn.playerIn:
                        self.makeTurn()
                        self.makeChoice()
                    self.nextTurn()
        self.winner()

def addPlayer(pokerInstance, table, username):
    pokerInstance.noOfPlayers += 1
    pokerInstance.save()

    player = CustomUser.objects.get(username=username)
    playerInstance = Players.objects.create(user=player, poker=pokerInstance, moneyInTable=table.buyIn)
    player.money -= table.buyIn
    player.save()

def startGame(table, tableGroup):
    dealer = 0
    while True:
        table.refresh_from_db()
        players = ['a']
        while len(players) == 1:
            players = Players.objects.filter(poker_id=tableGroup)

        playersInGame = []
        for item in players:
            if item.moneyInTable > 0:
                playersInGame.append(Player(item.user.username, item.moneyInTable))
        print('playersInGame:', playersInGame)

        try:
            game = Room.objects.get(groupName=tableGroup)
        except:
            print('everyone left (startGame)')
            table.lastUsed = datetime.now(timezone.utc)
            table.save()
            sys.exit()

        if len(playersInGame) > 1:
            time.sleep(0.2)
            print('game started')
            Game((table.buyIn)//100, dealer, tableGroup, table, playersInGame)
            dealer +=1
        time.sleep(1)

def main(pk, username):
    table = Table.objects.get(pk=pk)
    tableGroup = 'table_' + str(pk)
    try:
        pokerInstance = Room.objects.get(groupName=tableGroup)
        addPlayer(pokerInstance, table, username)

    except Room.DoesNotExist:
        pokerInstance = Room.objects.create(table=table, groupName=tableGroup)  #if the room dosen't exist startGame
        addPlayer(pokerInstance, table, username)
        startGame(table, tableGroup)