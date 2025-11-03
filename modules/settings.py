# Settings for MeshBot and PongBot
# 2024 Kelly Keeton K7MHI
import configparser

# messages
NO_DATA_NOGPS = "No location data: does your device have GPS?"
ERROR_FETCHING_DATA = "error fetching data"
WELCOME_MSG = 'MeshBot, here for you like a friend who is not. Try sending: ping @foo  or, CMD? for more'
EMERGENCY_RESPONSE = "MeshBot detected a possible request for Emergency Assistance and alerted a wider audience."
MOTD = 'Thanks for using MeshBOT! Have a good day!'
NO_ALERTS = "No alerts found."

# setup the global variables
SITREP_NODE_COUNT = 3 # number of nodes to report in the sitrep
msg_history = [] # message history for the store and forward feature
bbs_ban_list = [] # list of banned users, imported from config
bbs_admin_list = [] # list of admin users, imported from config
repeater_channels = [] # list of channels to listen on for repeater mode, imported from config
antiSpam = True # anti-spam feature to prevent flooding public channel
ping_enabled = True # ping feature to respond to pings, ack's etc.
sitrep_enabled = True # sitrep feature to respond to sitreps
lastHamLibAlert = 0 # last alert from hamlib
lastFileAlert = 0 # last alert from file monitor
max_retry_count1 = max_retry_count2 = max_retry_count3 = max_retry_count4 = max_retry_count5 = max_retry_count6 = max_retry_count7 = max_retry_count8 = max_retry_count9 = 4 # default retry count for interfaces
retry_int1 = False
retry_int2 = False
wiki_return_limit = 3 # limit the number of sentences returned off the first paragraph first hit
GAMEDELAY = 28800 # 8 hours in seconds for game mode holdoff
cmdHistory = [] # list to hold the last commands
seenNodes = [] # list to hold the last seen nodes
cmdHistory = [] # list to hold the command history for lheard and history commands
msg_history = [] # list to hold the message history for the messages command
max_bytes = 200 # Meshtastic has ~237 byte limit, use conservative 200 bytes for message content
voxMsgQueue = [] # queue for VOX detected messages
tts_read_queue = [] # queue for TTS messages
wsjtxMsgQueue = [] # queue for WSJT-X detected messages
js8callMsgQueue = [] # queue for JS8Call detected messages
autoBanlist = [] # list of nodes to autoban for repeated offenses
apiThrottleList = [] # list of nodes to throttle API requests for repeated offenses
# Game trackers
surveyTracker = []           # Survey game tracker
tictactoeTracker = []        # TicTacToe game tracker
hamtestTracker = []          # Ham radio test tracker
hangmanTracker = []          # Hangman game tracker
golfTracker = []             # GolfSim game tracker
mastermindTracker = []       # Mastermind game tracker
vpTracker = []               # Video Poker game tracker
jackTracker = []             # Blackjack game tracker
lemonadeTracker = []         # Lemonade Stand game tracker
dwPlayerTracker = []         # DopeWars player tracker
jackTracker = []             # Jack game tracker
mindTracker = []             # Mastermind (mmind) game tracker

# Memory Management Constants
MAX_MSG_HISTORY = 250
MAX_CMD_HISTORY = 250
MAX_SEEN_NODES = 1000
CLEANUP_INTERVAL = 86400 # 24 hours in seconds
GAMEDELAY = 3 * CLEANUP_INTERVAL # 3 days in seconds

# Read the config file, if it does not exist, create basic config file
config = configparser.ConfigParser() 
config_file = "config.ini"

try:
    config.read(config_file, encoding='utf-8')
except Exception as e:
    print(f"System: Error reading config file: {e}")
    # exit if we can't read the config file
    print(f"System: Check the config.ini against config.template file for missing sections or values.")
    print(f"System: Exiting...")
    exit(1)

if config.sections() == []:
    print(f"System: Error reading config file: {config_file} is empty or does not exist.")
    config['interface'] = {'type': 'serial', 'port': "/dev/ttyACM0", 'hostname': '', 'mac': ''}
    config['general'] = {'respond_by_dm_only': 'True', 'defaultChannel': '0', 'motd': MOTD, 'welcome_message': WELCOME_MSG, 'zuluTime': 'False'}
    config.write(open(config_file, 'w'))
    print (f"System: Config file created, check {config_file} or review the config.template")

