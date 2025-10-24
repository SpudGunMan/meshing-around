# https://github.com/pwdkramer/pythonMastermind/blob/main/main.py
# Adapted for Meshtastic mesh-bot by K7MHI Kelly Keeton 2024

import random
import time
import pickle
from modules.log import *

def chooseDifficultyMMind(message):
    usrInput = message.lower()
    msg = ''
    valid_colorsMMind = "RYGB"
    
    if not usrInput.startswith("n") and not usrInput.startswith("h") and not usrInput.startswith("x"):
        # default to normal difficulty
        usrInput = "n"
    
    if usrInput == "n":
        msg += f"The colors to choose from are:\nR🔴, Y🟡, G🟢, B🔵"
    elif usrInput == "h":
        valid_colorsMMind += "OP"
        msg += f"The colors to choose from are\nR🔴, Y🟡, G🟢, B🔵, O🟠, P🟣"
    elif usrInput == "x":
        valid_colorsMMind += "OPWK"
        msg += f"The colors to choose from are\nR🔴, Y🟡, G🟢, B🔵, O🟠, P🟣, W⚪, K⚫"
    return msg


#possible colors on nomral: Red, Yellow, Green, Blue
#added colors on hard: Orange, Purple
def makeCodeMMind(diff):
    secret_code = ""
    for i in range(4):
        if diff == "n":
            roll = random.randrange(1, 5)
        elif diff == "h":
            roll = random.randrange(1,7)
        elif diff == "x":
            roll = random.randrange(1,9)
        else:
            print("Difficulty error in makeCode()")
        if roll == 1:
            secret_code += "R"
        elif roll == 2:
            secret_code += "Y"
        elif roll == 3:
            secret_code += "G"
        elif roll == 4:
            secret_code += "B"
        elif roll == 5:
            secret_code += "O"
        elif roll == 6:
            secret_code += "P"
        elif roll == 7:
            secret_code += "W"
        elif roll == 8:
            secret_code += "K"
        else:
            print("Error with range of roll in makeCode()")
    return secret_code

#get guess from user
def getGuessMMind(diff, guess, nodeID):
    valid_colors = {
        "n": "RYGB",
        "h": "RYGBOP",
        "x": "RYGBOPWK"
    }
    user_guess = guess.strip().upper()
    if len(user_guess) != 4 or any(c not in valid_colors.get(diff, "RYGB") for c in user_guess):
        return "XXXX"
    
    #increase the turn count and store in tracker
    for i in range(len(mindTracker)):
        if mindTracker[i]['nodeID'] == nodeID:
            mindTracker[i]['turns'] += 1
            mindTracker[i]['last_played'] = time.time()
            mindTracker[i]['diff'] = diff
    return user_guess

def getHighScoreMMind(nodeID, turns, diff):
    import os
    hs_file = 'data/mmind_hs.pkl'
    # Try to load existing high scores
    if os.path.exists(hs_file):
        try:
            with open(hs_file, 'rb') as f:
                mindHighScore = pickle.load(f)
        except Exception as e:
            logger.debug(f"System: MasterMind: Error loading high score file: {e}")
            mindHighScore = []
    else:
        mindHighScore = []

    # If nodeID==0, just return 0
    if nodeID == 0:
        mindHighScore = [{'nodeID': 0, 'turns': 0, 'diff': 'n'}]
        return mindHighScore

    # If no high score, add this one
    if not mindHighScore:
        mindHighScore = [{'nodeID': nodeID, 'turns': turns, 'diff': diff}]
        with open(hs_file, 'wb') as f:
            pickle.dump(mindHighScore, f)
        return mindHighScore

    # If the diff matches, compare and update if better
    if mindHighScore[0]['diff'] == diff:
        if turns < mindHighScore[0]['turns']:
            mindHighScore[0] = {'nodeID': nodeID, 'turns': turns, 'diff': diff}
            with open(hs_file, 'wb') as f:
                pickle.dump(mindHighScore, f)
        return mindHighScore

    # If the diff is different, replace with new high score for new diff
    mindHighScore[0] = {'nodeID': nodeID, 'turns': turns, 'diff': diff}
    with open(hs_file, 'wb') as f:
        pickle.dump(mindHighScore, f)
    return mindHighScore


def getEmojiMMind(secret_code):
    # for each letter in the secret code, convert to emoji for display
    secret_code = secret_code.upper()
    secret_code_emoji = ""
    for i in range(len(secret_code)):
        if secret_code[i] == "R":
            secret_code_emoji += "🔴"
        elif secret_code[i] == "Y":
            secret_code_emoji += "🟡"
        elif secret_code[i] == "G":
            secret_code_emoji += "🟢"
        elif secret_code[i] == "B":
            secret_code_emoji += "🔵"
        elif secret_code[i] == "O":
            secret_code_emoji += "🟠"
        elif secret_code[i] == "P":
            secret_code_emoji += "🟣"
        elif secret_code[i] == "W":
            secret_code_emoji += "⚪"
        elif secret_code[i] == "K":
            secret_code_emoji += "⚫"
        elif secret_code[i] == "X":
            secret_code_emoji += "❌"
    return secret_code_emoji

