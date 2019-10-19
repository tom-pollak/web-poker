import random
from .models import Players, Room
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from tables.models import Table
import time
from accounts.models import CustomUser
import sys
from datetime import datetime, timezone

class Player:
    def __init__(self, username, money):
        self.username = username
        self.money = money
        self.hand = []
        self.playerIn = True
        self.putIn = 0
        self.callAmount = 0

    def get_username(self):
        return self.username
    
    def get_money(self):
        return self.money
    
    def increaseMoney(self, increaseAmount):
        self.money += increaseAmount
    
    def get_callAmount(self):
        return self.callAmount

    def make_hand(self, hand):
        self.hand = hand
    
    def get_hand(self):
        return self.hand

    def get_playerIn(self):
        return self.playerIn
    
    def fold(self):
        self.playerIn = False

    def get_putIn(self):
        return self.putIn

    def call(self, moneyToPutIn):
        if self.money > moneyToPutIn:
            self.money -= moneyToPutIn

        else: #all-in situation
            moneyToPutIn = self.money
            self.money = 0

        if moneyToPutIn == 0:
            print('no money put in')

        self.putIn += moneyToPutIn
        self.callAmount = 0
        return moneyToPutIn

class Cards:
    def __init__(self, players):
        self.players = players
        self.noOfPlayers = len(self.players)
        self.playerHands = []
        self.deck = []
        self.comCards = []
        self.makeDeck()
        self.hands()

    def makeDeck(self):
        self.deck = [[k, j] for j in range(4) for k in range(2,15)]

    def hands(self):
        random.shuffle(self.deck)
        self.comCards = self.deck[:5][:]
        del self.deck[:5]
        for player in self.players:
            playerHand = []
            playerHand = self.deck[:2][:]
            del self.deck[:2]
            player.make_hand(playerHand)

    def get_comCards(self):
        return self.comCards

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
                convertHand+= str(hand[a][0])

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
        self.playerWin = []
        self.split = [] #stores name strength of every hand of same value of another hand in 1d list
        self.splitted = [] #stores name of easch user with the same hand in a 2d list (useful 1)
        self.handStrength()
        self.winStack()

    def get_playerWin(self):
        return self.playerWin

    def handStrength(self):
        for player in self.players:
            self.orderHand = []
            self.hand = player.get_hand() + self.C.get_comCards() #only comCards uses here
            self.hand.sort(reverse=True)
            self.pairThree()
            self.straightFlush()
            self.win.append([self.strength, player, self.orderHand[:]])
        self.win.sort(key = lambda x: x[0], reverse=True)
        self.clash()

    def pairThree(self):
        countList = []
        hand = self.hand[:]
        pair = 0
        three = False
        pairIndex = []
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

            if countList[a][0] == 3:
                three = True
                if self.strength <= 3:
                    self.strength = 3
                    self.orderHand = [hand[a][:]] + self.orderHand
                    hand[a] = ''

            if countList[a][0] == 4:
                if self.strength <= 7:
                    self.strength = 7
                    self.orderHand = [hand[a][:]] + self.orderHand
                    hand[a] = ''

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
        flip = True
        count = 0
        while flip and count <= len(self.win):
            flip = False
            for a in range(len(self.win)):
                if len(self.win) > a+1:
                    if self.win[a][0] == self.win[a+1][0]:
                        flip = self.sorting(self.win[a][2], self.win[a+1][2])

                        if flip == 'split':
                            flip = True
                            if [self.win[a][0], self.win[a][1]] not in self.split:
                                self.split.append([self.win[a][0], self.win[a][1]])
                                self.split.append([self.win[a+1][0], self.win[a+1][1]])

                        elif flip:
                            temp = self.win[a][:]
                            self.win[a] = self.win[a+1][:]
                            self.win[a+1] = temp[:]
            count+=1

        if len(self.split) != 0:
            self.splitWork()

    def splitWork(self):
        temp = []
        strength = self.split[0][0]
        for a in range(len(self.split)):
            if self.split[a][0] == strength:
                temp.append(self.split[a][1])
            else:
                self.splitted.append(temp[:])
                strength = self.split[a][0]
                temp = []
        self.splitted.append(temp[:]) #on the last pass it wont go to the else statement

    def winStack(self):
        printed = False
        count = 0
        print('splitted:', self.splitted)
        while count < len(self.win):
            printed = False
            for pos in self.splitted:
                temp = []
                if self.win[count][1] in pos:
                    for player in pos:
                        temp.append([player, self.strengthList[self.win[count][0]]])
                        printed = True
                        count+=1
                    self.playerWin.append(temp[:])

            if not printed:
                self.playerWin.append([[self.win[count][1], self.strengthList[self.win[count][0]]]])
            count+=1
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
        self.order = []
        self.winnerList = []
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
            self.comCards = Cards.convert(self.C.get_comCards()[:3])
            message = 'Flop: '

        elif self.comCount == 2:
            self.comCards = Cards.convert(self.C.get_comCards()[:4])
            message = 'Turn: '

        elif self.comCount == 3:
            self.comCards = Cards.convert(self.C.get_comCards()[:])
            message = 'River: '
        
        message += self.comCards
        if message != '':
            self.sendMessage(message, self.tableGroup)
        self.comCount+=1

    def makePlayerOrder(self):
        playerList = []
        for player in self.players:
            playerList.append(player)

        for a in range(1, self.noOfPlayers+1):
            player = (self.dealer+a)%self.noOfPlayers
            self.order.append(playerList[player])
        self.nextTurn()

    def nextTurn(self):
        self.turnIndex = (self.turnIndex+1)%self.noOfPlayers
        self.turn = self.order[self.turnIndex]

    def getPlayer(self, player):
        try:
            player = player.get_username()
            userInstance = CustomUser.objects.get(username=player)
            self.player = Players.objects.get(user_id=userInstance.id)
        except Players.DoesNotExist:
            try:
                self.game = Room.objects.get(groupName=self.tableGroup)
            except Room.DoesNotExist:
                print('everyone left (getPlayer)') #untested
                sys.exit()
            return False
        return True

    def blinds(self):
        sb = self.addRaiseAmount(self.minimumBet)
        self.nextTurn()
        bb = self.addRaiseAmount(self.minimumBet)
        self.nextTurn()
        message = self.turn.get_username() + ' posted BB (' + str(bb + sb) + ')\n'
        message += self.turn.get_username() + ' posted SB (' + str(sb) + ')'
        self.sendMessage(message, self.tableGroup)
        
    def sendCards(self):
        for player in self.players:
            if player.get_playerIn():
                self.getPlayer(player)
                hand = Cards.convert(player.get_hand())
                async_to_sync(get_channel_layer().group_send)(
                    player.get_username(),
                    {
                        'type': 'cards',
                        'hand': hand,
                        'comCards': self.comCards,
                        'dealer': self.dealer,
                        'moneyInTable': str(player.get_money())

                    }
                )

    def getChoice(self):
        putIn = str(self.turn.get_callAmount())
        async_to_sync(get_channel_layer().group_send)(
            self.turn.get_username(),
            {
                'type': 'playerTurn',
                'putIn': putIn,
            }
        )

        playerLeft = False
        while self.game.action is None and not playerLeft:
            try:
                self.game.refresh_from_db()
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
                            self.sendMessage('Raise amount must be a positive integer', self.turn.get_username())
                            self.makeTurn()

            except Room.DoesNotExist:
                print('everyone left (getChoice)')
                self.table.lastUsed = datetime.now(timezone.utc)
                self.table.save()
                sys.exit()

            if not self.getPlayer(self.turn):
                self.choice = 'f'
                playerLeft = True
                print(self.turn.get_username(), 'left')

        self.game.action = None
        self.game.save()

    def makeTurn(self):
        try:
            self.game = Room.objects.get(groupName=self.tableGroup)
        except Room.DoesNotExist:
            print('everyone left (makeTurn)')
            self.table.lastUsed = datetime.now(timezone.utc)
            self.table.save()
            sys.exit()

        if self.getPlayer(self.turn):
            self.player.turn = True
            self.player.save()
            self.getChoice()

        else:
            self.choice = 'f'

    def makeChoice(self):
        money = 0
        if self.choice == 'c':
            money = self.turn.call(self.turn.get_callAmount())
            self.pot += money

        elif self.choice == 'r':
            money = self.addRaiseAmount(int(self.raiseAmount))

        elif self.choice == 'f':
            self.turn.fold()

        self.makeMessage(money)

    def addRaiseAmount(self, raiseAmount):
        self.better = self.turnIndex
        callAmount = self.turn.call(self.turn.get_callAmount())
        raiseAmount = self.turn.call(raiseAmount)
        self.pot += (raiseAmount + callAmount)

        for player in self.players:
            if self.turn != player:
                player.callAmount += raiseAmount
        return raiseAmount

    def updateDBMoney(self):
        for player in self.players:
            if self.getPlayer(player):
                self.player.moneyInTable = player.get_money()
                self.player.save()

    def makeMessage(self, money):
        if self.choice == 'f':
            message = self.turn.get_username() + ' folded'

        elif self.choice == 'r':
            if self.turn.get_money() == 0:
                message = self.turn.get_username() + ' went all-in'
            else:
                message = self.turn.get_username() + ' raised ' +  str(money)

        if self.choice == 'c':
            if money == 0:
                message = self.turn.get_username() + ' checked'
            else:
                message = self.turn.get_username() + ' called ' + str(money)

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
            if player.get_playerIn() and player.get_money() > 0:
                count+=1
        if count > 1:
            if self.table.getNoOfPlayers() > 1:
                return True
        return False

    def makeWinnerMessage(self):
        self.message = '\n------------------------------------------'
        showHands = []
        winningIndex = 999
        startIndex = a = (self.dealer+1)%self.noOfPlayers
        firstRun = True
        while a != startIndex or firstRun:
            firstRun = False
            for b in range(len(self.P.get_playerWin())):
                for player in self.P.get_playerWin()[b]:
                    if self.players[a] in player and b <= winningIndex:
                        winnningIndex = b
                        moneyWon = 0
                        for winner in self.winnerList:
                            if self.players[a] in winner:
                                moneyWon = winner[0]

                        showHands.append(
                            [   self.players[a].get_username(),
                                    Cards.convert(self.players[a].get_hand()),
                                player[1], #hand strength name
                                moneyWon
                            ]
                        )
            a = (a+1)%self.noOfPlayers


        for player in showHands:
            self.message += '\n%s: %s %s'%(player[0], player[2], player[1])
            if player[3] != 0:
                self.message += '\nWon %d'%(player[3])
        self.message += '\n------------------------------------------\n'

    def winner(self):
        playerWinners = []
        a = 0
        while self.pot != 0:
            winners = []
            for player in self.P.get_playerWin()[a]:
                if player[0].get_playerIn():
                    playerWinners.append(player[0])
            print('playerWinners:', playerWinners)

            winnerPrize = 0
            for winner in playerWinners:
                maxPrize = 0
                for player in self.players:
                    if player.get_putIn() > winner.get_putIn():
                        maxPrize += winner.get_putIn()
                    else:
                        maxPrize += player.get_putIn()
                winners.append([maxPrize, winner])
                winnerPrize += maxPrize

            while winnerPrize > self.pot:
                winners.sort(key = lambda x: x[0], reverse=True)
                winners[0][0] -= 1
                winnerPrize = 0
                for item in winners:
                    winnerPrize += item[0]

            self.pot -= winnerPrize
            for winner in winners:
                self.winnerList.append(winner)
            
            for player in winners:
                player[1].increaseMoney(player[0])
            self.updateDBMoney()
            a+=1
        
        self.makeWinnerMessage()
        self.sendMessage(self.message, self.tableGroup)


    def play(self):
        self.makePlayerOrder()
        for a in range(4):
            self.better = (self.dealer+1)%self.noOfPlayers #dunno about this line
            firstRun = True
            if a == 0:
                self.blinds()
            if self.checkMultiplePlayersIn():
                self.makeComCards()
                print('turnIndex:', self.turnIndex, end="")
                print(' |  better:', self.better)
                while (self.turnIndex != self.better or firstRun):
                    self.updateDBMoney()
                    self.sendCards()
                    print('players:', self.players)
                    firstRun = False
                    if self.turn.get_money() != 0 and self.turn.get_playerIn():
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

        if not game.game and len(playersInGame) > 1:
            time.sleep(0.2)
            game.game = True
            game.save()
            print('game started')
            Game((table.buyIn)//100, dealer, tableGroup, table, playersInGame)
            game.game = False
            game.save()
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