if 'sentry' not in config:
    config['sentry'] = {'SentryEnabled': 'False', 'SentryChannel': '2', 'SentryHoldoff': '9', 'sentryIgnoreList': '', 'SentryRadius': '100'}
    config.write(open(config_file, 'w'))

if 'location' not in config:
    config['location'] = {'enabled': 'True', 'lat': '48.50', 'lon': '-123.0', 'fuzzConfigLocation': 'True',}
    config.write(open(config_file, 'w'))

if 'bbs' not in config:
    config['bbs'] = {'enabled': 'False', 'bbsdb': 'data/bbsdb.pkl', 'bbs_ban_list': '', 'bbs_admin_list': ''}
    config.write(open(config_file, 'w'))

if 'repeater' not in config:
    config['repeater'] = {'enabled': 'False', 'repeater_channels': ''}
    config.write(open(config_file, 'w'))

if 'radioMon' not in config:
    config['radioMon'] = {'enabled': 'False', 'rigControlServerAddress': 'localhost:4532', 'sigWatchBrodcastCh': '2', 'signalDetectionThreshold': '-10', 'signalHoldTime': '10', 'signalCooldown': '5', 'signalCycleLimit': '5'}
    config.write(open(config_file, 'w'))

if 'games' not in config:
    config['games'] = {'dopeWars': 'True', 'lemonade': 'True', 'blackjack': 'True', 'videoPoker': 'True'}
    config.write(open(config_file, 'w'))

if 'messagingSettings' not in config:
    config['messagingSettings'] = {'responseDelay': '0.7', 'splitDelay': '0', 'MESSAGE_CHUNK_SIZE': '160'}
    config.write(open(config_file, 'w'))

if 'fileMon' not in config:
    config['fileMon'] = {'enabled': 'False', 'file_path': 'alert.txt', 'broadcastCh': '2'}
    config.write(open(config_file, 'w'))

if 'scheduler' not in config:
    config['scheduler'] = {'enabled': 'False'}
    config.write(open(config_file, 'w'))

if 'emergencyHandler' not in config:
    config['emergencyHandler'] = {'enabled': 'False', 'alert_channel': '2', 'alert_interface': '1', 'email': ''}
    config.write(open(config_file, 'w'))

if 'smtp' not in config:
    config['smtp'] = {'sysopEmails': '', 'enableSMTP': 'False', 'enableImap': 'False'}
    config.write(open(config_file, 'w'))

if 'checklist' not in config:
    config['checklist'] = {'enabled': 'False', 'checklist_db': 'data/checklist.db'}
    config.write(open(config_file, 'w'))

if 'qrz' not in config:
    config['qrz'] = {'enabled': 'False', 'qrz_db': 'data/qrz.db', 'qrz_hello_string': 'send CMD or DM me for more info.'}
    config.write(open(config_file, 'w'))

if 'inventory' not in config:
    config['inventory'] = {'enabled': 'False', 'inventory_db': 'data/inventory.db', 'disable_penny': 'False'}
    config.write(open(config_file, 'w'))

# interface1 settings
interface1_type = config['interface'].get('type', 'serial')
port1 = config['interface'].get('port', '')
hostname1 = config['interface'].get('hostname', '')
mac1 = config['interface'].get('mac', '')
interface1_enabled = True # gotta have at least one interface

# interface2 settings
if 'interface2' in config:
    interface2_type = config['interface2'].get('type', 'serial')
    port2 = config['interface2'].get('port', '')
    hostname2 = config['interface2'].get('hostname', '')
    mac2 = config['interface2'].get('mac', '')
    interface2_enabled = config['interface2'].getboolean('enabled', False)
else:
    interface2_enabled = False

# interface3 settings
if 'interface3' in config:
    interface3_type = config['interface3'].get('type', 'serial')
    port3 = config['interface3'].get('port', '')
    hostname3 = config['interface3'].get('hostname', '')
    mac3 = config['interface3'].get('mac', '')
    interface3_enabled = config['interface3'].getboolean('enabled', False)
