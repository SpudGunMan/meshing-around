# Port of https://github.com/tigerpointe/Lemonade-Stand/blob/main/lemonade.py MIT License Copyright (c) 2023 TigerPointe Software, LLC
# Adapted for Meshtastic mesh-bot by K7MHI Kelly Keeton 2024

from collections import OrderedDict   # ordered dictionaries
from random import randrange, uniform # random numbers
from types import SimpleNamespace     # namespaces support
import pickle                         # pickle file support
import time                           # time functions
from modules.log import logger        # mesh-bot logging
from modules.system import lemonadeTracker # player tracking
import locale # culture specific locale
import math   # math functions
import re     # regular expressions

# Set all of the locale category elements as default
# ex. print(locale.currency(12345.67, grouping=True))
locale.setlocale(locale.LC_ALL, '')
lemon_starting_cash = 30.00
lemon_total_weeks = 7

lemonadeCups = [{'nodeID': 0, 'cost': 2.50, 'count': 25, 'min': 0.99, 'unit': 0.00}]
lemonadeLemons = [{'nodeID': 0, 'cost': 4.00, 'count': 8, 'min': 2.00, 'unit': 0.00}]
lemonadeSugar = [{'nodeID': 0, 'cost': 3.00, 'count': 15, 'min': 1.50, 'unit': 0.00}]
lemonadeWeeks = [{'nodeID': 0, 'current': 1, 'total': lemon_total_weeks, 'sales': 99, 'potential': 0, 'unit': 0.00, 'price': 0.00, 'total_sales': 0}]
lemonadeScore = [{'nodeID': 0, 'value': 0.00, 'total': 0.00}]

def get_sales_amount(potential, unit, price):
    """Gets the sales amount.
    Multiply the potential sales by a ratio of unit cost to actual price; the
    exponent results in the values falling along a curve, rather than along a
    straight line, resulting in more realistic sales values at each price.
    Parameters
    potential : Potential sales
    unit      : Unit cost
    price     : Actual price
    """
    return math.floor(potential * (unit / (price ** 1.5)))

def getHighScoreLemon():
    high_score = {"userID": 0, "cash": 0, "success": 0}
    # Load high score table
    try:
        with open('data/lemonstand.pkl', 'rb') as file:
            high_score = pickle.load(file)
    except FileNotFoundError:
        logger.debug("System: Lemonade: No high score table found")
        # write a new high score file if one is not found
        with open('data/lemonstand.pkl', 'wb') as file:
            pickle.dump(high_score, file)
    return high_score

