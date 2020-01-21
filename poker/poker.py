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
    def hand(self):
        return self.__hand

    @hand.setter
    def hand(self, hand):
        self.__hand = hand

    @property
    def playerIn(self):
        return self.__playerIn
    
    @property
    def handStrength(self):
        return self.__handStrength
    
    @handStrength.setter
    def handStrength(self, strength):
        self.__handStrength = strength
    
    @property
    def moneyWon(self):
        return self.__moneyWon

    @property
    def callAmount(self):
        return self.__callAmount

    @callAmount.setter
    def callAmount(self, callAmount):
        if callAmount >= 0:
            self.__callAmount = callAmount
        else:
            raise Exception('call amount less than 0')

    @property
    def putIn(self):
        return self.__putIn

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

    #converts cards into human readable form
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
        self.split = []
        self.handStrength()
        self.winQueue()
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
            countList.append([count, temp]) #test this

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
                    self.orderHand = [hand[a][:]] 
                    hand[a] = ''



        #only use the strongest three of a kind
        threeIndex = threeIndex[:3]
        for three in threeIndex:
            self.orderHand.append(three)

        pairIndex.sort(reverse=True)
        pairIndex = pairIndex[:2]
        for item in pairIndex:
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
            self.orderHand.append(item)
        self.orderHand = self.orderHand[:5]

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
                #looking for straights
                if self.hand[b][0]+1 == self.hand[b+1][0]:
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

    #binary sort but adds the players to repeated array if values are the same
    def clash(self):
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

    def sorting(self, hand1, hand2):
        a = 0
        #finds the first card where the values differ
        while hand1[a][0] == hand2[a][0] and a < 4:
            a+=1

        if hand1[a][0] > hand2[a][0]:
            return False

        elif hand1[a][0] < hand2[a][0]:
            return True

        else:
            return 'split'

    #adds players with the the same hand to split in an array
    def splitWork(self, repeated):
        for a in range(0, len(repeated), 2):
            if a - 1 >= 0:
                if repeated[a] == repeated[a-1]:
                    self.split[-1].append(repeated[a+1])
                else:
                    self.split.append([repeated[a], repeated[a+1]])
    
    #adds each player to playerWin in an array
    def winQueue(self):
        for strength, player, hand in self.win:
            added = False
            for players in self.split:
                if player in players:
                    #if players in split it adds the split array instead
                    self.playerWin.append(players)
                    added = True
                    #deletes the added split array otherwise it would cause duplicates
                    del self.split[players][:]

            if not added:
                self.playerWin.append([player])
        print('playerWin:', self.playerWin)

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
            self.game = Room.objects.get(table=self.table)
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
            #everyone leaves while its your turn
            if self.game.noOfPlayers == 1:
                self.game.action = 'c'
                self.game.save()
                self.choice = 'c'

            elif self.game.action is not None:
                #the first character is the action the user wants to take
                #after that it is the optional raiseAmount
                self.choice = self.game.action[0]
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
        #iterates through each player from dealers left as they show first
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
        sortedPlayers = sorted(players, key = lambda x: x.putIn)
        winners.sort(key = lambda x: x.putIn)
        if len(winners) != 0:
            #money given out equal to the minimum players putIn
            money = sortedPlayers[0].putIn
            moneyMade = money * len(sortedPlayers)
            
            #if the money cannot be shared equally
            oddMoney = moneyMade % len(winners)
            if oddMoney != 0:
                print('odd money in pot:', str(oddMoney))
                #share the money between the all the winners except the last
                a = -1
                while players[a] not in winners:
                    a-=1
                newWinners = winners[winners.index(players[a])][:]
                pot = self.distributeMoney(players, newWinners, oddMoney)

            #decrease each players putIn by the min players putIn
            #increase each winners by the (min players putIn * players)// no winners
            moneyWon = moneyMade // len(winners)
            for player in sortedPlayers:
                if player.putIn != 0: #not sure if line needed
                    player.decreasePutIn(money)
                    if player in winners:
                        player.increaseMoney(moneyWon)

            #decrease pot by money given out
            pot -= moneyMade
            #delete minimum putIn player
            del players[players.index(sortedPlayers[0])]
            if winners[0] == sortedPlayers[0]:
                del winners[0]

            pot = self.distributeMoney(players, winners, pot)
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
            self.updateDBMoney()
            a+=1
        self.makeWinnerMessage()
        self.sendMessage(self.message, self.tableGroup)

    def play(self):
        self.nextTurn()
        for a in range(4):
            #one to the dealers left
            self.better = (self.dealer+1)%self.noOfPlayers
            firstRun = True
            if a == 0:
                self.blinds()
            self.makeComCards()
            if self.checkMultiplePlayersIn()[0]:
                while (self.turnIndex != self.better or firstRun):
                    self.updateDBMoney()
                    self.sendCards()
                    firstRun = False
                    if self.turn.money != 0 and self.turn.playerIn:
                        self.makeTurn()
                        self.makeChoice()
                    self.nextTurn()
        self.winner()

def addPlayer(room, table, username):
    player = CustomUser.objects.get(username=username)
    playerInstance = Players.objects.create(user=player, poker=room, moneyInTable=table.buyIn)
    player.money -= table.buyIn
    player.save()

    room.noOfPlayers += 1
    room.save()

def startGame(table, tableGroup):
    dealer = 0
    while True:
        #waits until their is more than one player in the table to start
        table.refresh_from_db()
        while table.getNoOfPlayers() <= 1:
            table.refresh_from_db()
            time.sleep(0.2)
        
        #if single player leaves table before anyone joins
        if table.getNoOfPlayers() < 1:
            print('everyone left (startGame)')
            table.lastUsed = datetime.now(timezone.utc)
            table.save()
            sys.exit()    

        #gets players in table
        playersInGame = []
        players = Players.objects.filter(poker_id=tableGroup) #table group is the primary key of Room
        #creates an array of Player objects
        for item in players:
            if item.moneyInTable > 0:
                playersInGame.append(Player(item.user.username, item.moneyInTable))
        #starts game
        Game((table.buyIn)//100, dealer, tableGroup, table, playersInGame)
        dealer +=1
        time.sleep(1)

def main(pk, username):
    table = Table.objects.get(pk=pk)
    tableGroup = 'table_' + str(pk)
    #check to see if table exists
    try:
        room = Room.objects.get(table=table)
        addPlayer(room, table, username)

    #if the room dosen't exist create one
    except Room.DoesNotExist:
        room = Room.objects.create(table=table, groupName=tableGroup)
        addPlayer(room, table, username)
        startGame(table, tableGroup)