else:
    interface3_enabled = False

# interface4 settings
if 'interface4' in config:
    interface4_type = config['interface4'].get('type', 'serial')
    port4 = config['interface4'].get('port', '')
    hostname4 = config['interface4'].get('hostname', '')
    mac4 = config['interface4'].get('mac', '')
    interface4_enabled = config['interface4'].getboolean('enabled', False)
else:
    interface4_enabled = False

# interface5 settings
if 'interface5' in config:
    interface5_type = config['interface5'].get('type', 'serial')
    port5 = config['interface5'].get('port', '')
    hostname5 = config['interface5'].get('hostname', '')
    mac5 = config['interface5'].get('mac', '')
    interface5_enabled = config['interface5'].getboolean('enabled', False)
else:
    interface5_enabled = False

# interface6 settings
if 'interface6' in config:
    interface6_type = config['interface6'].get('type', 'serial')
    port6 = config['interface6'].get('port', '')
    hostname6 = config['interface6'].get('hostname', '')
    mac6 = config['interface6'].get('mac', '')
    interface6_enabled = config['interface6'].getboolean('enabled', False)
else:
    interface6_enabled = False

# interface7 settings
if 'interface7' in config:
    interface7_type = config['interface7'].get('type', 'serial')
    port7 = config['interface7'].get('port', '')
    hostname7 = config['interface7'].get('hostname', '')
    mac7 = config['interface7'].get('mac', '')
    interface7_enabled = config['interface7'].getboolean('enabled', False)
else:
    interface7_enabled = False

# interface8 settings
if 'interface8' in config:
    interface8_type = config['interface8'].get('type', 'serial')
    port8 = config['interface8'].get('port', '')
    hostname8 = config['interface8'].get('hostname', '')
    mac8 = config['interface8'].get('mac', '')
    interface8_enabled = config['interface8'].getboolean('enabled', False)
else:
    interface8_enabled = False

# interface9 settings
if 'interface9' in config:
    interface9_type = config['interface9'].get('type', 'serial')
    port9 = config['interface9'].get('port', '')
    hostname9 = config['interface9'].get('hostname', '')
    mac9 = config['interface9'].get('mac', '')
    interface9_enabled = config['interface9'].getboolean('enabled', False)
else:
    interface9_enabled = False

multiple_interface = False
if interface2_enabled or interface3_enabled or interface4_enabled or interface5_enabled or interface6_enabled or interface7_enabled or interface8_enabled or interface9_enabled:
    multiple_interface = True
    

