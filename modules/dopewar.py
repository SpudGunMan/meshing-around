# Port of https://github.com/Reconfirefly/drugwars/tree/master
# Adapted for Meshtastic mesh-bot by K7MHI Kelly Keeton 2024

import random
import time
import pickle
from modules.log import *

# Global variables
total_days = 7 # number of days or rotations the player has to play
starting_cash = 5000
# Database for the game reset on boot
dwInventoryDb = [{'userID': 1234567890, 'inventory': 0, 'priceList': [], 'amount': []}]
dwCashDb = [{'userID': 1234567890, 'cash': starting_cash},]
dwGameDayDb = [{'userID': 1234567890, 'day': 0},]
dwLocationDb = [{'userID': 1234567890, 'location': 'USA', 'loc_choice': 0},]
dwPlayerTracker = [{'userID': 1234567890, 'last_played': time.time(), 'cmd': 'start'},]
# high score is saved in a pickle file
dwHighScore = {}

class Drugs:

    def __init__(self, name, price_range):
        self.name = name
        self.price_range = price_range
        self.price_check()

    def price_check(self):
        # the * is to unpack the touple of values that the random goes between
        self.price = random.randint(*self.price_range)
        # print("the price of " + self.name + " is " + str(self.price))
        return self.price

class Events:

    def __init__(self, name, text, price_range):
        self.name = name
        self.price_range = price_range
        self.text = text
        self.price_mod()

    def price_mod(self):
        self.price = random.randint(*self.price_range)
        return self.price

my_drugs = [
    # Drugs("Name", (min price, max price), amount)
    Drugs("Cocaine", (15000, 28000)),
    Drugs("Heroin", (2000, 10000)),
    Drugs("Weed", (300, 1000)),
    Drugs("Hash", (200, 1200)),
    Drugs("Opium", (400, 1800)),
    Drugs("Acid", (1000, 4200)),
    Drugs("Ludes", (18, 75)),
]

event_list = [
    # Events("Name", "Text", (min price, max price))
    Events("Cocaine", 'El Chapo Arrested! 🚔 Coke price thru the roof! 📈', (40000, 110000)),
    Events("Heroin", 'Trump cracks down on opiates! Heroin in high demand by addicts📈', (9000, 25000)),
    Events("Weed", 'The DEA has fully legalized weed! Prices are at an all time low!📉', (50, 400)),
    Events("Hash", 'Ricky\'s hash driveway burned down! 🚒 Look at the price boys!📈', (800, 2000)),
    Events("Opium", 'Shenzhen 深圳 Opium 鸦片 Den 塔 was raided! 🚔 Street price is popping off!📈', (1800, 6000)),
    Events("Acid", 'The Grateful Dead are on tour! Acid prices are skyrocketing!📈', (5000, 15000)),
    Events("Ludes", 'The Wolf of Wall Street is back! Ludes are in demand!', (100, 300)),
    Events("Cocaine", "The Biden administration has legalized cocaine! Prices are at an all time low!📉", (3000, 10000)),
    Events("Heroin", "Oregon has legalized heroin! Prices are at an all time low!📉", (500, 2500)),
    Events("Weed", "Prices are at an all time HIGH!📈", (1000, 5000)),
    Events("Hash", "The Middle East has legalised hash! Prices are at an all time low!📉", (50, 1000)),
    Events("Opium", "The Sackler's flood the market with cheap opium! Prices are at an all time low!📉", (300, 900)),
    Events("Acid", "The FBI admits to dosing the water supply with LSD! Acid at an all time low!📉", (500, 2000)),
    Events("Ludes", "The FDA approves ludes for sale! Prices are at an all time low!📉", (3, 45))
]

def generatelocations():
    # dictionary of locations
    locs = {'Canada': ('Red Deer', 'Edmonton', 'Calgary', 'Toronto', 'Vancouver', 'St. Johns'),
            'USA': ('L.A.', 'NYC', 'Chicago', 'Miami', 'Houston', 'Phoenix'), 'Mexico': ('Tijuana', 'Mexico City', 'Cancun', 'Juarez', 'Acapulco', 'Guadalajara'),\
            'South America': ('Bogota', 'Caracas', 'Lima', 'Santiago', 'Buenos Aires', 'Rio'), 'Europe': ('London', 'Paris', 'Berlin', 'Rome', 'Madrid', 'Moscow')}

    country = list(locs.keys())
    country = country[random.randint(0, len(country)-1)]

    # return the location list for the user's country
    location = []
    for i in range(len(locs[country])):
        location.append(locs[country][i])
    return location

