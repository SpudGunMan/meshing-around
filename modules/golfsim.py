# https://github.com/danfriedman30/pythongame
# Adapted for Meshtastic mesh-bot by K7MHI Kelly Keeton 2024

import random
import time
from modules.log import *

# Clubs setup
driver_distances = list(range(230, 280, 5))
low_distances = list(range(185, 215, 5))
mid_distances = list(range(130, 185, 5))
high_distances = list(range(90, 135, 5))
gap_wedge_distances = list(range(50, 85, 5))
lob_wedge_distances = list(range(10, 50, 5))
putt_outcomes = [1, 2, 3]

# Hole/Course Setup
full_hole_range = list(range(130, 520, 5))
par3_range = list(range(130, 255, 5))
par4_range = list(range(255, 445, 5))
par5_range = list(range(445, 520, 5))
par3_4_range = par3_range + par4_range
par3_5_range = par3_range + par5_range
par4_5_range = par4_range + par5_range

# Player setup
playingHole = False
golfTracker = [{'nodeID': 0, 'last_played': time.time(), 'cmd': '', 'hole': 0, 'distance_remaining': 0, 'hole_shots': 0, 'hole_strokes': 0, 'hole_to_par': 0, 'total_strokes': 0, 'total_to_par': 0, 'par': 0, 'hazard': ''}]

# Club functions
def hit_driver():
    club_distance = random.choice(driver_distances)
    return club_distance

def hit_low_iron():
    club_distance = random.choice(low_distances)
    return club_distance

def hit_mid_iron():
    club_distance = random.choice(mid_distances)
    return club_distance

def hit_high_iron():
    club_distance = random.choice(high_distances)
    return club_distance

def hit_gap_wedge():
    club_distance = random.choice(gap_wedge_distances)
    return club_distance

def hit_lob_wedge():
    club_distance = random.choice(lob_wedge_distances)
    return club_distance

def finish_hole():
    finish = random.choice(putt_outcomes)
    return finish

def endGameGolf(nodeID):
    # pop player from tracker
    for i in range(len(golfTracker)):
        if golfTracker[i]['nodeID'] == nodeID:
            golfTracker.pop(i)
    logger.debug("System: GolfSim: Player " + str(nodeID) + " has ended their round.")

def getScorecardGolf(scorecard):
    # Scorecard messages, convert score to message comment
    msg = ""
    if scorecard == 8:
        # Quadruple bogey
        msg += " +Quad Bogey☃️ "
    elif scorecard == 7:
        # Triple bogey
        msg += " +Triple Bogey "
    elif scorecard == 6:
        # Double bogey
        msg += " +Double Bogey "
    elif scorecard == 5:
        # Bogey
        msg += " +Bogey "
    elif scorecard > 0:
        # Over par
        msg += f" +Par {str(scorecard)} "
    elif scorecard == 0:
        # Even par
        msg += " Even Par💪 "
    elif scorecard == -1:
        # Birdie
        msg += " -Birdie🐦 "
    elif scorecard == -2:
        # Eagle
        msg += " -Eagle🦅 "
    elif scorecard == -3:
        # Albatross
        msg += " -Albatross🦅🦅 "
    else:
        # Under par
        msg += f" -Par {str(abs(scorecard))} "
    return msg