# variables from the config.ini file
try:
    # general
    useDMForResponse = config['general'].getboolean('respond_by_dm_only', True)
    publicChannel = config['general'].getint('defaultChannel', 0) # the meshtastic public channel
    ignoreChannels = config['general'].get('ignoreChannels', '').split(',') # ignore these channels
    ignoreDefaultChannel = config['general'].getboolean('ignoreDefaultChannel', False)
    cmdBang = config['general'].getboolean('cmdBang', False) # default off
    explicitCmd = config['general'].getboolean('explicitCmd', True) # default on
    zuluTime = config['general'].getboolean('zuluTime', False) # aka 24 hour time
    log_messages_to_file = config['general'].getboolean('LogMessagesToFile', False) # default off
    log_backup_count = config['general'].getint('LogBackupCount', 32) # default 32 days
    syslog_to_file = config['general'].getboolean('SyslogToFile', True) # default on
    LOGGING_LEVEL = config['general'].get('sysloglevel', 'DEBUG') # default DEBUG
    urlTimeoutSeconds = config['general'].getint('urlTimeout', 15) # default 15 seconds for URL fetch timeout
    store_forward_enabled = config['general'].getboolean('StoreForward', True)
    storeFlimit = config['general'].getint('StoreLimit', 3) # default 3 messages for S&F
    reverseSF = config['general'].getboolean('reverseSF', False) # default False, send oldest first
    welcome_message = config['general'].get('welcome_message', WELCOME_MSG)
    welcome_message = (f"{welcome_message}").replace('\\n', '\n') # allow for newlines in the welcome message
    motd_enabled = config['general'].getboolean('motdEnabled', True)
    MOTD = config['general'].get('motd', MOTD)
    autoPingInChannel = config['general'].getboolean('autoPingInChannel', False)
    enableCmdHistory = config['general'].getboolean('enableCmdHistory', True)
    lheardCmdIgnoreNode = config['general'].get('lheardCmdIgnoreNode', '').split(',')
    whoami_enabled = config['general'].getboolean('whoami', True)
    dad_jokes_enabled = config['general'].getboolean('DadJokes', False)
    dad_jokes_emojiJokes = config['general'].getboolean('DadJokesEmoji', False)
    bee_enabled = config['general'].getboolean('bee', False) # 🐝 off by default undocumented
    solar_conditions_enabled = config['general'].getboolean('spaceWeather', True)
    wikipedia_enabled = config['general'].getboolean('wikipedia', False)
    use_kiwix_server = config['general'].getboolean('useKiwixServer', False)
    kiwix_url = config['general'].get('kiwixURL', 'http://127.0.0.1:8080')
    kiwix_library_name = config['general'].get('kiwixLibraryName', 'wikipedia_en_100_nopic_2024-06')
    llm_enabled = config['general'].getboolean('ollama', False) # https://ollama.com
    ollamaHostName = config['general'].get('ollamaHostName', 'http://localhost:11434') # default localhost
    llmModel = config['general'].get('ollamaModel', 'gemma3:270m') # default gemma3:270m
    rawLLMQuery = config['general'].getboolean('rawLLMQuery', True) #default True
    llmReplyToNonCommands = config['general'].getboolean('llmReplyToNonCommands', True) # default True
    llmUseWikiContext = config['general'].getboolean('llmUseWikiContext', False) # default False
    useOpenWebUI = config['general'].getboolean('useOpenWebUI', False) # default False
    openWebUIURL = config['general'].get('openWebUIURL', 'http://localhost:3000') # default localhost:3000
    openWebUIAPIKey = config['general'].get('openWebUIAPIKey', '') # default empty
    dont_retry_disconnect = config['general'].getboolean('dont_retry_disconnect', False) # default False, retry on disconnect
    favoriteNodeList = config['general'].get('favoriteNodeList', '').split(',')
    enableEcho = config['general'].getboolean('enableEcho', False) # default False
    echoChannel = config['general'].getint('echoChannel', '9') # default 9, empty string to ignore
    rssEnable = config['general'].getboolean('rssEnable', True) # default True
    rssFeedURL = config['general'].get('rssFeedURL', 'http://www.hackaday.com/rss.xml,https://www.arrl.org/rss/arrl.rss').split(',')
    rssMaxItems = config['general'].getint('rssMaxItems', 3) # default 3 items
    rssTruncate = config['general'].getint('rssTruncate', 100) # default 100 characters
    rssFeedNames = config['general'].get('rssFeedNames', 'default,arrl').split(',')
    newsAPI_KEY = config['general'].get('newsAPI_KEY', '') # default empty
    newsAPIregion = config['general'].get('newsAPIregion', 'us') # default us
    enable_headlines = config['general'].getboolean('enableNewsAPI', False) # default False
    newsAPIsort = config['general'].get('sort_by', 'relevancy') # default publishedAt

    # sentry
    sentry_enabled = config['sentry'].getboolean('SentryEnabled', False) # default False
    secure_channel = config['sentry'].getint('SentryChannel', 2) # default 2
    secure_interface = config['sentry'].getint('SentryInterface', 1) # default 1
    sentry_holdoff = config['sentry'].getint('SentryHoldoff', 9) # default 9
    sentryIgnoreList = config['sentry'].get('sentryIgnoreList', '').split(',')
    sentryWatchList = config['sentry'].get('sentryWatchList', '').split(',')
    sentry_radius = config['sentry'].getint('SentryRadius', 100) # default 100 meters
    email_sentry_alerts = config['sentry'].getboolean('emailSentryAlerts', False) # default False
    highfly_enabled = config['sentry'].getboolean('highFlyingAlert', True) # default True
    highfly_altitude = config['sentry'].getint('highFlyingAlertAltitude', 2000) # default 2000 meters
    highfly_channel = config['sentry'].getint('highFlyingAlertChannel', 2) # default 2
    highfly_interface = config['sentry'].getint('highFlyingAlertInterface', 1) # default 1
    highfly_ignoreList = config['sentry'].get('highFlyingIgnoreList', '').split(',') # default empty
    highfly_check_openskynetwork = config['sentry'].getboolean('highflyOpenskynetwork', True) # default True check with OpenSkyNetwork if highfly detected
    detctionSensorAlert = config['sentry'].getboolean('detectionSensorAlert', False) # default False
    reqLocationEnabled = config['sentry'].getboolean('reqLocationEnabled', False) # default False
    cmdShellSentryAlerts = config['sentry'].getboolean('cmdShellSentryAlerts', False) # default False
    sentryAlertNear = config['sentry'].get('sentryAlertNear', 'sentry_alert_near.sh') # default sentry_alert_near.sh
    sentryAlertFar = config['sentry'].get('sentryAlertFar', 'sentry_alert_far.sh') # default sentry_alert_far.sh

    # location
    location_enabled = config['location'].getboolean('enabled', True)
    latitudeValue = config['location'].getfloat('lat', 48.50)
    longitudeValue = config['location'].getfloat('lon', -123.0)
    fuzz_config_location = config['location'].getboolean('fuzzConfigLocation', True) # default True
    fuzzItAll = config['location'].getboolean('fuzzAllLocations', False) # default False, only fuzz config location
    use_meteo_wxApi = config['location'].getboolean('UseMeteoWxAPI', False) # default False use NOAA
    use_metric = config['location'].getboolean('useMetric', False) # default Imperial units
    repeater_lookup = config['location'].get('repeaterLookup', 'rbook') # default repeater lookup source
    n2yoAPIKey = config['location'].get('n2yoAPIKey', '') # default empty
    satListConfig = config['location'].get('satList', '25544').split(',') # default 25544 ISS
    riverListDefault = config['location'].get('riverList', '').split(',') # default None
    coastalEnabled = config['location'].getboolean('coastalEnabled', False) # default False
    myCoastalZone = config['location'].get('myCoastalZone', None) # default None
    coastalForecastDays = config['location'].getint('coastalForecastDays', 3) # default 3 days

    # location alerts
    eAlertBroadcastEnabled = config['location'].getboolean('eAlertBroadcastEnabled', False) # old deprecated name
    ipawsAlertEnabled = config['location'].getboolean('ipawsAlertEnabled', False) # default False new ^
    # Keep both in sync for backward compatibility
    if eAlertBroadcastEnabled or ipawsAlertEnabled:
        eAlertBroadcastEnabled = True
        ipawsAlertEnabled = True
    wxAlertBroadcastEnabled = config['location'].getboolean('wxAlertBroadcastEnabled', False) # default False
    volcanoAlertBroadcastEnabled = config['location'].getboolean('volcanoAlertBroadcastEnabled', False) # default False
    enableGBalerts = config['location'].getboolean('enableGBalerts', False) # default False
    enableDEalerts = config['location'].getboolean('enableDEalerts', False) # default False

    ignoreEASenable = config['location'].getboolean('ignoreEASenable', False) # default False
    ignoreEASwords = config['location'].get('ignoreEASwords', 'test,advisory').split(',') # default test,advisory
    ignoreFEMAenable = config['location'].getboolean('ignoreFEMAenable', True) # default True
    ignoreFEMAwords = config['location'].get('ignoreFEMAwords', 'test,exercise').split(',') # default test,exercise
    ignoreUSGSEnable = config['location'].getboolean('ignoreVolcanoEnable', False) # default False
    ignoreUSGSWords = config['location'].get('ignoreVolcanoWords', 'test,advisory').split(',') # default test,advisory
    
    forecastDuration = config['location'].getint('NOAAforecastDuration', 4) # NOAA forcast days
    numWxAlerts = config['location'].getint('NOAAalertCount', 2) # default 2 alerts
    enableExtraLocationWx = config['location'].getboolean('enableExtraLocationWx', False) # default False
    myStateFIPSList = config['location'].get('myFIPSList', '').split(',') # default empty
    mySAMEList = config['location'].get('mySAMEList', '').split(',') # default empty
    myRegionalKeysDE = config['location'].get('myRegionalKeysDE', '110000000000').split(',') # default city Berlin
    eAlertBroadcastChannel = config['location'].get('eAlertBroadcastCh', '').split(',') # default empty

    # any US alerts enabled
    usAlerts = (
        ipawsAlertEnabled or
        wxAlertBroadcastEnabled or
        volcanoAlertBroadcastEnabled or
        eAlertBroadcastEnabled
        )
    
    # emergency response
    emergency_responder_enabled = config['emergencyHandler'].getboolean('enabled', False)
    emergency_responder_alert_channel = config['emergencyHandler'].getint('alert_channel', 2) # default 2
    emergency_responder_alert_interface = config['emergencyHandler'].getint('alert_interface', 1) # default 1
    emergency_responder_email = config['emergencyHandler'].get('email', '').split(',')


    # bbs
    bbs_enabled = config['bbs'].getboolean('enabled', False)
    bbsdb = config['bbs'].get('bbsdb', 'data/bbsdb.pkl')
    bbs_ban_list = config['bbs'].get('bbs_ban_list', '').split(',')
    bbs_admin_list = config['bbs'].get('bbs_admin_list', '').split(',')
    bbs_link_enabled = config['bbs'].getboolean('bbslink_enabled', False)
    bbs_link_whitelist = config['bbs'].get('bbslink_whitelist', '').split(',')
    bbsAPI_enabled = config['bbs'].getboolean('bbsAPI_enabled', False)
    
    # checklist
    checklist_enabled = config['checklist'].getboolean('enabled', False)
    checklist_db = config['checklist'].get('checklist_db', 'data/checklist.db')
    reverse_in_out = config['checklist'].getboolean('reverse_in_out', False)
    checklist_auto_approve = config['checklist'].getboolean('auto_approve', True) # default True

    # qrz hello
    qrz_hello_enabled = config['qrz'].getboolean('enabled', False)
    qrz_db = config['qrz'].get('qrz_db', 'data/qrz.db')
    qrz_hello_string = config['qrz'].get('qrz_hello_string', 'MeshBot says Hello! DM for more info.')
    train_qrz = config['qrz'].getboolean('training', True)
    
    # inventory and POS
    inventory_enabled = config['inventory'].getboolean('enabled', False)
    inventory_db = config['inventory'].get('inventory_db', 'data/inventory.db')
    disable_penny = config['inventory'].getboolean('disable_penny', False)
    
    # E-Mail Settings
    sysopEmails = config['smtp'].get('sysopEmails', '').split(',')
    enableSMTP = config['smtp'].getboolean('enableSMTP', False)
    enableImap = config['smtp'].getboolean('enableImap', False)
    SMTP_SERVER = config['smtp'].get('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = config['smtp'].getint('SMTP_PORT', 587)
    FROM_EMAIL = config['smtp'].get('FROM_EMAIL', 'none@gmail.com')
    SMTP_AUTH = config['smtp'].getboolean('SMTP_AUTH', True)
    SMTP_USERNAME = config['smtp'].get('SMTP_USERNAME', FROM_EMAIL)
    SMTP_PASSWORD = config['smtp'].get('SMTP_PASSWORD', 'password')
    EMAIL_SUBJECT = config['smtp'].get('EMAIL_SUBJECT', 'Meshtastic✉️')
    IMAP_SERVER = config['smtp'].get('IMAP_SERVER', 'imap.gmail.com')
    IMAP_PORT = config['smtp'].getint('IMAP_PORT', 993)
    IMAP_USERNAME = config['smtp'].get('IMAP_USERNAME', SMTP_USERNAME)
    IMAP_PASSWORD = config['smtp'].get('IMAP_PASSWORD', SMTP_PASSWORD)
    IMAP_FOLDER = config['smtp'].get('IMAP_FOLDER', 'inbox')

    # repeater
    repeater_enabled = config['repeater'].getboolean('enabled', False)
    repeater_channels = config['repeater'].get('repeater_channels', '').split(',')

    # scheduler
    scheduler_enabled = config['scheduler'].getboolean('enabled', False)
    schedulerInterface = config['scheduler'].getint('interface', 1) # default interface 1
    schedulerChannel = config['scheduler'].getint('channel', 2) # default channel 2
    schedulerMessage = config['scheduler'].get('message', 'Scheduled message') # default message
    schedulerInterval = config['scheduler'].get('interval', '') # default empty
    schedulerTime = config['scheduler'].get('time', '') # default empty
    schedulerValue = config['scheduler'].get('value', '') # default empty
    schedulerMotd = config['scheduler'].getboolean('schedulerMotd', False) # default False

    # radio monitoring
    radio_detection_enabled = config['radioMon'].getboolean('enabled', False)
    dxspotter_enabled = config['radioMon'].getboolean('dxspotter_enabled', True) # default True
    rigControlServerAddress = config['radioMon'].get('rigControlServerAddress', 'localhost:4532') # default localhost:4532
    sigWatchBroadcastCh = config['radioMon'].get('sigWatchBroadcastCh', '2').split(',') # default Channel 2
    sigWatchBroadcastInterface = config['radioMon'].getint('sigWatchBroadcastInterface', 1) # default interface 1
    signalDetectionThreshold = config['radioMon'].getint('signalDetectionThreshold', -10) # default -10 dBm
    signalHoldTime = config['radioMon'].getint('signalHoldTime', 10) # default 10 seconds
    signalCooldown = config['radioMon'].getint('signalCooldown', 5) # default 1 second
    signalCycleLimit = config['radioMon'].getint('signalCycleLimit', 5) # default 5 cycles, used with SIGNAL_COOLDOWN
    voxDetectionEnabled = config['radioMon'].getboolean('voxDetectionEnabled', False) # default VOX detection disabled
    voxDescription = config['radioMon'].get('voxDescription', 'VOX') # default VOX detected audio message
    useLocalVoxModel = config['radioMon'].getboolean('useLocalVoxModel', False) # default False
    localVoxModelPath = config['radioMon'].get('localVoxModelPath', 'no') # default models/vox.tflite
    voxLanguage = config['radioMon'].get('voxLanguage', 'en-US') # default en-US
    voxInputDevice = config['radioMon'].get('voxInputDevice', 'default') # default default
    voxOnTrapList = config['radioMon'].getboolean('voxOnTrapList', False) # default False
    voxTrapList = config['radioMon'].get('voxTrapList', 'chirpy').split(',') # default chirpy
    voxEnableCmd = config['radioMon'].getboolean('voxEnableCmd', True) # default True
    meshagesTTS = config['radioMon'].getboolean('meshagesTTS', False) # default False
    ttsChannels = config['radioMon'].get('ttsChannels', '2').split(',') # default Channel 2
    ttsnoWelcome = config['radioMon'].getboolean('ttsnoWelcome', False) # default False
    
    # WSJT-X and JS8Call monitoring
    wsjtx_detection_enabled = config['radioMon'].getboolean('wsjtxDetectionEnabled', False) # default WSJT-X detection disabled
    wsjtx_udp_server_address = config['radioMon'].get('wsjtxUdpServerAddress', '127.0.0.1:2237') # default localhost:2237
    wsjtx_watched_callsigns = config['radioMon'].get('wsjtxWatchedCallsigns', '') # default empty (all callsigns)
    js8call_detection_enabled = config['radioMon'].getboolean('js8callDetectionEnabled', False) # default JS8Call detection disabled
    js8call_server_address = config['radioMon'].get('js8callServerAddress', '127.0.0.1:2442') # default localhost:2442
    js8call_watched_callsigns = config['radioMon'].get('js8callWatchedCallsigns', '') # default empty (all callsigns)

    # file monitor
    file_monitor_enabled = config['fileMon'].getboolean('filemon_enabled', False)
    file_monitor_file_path = config['fileMon'].get('file_path', 'alert.txt') # default alert.txt
    file_monitor_broadcastCh = config['fileMon'].get('broadcastCh', '2').split(',') # default Channel 2
    read_news_enabled = config['fileMon'].getboolean('enable_read_news', False) # default disabled
    news_file_path = config['fileMon'].get('news_file_path', '../data/news.txt') # default ../data/news.txt
    news_random_line_only = config['fileMon'].getboolean('news_random_line', False) # default False
    news_block_mode = config['fileMon'].getboolean('news_block_mode', False) # default False
    if news_random_line_only and news_block_mode:
        news_random_line_only = False
    enable_runShellCmd = config['fileMon'].getboolean('enable_runShellCmd', False) # default False
    allowXcmd = config['fileMon'].getboolean('allowXcmd', False) # default False
    xCmd2factorEnabled = config['fileMon'].getboolean('twoFactor_enabled', True) # default True
    xCmd2factor_timeout = config['fileMon'].getint('twoFactor_timeout', 100) # default 100 seconds

    # games
    game_hop_limit = config['games'].getint('game_hop_limit', 5) # default 5 hops
    disable_emojis_in_games = config['games'].getboolean('disable_emojis', False) # default False
    dopewars_enabled = config['games'].getboolean('dopeWars', True)
    lemonade_enabled = config['games'].getboolean('lemonade', True)
    blackjack_enabled = config['games'].getboolean('blackjack', True)
    videoPoker_enabled = config['games'].getboolean('videoPoker', True)
    mastermind_enabled = config['games'].getboolean('mastermind', True)
    golfSim_enabled = config['games'].getboolean('golfSim', True)
    hangman_enabled = config['games'].getboolean('hangman', True)
    hamtest_enabled = config['games'].getboolean('hamtest', True)
    tictactoe_enabled = config['games'].getboolean('tictactoe', True)
    quiz_enabled = config['games'].getboolean('quiz', False)
    survey_enabled = config['games'].getboolean('survey', False)
    default_survey = config['games'].get('defaultSurvey', 'example') # default example
    surveyRecordID = config['games'].getboolean('surveyRecordID', True)
    surveyRecordLocation = config['games'].getboolean('surveyRecordLocation', True)
    wordOfTheDay = config['games'].getboolean('wordOfTheDay', True)

    # messaging settings
    responseDelay = config['messagingSettings'].getfloat('responseDelay', 0.7) # default 0.7
    splitDelay = config['messagingSettings'].getfloat('splitDelay', 0) # default 0
    MESSAGE_CHUNK_SIZE = config['messagingSettings'].getint('MESSAGE_CHUNK_SIZE', 160) # default 160 chars
    wantAck = config['messagingSettings'].getboolean('wantAck', False) # default False
    maxBuffer = config['messagingSettings'].getint('maxBuffer', 200) # default 200 bytes
    enableHopLogs = config['messagingSettings'].getboolean('enableHopLogs', False) # default False
    debugMetadata = config['messagingSettings'].getboolean('debugMetadata', False) # default False
    metadataFilter = config['messagingSettings'].get('metadataFilter', '').split(',') # default empty
    DEBUGpacket = config['messagingSettings'].getboolean('DEBUGpacket', False) # default False
    noisyNodeLogging = config['messagingSettings'].getboolean('noisyNodeLogging', False) # default False
    logMetaStats = config['messagingSettings'].getboolean('logMetaStats', True) # default True
    noisyTelemetryLimit = config['messagingSettings'].getint('noisyTelemetryLimit', 5) # default 5 packets
    autoBanEnabled = config['messagingSettings'].getboolean('autoBanEnabled', False) # default False
    autoBanThreshold = config['messagingSettings'].getint('autoBanThreshold', 5) # default 5 offenses
    autoBanTimeframe = config['messagingSettings'].getint('autoBanTimeframe', 3600) # default 1 hour in seconds
    apiThrottleValue = config['messagingSettings'].getint('apiThrottleValue', 20) # default 20 requests
except Exception as e:
    print(f"System: Error reading config file: {e}")
    print("System: Check the config.ini against config.template file for missing sections or values.")
    print("System: Exiting...")
    exit(1)
