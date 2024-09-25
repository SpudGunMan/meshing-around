# Load the bbs messages from the database file to screen for admin functions
import pickle # pip install pickle


# load the bbs messages from the database file
try:
    with open('../bbsdb.pkl', 'rb') as f:
        bbs_messages = pickle.load(f)
except Exception as e:
    try:
        with open('bbsdb.pkl', 'rb') as f:
            bbs_messages = pickle.load(f)
    except Exception as e:
        print ("\nSystem: bbsdb.pkl not found")

try:
    with open('../bbsdm.pkl', 'rb') as f:
        bbs_dm = pickle.load(f)
except Exception as e:
    try:
        with open('bbsdm.pkl', 'rb') as f:
            bbs_dm = pickle.load(f)
    except Exception as e:
        print ("\nSystem: bbsdm.pkl not found")

# Game HS tables
try:
    with open('../lemonade_hs.pkl', 'rb') as f:
       lemon_score = pickle.load(f)
except Exception as e:
    try:
        with open('lemonade_hs.pkl', 'rb') as f:
            lemon_score = pickle.load(f)
    except Exception as e:
        print ("\nSystem: lemonade_hs.pkl not found")

try:
    with open('../dopewar_hs.pkl', 'rb') as f:
        dopewar_score = pickle.load(f)
except Exception as e:
    try:
        with open('dopewar_hs.pkl', 'rb') as f:
            dopewar_score = pickle.load(f)
    except Exception as e:
        print ("\nSystem: dopewar_hs.pkl not found")


print ("\nSystem: bbs_messages")
print (bbs_messages)
print ("\nSystem: bbs_dm")
print (bbs_dm)
print ("Game HS tables")
print (f"lemon:{lemon_score}")
print (f"dopewar:{dopewar_score}")