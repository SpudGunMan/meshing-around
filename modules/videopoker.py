# Port of https://github.com/devtronvarma/Video-Poker-Terminal-Game
# Adapted for Meshtastic mesh-bot by K7MHI Kelly Keeton 2024
import random
import time
from modules.log import *

vpStartingCash = 20
vpTracker= [{'nodeID': 0, 'cmd': 'new', 'time': time.time(), 'cash': vpStartingCash, 'player': None, 'deck': None, 'highScore': 0, 'drawCount': 0}]

# Define the Card class
class CardVP:

    card_values = {  # value of the ace is high until it needs to be low
        2: 2,
        3: 3,
        4: 4,
        5: 5,
        6: 6,
        7: 7,
        8: 8,
        9: 9,
        10: 10,
        'Jack': 11,
        'Queen': 12,
        'King': 13,
        'Ace': 14
    }

    def __init__(self, suit, rank):
        """
        :param suit: The face of the card, e.g. Spade or Diamond
        :param rank: The value of the card, e.g 3 or King
        """
        self.suit = suit.capitalize()
        self.rank = rank
        self.points = self.card_values[rank]

# Function to output ascii version of the cards in a hand in the terminal
def drawCardsVp(*cards, return_string=True):
    """
    Instead of a boring text version of the card we render an ASCII image of the card.
    :param cards: One or more card objects
    :param return_string: By default we return the string version of the card, but the dealer hide the 1st card and we
    keep it as a list so that the dealer can add a hidden card in front of the list
    """
    # we will use this to prints the appropriate icons for each card
    suits_name = ['Spades', 'Diamonds', 'Hearts', 'Clubs']
    suits_symbols = ['♠️', '♦️', '♥️', '♣️']

    # create an empty list of list, each sublist is a line 2 lines for the card
    lines = [[] for i in range(1)]

    for index, card in enumerate(cards):
        # "King" should be "K" and "10" should still be "10"
        if card.rank == 10:  # ten is the only one who's rank is 2 char long
            rank = str(card.rank)
        else:
            rank = str(card.rank)[0]  # some have a rank of 'King' this changes that to a simple 'K' ("King" doesn't fit)
        # get the cards suit in two steps
        suit = suits_name.index(card.suit)
        suit = suits_symbols[suit]

        # add the individual card on a line by line basis
        lines[0].append('{}{} '.format(rank, suit))

    result = []
    #result.append('1       2       3       4      5')  # add the index for the cards to top row
    for index, line in enumerate(lines):
        result.append(''.join(lines[index]))

    # hidden cards do not use string
    if return_string:
        return '\n'.join(result)
    else:
        return result

# Define Deck class 
class DeckVP:
    
    def __init__(self):
        self.cards = []
        self.build()

    # method for building the deck
    def build(self):
        for s in ['Spades', 'Diamonds', 'Hearts', 'Clubs']:
            for v in range(2, 11):
                self.cards.append(CardVP(s,v))
            for c in ["Jack", "Queen", "King", "Ace"]:
                self.cards.append(CardVP(s,c))

    # method to show cards in deck
    def display(self):
        for c in self.cards:
            print(drawCardsVp(c))

    # method to shuffle cards in deck
    def shuffle(self):
        for i in range(len(self.cards) - 1, 0, -1):
            r = random.randint(0, i)
            self.cards[i], self.cards[r] = self.cards[r], self.cards[i]

    # method to draw card from the deck
    def draw_card(self):
        return self.cards.pop()