# Main game loop
def playGolf(nodeID, message, finishedHole=False):
    msg = ''
    global golfTracker
    # Course setup
    par3_count = 0
    par4_count = 0
    par5_count = 0
    # Scorecard setup
    total_strokes = 0
    total_to_par = 0
    par = 0

    # get player's last command from tracker if not new player
    last_cmd = ""
    for i in range(len(golfTracker)):
        if golfTracker[i]['nodeID'] == nodeID:
            last_cmd = golfTracker[i]['cmd']
            hole = golfTracker[i]['hole']
            distance_remaining = golfTracker[i]['distance_remaining']
            hole_shots = golfTracker[i]['hole_shots']
            par = golfTracker[i]['par']
            total_strokes = golfTracker[i]['total_strokes']
            total_to_par = golfTracker[i]['total_to_par']

    if last_cmd == "" or last_cmd == "new":
        # Start a new hole
        if hole <= 9:
            # Set up hole count restrictions on par
            if par3_count < 2 and par4_count < 5 and par5_count < 2:
                hole_length = random.choice(full_hole_range)
            if par3_count >= 2 and par4_count < 5 and par5_count < 2:
                hole_length = random.choice(par4_5_range)
            if par3_count >= 2 and par4_count < 5 and par5_count >= 2:
                hole_length = random.choice(par4_range)
            if par3_count < 2 and par4_count < 5 and par5_count >= 2:
                hole_length = random.choice(par3_4_range)
            if par3_count < 2 and par4_count >= 5 and par5_count >= 2:
                hole_length = random.choice(par3_range)
            if par3_count >= 2 and par4_count >= 5 and par5_count < 2:
                hole_length = random.choice(par5_range)
            if par3_count < 2 and par4_count >= 5 and par5_count < 2:
                hole_length = random.choice(par3_5_range)

            # Set up par for the hole
            if hole_length <= 250:
                par = 3
                par3_count += 1
            elif hole_length > 250 and hole_length <= 440:
                par = 4
                par4_count += 1
            elif hole_length > 440:
                par = 5
                par5_count += 1

            # roll for chance of hazard
            hazard_chance = random.randint(1, 100)
            weather_chance = random.randint(1, 100)
            # have low chances of hazards and weather
            hasHazard = False
            hazard = ""
            if hazard_chance < 25:
                # Further reduce chance of hazards with weather
                if weather_chance < 15:
                    # randomly calculate a hazard for the hole sand, water, trees, buildings, etc
                    hazard = random.choice(["Sand", "Water", "Trees", "Buildings"])
                    hasHazard = True
                    

            # Set initial parameters before starting a hole
            distance_remaining = hole_length
            hole_shots = 0

            # save player's current game state
            for i in range(len(golfTracker)):
                if golfTracker[i]['nodeID'] == nodeID:
                    golfTracker[i]['distance_remaining'] = distance_remaining
                    golfTracker[i]['cmd'] = 'stroking'
                    golfTracker[i]['par'] = par
                    golfTracker[i]['total_strokes'] = total_strokes
                    golfTracker[i]['total_to_par'] = total_to_par
                    golfTracker[i]['hazard'] = hazard

            # Show player the hole information
            msg += "⛳️#" + str(hole) + " is a " + str(hole_length) + "-yard Par " + str(par) + "."
            if hasHazard: 
                msg += "⚠️" + hazard + "."
            else:
                # add weather conditions with random choice from list, this is fluff
                msg += random.choice(["☀️", "💨", "☀️", "☀️", "⛅️", "☁️", "☀️"])

            if not finishedHole:
                msg += f"\nChoose your club."

            return msg

    if last_cmd == 'stroking':

        # Get player's current game state
        for i in range(len(golfTracker)):
            if golfTracker[i]['nodeID'] == nodeID:
                distance_remaining = golfTracker[i]['distance_remaining']
                hole = golfTracker[i]['hole']
                hole_shots = golfTracker[i]['hole_shots']
                par = golfTracker[i]['par']
                total_strokes = golfTracker[i]['total_strokes']
                total_to_par = golfTracker[i]['total_to_par']
                hazard = golfTracker[i]['hazard']

        # Start loop to be able to choose clubs while at least 20 yards away
        if distance_remaining >= 20:
            msg = ""
            club = message.lower()
            shot_distance = 0

            pin_distance = distance_remaining

            if club == "driver" or club.startswith("d"):
                shot_distance = hit_driver()
                msg += "🏌️Hit D " + str(shot_distance) + "yd. "
                distance_remaining = abs(distance_remaining - shot_distance)
                hole_shots += 1
            elif "low" in club or club.startswith("l"):
                shot_distance = hit_low_iron()
                msg += "🏌️Hit L Iron " + str(shot_distance) + "yd. "
                distance_remaining = abs(distance_remaining - shot_distance)
                hole_shots += 1
            elif "mid" in club or club.startswith("m"):
                shot_distance = hit_mid_iron()
                msg += "🏌️Hit M Iron " + str(shot_distance) + "yd. "
                distance_remaining = abs(distance_remaining - shot_distance)
                hole_shots += 1
            elif "high" in club or club.startswith("h"):
                shot_distance = hit_high_iron()
                msg += "🏌️Hit H Iron " + str(shot_distance) + "yd. "
                distance_remaining = abs(distance_remaining - shot_distance)
                hole_shots += 1
            elif "gap" in club or club.startswith("g"):
                shot_distance = hit_gap_wedge()
                msg += "🏌️Hit G Wedge " + str(shot_distance) + "yd ."
                distance_remaining = abs(distance_remaining - shot_distance)
                hole_shots += 1
            elif "wedge" in club or club.startswith("w"):
                shot_distance = hit_lob_wedge()
                msg += "🏌️Hit L Wedge " + str(shot_distance) + "yd. "
                distance_remaining = abs(distance_remaining - shot_distance)
                hole_shots += 1
            elif club == "caddy" or club.startswith("c"):
                # Show player the club distances
                msg += f"Caddy Guess:\nD:{hit_driver()} L:{hit_low_iron()} M:{hit_mid_iron()} H:{hit_high_iron()} G:{hit_gap_wedge()} W:{hit_lob_wedge()}"
            else:
                msg += "Didnt get your club 🥪♣️🪩 choice"
                return msg

            if distance_remaining - pin_distance > pin_distance or shot_distance > pin_distance:
                # Check for over-shooting the hole
                if distance_remaining > 20:
                    # did it go off the "green"?
                    msg += "Overshot the green!🚀"
            if distance_remaining == 0:
                msg += "🎯Perfect shot! "
                last_cmd = 'putt'
            elif distance_remaining < 20:
                # Roll Dice
                hole_in_one_chance = random.randint(1, 100)
                wind_factor = random.randint(1, 10)
                skill_factor = random.randint(1, 10)
                critter_factor = random.randint(1, 50)

                # Check for hole in one
                if hole_in_one_chance <= 5 and wind_factor > 7 and skill_factor > 8:
                    distance_remaining = 0
                # Check for critters
                if skill_factor > 8 and critter_factor < 40 and wind_factor > 2 and hole_in_one_chance > 5:
                    msg += random.choice(["A 🐿️ steals your ball!😡 ","You Hit a 🦅 soring past ", "🐊 need we say more? ", "hit a 🪟 of a 🏡 "])
                    distance_remaining = -1
                # Handle hazard
                if hazard == "Water" and skill_factor < 7:
                    msg += "In the water!🌊"
                    distance_remaining = -1
                if hazard == "Sand" and skill_factor < 5:
                    msg += "In the sand!🏖️"
                    distance_remaining = random.randint(5, 10)
                if hazard == "Trees" and skill_factor < 3:
                    msg += "In the trees!🌲"
                    distance_remaining += random.randint(5, 20)
                if hazard == "Buildings" and skill_factor < 2:
                    msg += "In the parking lot!🚗"
                    distance_remaining += random.randint(10, 30)
                
                # Check we didnt go off the green or into a hazard
                if distance_remaining < 20:
                    last_cmd = 'putt'
                else:
                    last_cmd = 'stroking'
            else:
                msg += "\nYou have " + str(distance_remaining) + "yd. ⛳️"
                msg += "\nClub?[D, L, M, H, G, W]🏌️"

                # save player's current game state, keep stroking
                for i in range(len(golfTracker)):
                    if golfTracker[i]['nodeID'] == nodeID:
                        golfTracker[i]['distance_remaining'] = distance_remaining
                        golfTracker[i]['hole_shots'] = hole_shots
                        golfTracker[i]['total_strokes'] = total_strokes
                        golfTracker[i]['cmd'] = 'stroking'

                return msg

    if last_cmd == 'putt':
        # Finish the hole by putting
        critter = False
        if distance_remaining < 20:
            if distance_remaining == 0:
                putts = 0
            elif distance_remaining == -1:
                putts = 0
                critter = True
            else:
                putts = finish_hole()

            # Calculate hole and round scores
            hole_strokes = hole_shots + putts
            hole_to_par = hole_strokes - par
            total_strokes += hole_strokes
            total_to_par += hole_to_par

            debug = f"System: GolfSim: Player {nodeID} finished hole {hole} with {hole_strokes} strokes,{hole_shots}+{putts} putts, and {hole_to_par} to {hole_strokes}-{par}par"
            print(debug)
            if not critter:
                # Show player hole/round scoring info
                if putts == 0 and hole_strokes == 1:
                    msg += "🎯Hole in one!⛳️"
                elif putts == 0:
                    msg += "You're in the hole at " + str(hole_strokes) + " strokes!"
                else:
                    msg += "You're on the green! After " + str(putts) + " putt(s), you're in for " + str(hole_strokes) + " strokes."
                msg += getScorecardGolf(hole_to_par)

                if hole not in [1, 10]:
                    # Show player total scoring info for the round, except hole 1 and 10
                    msg += "\nYou've hit a total of " + str(total_strokes) + " strokes today, for"
                    msg += getScorecardGolf(total_to_par)

                # Move to next hole
                hole += 1
                # Scorecard reset
                hole_to_par = 0
                total_to_par = 0
                hole_strokes = 0
            else:
                msg += f"Got a new ball at Pro-Shop, marshal put you @" # flow into same hole haha
        
        # Save player's current game state
        for i in range(len(golfTracker)):
            if golfTracker[i]['nodeID'] == nodeID:
                golfTracker[i]['hole_strokes'] = hole_strokes
                golfTracker[i]['hole_to_par'] = hole_to_par
                golfTracker[i]['total_strokes'] = total_strokes
                golfTracker[i]['total_to_par'] = total_to_par
                golfTracker[i]['hole'] = hole
                golfTracker[i]['cmd'] = 'new'
                golfTracker[i]['last_played'] = time.time()

        if hole >= 9:
            # Final score messages & exit prompt
            msg += f"🎉Finished 9-hole round⛳️"
            # pop player from tracker
            for i in range(len(golfTracker)):
                if golfTracker[i]['nodeID'] == nodeID:
                    golfTracker.pop(i)
            logger.debug("System: GolfSim: Player " + str(nodeID) + " has finished their round.")
        else:
            # Show player the next hole
            msg += playGolf(nodeID, 'new', True)
            msg += "\n🏌️[D, L, M, H, G, W, End]🏌️"
            
    return msg
