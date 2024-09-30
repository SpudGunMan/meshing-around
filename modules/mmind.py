# https://github.com/pwdkramer/pythonMastermind/blob/main/main.py
# Adapted for Meshtastic mesh-bot by K7MHI Kelly Keeton 2024

import random
import time
from modules.log import *

mindTracker = [{'nodeID': 0, 'last_played': time.time(), 'cmd': '', 'secret_code': '', 'diff': 'n', 'turns': 1}]

def chooseDifficultyMMind(message):
    usrInput = message.lower()
    msg = ''
    valid_colorsMMind = "RYGB"
    
    if not usrInput.startswith("n") and not usrInput.startswith("h"):
        msg += "Please enter either '(N)ormal' or '(H)ard'"

    if usrInput == "n":
        msg += f"The colors to choose from are:\nR🔴, Y🟡, G🟢, B🔵"
    elif usrInput == "h":
        valid_colorsMMind += "OP"
        msg += f"The colors to choose from are\nR🔴, Y🟡, G🟢, B🔵, O🟠, P🟣"
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
    return secret_code_emoji

#compare userGuess with secret code and provide feedback
def compareCodeMMind(secret_code, user_guess):
    game_won = False
    perfect_pins = 0
    wrong_position = 0
    msg = ''
    if secret_code == user_guess: #correct guess, user wins
        perfect_pins = 4
    else: #provide feedback on guess
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
                    break
    msg += "Guess:{}\n".format(getEmojiMMind(user_guess))
    if perfect_pins > 0:
        msg += "✅ color ✅ position: {}\n".format(perfect_pins)
    if wrong_position > 0:
        msg += "✅ color 🚫 position: {}".format(wrong_position)
    
    if "✅" not in msg:
        msg += "🚫No correct pins in your guess.😿"

    return msg

#game loop with turn counter
def playGameMMind(diff, secret_code, turn_count, nodeID, message):
    msg = ''
    if turn_count <= 10:
        user_guess = getGuessMMind(diff, message)
        if user_guess == "XXXX":
            msg += "Invalid guess. Please enter 4 valid colors."
            return msg
        check_guess = compareCodeMMind(secret_code, user_guess)

        if "✅ position: 4" in check_guess:
            won = True
        else:
            won = False

        msg += "Turn {}:".format(turn_count)
        msg += check_guess
        if won == True:
            msg += "\n🎉🧠 You guessed the code! {}".format(getEmojiMMind(secret_code))
            endGameMMind(nodeID)
        elif turn_count >= 11 and won == False:
            msg += "\nGame Over! The code was: {}".format(getEmojiMMind(secret_code))
            endGameMMind(nodeID)
        turn_count += 1
        # store turn count in tracker
        for i in range(len(mindTracker)):
            if mindTracker[i]['nodeID'] == nodeID:
                mindTracker[i]['turns'] = turn_count
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

    logger.debug("System: MasterMind: last_cmd: " + str(last_cmd))

    if last_cmd == "new":
        if message.lower().startswith("n") or message.lower().startswith("h"):
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
