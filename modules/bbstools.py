# helper functions for various BBS messaging tasks
# K7MHI Kelly Keeton 2024

import pickle # pip install pickle
from modules.log import *
import time

useSynchCompression = False

if useSynchCompression:
    import zlib
    from modules.system import send_raw_bytes

trap_list_bbs = ("bbslist", "bbspost", "bbsread", "bbsdelete", "bbshelp", "bbsinfo", "bbslink", "bbsack")

# global message list, later we will use a pickle on disk
bbs_messages = []
bbs_dm = []


def load_bbsdb():
    global bbs_messages
    # load the bbs messages from the database file
    try:
        with open('data/bbsdb.pkl', 'rb') as f:
            new_bbs_messages = pickle.load(f)
            if isinstance(new_bbs_messages, list):
                for msg in new_bbs_messages:
                    #example [1, 'Welcome to meshBBS', 'Welcome to the BBS, please post a message!', 0]
                    msgHash = hash(tuple(msg[1:3]))  # Create a hash of the message content (subject and body)
                    # Check if the message already exists in bbs_messages
                    if all(hash(tuple(existing_msg[1:3])) != msgHash for existing_msg in bbs_messages):
                        # if the message is not a duplicate, add it to bbs_messages Maintain the message ID sequence
                        new_id = len(bbs_messages) + 1
                        bbs_messages.append([new_id, msg[1], msg[2], msg[3]])
    except FileNotFoundError:
        logger.debug("System: bbsdb.pkl not found, creating new one")
        bbs_messages = [[1, "Welcome to meshBBS", "Welcome to the BBS, please post a message!",0]]
        try:
            with open('data/bbsdb.pkl', 'wb') as f:
                pickle.dump(bbs_messages, f)
        except Exception as e:
            logger.error(f"System: Error creating bbsdb.pkl: {e}")
    except Exception as e:
        logger.error(f"System: Error loading bbsdb.pkl: {e}")
        bbs_messages = [[1, "Welcome to meshBBS", "Welcome to the BBS, please post a message!",0]]

def save_bbsdb():
    global bbs_messages
    # save the bbs messages to the database file
    try:
        logger.debug("System: Saving data/bbsdb.pkl")
        with open('data/bbsdb.pkl', 'wb') as f:
            pickle.dump(bbs_messages, f)
    except Exception as e:
        logger.error(f"System: Error saving bbsdb: {e}")

def bbs_help():
    # help message
    return "BBS Commands:\n'bbslist'\n'bbspost $subject #message'\n'bbsread #'\n'bbsdelete #'\n'cmd'"

def bbs_list_messages():
    #print (f"System: raw bbs_messages: {bbs_messages}")
    # return a string with new line for each message subject in the list bbs_messages
    message_list = ""
    for message in bbs_messages:
        # message[0] is the messageID, message[1] is the subject
        message_list += "[#" + str(message[0]) + "] " + message[1] + "\n"

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
        if fromNode == bbs_messages[messageID - 1][3] or str(fromNode) in bbs_admin_list:
            bbs_messages.pop(messageID - 1)
            # reset the messageID
            for i in range(len(bbs_messages)):
                bbs_messages[i][0] = i + 1

            # save the bbsdb
            save_bbsdb()
            
            return "Msg #" + str(messageID) + " deleted."
        else:
            logger.warning(f"System: node {fromNode}, tried to delete a message: {bbs_messages[messageID - 1]} and was dropped.")
            return "You are not authorized to delete this message."
    else:
        return "Please specify a message number to delete."

def bbs_post_message(subject, message, fromNode, threadID=0, replytoID=0):
    # post a message to the bbsdb
    now = today.strftime('%Y-%m-%d %H:%M:%S')
    thread = threadID
    replyto = replytoID
    # post a message to the bbsdb and assign a messageID
    messageID = len(bbs_messages) + 1

    # Check the BAN list for naughty nodes and silently drop the message
    if str(fromNode) in bbs_ban_list:
        logger.warning(f"System: Naughty node {fromNode}, tried to post a message: {subject}, {message} and was dropped.")
        return "Message posted. ID is: " + str(messageID)
    # validate message length isnt three times the MESSAGE_CHUNK_SIZE
    if len(message) > (3 * MESSAGE_CHUNK_SIZE):
        return "Message too long, max length is " + str(3 * MESSAGE_CHUNK_SIZE) + " characters."
    # validate not a duplicate message
    for msg in bbs_messages:
        if msg[1].strip().lower() == subject.strip().lower() and msg[2].strip().lower() == message.strip().lower():
            messageID = msg[0]
            return "Message posted. ID is: " + str(messageID)
    # validate its not overlength by keeping in chunker limit
    # append the message to the list
    bbs_messages.append([messageID, subject, message, fromNode, now, thread, replyto])
    logger.info(f"System: NEW Message Posted, subject: {subject}, message: {message} from {fromNode}")

    # save the bbsdb
    save_bbsdb()

    return "Message posted. ID is: " + str(messageID)