def generate_event():
    # roll to see if an event happens
    event_choice = random.randint(0, len(event_list)-1)
    if random.randint(0, 100) > 35:
        return event_choice
    else:
        return -1

def officer(nodeID):
    global dwCashDb, dwInventoryDb

    # get the inventory for the user
    for i in range(0, len(dwInventoryDb)):
        if dwInventoryDb[i].get('userID') == nodeID:
            inventory = dwInventoryDb[i].get('inventory')
    amount = check_inv(nodeID)
    
    # get the cash for the user
    for i in range(0, len(dwCashDb)):
        if dwCashDb[i].get('userID') == nodeID:
            cash = dwCashDb[i].get('cash')

    # rolls to see if the officer takes drugs from you
    # odds are (1 - event chance) * (officer chance) * (confiscation chance)
    # currently (1 - 0.35) * (0.20) * (0.35) = 4.55%
    # chance is approximate, not sure how randint handles endpoints, close enough for my purposes
    if random.randint(0, 100) > 65: # confiscation chance
        k = 0
        j = 0
        # removes all drugs from inventory tally and individual class attirbute
        for i in range(0, len(my_drugs)):
            j = amount[i]
            amount[i] = 0
            k += j
        inventory -= k
        # sends 'conf' for confiscated. sending a string is better than a number here
        cash_taken = 'conf'
        return cash_taken
    # rolls to see if the officer takes cash from you
    # odds are (1 - event chance) * (officer chance) * (1 - confiscation chance)
    # currently (1 - 0.35) * (0.20) * (0.65) = 8.45%
    # chance is approximate, not sure how randint handles endpoints, close enough for my purposes
    cash_taken = random.randint(1, cash-1)
    cash -= cash_taken
    
    # Update the cash_db and inventory_db
    for i in range(0, len(dwCashDb)):
        if dwCashDb[i].get('userID') == nodeID:
            dwCashDb[i]['cash'] = cash
    for i in range(0, len(dwInventoryDb)):
        if dwInventoryDb[i].get('userID') == nodeID:
            dwInventoryDb[i]['inventory'] = inventory
            amount = dwInventoryDb[i].get('amount')

    return cash_taken


def price_change(event_number):
    price_list = []
    for i in range(0, len(my_drugs)):
        j = my_drugs[i]
        k = j.price_check()
        price_list.append(k)
    
    # check if IndexError will be thrown and find a new event_number with generate_event
    while event_number > len(price_list)-1:
        event_number = generate_event()
    
    if event_number != -1:
        price_list[event_number] = event_list[event_number].price_mod()

    return price_list

def check_inv(nodeID):
    global dwInventoryDb

    # get the inventory ammount for the user
    for i in range(0, len(dwInventoryDb)):
        if dwInventoryDb[i].get('userID') == nodeID:
            amount = dwInventoryDb[i].get('amount')

    # if ammount is empty list initialize it
    if not amount:
        amount = []
        for i in range(0, len(my_drugs)):
            amount.append(0,)
        
        # save the amount to the inventory_db
        for i in range(0, len(dwInventoryDb)):
            if dwInventoryDb[i].get('userID') == nodeID:
                dwInventoryDb[i]['amount'] = amount
    
    return amount

