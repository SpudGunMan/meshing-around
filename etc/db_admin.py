# Load the bbs messages from the database file to screen for admin functions
import pickle # pip install pickle


# load the bbs messages from the database file
try:
    with open('../data/bbsdb.pkl', 'rb') as f:
        bbs_messages = pickle.load(f)
except Exception as e:
    try:
        with open('data/bbsdb.pkl', 'rb') as f:
            bbs_messages = pickle.load(f)
    except Exception as e:
        bbs_messages = "System: data/bbsdb.pkl not found"

try:
    with open('../data/bbsdm.pkl', 'rb') as f:
        bbs_dm = pickle.load(f)
except Exception as e:
    try:
        with open('data/bbsdm.pkl', 'rb') as f:
            bbs_dm = pickle.load(f)
    except Exception as e:
        bbs_dm = "System: data/bbsdm.pkl not found"

try:
    with open('../data/email_db.pickle', 'rb') as f:
        email_db = pickle.load(f)
except Exception as e:
    try:
        with open('data/email_db.pickle', 'rb') as f:
            email_db = pickle.load(f)
    except Exception as e:
        email_db = "System: data/email_db.pickle not found"

try:
    with open('../data/sms_db.pickle', 'rb') as f:
        sms_db = pickle.load(f)
except Exception as e:
    try:
        with open('data/sms_db.pickle', 'rb') as f:
            sms_db = pickle.load(f)
    except Exception as e:
        sms_db = "System: data/sms_db.pickle not found"


# Game HS tables
try:
    with open('../data/lemonstand.pkl', 'rb') as f:
       lemon_score = pickle.load(f)
except Exception as e:
    try:
        with open('data/lemonstand.pkl', 'rb') as f:
            lemon_score = pickle.load(f)
    except Exception as e:
        lemon_score = "System: data/lemonstand.pkl not found"

try:
    with open('../data/dopewar_hs.pkl', 'rb') as f:
        dopewar_score = pickle.load(f)
except Exception as e:
    try:
        with open('data/dopewar_hs.pkl', 'rb') as f:
            dopewar_score = pickle.load(f)
    except Exception as e:
        dopewar_score = "System: data/dopewar_hs.pkl not found"

try:
    with open('../data/blackjack_hs.pkl', 'rb') as f:
        blackjack_score = pickle.load(f)
except Exception as e:
    try:
        with open('data/blackjack_hs.pkl', 'rb') as f:
            blackjack_score = pickle.load(f)
    except Exception as e:
        blackjack_score = "System: data/blackjack_hs.pkl not found"

try:
    with open('../data/videopoker_hs.pkl', 'rb') as f:
        videopoker_score = pickle.load(f)
except Exception as e:
    try:
        with open('data/videopoker_hs.pkl', 'rb') as f:
            videopoker_score = pickle.load(f)
    except Exception as e:
        videopoker_score = "System: data/videopoker_hs.pkl not found"

try:
    with open('../mmind_hs.pkl', 'rb') as f:
        mmind_score = pickle.load(f)
except Exception as e:
    try:
        with open('mmind_hs.pkl', 'rb') as f:
            mmind_score = pickle.load(f)
    except Exception as e:
        mmind_score = "System: mmind_hs.pkl not found"

try:
    with open('../data/golfsim_hs.pkl', 'rb') as f:
        golfsim_score = pickle.load(f)
except Exception as e:
    try:
        with open('data/golfsim_hs.pkl', 'rb') as f:
            golfsim_score = pickle.load(f)
    except Exception as e:
        golfsim_score = "System: data/golfsim_hs.pkl not found"


print ("\n Meshing-Around Database Admin Tool\n")
print ("System: bbs_messages")
print (bbs_messages)
print ("\nSystem: bbs_dm")
print (bbs_dm)
print ("\nSystem: email_db")
print (email_db)
print ("\nSystem: sms_db")
print (sms_db)
print (f"\n\nGame HS tables\n")
print (f"lemon:{lemon_score}")
print (f"dopewar:{dopewar_score}")
print (f"blackjack:{blackjack_score}")
print (f"videopoker:{videopoker_score}")
print (f"mmind:{mmind_score}")
print (f"golfsim:{golfsim_score}")
print ("\n")