def bbs_read_message(messageID = 0):
    #if messageID out of range ignore
    if (messageID - 1) >= len(bbs_messages):
        return "Message not found."
    if messageID > 0:
        fromNode = bbs_messages[messageID - 1][3]
        fromNodeHex = hex(fromNode)[-4:]
        message = bbs_messages[messageID - 1]
        return f"Msg #{message[0]}\nFrom:{fromNodeHex}\n{message[2]}"
    else:
        return "Please specify a message number to read."
   
def save_bbsdm():
    global bbs_dm
    # save the bbs messages to the database file
    logger.debug("System: Saving Updated BBS Direct Messages data/bbsdm.pkl")
    with open('data/bbsdm.pkl', 'wb') as f:
        pickle.dump(bbs_dm, f)

def load_bbsdm():
    global bbs_dm
    # load the bbs messages from the database file
    try:
        with open('data/bbsdm.pkl', 'rb') as f:
            new_bbs_dm = pickle.load(f)
            if isinstance(new_bbs_dm, list):
                for msg in new_bbs_dm:
                    if msg not in bbs_dm:
                        bbs_dm.append(msg)
    except:
        bbs_dm = [[1234567890, "Message", 1234567890]]
        logger.debug("System: Creating new data/bbsdm.pkl")
        with open('data/bbsdm.pkl', 'wb') as f:
            pickle.dump(bbs_dm, f)

def bbs_post_dm(toNode, message, fromNode):
    global bbs_dm
    # Check the BAN list for naughty nodes and silently drop the message
    if str(fromNode) in bbs_ban_list:
        logger.warning(f"System: Naughty node {fromNode}, tried to post a message: {message} and was dropped.")
        return "DM Posted for node " + str(toNode)
    
    # validate message length isnt three times the MESSAGE_CHUNK_SIZE
    if len(message) > (3 * MESSAGE_CHUNK_SIZE):
        return "Message too long, max length is " + str(3 * MESSAGE_CHUNK_SIZE) + " characters."
    # validate not a duplicate message
    for msg in bbs_dm:
        if msg[0] == int(toNode) and msg[1].strip().lower() == message.strip().lower():
            return "DM Posted for node " + str(toNode)

    # append the message to the list
    bbs_dm.append([int(toNode), message, int(fromNode)])

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
        if msg[0] == toNode:
            return msg
    return False

def bbs_delete_dm(toNode, message):
    global bbs_dm
    # delete a message from the bbsdm
    for msg in bbs_dm:
        if msg[0] == toNode:
            # check if the message matches
            if msg[1] == message:
                bbs_dm.remove(msg)
            # save the bbsdb
            save_bbsdm()
            return "System: cleared mail for" + str(toNode)
    return "System: No DM found for node " + str(toNode)

def compress_data(data_to_compress):
    # Prepare message as bytes
    compressed = zlib.compress(data_to_compress.encode('utf-8'))
    return compressed

def decompress_data(data_bytes):
    try:
        decompressed = zlib.decompress(data_bytes)
        msg = decompressed.decode('utf-8')
        return msg
    except Exception as e:
        logger.warning(f"Error decompressing data: {e}")
        return False

def bbs_receive_compressed(data_bytes, fromNode, RxNode):
    try:
        decompressed = zlib.decompress(data_bytes)
        msg = decompressed.decode('utf-8')
        
        bbs_sync_posts(msg, fromNode, RxNode)

        return msg
    except Exception as e:
        logger.error(f"Error decompressing BBS message: {e}")
        return None

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
            fromNodeHex = input.split("@")[1]
            try:
                bbs_post_message(subject, body, int(fromNodeHex, 16))
            except:
                logger.error(f"System: Error parsing bbslink from node {peerNode}: {input}")
                fromNodeHex = hex(peerNode)
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
        logger.debug(f"System: wait to bbslink with peer " + str(peerNode))
        fromNodeHex = hex(bbs_messages[messageID][3])
        time.sleep(5 + responseDelay)
        # every 5 messages add extra delay
        if messageID % 5 == 0:
            time.sleep(10 + responseDelay)
        logger.debug(f"System: Sending bbslink message {messageID} of {len(bbs_messages)} to peer " + str(peerNode))
        msg = f"bbslink {messageID} ${bbs_messages[messageID][1]} #{bbs_messages[messageID][2]} @{fromNodeHex}"
        if useSynchCompression:
            compressed = compress_data(msg)
            send_raw_bytes(peerNode, compressed)
            logger.debug("System: Sent compressed bbslink message to peer " + str(peerNode))
        else:
            return msg
    else:
        logger.debug("System: bbslink sync complete with peer " + str(peerNode))


#initialize the bbsdb's
load_bbsdb()
load_bbsdm()