# Define Player Class
class PlayerVP:
    def __init__(self):
        self.hand = []
        self.bankroll = 20

    # Method for initial five-card draw
    def draw_cards(self, deck):
        for i in range(5):
            self.hand.append(deck.draw_card())
        return self

    # Method for displaying player's hand
    def show_hand(self):
        msg = (drawCardsVp(
                self.hand[0],
                self.hand[1],
                self.hand[2],
                self.hand[3],
                self.hand[4]))
        return msg

    # Method for placing a bet
    def bet(self, ammount=0):
        bet = int(ammount)
        self.bet_size = bet
        self.bankroll -= self.bet_size

    # Method for selecting cards to redraw
    def redraw(self, deck, message):
        # if message has single digit, then it is the card to redraw, else it is the list of cards to redraw with a comma
        if len(message) == 1:
            try:
                # if single digit is the letter a redraw all cards
                if message.lower() == "a":
                    for i in range(5):
                        self.hand[i] = deck.draw_card()
                else:
                    # error trap for bad input
                    redraw_index = int(message) - 1
                    self.hand[redraw_index] = deck.draw_card()

                return self.show_hand()
            except Exception as e:
                pass
        else:
            try:
                # error trap for bad input
                if "," in message:
                    redraw_list = [int(x) - 1 for x in message.split(',')]
                if "." in message:
                    redraw_list = [int(x) - 1 for x in message.split('.')]
                if " " in message:
                    redraw_list = [int(x) - 1 for x in message.split(' ')]
                for i in redraw_list:
                    self.hand[i] = deck.draw_card()
                return self.show_hand()    
            except Exception as e:
                pass
    
        return "Re-Draw/Deal ex:1,3,4 to hold cards 1,3 and 4, or (N)o to keep current (H)and"

    # Method for scoring hand, calculating winnings, and outputting message
    def score_hand(self, resetHand = True):
        points = sorted([self.hand[i].points for i in range(5)])
        suits = [self.hand[i].suit for i in range(5)]
        points_repeat = [points.count(i) for i in points]
        suits_repeat = [suits.count(i) for i in suits]
        diff = max(points) - min(points)
        hand_name = ""
        msg = ""
        payoff = {
            "👑Royal Flush🚽": 10,
            "🧻Straight Flush🚽": 9,
            "Flush🚽": 8,
            "Full House🏠": 7,
            "Four of a Kind👯👯": 6,
            "Three of a Kind☘️": 5,
            "Two Pair👯👯": 4,
            "Straight📏": 3,
            "Pair👯": 2,
            "Bad Hand 🙈": -1,
        }

        if 5 in suits_repeat:
            if points == [10, 11, 12, 13, 14]: #find royal flush
                hand_name = "👑Royal Flush🚽"
                if resetHand:
                    self.bankroll += self.bet_size * payoff[hand_name]
            elif diff == 4 and max(points_repeat) == 1: # find straight flush w/o ace low
                hand_name = "🧻Straight Flush🚽"
                if resetHand:
                    self.bankroll += self.bet_size * payoff[hand_name]
            elif diff == 12 and points[4] == 14: # find straight flush w/ace low
                check = 0
                for i in range(1, 4):
                    check += points[i] - points[i - 1]
                if check == 3:
                    hand_name =  "🧻Straight Flush🚽"
                    if resetHand:
                        self.bankroll += self.bet_size * payoff[hand_name]
                else:
                    hand_name =  "Flush🚽"
                    if resetHand:
                        self.bankroll += self.bet_size * payoff[hand_name]
            else:
                hand_name = "Flush🚽"
                if resetHand:
                    self.bankroll += self.bet_size * payoff[hand_name]
        elif sorted(points_repeat) == [2,2,3,3,3]: # find full house
            hand_name = "Full House🏠"
            if resetHand:
                self.bankroll += self.bet_size * payoff[hand_name]
        elif 4 in points_repeat: # find four of a kind
            hand_name = "Four of a Kind👯👯"
            if resetHand:
                self.bankroll += self.bet_size * payoff[hand_name]
        elif 3 in points_repeat: # find three of a kind
            hand_name = "Three of a Kind☘️"
            if resetHand:
                self.bankroll += self.bet_size * payoff[hand_name]
        elif points_repeat.count(2) == 4: # find two-pair
            hand_name = "Two Pair👯👯"
            if resetHand:
                self.bankroll += self.bet_size * payoff[hand_name]
        elif 2 in points_repeat: # find pair
            logger.debug(f"System: VideoPoker: 235 self.bankroll: {self.bankroll} bet_size: {self.bet_size}")
            hand_name = "Pair👯"
            if resetHand:
                self.bankroll += self.bet_size * payoff[hand_name]
        elif diff == 4 and max(points_repeat) == 1: # find straight w/o ace low
            hand_name = "Straight📏"
            if resetHand:
                self.bankroll += self.bet_size * payoff[hand_name]
        elif diff == 12 and points[4] == 14: # find straight w/ace low
            check = 0
            for i in range(1, 4):
                check += points[i] - points[i - 1]
                if check == 3:
                    hand_name = "Straight📏"
                    if resetHand:
                        self.bankroll += self.bet_size * payoff[hand_name]
                else:
                    hand_name = "Bad Hand 🙈"
        else: # for everything Hand
            hand_name = "Bad Hand 🙈"

        if resetHand:
            self.hand = []
            msg = f"\nYour hand, {hand_name}. Your bankroll is now {self.bankroll} coins."
        else:
            if hand_name != "":
                msg = f"\nShowing:{hand_name}"
        return msg


def getLastCmdVp(nodeID):
    last_cmd = ""
    for i in range(len(vpTracker)):
        if vpTracker[i]['nodeID'] == nodeID:
            last_cmd = vpTracker[i]['cmd']
    return last_cmd

def setLastCmdVp(nodeID, cmd):
    for i in range(len(vpTracker)):
        if vpTracker[i]['nodeID'] == nodeID:
            vpTracker[i]['cmd'] = cmd

