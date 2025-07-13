# helper functions for various BBS messaging tasks
# K7MHI Kelly Keeton 2024

import pickle # pip install pickle
from modules.log import *
import time
from dataclasses import dataclass
from typing import List

trap_list_bbs = ("bbslist", "bbspost", "bbsread", "bbsdelete", "bbshelp", "bbsinfo", "bbslink", "bbsack")

@dataclass
class BbsMessage:
    message_id: int
    subject: str
    body: str
    from_node: int

@dataclass
class BbsDm:
    to_node: int
    message: str
    from_node: int

# global message list, later we will use a pickle on disk
bbs_messages: List[BbsMessage] = [] 
bbs_dm: List[BbsDm] = []

def load_bbsdb():
    global bbs_messages

    # Be clear that we're loading a fresh database
    bbs_messages = []

    # load the bbs messages from the database file
    try:
        with open('data/bbsdb.pkl', 'rb') as f:
            serialized_messages = pickle.load(f)
            for message in serialized_messages:
                message_id, subject, body, from_node = message
                bbs_messages.append(BbsMessage(message_id, subject, body, from_node))
    except Exception as e:
        bbs_messages = [BbsMessage(
            message_id=1,
            subject="Welcome to meshBBS",
            body="Welcome to the BBS, please post a message!",
            from_node=0
        )]
        logger.debug("System: Creating new data/bbsdb.pkl")
        save_bbsdb()

def save_bbsdb():
    global bbs_messages

    serialized_messages = []
    for message in bbs_messages:
        serialized_messages.append([
            message.message_id,
            message.subject,
            message.body,
            message.from_node
        ])

    # save the bbs messages to the database file
    logger.debug("System: Saving data/bbsdb.pkl")
    with open('data/bbsdb.pkl', 'wb') as f:
        pickle.dump(serialized_messages, f)

def bbs_help():
    # help message
    return "BBS Commands:\n'bbslist'\n'bbspost message...'\n'bbspost $subject #message'\n'bbsread #'\n'bbsdelete #'"

def bbs_list_messages():
    #print (f"System: raw bbs_messages: {bbs_messages}")
    # return a string with new line for each message subject in the list bbs_messages
    message_list = ""
    for message in bbs_messages:
        message_list += "Msg #" + str(message.message_id) + " " + message.subject + "\n"

    # last newline removed
    message_list = message_list[:-1]
    return message_list

def bbs_delete_message(messageID = 0, fromNode = 0):
    #if messageID out of range ignore
    if (messageID - 1) >= len(bbs_messages):
        return "Message not found."
    
    # delete a message from the bbsdb
    if messageID > 0:
        # if same user wrote message they can delete it
        if fromNode == bbs_messages[messageID - 1].from_node or str(fromNode) in bbs_admin_list:
            bbs_messages.pop(messageID - 1)
            # reset the messageID
            for i in range(len(bbs_messages)):
                bbs_messages[i].message_id = i + 1

            # save the bbsdb
            save_bbsdb()
            
            return "Msg #" + str(messageID) + " deleted."
        else:
            logger.warning(f"System: node {fromNode}, tried to delete a message: {bbs_messages[messageID - 1]} and was dropped.")
            return "You are not authorized to delete this message."
    else:
        return "Please specify a message number to delete."

def bbs_automatic_subject_from_body(body):
    max_subject_length = 25

    # Clean up any whitespace
    subject = body.strip()

    if len(subject) > max_subject_length:
        subject = subject[:max_subject_length].strip() + '...'

    return subject

def bbs_post_message(subject, message, fromNode):
    # post a message to the bbsdb and assign a messageID
    messageID = len(bbs_messages) + 1

    # Check the BAN list for naughty nodes and silently drop the message
    if str(fromNode) in bbs_ban_list:
        logger.warning(f"System: Naughty node {fromNode}, tried to post a message: {subject}, {message} and was dropped.")
        return "Message posted. ID is: " + str(messageID)
    
    # validate not a duplicate message
    for msg in bbs_messages:
        if msg.subject.strip().lower() == subject.strip().lower() and msg.body.strip().lower() == message.strip().lower():
            messageID = msg.message_id
            return "Message posted. ID is: " + str(messageID)

    # append the message to the list
    bbs_messages.append(BbsMessage(messageID, subject, message, fromNode))
    logger.info(f"System: NEW Message Posted, subject: {subject}, message: {message} from {fromNode}")

    # save the bbsdb
    save_bbsdb()

    return "Message posted. ID is: " + str(messageID)