def buy_func(nodeID, price_list, choice=0, value='0'):
    global dwCashDb, dwInventoryDb, dwPlayerTracker
    msg = ''
                 
    # get the inventory for the user
    for i in range(0, len(dwInventoryDb)):
        if dwInventoryDb[i].get('userID') == nodeID:
            inventory = dwInventoryDb[i].get('inventory')
    amount = check_inv(nodeID)
    
    # get the cash for the user
    for i in range(0, len(dwCashDb)):
        if dwCashDb[i].get('userID') == nodeID:
            cash = dwCashDb[i].get('cash')

    drug_choice = choice
    if choice == 0:
       msg = "Enter b or s and the drug number and qty you want to buy or sell. ex: b,1,10 buys 10 of drug 1"
       return msg
    else:
        if drug_choice in range(1, len(my_drugs) + 1):
            drug_choice = drug_choice - 1
            msg = my_drugs[drug_choice].name + ": you have " + str(amount[drug_choice]) + " "
            msg += " The going price is: $" + str(price_list[drug_choice]) + " "

    buy_amount = value
    if buy_amount == 'm':
        buy_amount = cash // price_list[drug_choice]
        if buy_amount > 100 - inventory:
            buy_amount = 100 - inventory
    
    if buy_amount == 0:
        msg = "Enter b or s and the drug number and qty you want to buy or sell. ex: b,1,10 buys 10 of drug 1"
        return msg

    buy_amount = int(buy_amount)
    if buy_amount not in range(1, 101):
        msg = f"Enter qty or m for max"
        return msg
    if buy_amount > 100 - inventory:
        msg = "You don\'t have enough space for all that."
        return msg
    if buy_amount * price_list[drug_choice] <= cash:
        amount[drug_choice] += buy_amount
        cash -= buy_amount * price_list[drug_choice]
        inventory += buy_amount
        msg += "You bought " + str(buy_amount) + " " + my_drugs[drug_choice].name + '. Remaining cash: $' + str(cash)
        msg += f"\nBuy Sell Fly?"
    else:
        msg = "You don\'t have enough cash!"
        return msg

    # update the cash_db and inventory_db values
    for i in range(0, len(dwCashDb)):
        if dwCashDb[i].get('userID') == nodeID:
            dwCashDb[i]['cash'] = cash
    for i in range(0, len(dwInventoryDb)):
        if dwInventoryDb[i].get('userID') == nodeID:
            dwInventoryDb[i]['inventory'] = inventory
    # save the last command as ask_bsf
    for i in range(0, len(dwPlayerTracker)):
        if dwPlayerTracker[i].get('userID') == nodeID:
            dwPlayerTracker[i]['cmd'] = 'ask_bsf'

    return msg


def sell_func(nodeID, price_list, choice=0, value='0'):
    global dwCashDb, dwInventoryDb, dwPlayerTracker
    msg = ''

    # get the inventory for the user
    for i in range(0, len(dwInventoryDb)):
        if dwInventoryDb[i].get('userID') == nodeID:
            inventory = dwInventoryDb[i].get('inventory')
    amount = check_inv(nodeID)
    
    # get the cash for the user
    for i in range(0, len(dwCashDb)):
        if dwCashDb[i].get('userID') == nodeID:
            cash = dwCashDb[i].get('cash')

    # get the drug choice and amount to sell
    drug_choice = choice
    sell_amount = value

    try:
        if sell_amount == 'm':
            sell_amount = amount[drug_choice - 1]
        else:
            sell_amount = int(sell_amount)
            if sell_amount not in range(1, 101):
                msg = f"You can only sell between 1 and 100"
                return msg
    except ValueError:
        msg = f"Enter qty or m for max"
        return msg
    
    # check if the user has any of the drug they are trying to sell
    if choice == 0:
        msg = "Enter b or s and the drug number and qty you want to buy or sell. ex: b,1,10 buys 10 of drug 1"
        return msg
    else:
        if drug_choice in range(1, len(my_drugs) + 1) and amount[drug_choice - 1] > 0:
            drug_choice = drug_choice - 1
            msg = my_drugs[drug_choice].name + ": you have " + str(amount[drug_choice]) +\
                " The going price is: $" + str(price_list[drug_choice])
            # check if the user has enough of the drug to sell
            if sell_amount <= amount[drug_choice]:
                amount[drug_choice] -= sell_amount
                cash += sell_amount * price_list[drug_choice]
                inventory -= sell_amount
                msg += " You sold " + str(sell_amount) + " " + my_drugs[drug_choice].name + ' for $' +\
                    str(sell_amount * price_list[drug_choice]) + ' total cash: $' + str(cash)
            else:
                msg = "You don\'t have that much"
                return msg
        else:
            msg = 'You don\'t have any ' + my_drugs[drug_choice].name
            return msg

    # update the cash_db and inventory_db values
    for i in range(0, len(dwCashDb)):
        if dwCashDb[i].get('userID') == nodeID:
            dwCashDb[i]['cash'] = cash
    for i in range(0, len(dwInventoryDb)):
        if dwInventoryDb[i].get('userID') == nodeID:
            dwInventoryDb[i]['inventory'] = inventory
            dwInventoryDb[i]['amount'] = amount
    # save the last command as ask_bsf
    for i in range(0, len(dwPlayerTracker)):
        if dwPlayerTracker[i].get('userID') == nodeID:
            dwPlayerTracker[i]['cmd'] = 'ask_bsf'
    
    return msg


