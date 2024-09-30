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
golfTracker = [{'nodeID': 0, 'last_played': time.time(), 'cmd': '', 'hole': 0, 'distance_remaining': 0, 'hole_shots': 0, 'hole_strokes': 0, 'hole_to_par': 0, 'total_strokes': 0, 'total_to_par': 0}]

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

# Main game loop
def playGolf(nodeID, message):
    msg = ''
    global golfTracker

    # get player's last command from tracker if not new player
    last_cmd = ""
    for i in range(len(golfTracker)):
        if golfTracker[i]['nodeID'] == nodeID:
            last_cmd = golfTracker[i]['cmd']
            hole = golfTracker[i]['hole']

    if last_cmd == "" or last_cmd == "new":
        par3_count = 0
        par4_count = 0
        par5_count = 0
        # Scorecard setup
        total_strokes = 0
        total_to_par = 0

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

            # Show player the hole information
            msg += "⛳️#" + str(hole) + " is a " + str(hole_length) + "-yard Par " + str(par) + "."
            # add weather conditions with random choice from list
            msg += " Cond:" + random.choice(["Calm", "Breezy", "Calm", "Calm", "Gusty", "Windy", "Calm"]) + "."
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

        # Start loop to be able to choose clubs while at least 20 yards away
        if distance_remaining >= 20:
            msg = ""
            club = message.lower()
            shot_distance = 0

            pin_distance = distance_remaining

            if club == "driver" or club.startswith("d"):
                shot_distance = hit_driver()
                msg += "You hit your Driver " + str(shot_distance) + " yards."
                distance_remaining = abs(distance_remaining - shot_distance)
                hole_shots += 1
            elif "low" in club or club.startswith("l"):
                shot_distance = hit_low_iron()
                msg += "You hit your Low Iron " + str(shot_distance) + " yards."
                distance_remaining = abs(distance_remaining - shot_distance)
                hole_shots += 1
            elif "mid" in club or club.startswith("m"):
                shot_distance = hit_mid_iron()
                msg += "You hit your Mid Iron " + str(shot_distance) + " yards."
                distance_remaining = abs(distance_remaining - shot_distance)
                hole_shots += 1
            elif "high" in club or club.startswith("h"):
                shot_distance = hit_high_iron()
                msg += "You hit your High Iron " + str(shot_distance) + " yards."
                distance_remaining = abs(distance_remaining - shot_distance)
                hole_shots += 1
            elif "gap" in club or club.startswith("g"):
                shot_distance = hit_gap_wedge()
                msg += "You hit your Gap Wedge " + str(shot_distance) + " yards."
                distance_remaining = abs(distance_remaining - shot_distance)
                hole_shots += 1
            elif "wedge" in club or club.startswith("w"):
                shot_distance = hit_lob_wedge()
                msg += "You hit your Lob Wedge " + str(shot_distance) + " yards."
                distance_remaining = abs(distance_remaining - shot_distance)
                hole_shots += 1

            if distance_remaining - pin_distance > pin_distance or shot_distance > pin_distance:
                msg += "You've hit it past the hole!😖"

            if distance_remaining == 0:
                msg += "💰Perfect shot! "
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
                    msg += random.choice["A 🐿️ steals your ball!😡","You Hit a 🦅 soring past"]
                    distance_remaining = -1

                # Send to putting
                last_cmd = 'putt'
            else:
                msg += "You have " + str(distance_remaining) + " yards left."
                msg += "Club?[D, H, M, L, G, W]🏌️"

                # save player's current game state, keep stroking
                for i in range(len(golfTracker)):
                    if golfTracker[i]['nodeID'] == nodeID:
                        golfTracker[i]['distance_remaining'] = distance_remaining
                        golfTracker[i]['hole_shots'] = hole_shots
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

            if not critter:
                # Calculate hole and round scores
                hole_strokes = hole_shots + putts
                hole_to_par = hole_strokes - par
                total_strokes += hole_strokes
                total_to_par += hole_to_par

                # Show player hole/round scoring info
                if putts == 0 and hole_strokes == 1:
                    msg += "🎯Hole in one!⛳️"
                elif putts == 0:
                    msg += "You're in the hole at " + str(hole_strokes) + " strokes!"
                else:
                    msg += "You're on the green! After " + str(putts) + " putt(s), you're in for " + str(hole_strokes) + " strokes."
                
                if hole_to_par > 0:
                    msg += "Your score for the hole is +" + str(hole_to_par) + " to par."
                elif hole_to_par == 0:
                    msg += "Your score for the hole is even to par."
                else:
                    msg += "Your score for the hole is " + str(hole_to_par) + " to par."

                msg += "You've hit a total of " + str(total_strokes) + " strokes so far."
                if total_to_par > 0:
                    msg += "Your score for the round is +" + str(total_to_par) + " to par."
                elif total_to_par == 0:
                    msg += "Your score for the round is even to par."
                else:
                    msg += "Your score for the round is " + str(total_to_par) + " to par."

                # Move to next hole
                hole += 1
            else:
                msg += "🐿️ you ran to the pro-shop to get a new ball, they put you back at the same hole"
        
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
            msg += f"\n🎉Finished 9-hole round⛳️"
            msg += "Total strokes " + str(total_strokes) + "."
            if total_to_par > 0:
                msg += "Your score for the day is +" + str(total_to_par) + " to par."
            elif total_to_par == 0:
                msg += "Your score for the day is even to par."
            else:
                msg += "Your score for the day is " + str(total_to_par) + " to par."
            # pop player from tracker
            for i in range(len(golfTracker)):
                if golfTracker[i]['nodeID'] == nodeID:
                    golfTracker.pop(i)
            logger.debug("System: GolfSim: Player " + str(nodeID) + " has finished their round.")
        else:
            msg += "⛳️#" + str(hole) + " is next, keep playing? or (E)nd the round."
            
    return msg