def bbs_read_message(messageID = 0):
    #if messageID out of range ignore
    if (messageID - 1) >= len(bbs_messages):
        return "Message not found."
    if messageID > 0:
        message = bbs_messages[messageID - 1]
        return f"Msg #{message.message_id}\nMsg Body: {message.body}"
    else:
        return "Please specify a message number to read."
   
def save_bbsdm():
    global bbs_dm
    # save the bbs messages to the database file
    logger.debug("System: Saving Updated BBS Direct Messages data/bbsdm.pkl")

    serialized_dms = []
    for dm in bbs_dm:
        serialized_dms.append([dm.to_node, dm.message, dm.from_node])
    with open('data/bbsdm.pkl', 'wb') as f:
        pickle.dump(serialized_dms, f)

def load_bbsdm():
    global bbs_dm
    # load the bbs messages from the database file
    try:
        with open('data/bbsdm.pkl', 'rb') as f:
            serialized_dms = pickle.load(f)
            bbs_dm = []
            for dm in serialized_dms:
                to_node, message, from_node = dm
                bbs_dm.append(BbsDm(to_node, message, from_node))
    except:
        bbs_dm = [BbsDm(to_node=1234567890, message="Message", from_node=1234567890)]
        logger.debug("System: Creating new data/bbsdm.pkl")
        save_bbsdm()

def bbs_post_dm(toNode, message, fromNode):
    global bbs_dm
    # Check the BAN list for naughty nodes and silently drop the message
    if str(fromNode) in bbs_ban_list:
        logger.warning(f"System: Naughty node {fromNode}, tried to post a message: {message} and was dropped.")
        return "DM Posted for node " + str(toNode)

    # append the message to the list
    bbs_dm.append(BbsDm(int(toNode), message, int(fromNode)))

    # save the bbsdb
    save_bbsdm()
    return "BBS DM Posted for node " + str(toNode)

def get_bbs_stats():
    global bbs_messages, bbs_dm
    # Return some stats on the bbs pending messages and total posted messages
    return f"📡BBSdb has {len(bbs_messages)} messages.\nDirect ✉️ Messages waiting: {(len(bbs_dm) - 1)}"

def bbs_check_dm(toNode):
    global bbs_dm
    # Check for any messages for toNode
    for msg in bbs_dm:
        if msg.to_node == toNode:
            return msg
    return False

def bbs_delete_dm(toNode, message):
    global bbs_dm
    # delete a message from the bbsdm
    for msg in bbs_dm:
        if msg.to_node == toNode:
            # check if the message matches
            if msg.message == message:
                bbs_dm.remove(msg)
                # save the bbsdb
                save_bbsdm()
                return "System: cleared mail for" + str(toNode)
    return "System: No DM found for node " + str(toNode)

def bbs_sync_posts(input, peerNode, RxNode):
    messageID =  0

    # check if the bbs link is enabled
    if bbs_link_whitelist != ['']:
        if str(peerNode) not in bbs_link_whitelist:
            logger.warning(f"System: BBS Link is disabled for node {peerNode}.")
            return "System: BBS Link is disabled for your node."
    if bbs_link_enabled == False:
        return "System: BBS Link is disabled."
    
    # respond when another bot asks for the bbs posts to sync
    if "bbslink" in input.lower():
        if "$" in input and "#" in input:
            #store the message
            subject = input.split("$")[1].split("#")[0]
            body = input.split("#")[1]
            bbs_post_message(subject, body, peerNode)
            messageID = input.split(" ")[1]
            return f"bbsack {messageID}"
    elif "bbsack" in input.lower():
        # increment the messageID
        if len(input.split(" ")) > 1:
            try:
                messageID = int(input.split(" ")[1]) + 1
            except:
                return "link error"
        else:
            return "link error"

    # send message with delay to keep chutil happy
    if messageID < len(bbs_messages):
        logger.debug(f"System: Sending bbslink message {messageID} to peer " + str(peerNode))
        time.sleep(5 + responseDelay)
        # every 5 messages add extra delay
        if messageID % 5 == 0:
            time.sleep(10 + responseDelay)
        return f"bbslink {messageID} ${bbs_messages[messageID].subject} #{bbs_messages[messageID].body}"
    else:
        logger.debug("System: bbslink sync complete with peer " + str(peerNode))


#initialize the bbsdb's
load_bbsdb()
load_bbsdm()