def get_location_table(nodeID, choice=0):
    global dwLocationDb
    # get the location for the user
    for i in range(0, len(dwLocationDb)):
        if dwLocationDb[i].get('userID') == nodeID:
            loc = dwLocationDb[i].get('location')
            
    # list the lcaitons and their index in two columns
    loc_table_string = ''
    for i in range(len(loc)):
            loc_table_string += str(i+1) + '. ' + loc[i] + '  ' 
    loc_table_string += f'Where do you want to go?#'
    return loc_table_string


def endGameDw(nodeID):
    global dwCashDb, dwInventoryDb, dwLocationDb, dwGameDayDb, dwHighScore
    msg = ''
    dwHighScore = getHighScoreDw()
    # Confirm the cash for the user
    for i in range(0, len(dwCashDb)):
        if dwCashDb[i].get('userID') == nodeID:
            cash = dwCashDb[i].get('cash')
    logger.debug("System: DopeWars: Game Over for user: " + str(nodeID) + " with cash: " + str(cash))

    # remove the player from the game databases
    for i in range(0, len(dwCashDb)):
        if dwCashDb[i].get('userID') == nodeID:
            dwCashDb.pop(i)
    for i in range(0, len(dwInventoryDb)):
        if dwInventoryDb[i].get('userID') == nodeID:
            dwInventoryDb.pop(i)
    for i in range(0, len(dwLocationDb)):
        if dwLocationDb[i].get('userID') == nodeID:
            dwLocationDb.pop(i)
    for i in range(0, len(dwGameDayDb)):
        if dwGameDayDb[i].get('userID') == nodeID:
            dwGameDayDb.pop(i)
    for i in range(0, len(dwPlayerTracker)):
        if dwPlayerTracker[i].get('userID') == nodeID:
            dwPlayerTracker.pop(i)

    # checks if the player's score is higher than the high score and writes a new high score if it is
    if cash > dwHighScore.get('cash'):
        dwHighScore = ({'userID': nodeID, 'cash': round(cash, 2)})
        with open('dopewar_hs.pkl', 'wb') as file:
            pickle.dump(dwHighScore, file)
        msg = "You finished with $" + str(cash) + " and beat the high score!🎉💰"
        return msg
    if cash > starting_cash:
        msg = 'You made money! 💵 Up ' + str((cash/starting_cash).__round__()) + 'x! Well done.'
        return msg
    if cash == starting_cash:
        msg = 'You broke even... hope you at least had fun 💉💊'
        return msg
    if cash < starting_cash:
        msg = "You lost money, better go get a real job.💸"

    logger.debug("System: DopeWars: Game Over for user: " + str(nodeID) + " with cash: " + str(cash))
    
    return msg

def getHighScoreDw():
    global dwHighScore
    # Load high score table
    try:
        with open('dopewar_hs.pkl', 'rb') as file:
            dwHighScore = pickle.load(file)
    except FileNotFoundError:
        logger.debug("System: DopeWars: No high score table found")
        # high score pickle file is a touple of the nodeID and the high score
        dwHighScore = ({"userID": 4258675309, "cash": 100})
        # write a new high score file if one is not found
        with open('dopewar_hs.pkl', 'wb') as file:
            pickle.dump(dwHighScore, file)
    return dwHighScore

def render_game_screen(userID, day_play, total_day, loc_choice, event_number, price_list, cash_stolen):
    global dwCashDb, dwInventoryDb, dwLocationDb
    msg = ''
    # get the location for the user
    for i in range(0, len(dwLocationDb)):
        if dwLocationDb[i].get('userID') == userID:
            loc = dwLocationDb[i].get('location')
    
    
    if event_number != -1:
        msg += event_list[event_number].text + f"\n"
    if event_number == -1 and cash_stolen != 0 and cash_stolen != 'conf':
        msg += "🚔Officer Leroy stopped you and took $" + str(cash_stolen) + " from you." + f"\n"
    if event_number == -1 and cash_stolen == 'conf':
        msg += "🚔Officer Leroy stopped you and took all of your drugs." + f"\n"

    # get the inventory for the user
    for i in range(0, len(dwInventoryDb)):
        if dwInventoryDb[i].get('userID') == userID:
            inventory = dwInventoryDb[i].get('inventory') 

    amount = check_inv(userID)
    # get the cash for the user
    for i in range(0, len(dwCashDb)):
        if dwCashDb[i].get('userID') == userID:
            cash = dwCashDb[i].get('cash')

    msg += "Location: " + loc[int(loc_choice) - 1] + ", Day:" + str(day_play) + '/' + str(total_day) + ", $" + str(cash) + " Backpack: " + str(inventory) + "/100" + f"\n"
    for i, drug in enumerate(my_drugs, 1):
        qty = amount[i-1]
        msg += f'#{str(i)}.{drug.name}/${price_list[i-1]}({qty})    '

    return msg


