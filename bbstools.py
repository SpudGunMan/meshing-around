# helper functions for various BBS messaging tasks
# K7MHI Kelly Keeton 2024

from dadjokes import Dadjoke # pip install dadjokes
import pickle # pip install pickle
import os

# global message list
bbs_messages = []

def tell_joke():
    # tell a dad joke, does it need an explanationn :)
    dadjoke = Dadjoke()
    return dadjoke.joke

def load_bbsdb():
    global bbs_messages
    # load the bbs messages from the database file
    if not os.path.exists('bbsdb.pkl'):
        # if not, create it
        bbs_messages = [[1, "Welcome to meshBBS", "Welcome to the BBS, please post a message!"]]
        print ("\nSystem: Creating new bbsdb.pkl")
        with open('bbsdb.pkl', 'wb') as f:
            pickle.dump(bbs_messages, f)
    else:
        with open('bbsdb.pkl', 'rb') as f:
            bbs_messages = pickle.load(f)

def save_bbsdb():
    global bbs_messages
    # save the bbs messages to the database file
    print ("System: Saving bbsdb.pkl\n")
    with open('bbsdb.pkl', 'wb') as f:
        pickle.dump(bbs_messages, f)

def bbs_help():
    # help message
    return "BBS Commands:\n'bbslist'\n'bbspost $subject #message'\n'bbsread #'\n'bbsdelete #'"

def bbs_list_messages():
    #print (f"System: raw bbs_messages: {bbs_messages}")
    # return a string with new line for each message subject in the list bbs_messages
    message_list = ""
    for message in bbs_messages:
        # message[0] is the messageID, message[1] is the subject
        message_list += "Msg #" + str(message[0]) + " " + message[1] + "\n"

    # last newline removed
    message_list = message_list[:-1]
    return message_list

def bbs_delete_message(messageID = 0):
    # delete a message from the bbsdb
    if messageID > 0:
        bbs_messages.pop(messageID - 1)
        # reset the messageID
        for i in range(len(bbs_messages)):
            bbs_messages[i][0] = i + 1
        
        return "Msg #" + str(messageID) + " deleted."
    else:
        return "Please specify a message number to delete."

def bbs_post_message(subject, message):
    # post a message to the bbsdb and assign a messageID
    messageID = len(bbs_messages) + 1
    
    #print (f"System: messageID: {messageID}, subject: {subject}, message: {message}")
    # append the message to the list
    bbs_messages.append([messageID, subject, message])
    return "Message posted. ID is: " + str(messageID)

def bbs_read_message(messageID = 0):
    if messageID > 0:
        message = bbs_messages[messageID - 1]
        return f"Msg #{message[0]}\nMsg Body: {message[2]}"
    else:
        return "Please specify a message number to read."

#initialize the bbsdb
load_bbsdb()

