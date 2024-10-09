# https://github.com/pwdkramer/pythonMastermind/blob/main/main.py
# Adapted for Meshtastic mesh-bot by K7MHI Kelly Keeton 2024

import random
import time
import pickle
from modules.log import *

mindTracker = [{'nodeID': 0, 'last_played': time.time(), 'cmd': '', 'secret_code': '', 'diff': 'n', 'turns': 1}]

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
def getGuessMMind(diff, guess):
    msg = ''
    if diff == "n":
        valid_colorsMMind = "RYGB"
    elif diff == "h":
        valid_colorsMMind = "RYGBOP"
    elif diff == "x":
        valid_colorsMMind = "RYGBOPWK"
        
    user_guess = guess.upper()
    valid_guess = True
    if len(user_guess) != 4:
        valid_guess = False
    for i in range(len(user_guess)):
        if user_guess[i] not in valid_colorsMMind:
            valid_guess = False
    if valid_guess == False:
        user_guess = "XXXX"
    return user_guess

def getHighScoreMMind(nodeID, turns, diff):
    # check if player is in high score list and pick the lowest score
    try:
        with open('mmind_hs.pkl', 'rb') as f:
            mindHighScore = pickle.load(f)
    except:
        logger.debug("System: MasterMind: High Score file not found.")
        mindHighScore = [{'nodeID': nodeID, 'turns': turns, 'diff': diff}]
        with open('mmind_hs.pkl', 'wb') as f:
            pickle.dump(mindHighScore, f)

    if nodeID == 0:
        # just return the high score
        return mindHighScore

    # calculate lowest score
    lowest_score = mindHighScore[0]['turns']

    if mindHighScore[0]['diff'] == "n" and diff == "n":
        if lowest_score > turns:
            # update the high score for normal if new score is lower
            mindHighScore[0]['nodeID'] = nodeID
            mindHighScore[0]['turns'] = turns
            mindHighScore[0]['diff'] = diff
            
            # write new high score to file
            with open('mmind_hs.pkl', 'wb') as f:
                pickle.dump(mindHighScore, f)
            return mindHighScore
    elif mindHighScore[0]['diff'] == "n" and diff == "h":
        # update the high score for hard if normal is the only high score
        mindHighScore[0]['nodeID'] = nodeID
        mindHighScore[0]['turns'] = turns
        mindHighScore[0]['diff'] = diff
        
        # write new high score to file
        with open('mmind_hs.pkl', 'wb') as f:
            pickle.dump(mindHighScore, f)
        return mindHighScore
    elif mindHighScore[0]['diff'] == "h" and diff == "h":
        if lowest_score > turns:
            # update the high score for hard if new score is lower
            mindHighScore[0]['nodeID'] = nodeID
            mindHighScore[0]['turns'] = turns
            mindHighScore[0]['diff'] = diff
            
            # write new high score to file
            with open('mmind_hs.pkl', 'wb') as f:
                pickle.dump(mindHighScore, f)
            return mindHighScore
    elif mindHighScore[0]['diff'] == "n" or mindHighScore[0]['diff'] == "h" and diff == "x":
        # update the high score for expert if normal or high is the only high score
        mindHighScore[0]['nodeID'] = nodeID
        mindHighScore[0]['turns'] = turns
        mindHighScore[0]['diff'] = diff
        
        # write new high score to file
        with open('mmind_hs.pkl', 'wb') as f:
            pickle.dump(mindHighScore, f)
        return mindHighScore
    elif mindHighScore[0]['diff'] == "x" and diff == "x":
        if lowest_score > turns:
            # update the high score for expert if new score is lower
            mindHighScore[0]['nodeID'] = nodeID
            mindHighScore[0]['turns'] = turns
            mindHighScore[0]['diff'] = diff
            
            # write new high score to file
            with open('mmind_hs.pkl', 'wb') as f:
                pickle.dump(mindHighScore, f)
            return mindHighScore
    return 0


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
def compareCodeMMind(secret_code, user_guess):
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
        for i in range(len(user_guess)): #check for perfect pins
            if user_guess[i] == secret_code[i]:
                perfect_pins += 1
            else:
                temp_code.append(secret_code[i])
                temp_guess.append(user_guess[i])
        for i in range(len(temp_guess)): #check for right color wrong position
            for j in range(len(temp_code)):
                if temp_guess[i] == temp_code[j]:
                    wrong_position += 1
                    temp_code[j] = "0"
    # display feedback
    if game_won:
        msg += f"Correct{getEmojiMMind(user_guess)}\n"
    else:
        msg += f"Guess{getEmojiMMind(user_guess)}\n"

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
        user_guess = getGuessMMind(diff, message)
        if user_guess == "XXXX":
            msg += f"⛔️Invalid guess. Please enter 4 valid colors letters.\n🔴🟢🔵🔴 is RGBR"
            return msg
        check_guess = compareCodeMMind(secret_code, user_guess)

        # display turn count and feedback
        msg += "Turn {}:".format(turn_count)
        if check_guess.startswith("Correct"):
            won = True
        msg += check_guess
    
        if won == True:
            msg += f"\n🎉🧠 you win 🥷🤯"
            # get high score
            high_score = getHighScoreMMind(nodeID, turn_count, diff)
            if high_score != 0:
                msg += f"\n🏆 High Score:{high_score[0]['turns']} turns, Difficulty:{high_score[0]['diff'].upper()}"
            
            msg += "\nWould you like to play again?\n(N)ormal, (H)ard, e(X)pert (E)nd?"
            # reset turn count in tracker
            for i in range(len(mindTracker)):
                if mindTracker[i]['nodeID'] == nodeID:
                    mindTracker[i]['turns'] = 1
                    mindTracker[i]['secret_code'] = ''
                    mindTracker[i]['cmd'] = 'new'
        else:
            # increment turn count and keep playing
            turn_count += 1
            # store turn count in tracker
            for i in range(len(mindTracker)):
                if mindTracker[i]['nodeID'] == nodeID:
                    mindTracker[i]['turns'] = turn_count
    elif won == False:
        msg += f"🙉Game Over🙈\nThe code was: {getEmojiMMind(secret_code)}"
        msg += "\nYou have run out of turns.😿"
        msg += "\nWould you like to play again? (N)ormal, (H)ard, or e(X)pert?"
        # reset turn count in tracker
        for i in range(len(mindTracker)):
            if mindTracker[i]['nodeID'] == nodeID:
                mindTracker[i]['turns'] = 1
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
