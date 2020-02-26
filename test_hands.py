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

def makeHandsMan(players):
    comCards = [[5, 3], [7, 1], [13, 2], [6, 2], [11, 2]]
    hands = [[
            [7, 3], [7, 0] #first player hand
        ], [
            [13, 3], [4, 2] #second player hand etc
        ], [
            [3, 1], [4, 3]
    ]]

    for player, hand in zip(players, hands):
        playerHand = hand + comCards
        playerHand.sort(key = lambda x: x[0], reverse = True)
        hand = convert(playerHand)
        print(player, hand)

players = ['player1', 'player2', 'player3']
makeHandsMan(players)