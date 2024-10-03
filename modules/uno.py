# https://github.com/melvin-02/UNO-game
# Adapted for Meshtastic mesh-bot by K7MHI Kelly Keeton 2024

import random
import time
from modules.log import *

color = ('RED', 'GREEN', 'BLUE', 'YELLOW')
rank = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'Skip', 'Reverse', 'Draw2', 'Draw4', 'Wild')
ctype = {'0': 'number', '1': 'number', '2': 'number', '3': 'number', '4': 'number', '5': 'number', '6': 'number',
         '7': 'number', '8': 'number', '9': 'number', 'Skip': 'action', 'Reverse': 'action', 'Draw2': 'action',
         'Draw4': 'action_nocolor', 'Wild': 'action_nocolor'}

# Player List
unoLobby = []
unoTracker = [{'nodeID': 0, 'last_played': time.time(), 'cmd': '', 'playerName': ''}]
unoGameTable = {'turn': -1, 'direction': 1, 'deck': None, 'hands': None, 'top_card': None}

class Card:
    def __init__(self, color, rank):
        self.rank = rank
        if ctype[rank] == 'number':
            self.color = color
            self.cardtype = 'number'
        elif ctype[rank] == 'action':
            self.color = color
            self.cardtype = 'action'
        else:
            self.color = None
            self.cardtype = 'action_nocolor'

    def __str__(self):
        if self.color is None:
            return self.rank
        else:
            return self.color + " " + self.rank

class Deck:
    def __init__(self):
        self.deck = []
        self.discard_pile = []
        for clr in color:
            for ran in rank:
                if ctype[ran] != 'action_nocolor':
                    self.deck.append(Card(clr, ran))
                    self.deck.append(Card(clr, ran))
                else:
                    self.deck.append(Card(clr, ran))

    def __str__(self):
        deck_comp = ''
        for card in self.deck:
            deck_comp += '\n' + card.__str__()
        return 'The deck has ' + deck_comp

    def shuffle(self):
        random.shuffle(self.deck)

    def deal(self):
        if not self.deck:
            self.reshuffle_discard_pile()
        return self.deck.pop()

    def reshuffle_discard_pile(self):
        if len(self.discard_pile) > 1:
            top_card = self.discard_pile.pop()
            self.deck = self.discard_pile[:]
            self.discard_pile = [top_card]
            self.shuffle()
        else:
            raise IndexError("No cards left to reshuffle")

class Hand:
    def __init__(self):
        self.cards = []
        self.cardsstr = []
        self.number_cards = 0
        self.action_cards = 0

    def add_card(self, card):
        self.cards.append(card)
        self.cardsstr.append(str(card))
        if card.cardtype == 'number':
            self.number_cards += 1
        else:
            self.action_cards += 1
        self.sort_cards()

    def remove_card(self, place):
        self.cardsstr.pop(place - 1)
        return self.cards.pop(place - 1)

    def cards_in_hand(self):
        msg = ''
        for i in range(len(self.cardsstr)):
            msg += f' {i + 1}.{self.cardsstr[i]}'
        return msg

    def single_card(self, place):
        return self.cards[place - 1]

    def no_of_cards(self):
        return len(self.cards)

    def sort_cards(self):
        self.cards.sort(key=lambda card: (
            card.color if card.color is not None else '',
            int(card.rank) if card.cardtype == 'number' and card.rank is not None else 0))
        self.cardsstr = [str(card) for card in self.cards]

def choose_first():
    global unoLobby
    if unoLobby != []:
        random_player = random.choice(unoLobby)
        return random_player
    else:
        return None

def single_card_check(top_card, card):
    if card.color == top_card.color or top_card.rank == card.rank or card.cardtype == 'action_nocolor':
        return True
    else:
        return False

def full_hand_check(hand, top_card):
    for c in hand.cards:
        if c.color == top_card.color or c.rank == top_card.rank or c.cardtype == 'action_nocolor':
            #return hand.remove_card(hand.cardsstr.index(str(c)) + 1)
            return hand.remove_card(hand.cards.index(c) + 1)
    else:
        return 'no card'

def win_check(hand):
    if len(hand.cards) == 0:
        return True
    else:
        return False

def last_card_check(hand):
    for c in hand.cards:
        if c.cardtype != 'number':
            return True
        else:
            return False

def getNextPlayer(playerIndex, direction=1, skip=False):
    current_index = unoLobby.index(playerIndex)
    next_index = (current_index + direction) % len(unoLobby)
    if skip:
        next_index = (next_index + direction) % len(unoLobby)
    return unoLobby[next_index]

def getNextPlayerID(playerIndex, direction=1, skip=False):
    current_index = unoLobby.index(playerIndex)
    next_index = (current_index + direction) % len(unoLobby)
    if skip:
        next_index = (next_index + direction) % len(unoLobby)
    return unoTracker[next_index]['nodeID']

def unoPlayerDetail(nodeID):
    for i in range(len(unoTracker)):
        if unoTracker[i] == nodeID:
            return f'{unoTracker[i]}'
        
def getUnoPname(nodeID):
    global unoTracker
    for i in range(len(unoTracker)):
        if unoTracker[i]['nodeID'] == nodeID:
            return unoTracker[i]['playerName']

def setLastCmd(nodeID, cmd):
    global unoTracker
    for i in range(len(unoTracker)):
        if unoTracker[i]['nodeID'] == nodeID:
            unoTracker[i]['cmd'] = cmd

def getLastCmd(nodeID):
    global unoTracker
    for i in range(len(unoTracker)):
        if unoTracker[i]['nodeID'] == nodeID:
            return unoTracker[i]['cmd']

def getUnoIDs():
    global unoTracker, unoLobby
    userIDlist = []
    for i in range(len(unoLobby)):
        for j in range(len(unoTracker)):
            if unoTracker[j]['playerName'] == unoLobby[i]:
                unoTracker[j]['last_played'] = time.time()
                userIDlist.append(unoTracker[j]['nodeID'])
                return (userIDlist)
            
def playUno(nodeID, message):
    global unoTracker, unoGameTable, unoLobby
    playing = False
    nextPlayerNodeID = 0
    msg = 'Feature Not Implemented'


    return msg