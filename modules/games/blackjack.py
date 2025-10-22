# Port of https://github.com/Himan10/BlackJack
# Adapted for Meshtastic mesh-bot by K7MHI Kelly Keeton 2024

from random import choices, shuffle
from modules.log import *
import time
import pickle

jack_starting_cash = 100  # Replace 100 with your desired starting cash value
from modules.settings import jackTracker

SUITS = ("♥️", "♦️", "♠️", "♣️")
RANKS = (
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "J",
    "Q",
    "K",
    "A",
)
VALUES = {
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "10": 10,
    "J": 10,
    "Q": 10,
    "K": 10,
    "A": 11,
}

class jackCard:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return self.rank + " of " + self.suit

class jackDeck:
    """ Creating a Deck of cards and Deal two cards to both player and dealer. """

    def __init__(self):
        self.deck = []
        self.player = []
        self.dealer = []
        for suit in SUITS:
            for rank in RANKS:
                self.deck.append((suit, rank))

    def shuffle(self):
        shuffle(self.deck)

    def deal_cards(self):
        self.player = choices(self.deck, k=2)
        self.delete_cards(self.player)
        self.dealer = choices(self.deck, k=2)
        self.delete_cards(self.dealer)  # Delete Drawn Cards
        return self.player, self.dealer

    def delete_cards(self, total_drawn):
        """ Delete Drawn cards from the Decks """
        try:
            for i in total_drawn:
                self.deck.remove(i)
        except ValueError:
            pass

class jackHand:
    """ Adding the values of player/dealer cards and change the values of Aces acc. to situation. """
    def __init__(self):
        self.cards = []
        self.value = 0
        self.aces = 0

    def add_cards(self, card):
        self.cards.extend(card)
        for count, ele in enumerate(card, 0):
            if ele[1] == "A":
                self.aces += 1
            self.value += VALUES[ele[1]]
        self.adjust_for_ace()

    def adjust_for_ace(self):
        while self.aces > 0 and self.value > 21:
            self.value -= 10
            self.aces -= 1

class jackChips:
    """ Player/dealer chips for making bets and Adding/Deducting amount in/from Player's total. """
    def __init__(self):
        self.total = jack_starting_cash
        self.bet = 0
        self.winnings = 0

    def win_bet(self):
        self.total += self.bet
        self.winnings += 1

    def loss_bet(self):
        self.total -= self.bet
        self.winnings -= 1

def success_rate(next_card, player_hand):
    # Estimate the chance of a successful 'HIT' (not busting) in blackjack.

    # If player already has 21 or more, hitting will always bust
    if player_hand.value >= 21:
        return "\n🧠 What do you think?"

    # Calculate how much more the player can add without busting
    max_safe = 21 - player_hand.value

    safe_cards = 0
    total_cards = 0
    for rank in VALUES:
        # 4 cards of each rank in a standard deck
        count = 4
        card_value = VALUES[rank]
        # Ace can be 1 or 11, but here we treat it as 1 if 11 would bust
        if rank == "A":
            card_value = 1 if player_hand.value + 11 > 21 else 11
        # Count as safe if it won't bust the player
        if card_value <= max_safe:
            safe_cards += count
        total_cards += count

    # Calculate probability
    success_chance = int((safe_cards / total_cards) * 100)
    fail_chance = 100 - success_chance

    return f"\n🧠Hit: {fail_chance}% 👎, {success_chance}% 👍"

def hits(obj_de):
    new_card = [obj_de.deal_cards()[0][0]]
    # obj_h.add_cards(new_card)
    return new_card

def display_hand(hand):
    # Display the cards in the hand nicely
    d = "" # display
    for card in hand:
        d += f"{card[1]}{card[0]}"
        if card != hand[-1]:
            d += ", "
    return d

def show_some(player_cards, dealer_cards, obj_h):
    msg = f"Player[{obj_h.value}] {display_hand(player_cards)}  "
    msg += f"\nDealer[{VALUES[dealer_cards[1][1]]}] {dealer_cards[1][1]}{dealer_cards[1][0]} "
    return msg