def playLemonstand(nodeID, message, celsius=False, newgame=False):
    global lemonadeTracker, lemonadeCups, lemonadeLemons, lemonadeSugar, lemonadeWeeks, lemonadeScore
    msg = ""
    potential = 0
    unit = 0.0
    price = 0.0
    total_sales = 0
    lemonsLastCmd = ''

    high_score = getHighScoreLemon()

    def saveValues(nodeID, inventory, cups, lemons, sugar, weeks, score):
        # save playerDB values
        for i in range(len(lemonadeTracker)):
            if lemonadeTracker[i]['nodeID'] == nodeID:
                lemonadeTracker[i]['cups'] = inventory.cups
                lemonadeTracker[i]['lemons'] = inventory.lemons
                lemonadeTracker[i]['sugar'] = inventory.sugar
                lemonadeTracker[i]['cash'] = inventory.cash
                lemonadeTracker[i]['start'] = inventory.start
        for i in range(len(lemonadeCups)):
            if lemonadeCups[i]['nodeID'] == nodeID:
                lemonadeCups[i]['cost'] = cups.cost
                lemonadeCups[i]['unit'] = cups.unit
        for i in range(len(lemonadeLemons)):
            if lemonadeLemons[i]['nodeID'] == nodeID:
                lemonadeLemons[i]['cost'] = lemons.cost
                lemonadeLemons[i]['unit'] = lemons.unit
        for i in range(len(lemonadeSugar)):
            if lemonadeSugar[i]['nodeID'] == nodeID:
                lemonadeSugar[i]['cost'] = sugar.cost
                lemonadeSugar[i]['unit'] = sugar.unit
        for i in range(len(lemonadeWeeks)):
            if lemonadeWeeks[i]['nodeID'] == nodeID:
                lemonadeWeeks[i]['current'] = weeks.current
                lemonadeWeeks[i]['total'] = weeks.total
                lemonadeWeeks[i]['sales'] = weeks.sales
                lemonadeWeeks[i]['potential'] = potential
                lemonadeWeeks[i]['unit'] = unit
                lemonadeWeeks[i]['price'] = price
                lemonadeWeeks[i]['total_sales'] = weeks.total_sales
        for i in range(len(lemonadeScore)):
            if lemonadeScore[i]['nodeID'] == nodeID:
                lemonadeScore[i]['value'] = score.value
                lemonadeScore[i]['total'] = score.total

    title="LemonStand🍋"
    # Define the temperature unit symbols
    fahrenheit_unit = "ºF"
    celsius_unit    = "ºC"

    # Inventory data (contains the item levels)
    inventoryd = {
        'cups'   : 0,
        'lemons' : 0,
        'sugar'  : 0,
        'cash'   : lemon_starting_cash,
        'start'  : lemon_starting_cash
    }
    inventory = SimpleNamespace(**inventoryd)

    # Cups data (includes a calculated cost per unit)
    cupsd = {
        'cost'  : 2.50, # current price
        'count' : 25,   # servings per box
        'min'   : 0.99, # minimum price
        'unit'  : 0.00  # unit price
    }
    cups = SimpleNamespace(**cupsd)
    cups.unit = round(cups.cost / cups.count, 2)

    # Lemons data (includes a calculated cost per unit)
    lemonsd = {
        'cost'  : 4.00, # current price
        'count' : 8,    # servings per bag
        'min'   : 2.00, # minimum price
        'unit'  : 0.00  # unit price
    }
    lemons = SimpleNamespace(**lemonsd)
    lemons.unit = round(lemons.cost / lemons.count, 2)

    # Sugar data (includes a calculated cost per unit)
    sugard = {
        'cost'  : 3.00, # current price
        'count' : 15,   # servings per bag
        'min'   : 1.50, # minimum price
        'unit'  : 0.00  # unit price
    }
    sugar = SimpleNamespace(**sugard)
    sugar.unit  = round(sugar.cost / sugar.count, 2)

    # Weeks data (measures the session duration)
    weeksd = {
        'current' : 1,   # start with the 1st week
        'total'   : 12,  # span the 12 weeks of Summer
        'sales'   : 99,  # 99 maximum sales per week
        'total_sales' : 0, # total sales
        'summary' : []   # empty array
    }
    weeks = SimpleNamespace(**weeksd)

    # Forecast data (includes percentage values, UTF8 glyphs and display names)
    forecastd = OrderedDict()
    forecastd['sunny']  = [1.00, 0x2600, "Sunny"]
    forecastd['partly'] = [0.90, 0x26C5, "Partly Sunny"]
    forecastd['cloudy'] = [0.70, 0x2601, "Mostly Cloudy"]
    forecastd['rainy']  = [0.40, 0x2602, "Rainy"]
    forecastd['stormy'] = [0.10, 0x26C8, "Stormy"]

    # Temperature data (uses Fahrenheit as the percentage values)
    temperatured = {
        'min'      : 69,
        'max'      : 100,
        'units'    : fahrenheit_unit,
        'forecast' : None,
        'value'    : None
    }
    temperature = SimpleNamespace(**temperatured)

    # Score data (based on actual vs. maximum net sales)
    scored = {
        'value' : 0.00,
        'total' : 0.00
    }
    score = SimpleNamespace(**scored)

    # Check for Celsius
    if (celsius):
        temperature.units = celsius_unit

    # load playerDB values
    for i in range(len(lemonadeTracker)):
        if lemonadeTracker[i]['nodeID'] == nodeID:
            inventory.cups = lemonadeTracker[i]['cups']
            inventory.lemons = lemonadeTracker[i]['lemons']
            inventory.sugar = lemonadeTracker[i]['sugar']
            inventory.cash = lemonadeTracker[i]['cash']
            inventory.start = lemonadeTracker[i]['start']
            lemonsLastCmd = lemonadeTracker[i]['cmd']
    for i in range(len(lemonadeCups)):
        if lemonadeCups[i]['nodeID'] == nodeID:
            cups.cost = lemonadeCups[i]['cost']
            cups.unit = lemonadeCups[i]['unit']
    for i in range(len(lemonadeLemons)):
        if lemonadeLemons[i]['nodeID'] == nodeID:
            lemons.cost = lemonadeLemons[i]['cost']
            lemons.unit = lemonadeLemons[i]['unit']
    for i in range(len(lemonadeSugar)):
        if lemonadeSugar[i]['nodeID'] == nodeID:
            sugar.cost = lemonadeSugar[i]['cost']
            sugar.unit = lemonadeSugar[i]['unit']
    for i in range(len(lemonadeWeeks)):
        if lemonadeWeeks[i]['nodeID'] == nodeID:
            weeks.current = lemonadeWeeks[i]['current']
            weeks.total = lemonadeWeeks[i]['total']
            weeks.sales = lemonadeWeeks[i]['sales']
            potential = lemonadeWeeks[i]['potential']
            unit = lemonadeWeeks[i]['unit']
            price = lemonadeWeeks[i]['price']
            weeks.total_sales = lemonadeWeeks[i]['total_sales']
    for i in range(len(lemonadeScore)):
        if lemonadeScore[i]['nodeID'] == nodeID:
            score.value = lemonadeScore[i]['value']
            score.total = lemonadeScore[i]['total']
    if (newgame):
        # reset the game values
        inventory.cups = 0
        inventory.lemons = 0
        inventory.sugar = 0
        inventory.cash = lemon_starting_cash
        inventory.start = lemon_starting_cash
        cups.cost = 2.50
        cups.unit = round(cups.cost / cups.count, 2)
        lemons.cost = 4.00
        lemons.unit = round(lemons.cost / lemons.count, 2)
        sugar.cost = 3.00
        sugar.unit = round(sugar.cost / sugar.count, 2)
        weeks.current = 1
        weeks.total_sales = 0
        weeks.summary = []
        score.value = 0.00
        score.total = 0.00
        lemonsLastCmd = "cups"
        # set the last command to new in the inventory db
        for i in range(len(lemonadeTracker)):
            if lemonadeTracker[i]['nodeID'] == nodeID:
                lemonadeTracker[i]['cmd'] = "cups"
                lemonadeTracker[i]['last_played'] = time.time()
        saveValues(nodeID, inventory, cups, lemons, sugar, weeks, score)
    # Start the main loop
    if (weeks.current <= weeks.total):
        if newgame or "new" in lemonsLastCmd:
            logger.debug("System: Lemonade: New Game: " + str(nodeID))
            # Create a new display buffer for the text messages
            buffer= ""
    
            # the current week number
            buffer += title + "Week #" + str(weeks.current) + "of" + str(weeks.total)

            # Generate a random weather forecast and temperature and display
            temperature.forecast = randrange(0, len(forecastd))
            temperature.value = randrange(temperature.min, temperature.max)
            formatted = str(temperature.value)
            if (temperature.units == celsius_unit):
                formatted = str(round(((temperature.value - 32) * (5/9))))
            glyph = chr(forecastd[list(forecastd)[temperature.forecast]][1])
            buffer += ". " + \
                        formatted + temperature.units + " " + \
                        forecastd[list(forecastd)[temperature.forecast]][2] + \
                        " " + glyph + f"\n"

            # Calculate the potential sales as a percentage of the maximum value
            # (lower temperature = fewer sales, severe weather = fewer sales)
            forecast  = forecastd[list(forecastd)[temperature.forecast]][0]
            potential = math.floor(weeks.sales * \
                                (temperature.value / 100) * \
                                forecast)

            # Update the cups cost
            cups.cost = cups.cost + round(uniform(-1.50, 1.50), 2)
            if (cups.cost < cups.min):
                cups.cost = cups.min
            cups.unit = round(cups.cost / cups.count, 2)

            # Update the lemons cost
            lemons.cost = lemons.cost + round(uniform(-1.50, 1.50), 2)
            if (lemons.cost < lemons.min):
                lemons.cost = lemons.min
            lemons.unit = round(lemons.cost / lemons.count, 2)

            # Update the sugar cost
            sugar.cost = sugar.cost + round(uniform(-1.50, 1.50), 2)
            if (sugar.cost < sugar.min):
                sugar.cost = sugar.min
            sugar.unit = round(sugar.cost / sugar.count, 2)

            # Calculate the unit cost and display the estimated sales from the forecast potential
            unit = max(0.01, min(cups.unit + lemons.unit + sugar.unit, 4.0))  # limit the unit cost between $0.01 and $4.00
            buffer += f"\nSupplyCost" + locale.currency(round(unit, 2), grouping=True) + " a cup."
            buffer += f"\nSales Potential:" + str(potential) + " cups."

            # Display the current inventory
            buffer += f"\nInventory:"
            buffer += "🥤:" + str(inventory.cups)
            buffer += "🍋:" + str(inventory.lemons)
            buffer += "🍚:" + str(inventory.sugar)

            # Display the updated item prices
            buffer += f"\nPrices:\n"
            buffer += f"\n🥤:" + locale.currency(round(cups.cost, 2), grouping=True) + " 📦 of " + str(cups.count) + "."
            buffer += f"\n🍋:" + locale.currency(round(lemons.cost, 2), grouping=True) + " 🧺 of " + str(lemons.count) + "."
            buffer += f"\n🍚:" + locale.currency(round(sugar.cost, 2), grouping=True) + " bag for " + str(sugar.count) + "🥤."
            # Display the current cash
            gainloss   = inventory.cash - inventory.start
            buffer += f"\n💵:" + locale.currency(round(inventory.cash, 2), grouping=True)
            
            
            # if the player is in the red
            pnl = locale.currency(round(gainloss, 2), grouping=True)
            if "0.00" not in pnl:
                if pnl.startswith("-"):
                    buffer += "📊P&L📉" + pnl
                else:
                    buffer += "📊P&L📈" + pnl

            buffer += f"\n🥤 to buy?\nHave {inventory.cups} Cost {locale.currency(cups.cost, grouping=True)} a 📦 of {str(cups.count)}"
            saveValues(nodeID, inventory, cups, lemons, sugar, weeks, score)
            return buffer
        
        if "cups" in lemonsLastCmd and not newgame:
            # Read the number of cup boxes to purchase
            newcups = -1
            if "n" in message.lower():
                message = "0"
            try:
                newcups = int(message)
                if (newcups > 0):
                    cost = round(newcups * cups.cost, 2)
                    if (cost > inventory.cash):
                        return "You do not have enough 💵."
                    inventory.cups += (newcups * cups.count)
                    inventory.cash -= cost
                    msg = "Purchased " + str(newcups) + " 📦 "
                    msg += str(inventory.cups) + " 🥤  in inventory. "  + locale.currency(round(inventory.cash, 2), grouping=True) + f" remaining"
                else:
                    msg =  "No 🥤 were purchased"
            except Exception as e:
                return "invalid input, enter the number of 🥤 to purchase or (N)one"
                
            msg += f"\n 🍋 to buy?\nHave {inventory.lemons}🥤 of 🍋 Cost {locale.currency(lemons.cost, grouping=True)} a 🧺 for {str(lemons.count)}🥤"
            # set the last command to lemons in the inventory db
            for i in range(len(lemonadeTracker)):
                if lemonadeTracker[i]['nodeID'] == nodeID:
                    lemonadeTracker[i]['cmd'] = "lemons"
            saveValues(nodeID, inventory, cups, lemons, sugar, weeks, score)
            return msg
                

        if "lemons" in lemonsLastCmd and not newgame:
            # Read the number of lemon bags to purchase
            newlemons = -1
            if "n" in message.lower():
                message = "0"
            try:
                newlemons = int(message)
                if (newlemons > 0):
                    cost = round(newlemons * lemons.cost, 2)
                    if (cost > inventory.cash):
                        return "You do not have enough cash."
                    inventory.lemons += (newlemons * lemons.count)
                    inventory.cash   -= cost
                    msg = "Purchased " + str(newlemons) + " 🧺 "
                    msg += str(inventory.lemons) + " 🍋  in inventory. "  + locale.currency(inventory.cash, grouping=True) + f" remaining"
                else:
                    msg =  "No 🍋 were purchased"
            except Exception as e:
                newlemons = -1
                return "⛔️invalid input, enter the number of 🍋 to purchase"
                
            msg += f"\n 🍚 to buy?\nYou have {inventory.sugar}🥤 of 🍚, Cost {locale.currency(sugar.cost, grouping=True)} a bag for {str(sugar.count)}🥤"
            # set the last command to sugar in the inventory db
            for i in range(len(lemonadeTracker)):
                if lemonadeTracker[i]['nodeID'] == nodeID:
                    lemonadeTracker[i]['cmd'] = "sugar"
            saveValues(nodeID, inventory, cups, lemons, sugar, weeks, score)
            return msg

        if "sugar" in lemonsLastCmd and not newgame:
            # Read the number of sugar bags to purchase
            newsugar = -1
            if "n" in message.lower():
                message = "0"
            try:
                newsugar = int(message)
                if (newsugar > 0):
                    cost = round(newsugar * sugar.cost, 2)
                    if (cost > inventory.cash):
                        return "You do not have enough cash."
                    inventory.sugar += (newsugar * sugar.count)
                    inventory.cash  -= cost
                    msg = " Purchased " + str(newsugar) + " bag(s) of 🍚 for " + locale.currency(cost, grouping=True)
                    msg += ". " + str(inventory.sugar) + f"🥤🍚 in inventory."
                else:
                    msg =  "No additional 🍚 was purchased"
            except Exception as e:
                return "⛔️invalid input, enter the number of 🍚 bags to purchase"

            msg += f"Cost of goods is {locale.currency(round(unit, 2), grouping=True)}"
            msg += f"per 🥤 {locale.currency(round(inventory.cash, 2), grouping=True)} 💵 remaining."
            msg += f"\nPrice to Sell? or (G)rocery to buy more 🥤🍋🍚"

            # set the last command to price in the inventory db
            for i in range(len(lemonadeTracker)):
                if lemonadeTracker[i]['nodeID'] == nodeID:
                    lemonadeTracker[i]['cmd'] = "price"
            saveValues(nodeID, inventory, cups, lemons, sugar, weeks, score)
            return msg
    
        if "price" in lemonsLastCmd and not newgame:
            # set the last command to sales in the inventory db
            for i in range(len(lemonadeTracker)):
                if lemonadeTracker[i]['nodeID'] == nodeID:
                    lemonadeTracker[i]['cmd'] = "sales"
                    if "g" in message.lower():
                        lemonadeTracker[i]['cmd'] = "cups"
                        msg = f"#of🥤\nto buy? Have {inventory.cups} Cost {locale.currency(cups.cost, grouping=True)} a 📦 of {str(cups.count)}"
                        return msg
                    else:
                        lemonsLastCmd = "sales"
            
            # Read the actual price
            price = 0.00
            while (price <= 0.00):
                try:
                    raw   = message
                    price = float(re.sub("[^0-9.-]", "", raw) or 0.00)
                    if (price <= 0.00):
                        return "The price must be greater than zero."
                except Exception as e:
                    price = 0.00
                    lemonsLastCmd = "price"
                    return "⛔️Invalid input, enter the price of the lemonade per 🥤"
            
            # this isnt sent to the user, not needed
            #msg = "  Setting the price at " + locale.currency(price, grouping=True)
            saveValues(nodeID, inventory, cups, lemons, sugar, weeks, score)
        

        if "sales" in lemonsLastCmd and not newgame:
            # Calculate the weekly sales based on price and lowest inventory level
            # (higher markup price = fewer sales, limited by the inventory on-hand)
            sales  = get_sales_amount(potential, unit, price)
            sales  = min(potential, sales, \
                        inventory.cups, inventory.lemons, \
                        inventory.sugar) # "min" returns lowest value
            margin = price - unit
            gross  = sales * price
            net    = sales * margin
            
            # Add a new row to the summary
            weeks.summary.append({ 'sales' : sales, 'price' : price })
                    
            # Update the inventory levels to reflect consumption
            inventory.cups   = inventory.cups   - sales
            inventory.lemons = inventory.lemons - sales
            inventory.sugar  = inventory.sugar  - sales
            inventory.cash   = inventory.cash   + gross
            gainloss= inventory.cash - inventory.start
    
            # Display the calculated sales information
            msg = "Results Week📊#" + str(weeks.current) + "of" + str(weeks.total)
            msg += " Cost/Price:" + locale.currency(unit, grouping=True) + "/" + locale.currency(price, grouping=True)
            msg += " P.Margin:" + locale.currency(margin, grouping=True)
            msg += " T.Sales:" + str(sales) + "@" + locale.currency(price, grouping=True)
            msg += " G.Profit: " + locale.currency(gross, grouping=True)
            msg += " N.Profit:" + locale.currency(net, grouping=True)

            # Display the updated inventory levels
            msg += f"\nRemaining"
            msg += " 🥤:" + str(inventory.cups)
            msg += " 🍋:" + str(inventory.lemons)
            msg += " 🍚:" + str(inventory.sugar)
            msg += " 💵:" + locale.currency(inventory.cash, grouping=True)
            # Display the gain/loss
            pnl = locale.currency(gainloss, grouping=True)
            if "0.00" not in pnl:
                if pnl.startswith("-"):
                    msg += "📊P&L📉" + pnl
                else:
                    msg += "📊P&L📈" + pnl
    
            # Display the weekly sales summary
            pad_week = len(str(weeks.total))
            pad_sale = len(str(weeks.sales))
            total = 0
            msg += f"\nWeekly📊"
            for i in range(len(weeks.summary)):
                msg += "#" + str(weeks.current).rjust(pad_week) + ".  " + str(weeks.summary[i]['sales']).rjust(pad_sale) + \
                    " sold x " + locale.currency(weeks.summary[i]['price'], grouping=True) + "ea. "
                total = total + weeks.summary[i]['sales']

            # Update the total sales for the game
            weeks.total_sales += total
            
            # Loop through a range of prices to find the highest net profit
            maxsales = 0
            maxprice = 0.00
            maxgross = 0.00
            maxnet   = 0.00
            minnet   = net
            for i in range(25, 2500, 25):
                price  = i / 100 # range uses integers, not currency (floats)
                sales  = get_sales_amount(potential, unit, price)
                margin = price - unit
                gross  = sales * price
                net    = sales * margin
                if (sales  >  0) and \
                    (sales <= potential) and \
                    (unit  <= price):
                        if (net > maxnet):
                            maxsales = sales
                            maxprice = price
                            maxgross = gross
                            maxnet   = net
            if (maxnet > minnet):
                msg += "Sales could have been:"
                msg += "  " + str(maxsales) + " sold x " + locale.currency(maxprice, grouping=True) + "ea. @" + \
                    locale.currency(maxgross, grouping=True) + " for a net profit of " + locale.currency(maxnet, grouping=True)
                if (inventory.cups <= 0):
                    msg += " You ran out of cups.🥤"
                if (inventory.lemons <= 0):
                    msg += " You ran out of lemons.🍋"
                if (inventory.sugar <= 0):
                    msg += " You ran out of sugar.🍚"
            else:
                msg += f"\nCongratulations 🍋🍋 your sales were perfect!🎉"
            
            # Increment the score counters
            score.value = score.value + minnet
            score.total = score.total + maxnet


            # Increment the week number
            if (weeks.current == weeks.total):
                # end of the game
                success = round((score.value / score.total) * 100)
                msg += f"\nYou've made " + locale.currency(score.value, grouping=True) + " out of a possible " + \
                    locale.currency(score.total, grouping=True) + " for a score of " + str(success) + "% "
                msg += f"\nYou've sold " + str(weeks.total_sales) + " total 🥤🍋"

                # check for high score
                high_score = getHighScoreLemon()
                if (inventory.cash > int(high_score['cash'])):
                    msg += f"\nCongratulations! You've set a new high score!🎉💰🍋"
                    high_score['cash'] = inventory.cash
                    high_score['success'] = success
                    high_score['userID'] = nodeID
                    with open('data/lemonstand.pkl', 'wb') as file:
                        pickle.dump(high_score, file)

            else:
                # keep playing
                
                weeks.current = weeks.current + 1

                msg += f"\nPlay another week🥤? or (E)nd Game"
                # set the last command to new in the inventory db
                for i in range(len(lemonadeTracker)):
                    if lemonadeTracker[i]['nodeID'] == nodeID:
                        lemonadeTracker[i]['cmd'] = "new"
                        lemonadeTracker[i]['last_played'] = time.time()
                saveValues(nodeID, inventory, cups, lemons, sugar, weeks, score)
            return msg
    else:
        return "Game Over! Start a (N)ew Game or (E)xit"