def dopeWarGameDay(nodeID, day_play, total_day):
    global dwCashDb, dwLocationDb, dwInventoryDb
    cash_stolen = 0

    # roll for the event of the day
    event_number = generate_event()

    # get the location for the user
    for i in range(0, len(dwLocationDb)):
        if dwLocationDb[i].get('userID') == nodeID:
            loc = dwLocationDb[i].get('location')
            loc_choice = dwLocationDb[i].get('loc_choice')

    # rolls to see if the officer event happens
    # odds are (1 - event chance) * (officer chance)
    # currently (1 - 0.35) * (0.20) = 13%
    # chance is approximate, not sure how randint handles endpoints, close enough for my purposes
    if event_number == -1 and random.randint(0, 100) > 80:
        cash_stolen = officer(nodeID)

    price_list = price_change(event_number)

    # set the price_list for the user
    for i in range(0, len(dwInventoryDb)):
        if dwInventoryDb[i].get('userID') == nodeID:
            dwInventoryDb[i]['priceList'] = price_list

    check_inv(nodeID)

    # main game display print
    msg = render_game_screen(nodeID, day_play, total_day, loc_choice, event_number, price_list, cash_stolen)
    
    return msg

def playDopeWars(nodeID, cmd):
    global dwGameDayDb, dwPlayerTracker, dwCashDb, dwInventoryDb, dwLocationDb, dwHighScore
    
    inGame = False
    msg = '' 

    # check if the player is currently playing the game
    for i in range(0, len(dwGameDayDb)):
        if dwGameDayDb[i].get('userID') == nodeID:
            inGame = True

    if not inGame:
        # initalize player in the database
        loc = generatelocations()
        dwInventoryDb.append({'userID': nodeID, 'inventory': 0, 'priceList': []})
        dwCashDb.append({'userID': nodeID, 'cash': starting_cash})
        dwLocationDb.append({'userID': nodeID, 'location': loc, 'loc_choice': 0})
        dwGameDayDb.append({'userID': nodeID, 'day': 0})
        dwPlayerTracker.append({'userID': nodeID, 'last_played': time.time(), 'cmd': 'start'})
        logger.debug("System: DopeWars: New player: " + str(nodeID))
    
    # get the day for the user
    for i in range(0, len(dwGameDayDb)):
        if dwGameDayDb[i].get('userID') == nodeID:
            game_day = dwGameDayDb[i].get('day')

    # get the player's last command
    for i in range(0, len(dwPlayerTracker)):
        if dwPlayerTracker[i].get('userID') == nodeID:
            last_cmd = dwPlayerTracker[i].get('cmd')

    # get the price_list for the user
    for i in range(0, len(dwInventoryDb)):
        if dwInventoryDb[i].get('userID') == nodeID:
            price_list = dwInventoryDb[i].get('priceList')

    # get the location for the user
    for i in range(0, len(dwLocationDb)):
        if dwLocationDb[i].get('userID') == nodeID:
            loc_choice = dwLocationDb[i].get('loc_choice')
    
    # Pick Starting City
    if last_cmd == 'start':
        # print the location table 
        msg = get_location_table(nodeID)

        # set the player's last command to location to start the game
        for i in range(0, len(dwPlayerTracker)):
            if dwPlayerTracker[i].get('userID') == nodeID:
                dwPlayerTracker[i]['cmd'] = 'location'

    if last_cmd == 'ask_bsf':
        msg = 'example Buy: b,Drug,Qty or Sell s,1,10. Fly: f. Price list: p or end'
        menu_choice = cmd.lower()
        if ',' in menu_choice:
            #split the choice into a letter and a number for the buy/sell functions
            menu_choice = menu_choice.split(',')
            try:
                if int(menu_choice[1]) not in range(1, 8):
                    raise ValueError
                else:
                    menu_choice[1] = int(menu_choice[1])
                if menu_choice[0] not in ['b', 's']:
                    raise ValueError
                if menu_choice[2] != 'm':
                    if int(menu_choice[2]) not in range(1, 101):
                        raise ValueError
                    else:
                        menu_choice[2] = int(menu_choice[2])
                
            except ValueError:
                msg = 'a value was bad, example dopeware Buy or Sell b,1,10 or s,1,m'
                return msg

            if menu_choice[0] == 'b':
                # set last command to ask_bsf and buy
                for i in range(0, len(dwPlayerTracker)):
                    if dwPlayerTracker[i].get('userID') == nodeID:
                        dwPlayerTracker[i]['cmd'] = 'ask_bsf'
                msg = buy_func(nodeID, price_list, menu_choice[1], menu_choice[2])
                return msg

            if menu_choice[0] == 's':
                # set last command to ask_bsf and sell
                for i in range(0, len(dwPlayerTracker)):
                    if dwPlayerTracker[i].get('userID') == nodeID:
                        dwPlayerTracker[i]['cmd'] = 'ask_bsf'
                msg = sell_func(nodeID, price_list, menu_choice[1], menu_choice[2])
                return msg
        elif 's' in menu_choice:
            msg = ''
            # sell everything we have in backpack
            for i in range(0, len(dwInventoryDb)):
                if dwInventoryDb[i].get('userID') == nodeID:
                    inventory = dwInventoryDb[i].get('inventory')
            if inventory == 0:
                msg = "You don't have anything to sell"
            else:
                for i in range(1, (len(my_drugs) +1)):
                    sell =  sell_func(nodeID, price_list, i, 'm')
                    # ignore starts with "You don't have any"
                    if not sell.startswith("You don't have any"):
                        msg += sell + '\n'
            return msg
        elif 'f' in menu_choice:
                # set last command to location
                for i in range(0, len(dwPlayerTracker)):
                    if dwPlayerTracker[i].get('userID') == nodeID:
                        dwPlayerTracker[i]['cmd'] = 'location'
                last_cmd = 'location'

        elif 'p' in menu_choice:
                # render_game_screen
                msg = render_game_screen(nodeID, game_day, total_days, loc_choice, -1, price_list, 0)
                return msg
        elif 'end' in menu_choice:
                msg = endGameDw(nodeID)
                return msg
        else:
            msg = 'example Buy: b,Drug,Qty or Sell s,1,10. Fly: f. Price list: p or end'
            return msg
        
    # Buy
    if last_cmd == 'buy':
        # ned to collect which drug # and qty to buy
        msg = buy_func(nodeID, price_list)
        return msg

    # Sell
    if last_cmd == 'sell':
        msg = sell_func(nodeID, price_list)
        return msg
        
        # Pick Location, and display main game screen
    if last_cmd == 'location':
        # validate the location choice
        try:
            loc_choice = int(cmd)
            if loc_choice not in range(1, 6):
                raise ValueError
        except ValueError:
            loc_choice = random.randint(1, 6)

        # set the player's location choice
        for i in range(0, len(dwLocationDb)):
            if dwLocationDb[i].get('userID') == nodeID:
                dwLocationDb[i]['loc_choice'] = loc_choice
        
        # set the player's last command
        for i in range(0, len(dwPlayerTracker)):
            if dwPlayerTracker[i].get('userID') == nodeID:
                dwPlayerTracker[i]['cmd'] = 'display_main'
        
        # increment the game_day
        game_day += 1
        for i in range(0, len(dwGameDayDb)):
            if dwGameDayDb[i].get('userID') == nodeID:
                dwGameDayDb[i]['day'] = game_day
        
        # update the player's last played time
        for i in range(0, len(dwPlayerTracker)):
            if dwPlayerTracker[i].get('userID') == nodeID:
                dwPlayerTracker[i]['last_played'] = time.time()

        last_cmd = 'display_main'
    
    # Display Main Game Screen and ask for buy, sell, or fly
    if last_cmd == 'display_main':
        msg = dopeWarGameDay(nodeID, game_day, total_days)
        msg += f"\nBuy, Sell, Fly? Price list?"
        # set the player's last command
        for i in range(0, len(dwPlayerTracker)):
            if dwPlayerTracker[i].get('userID') == nodeID:
                dwPlayerTracker[i]['cmd'] = 'ask_bsf'
    
    # Game end
    if game_day == total_days + 1:
        msg = endGameDw(nodeID)
    
    return msg