def show_all(player_cards, dealer_cards, obj_h, obj_d):
    msg = f"Player[{obj_h.value}] {display_hand(player_cards)}  "
    msg += f"\nDealer[{obj_d.value}] {display_hand(dealer_cards)}"
    return msg

def player_bust(obj_h, obj_c):
    if obj_h.value > 21:
        obj_c.loss_bet()
        return True
    return False

def player_wins(obj_h, obj_d, obj_c):
    if any((obj_h.value == 21, obj_h.value > obj_d.value and obj_h.value < 21)):
        obj_c.win_bet()
        return True
    return False

def dealer_bust(obj_d, obj_h, obj_c):
    if obj_d.value > 21:
        if obj_h.value < 21:
            obj_c.win_bet()
        return True
    return False

def dealer_wins(obj_h, obj_d, obj_c):
    if any((obj_d.value == 21, obj_d.value > obj_h.value and obj_d.value < 21)):
        obj_c.loss_bet()
        return True
    return False

def push(obj_h, obj_d):
    if obj_h.value == obj_d.value:
        return True
    return False

def player_surrender(obj_c):
    obj_c.loss_bet()
    return True

def gameStats(p_count, d_count, draw_c):
    msg = f"\n📊🏆P:{p_count},D:{d_count},T:{draw_c}"
    return msg

def getLastCmdJack(nodeID):
    for i in range(len(jackTracker)):
        if jackTracker[i]['nodeID'] == nodeID:
            return jackTracker[i]['cmd']
    return None

def setLastCmdJack(nodeID, cmd):
    for i in range(len(jackTracker)):
        if jackTracker[i]['nodeID'] == nodeID:
            jackTracker[i]['cmd'] = cmd
            return True
    return False

def saveHSJack(nodeID, highScore):
    # Save the game state to pickle
    highScore = {'nodeID': nodeID, 'highScore': highScore}
    try:
        with open('data/blackjack_hs.pkl', 'wb') as file:
            pickle.dump(highScore, file)
    except FileNotFoundError:
        logger.debug("System: BlackJack: Creating new data/blackjack_hs.pkl file")
        with open('data/blackjack_hs.pkl', 'wb') as file:
            pickle.dump(highScore, file)

def loadHSJack():
    try:
        with open('data/blackjack_hs.pkl', 'rb') as file:
            highScore = pickle.load(file)
            return highScore
    except FileNotFoundError:
        logger.debug("System: BlackJack: Creating new data/blackjack_hs.pkl file")
        highScore = {'nodeID': 0, 'highScore': 0}
        with open('data/blackjack_hs.pkl', 'wb') as file:
            pickle.dump(highScore, file)
        return 0