def playVideoPoker(nodeID, message):
    msg = ""

    # Initialize the player
    if getLastCmdVp(nodeID) is None or getLastCmdVp(nodeID=nodeID) == "":
        # create new player if not in tracker
        logger.debug(f"System: VideoPoker: New Player {nodeID}")
        vpTracker.append({'nodeID': nodeID, 'cmd': 'new', 'time': time.time(), 'cash': vpStartingCash, 'player': None, 'deck': None, 'highScore': 0, 'drawCount': 0})
        return f"Welcome to 🎰VideoPoker! you have {vpStartingCash} coins, Game Played via Direct Message. Whats your bet?"
    
    # Gather the player's bet
    if getLastCmdVp(nodeID) == "new" or getLastCmdVp(nodeID) == "gameOver":
        # Initialize shuffled Deck and Player
        player = PlayerVP()
        deck = DeckVP()
        deck.shuffle()
        drawCount = 1
        bet = 0
        msg = ''

        # load the player bankroll from tracker
        for i in range(len(vpTracker)):
            if vpTracker[i]['nodeID'] == nodeID:
                player.bankroll = vpTracker[i]['cash']
                vpTracker[i]['time'] = time.time()

        # Detect if message is a bet
        try:
            bet = int(message)
        except ValueError:
            msg += "Please enter a valid bet amount. 1 to 5 coins."

        # Check if bet is valid
        if bet > player.bankroll:
            msg += "You can only bet the money you have. No strip poker here..."
        elif bet < 1:
            msg += "You must bet at least 1 coin."
        elif bet > 5:
            msg += "You can only bet up to 5 coins."

        # if msg contains an error, return it
        if msg is not None and msg != '':
            return msg
        else:
            # Take the bet
            player.bet(str(message))
            # Bet placed, start the game
            setLastCmdVp(nodeID, "playing")

            # save player and deck to tracker
            for i in range(len(vpTracker)):
                if vpTracker[i]['nodeID'] == nodeID:
                    vpTracker[i]['player'] = player
                    vpTracker[i]['deck'] = deck
                    vpTracker[i]['cash'] = player.bankroll

    # Play the game
    if getLastCmdVp(nodeID) == "playing":
        msg = ''
    
        player.draw_cards(deck)
        msg += player.show_hand()
        # give hint to player
        msg += player.score_hand(resetHand=False)
        
        # save player and deck to tracker
        for i in range(len(vpTracker)):
            if vpTracker[i]['nodeID'] == nodeID:
                vpTracker[i]['player'] = player
                vpTracker[i]['deck'] = deck
                vpTracker[i]['drawCount'] = drawCount

        msg += f"\nDeal new card? \nex: 1,3,4 or (N)o,(A)ll"
        setLastCmdVp(nodeID, "redraw")
        return msg
    
    if getLastCmdVp(nodeID) == "redraw":
        msg = ''
        # load the player and deck from tracker
        for i in range(len(vpTracker)):
            if vpTracker[i]['nodeID'] == nodeID:
                player = vpTracker[i]['player']
                deck = vpTracker[i]['deck']
                drawCount  = vpTracker[i]['drawCount']

        # if player wants to redraw cards, and not done already
        if message.lower().startswith("n"):
            setLastCmdVp(nodeID, "endGame")
        if message.lower().startswith("h"):
            msg = player.show_hand()
            return msg
        else:
            if drawCount <= 1:
                msg = player.redraw(deck, message)
                if msg.startswith("Send Card"):
                    # if returned error message, return it
                    return msg
                drawCount += 1
                # save player and deck to tracker
                for i in range(len(vpTracker)):
                    if vpTracker[i]['nodeID'] == nodeID:
                        vpTracker[i]['player'] = player
                        vpTracker[i]['deck'] = deck
                        vpTracker[i]['drawCount'] = drawCount
                if drawCount == 2:
                    # this is the last draw will carry on to endGame for scoring
                    msg = player.redraw(deck, message) + f"\n"
                    if msg.startswith("Send Card"):
                        # if returned error message, return it
                        return msg
                    # redraw done
                    setLastCmdVp(nodeID, "endGame")
                else:
                    # show redrawn hand
                    return msg
            else:
                # redraw already done
                setLastCmdVp(nodeID, "endGame")
                
    if getLastCmdVp(nodeID) == "endGame":
        # load the player and deck from tracker
        for i in range(len(vpTracker)):
            if vpTracker[i]['nodeID'] == nodeID:
                player = vpTracker[i]['player']
                deck = vpTracker[i]['deck']

        msg += player.score_hand()

        if player.bankroll < 1:
            player.bankroll = vpStartingCash
            msg += "\nLooks 💸 like you're out of money. 💳 resetting ballance 🏧"
        elif player.bankroll > vpTracker[i]['highScore']:
            vpTracker[i]['highScore'] = player.bankroll
            msg += " 🎉HighScore!"

        msg += f"\nPlace your Bet, 'L' to leave the game."

        setLastCmdVp(nodeID, "gameOver")
        # reset player and deck in tracker
        for i in range(len(vpTracker)):
            if vpTracker[i]['nodeID'] == nodeID:
                vpTracker[i]['player'] = None
                vpTracker[i]['deck'] = None
                vpTracker[i]['drawCount'] = 0
                # save bankroll
                vpTracker[i]['cash'] = player.bankroll

        return msg

 