#compare userGuess with secret code and provide feedback
def compareCodeMMind(secret_code, user_guess, nodeID):
    game_won = False
    perfect_pins = 0
    wrong_position = 0
    msg = ''
    #logger.debug("System: MasterMind: secret_code: " + str(secret_code) + " user_guess: " + str(user_guess))
    if secret_code == user_guess: #correct guess, user wins
        perfect_pins = 4
        game_won = True
    else:
        # check for perfect pins and right color wrong position
        temp_code = []
        temp_guess = []
        # Check for perfect pins
        for i in range(len(user_guess)):
            if user_guess[i] == secret_code[i]:
                perfect_pins += 1
            else:
                temp_code.append(secret_code[i])
                temp_guess.append(user_guess[i])

        # Check for right color wrong position
        for guess in temp_guess:
            if guess in temp_code:
                wrong_position += 1
                temp_code.remove(guess)  # Remove the first occurrence of the matched color
    # display feedback
    if game_won:
        msg += f"\n🏆Correct{getEmojiMMind(user_guess)}\nYou are the master mind!🤯"
        # get turn count from tracker
        for i in range(len(mindTracker)):
            if mindTracker[i]['nodeID'] == nodeID:
                turns = mindTracker[i]['turns'] - 2  # subtract 2 to account for increment after last guess and starting at 1
                diff = mindTracker[i]['diff']
        # get high score
        high_score = getHighScoreMMind(nodeID, turns, diff)
        if high_score[0]['turns'] != 0:
            msg += f"\n🏆 High Score:{turns} turns, Difficulty:{diff}"
        # reset turn count in tracker
        msg += f"\nWould you like to play again? (N)ormal, (H)ard, or e(X)pert?"
        # reset turn count in tracker
        for i in range(len(mindTracker)):
            if mindTracker[i]['nodeID'] == nodeID:
                mindTracker[i]['turns'] = 0
                mindTracker[i]['secret_code'] = ''
                mindTracker[i]['cmd'] = 'new'
    else:
        msg += f"\nGuess{getEmojiMMind(user_guess)}\n"

    if perfect_pins > 0 and game_won == False:
        msg += "✅ color ✅ position: {}".format(perfect_pins)

    if wrong_position > 0:
        if "✅" in msg: msg += f"\n"
        msg += "✅ color 🚫 position: {}".format(wrong_position)
    
    if "✅" not in msg and game_won == False:
        msg += "🚫No pins in your guess😿 are in the code!"

    return msg

#game loop with turn counter
def playGameMMind(diff, secret_code, turn_count, nodeID, message):
    msg = ''
    won = False
    if turn_count <= 10:
        user_guess = getGuessMMind(diff, message, nodeID)
        if user_guess == "XXXX":
            msg += f"⛔️Invalid guess. Please enter 4 valid colors letters.\n🔴🟢🔵🔴 is RGBR"
            return msg
        check_guess = compareCodeMMind(secret_code, user_guess, nodeID)

        # display turn count and feedback
        msg += "Turn {}:".format(turn_count)
        if check_guess.startswith("Correct"):
            won = True
        msg += check_guess
    
        if won == True:
            msg += f"\n🎉🧠 you win 🥷🤯"
        else:
            # increment turn count and keep playing
            turn_count += 1
            # store turn count in tracker
            for i in range(len(mindTracker)):
                if mindTracker[i]['nodeID'] == nodeID:
                    mindTracker[i]['turns'] = turn_count
    elif won == False:
        msg += f"🙉Game Over🙈\nThe code was: {getEmojiMMind(secret_code)}"
        msg += f"\nYou have run out of turns.😿"
        msg += f"\nWould you like to play again? (N)ormal, (H)ard, or e(X)pert?"
        # reset turn count in tracker
        for i in range(len(mindTracker)):
            if mindTracker[i]['nodeID'] == nodeID:
                mindTracker[i]['turns'] = 0
                mindTracker[i]['secret_code'] = ''
                mindTracker[i]['cmd'] = 'new'

    return msg

def endGameMMind(nodeID):
    global mindTracker
    # remove player from tracker
    for i in range(len(mindTracker)):
        if mindTracker[i]['nodeID'] == nodeID:
            del mindTracker[i]
            logger.debug("System: MasterMind: Player removed: " + str(nodeID))
            break

#main game
def start_mMind(nodeID, message):
    global mindTracker
    last_cmd = ""
    msg = ''

    # get player's last command from tracker if not new player
    for i in range(len(mindTracker)):
        if mindTracker[i]['nodeID'] == nodeID:
            last_cmd = mindTracker[i]['cmd']

    if last_cmd == "new":
        if message.lower().startswith("n") or message.lower().startswith("h") or message.lower().startswith("x"):
            diff = message.lower()[0]
        else:
            diff = "n"

        # set player's last command to makeCode
        for i in range(len(mindTracker)):
            if mindTracker[i]['nodeID'] == nodeID:
                mindTracker[i]['cmd'] = 'makeCode'
                mindTracker[i]['diff'] = diff
        # Return color message to player
        msg += chooseDifficultyMMind(message.lower()[0])
        return msg
    
    if last_cmd == "makeCode":
        # get difficulty from tracker
        for i in range(len(mindTracker)):
            if mindTracker[i]['nodeID'] == nodeID:
                diff = mindTracker[i]['diff']

        secret_code = makeCodeMMind(diff)
        last_cmd = "playGame"
        # set player's last command to playGame
        for i in range(len(mindTracker)):
            if mindTracker[i]['nodeID'] == nodeID:
                mindTracker[i]['cmd'] = 'playGame'
                mindTracker[i]['secret_code'] = secret_code
                mindTracker[i]['last_played'] = time.time()
    
    if last_cmd == "playGame":
        # get difficulty, secret code, and turn count from tracker
        for i in range(len(mindTracker)):
            if mindTracker[i]['nodeID'] == nodeID:
                diff = mindTracker[i]['diff']
                secret_code = mindTracker[i]['secret_code']
                turn_count = mindTracker[i]['turns']

        msg += playGameMMind(diff, secret_code, turn_count, nodeID=nodeID, message=message)

    return msg
