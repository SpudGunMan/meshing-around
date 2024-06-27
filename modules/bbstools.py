# helper functions for various BBS messaging tasks
# K7MHI Kelly Keeton 2024

import pickle # pip install pickle
import os

bbs_ban_list = [] # list of banned nodes numbers ex: [2813308004, 4258675309]

trap_list_bbs = ("bbslist", "bbspost", "bbsread", "bbsdelete", "bbshelp")

# global message list, later we will use a pickle on disk
bbs_messages = []

def load_bbsdb():
    global bbs_messages
    # load the bbs messages from the database file
    if not os.path.exists('bbsdb.pkl'):
        # if not, create it
        bbs_messages = [[1, "Welcome to meshBBS", "Welcome to the BBS, please post a message!",0]]
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

def bbs_post_message(subject, message, fromNode = 0):
    # post a message to the bbsdb and assign a messageID
    messageID = len(bbs_messages) + 1

    # Check the BAN list for naughty nodes and silently drop the message
    if fromNode in bbs_ban_list:
        print (f"!!System: Naughty node {fromNode}, tried to post a message: {subject}, {message} and was dropped.")
        return "Message posted. ID is: " + str(messageID)

    # append the message to the list
    bbs_messages.append([messageID, subject, message, fromNode])
    print (f"System: NEW Message Posted, subject: {subject}, message: {message}")
    
    # save the bbsdb
    save_bbsdb()

    return "Message posted. ID is: " + str(messageID)

def bbs_read_message(messageID = 0):
    if messageID > 0:
        message = bbs_messages[messageID - 1]
        return f"Msg #{message[0]}\nMsg Body: {message[2]}"
    else:
        return "Please specify a message number to read."


#initialize the bbsdb
load_bbsdb()