def playBlackJack(nodeID, message, last_cmd=None):
    # Initalize the Game
    msg, last_cmd = '', None
    blackJack = False
    p_win, d_win, draw = 0, 0, 0
    p_chips = jackChips()
    p_hand = jackHand()
    d_hand = jackHand()
    p_cards, d_cards = [], []
    bet_money = 0
    # Initalize the Cards
    cards_deck = jackDeck()
    cards_deck.shuffle()
    p_cards, d_cards = cards_deck.deal_cards()
    # Deal the cards to player and dealer
    p_hand.add_cards(p_cards)
    d_hand.add_cards(d_cards)
    next_card = hits(cards_deck)

    # Check if player, use tracking
    for i in range(len(jackTracker)):
        if jackTracker[i]['nodeID'] == nodeID:
            last_cmd = jackTracker[i]['cmd']
            p_chips.total = jackTracker[i]['cash']
            p_win = jackTracker[i]['gameStats']['p_win']
            d_win = jackTracker[i]['gameStats']['d_win']
            draw = jackTracker[i]['gameStats']['draw']
            bet_money = jackTracker[i]['bet']
            if last_cmd == "playing":
                p_chips.bet = bet_money
                p_cards = jackTracker[i]['p_cards']
                d_cards = jackTracker[i]['d_cards']
                p_hand = jackTracker[i]['p_hand']
                d_hand = jackTracker[i]['d_hand']
                next_card = jackTracker[i]['next_card']

    if last_cmd is None:
        # create new player if not in tracker
        if nodeID != 0:
            #logger.debug(f"System: BlackJack: New Player {nodeID}")
            jackTracker.append({'nodeID': nodeID, 'cmd': 'new', 'last_played': time.time(), 'cash': jack_starting_cash,\
                'bet': 0, 'gameStats': {'p_win': p_win, 'd_win': d_win, 'draw': draw}, 'p_cards':p_cards, 'd_cards':d_cards, 'p_hand':p_hand.cards, 'd_hand':d_hand.cards, 'next_card':next_card})
            return f"You have {p_chips.total} chips.   Whats your bet?"
        return "Error: Player not found."

    if getLastCmdJack(nodeID) == "new":
        # Place Bet
        try:
            # handle B letter
            if message.lower() == "b":
                if bet_money == 0:
                    bet_money = 5
            elif message.lower() == "r":
                #resend the hand
                msg += show_some(p_cards, d_cards, p_hand)
                return msg
            elif "blackjack" in message.lower():
                return f"\nTo place a bet, enter the amount you wish to wager."
            else:
                try:
                    bet_money = int(message)
                except ValueError:
                    return f"\nInvalid Bet, please enter a valid number."

            if bet_money <= p_chips.total and bet_money >= 1:
                p_chips.bet = bet_money
            else:
                return f"\nInvalid Bet, the maximum bet you can place is {p_chips.total} and the minimum bet is 1."
        except ValueError:
            return f"\nInvalid Bet, the maximum bet, {p_chips.total}"

        # Show the cards
        msg += show_some(p_cards, d_cards, p_hand)
        # check for blackjack 21 and only two cards
        if p_hand.value == 21 and len(p_hand.cards) == 2:
            msg += f"\n🎰 BLAAAACKJACKKKK 💰"
            p_chips.total += round(p_chips.bet * 1.5)
            setLastCmdJack(nodeID, "dealerTurn")
            blackJack = True
            # Save the game state
            for i in range(len(jackTracker)):
                if jackTracker[i]['nodeID'] == nodeID:
                    jackTracker[i]['cash'] = int(p_chips.total)
                    break
        else:
            # Display the statistics
            stats = success_rate(next_card, p_hand)
            msg += stats
            setLastCmdJack(nodeID, "betPlaced")

    if getLastCmdJack(nodeID) == "betPlaced":
        setLastCmdJack(nodeID, "playing")
        msg += f"\n(H)it,(S)tand,(F)orfit,(D)ouble,(R)esend,(L)eave table"

        # save the game state
        for i in range(len(jackTracker)):
            if jackTracker[i]['nodeID'] == nodeID:
                jackTracker[i]['cash'] = p_chips.total
                jackTracker[i]['bet'] = p_chips.bet
                jackTracker[i]['p_cards'] = p_cards
                jackTracker[i]['d_cards'] = d_cards
                jackTracker[i]['p_hand'] = p_hand
                jackTracker[i]['d_hand'] = d_hand
                jackTracker[i]['next_card'] = next_card
        return msg


    while getLastCmdJack(nodeID) == "playing":  # Recall var. from hit and stand function
        next_card = hits(cards_deck)
        
        # Get the statistics
        stats = success_rate(next_card, p_hand)

        # Player's Turn
        choice = message.lower()

        if choice == "hit" or choice == "h":
            # hits(obj_de, p_hand)
            p_hand.add_cards(next_card)
            msg += show_some(p_hand.cards, d_cards, p_hand)
        elif choice == "stand" or choice == "s":
            setLastCmdJack(nodeID, "dealerTurn")
        elif choice == "forfit" or choice == "f":
            p_chips.bet = p_chips.bet / 2
            setLastCmdJack(nodeID, "dealerTurn")
            p_hand.value += 21
        elif choice == "double" or choice == "d":
            if p_chips.bet * 2 <= p_chips.total:
                p_chips.bet *= 2
                next_d_card = hits(cards_deck)
                p_hand.add_cards(next_d_card)
                setLastCmdJack(nodeID, "dealerTurn")
            else:
                return "You can't Double Down, dont have enough chips"
        elif choice == "resend" or choice == "r":
            msg += show_some(p_hand.cards, d_cards, p_hand)
        else:
            return "(H)it,(S)tand,(F)orfit,(D)ouble,(R)esend,(L)eave table"

        # Check if player bust
        if player_bust(p_hand, p_chips):
            d_win += 1
            msg += f"\n💥PlayerBUST💥"
            setLastCmdJack(nodeID, "dealerTurn")
        
        if getLastCmdJack(nodeID) == "playing":
            msg += stats
            msg += "[H,S,F,D]"

        # Save the game state
        for i in range(len(jackTracker)):
            if jackTracker[i]['nodeID'] == nodeID:
                jackTracker[i]['cash'] = int(p_chips.total)
                jackTracker[i]['bet'] = int(p_chips.bet)
                jackTracker[i]['gameStats']['p_win'] = int(p_win)
                jackTracker[i]['gameStats']['d_win'] = int(d_win)
                jackTracker[i]['gameStats']['draw'] = int(draw)
                jackTracker[i]['p_cards'] = p_cards
                jackTracker[i]['d_cards'] = d_cards
                jackTracker[i]['p_hand'] = p_hand
                jackTracker[i]['d_hand'] = d_hand
                break

        # Exit player's turn
        if getLastCmdJack(nodeID) == "dealerTurn":
            break
        
        return msg

    if getLastCmdJack(nodeID) == "dealerTurn":
        # Dealers Turn
        if not blackJack:
        # recall the game state
            for i in range(len(jackTracker)):
                if jackTracker[i]['nodeID'] == nodeID:
                    p_chips.total = jackTracker[i]['cash']
                    p_chips.bet = jackTracker[i]['bet']
                    p_win = jackTracker[i]['gameStats']['p_win']
                    d_win = jackTracker[i]['gameStats']['d_win']
                    draw = jackTracker[i]['gameStats']['draw']
                    p_cards = jackTracker[i]['p_cards']
                    d_cards = jackTracker[i]['d_cards']
                    p_hand = jackTracker[i]['p_hand']
                    d_hand = jackTracker[i]['d_hand']
                    next_card = jackTracker[i]['next_card']
                    break

        if p_hand.value <= 21:
            # Dealer's Turn
            while d_hand.value < 17:
                d_card = hits(cards_deck)
                d_hand.add_cards(d_card)
                if dealer_bust(d_hand, p_hand, p_chips):
                    p_win += 1
                    msg += f"\n💰DealerBUST💥"
                    break
            # Show all cards
            msg += show_all(p_hand.cards, d_hand.cards, p_hand, d_hand)

            # Check who wins
            if push(p_hand, d_hand):
                draw += 1
                msg += f"\n👌PUSH"
            elif player_wins(p_hand, d_hand, p_chips):
                p_win += 1
                msg += f"\n🎉PLAYER WINS🎰"
            elif dealer_wins(p_hand, d_hand, p_chips):
                d_win += 1
                msg += f"\n👎DEALER WINS"
        else:
            msg += f"\n👎DEALER WINS"

        # Display the Game Stats
        msg += gameStats(str(p_win), str(d_win), str(draw))

        # Display the chips left
        if p_chips.total < 1:
            if p_chips.total > 0:
                msg += f"\n🪙Keep the change you filthy animal!"
            else:
                msg += f"\n💸NO MORE CHIPS!🏧💳"
                p_chips.total = jack_starting_cash
        else:
            # check high score
            highScore = loadHSJack()
            if highScore != 0 and p_chips.total > highScore['highScore']:
                msg += f"\n💰HighScore💰{p_chips.total} "
                saveHSJack(nodeID, p_chips.total)
            else:
                msg += f"\n💰You have {p_chips.total} chips "

        msg += f"\nBet or Leave?"

        # Reset the game
        setLastCmdJack(nodeID, "new")
        jackTracker[i]['cash'] = p_chips.total
        jackTracker[i]['gameStats']['p_win'] = p_win
        jackTracker[i]['gameStats']['d_win'] = d_win
        jackTracker[i]['gameStats']['draw'] = draw
        jackTracker[i]['p_cards'] = []
        jackTracker[i]['d_cards'] = []
        jackTracker[i]['p_hand'] = []
        jackTracker[i]['d_hand'] = []
        jackTracker[i]['last_played'] = time.time()

    return msg
