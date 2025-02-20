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
max_retry_count1 = 4 # max retry count for interface 1
max_retry_count2 = 4 # max retry count for interface 2
retry_int1 = False
retry_int2 = False
wiki_return_limit = 3 # limit the number of sentences returned off the first paragraph first hit
playingGame = False
GAMEDELAY = 28800 # 8 hours in seconds for game mode holdoff
cmdHistory = [] # list to hold the last commands
seenNodes = [] # list to hold the last seen nodes

# Read the config file, if it does not exist, create basic config file
config = configparser.ConfigParser() 
config_file = "config.ini"

try:
    config.read(config_file, encoding='utf-8')
except Exception as e:
    print(f"System: Error reading config file: {e}")

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
    config['location'] = {'enabled': 'True', 'lat': '48.50', 'lon': '-123.0', 'UseMeteoWxAPI': 'False', 'useMetric': 'False', 'NOAAforecastDuration': '4', 'NOAAalertCount': '2', 'NOAAalertsEnabled': 'True', 'wxAlertBroadcastEnabled': 'False', 'wxAlertBroadcastChannel': '2', 'repeaterLookup': 'rbook'}
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
    ignoreDefaultChannel = config['general'].getboolean('ignoreDefaultChannel', False)
    zuluTime = config['general'].getboolean('zuluTime', False) # aka 24 hour time
    log_messages_to_file = config['general'].getboolean('LogMessagesToFile', False) # default off
    log_backup_count = config['general'].getint('LogBackupCount', 32) # default 32 days
    syslog_to_file = config['general'].getboolean('SyslogToFile', True) # default on
    LOGGING_LEVEL = config['general'].get('sysloglevel', 'DEBUG') # default DEBUG
    urlTimeoutSeconds = config['general'].getint('urlTimeout', 10) # default 10 seconds
    store_forward_enabled = config['general'].getboolean('StoreForward', True)
    storeFlimit = config['general'].getint('StoreLimit', 3) # default 3 messages for S&F
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
    llm_enabled = config['general'].getboolean('ollama', False) # https://ollama.com
    llmModel = config['general'].get('ollamaModel', 'gemma2:2b') # default gemma2:2b
    ollamaHostName = config['general'].get('ollamaHostName', 'http://localhost:11434') # default localhost
    # emergency response
    emergency_responder_enabled = config['emergencyHandler'].getboolean('enabled', False)
    emergency_responder_alert_channel = config['emergencyHandler'].getint('alert_channel', 2) # default 2
    emergency_responder_alert_interface = config['emergencyHandler'].getint('alert_interface', 1) # default 1
    emergency_responder_email = config['emergencyHandler'].get('email', '').split(',')

    # sentry
    sentry_enabled = config['sentry'].getboolean('SentryEnabled', False) # default False
    secure_channel = config['sentry'].getint('SentryChannel', 2) # default 2
    sentry_holdoff = config['sentry'].getint('SentryHoldoff', 9) # default 9
    sentryIgnoreList = config['sentry'].get('sentryIgnoreList', '').split(',')
    sentry_radius = config['sentry'].getint('SentryRadius', 100) # default 100 meters
    email_sentry_alerts = config['sentry'].getboolean('emailSentryAlerts', False) # default False

    # location
    location_enabled = config['location'].getboolean('enabled', True)
    latitudeValue = config['location'].getfloat('lat', 48.50)
    longitudeValue = config['location'].getfloat('lon', -123.0)
    use_meteo_wxApi = config['location'].getboolean('UseMeteoWxAPI', False) # default False use NOAA
    use_metric = config['location'].getboolean('useMetric', False) # default Imperial units
    repeater_lookup = config['location'].get('repeaterLookup', 'rbook') # default repeater lookup source
    n2yoAPIKey = config['location'].get('n2yoAPIKey', '') # default empty
    satListConfig = config['location'].get('satList', '25544').split(',') # default 25544 ISS
    riverListDefault = config['location'].get('riverList', '').split(',') # default 12061500 Skagit River
    # location alerts
    emergencyAlertBrodcastEnabled = config['location'].getboolean('eAlertBroadcastEnabled', False) # default False
    wxAlertBroadcastEnabled = config['location'].getboolean('wxAlertBroadcastEnabled', False) # default False
    enableGBalerts = config['location'].getboolean('enableGBalerts', False) # default False
    enableDEalerts = config['location'].getboolean('enableDEalerts', False) # default False
    wxAlertsEnabled = config['location'].getboolean('NOAAalertsEnabled', True) # default True
    mySAME = config['location'].get('mySAME', '').split(',') # default empty
    myRegionalKeysDE = config['location'].get('myRegionalKeysDE', '110000000000').split(',') # default city Berlin
    forecastDuration = config['location'].getint('NOAAforecastDuration', 4) # NOAA forcast days
    numWxAlerts = config['location'].getint('NOAAalertCount', 2) # default 2 alerts
    enableExtraLocationWx = config['location'].getboolean('enableExtraLocationWx', False) # default False
    ipawsPIN = config['location'].get('ipawsPIN', '000000') # default 000000
    ignoreFEMAword = config['location'].getboolean('ignoreFEMAword', True) # default True
    ignoreFEMAwords = config['location'].get('ignoreFEMAwords', 'test,exercise').split(',') # default test,exercise
    wxAlertBroadcastChannel = config['location'].get('wxAlertBroadcastCh', '2').split(',') # default Channel 2
    emergencyAlertBroadcastCh = config['location'].get('eAlertBroadcastCh', '2').split(',') # default Channel 2
    
    # bbs
    bbs_enabled = config['bbs'].getboolean('enabled', False)
    bbsdb = config['bbs'].get('bbsdb', 'data/bbsdb.pkl')
    bbs_ban_list = config['bbs'].get('bbs_ban_list', '').split(',')
    bbs_admin_list = config['bbs'].get('bbs_admin_list', '').split(',')
    bbs_link_enabled = config['bbs'].getboolean('bbslink_enabled', False)
    bbs_link_whitelist = config['bbs'].get('bbslink_whitelist', '').split(',')
    
    # checklist
    checklist_enabled = config['checklist'].getboolean('enabled', False)
    checklist_db = config['checklist'].get('checklist_db', 'data/checklist.db')
    reverse_in_out = config['checklist'].getboolean('reverse_in_out', False)

    # qrz hello
    qrz_hello_enabled = config['qrz'].getboolean('enabled', False)
    qrz_db = config['qrz'].get('qrz_db', 'data/qrz.db')
    qrz_hello_string = config['qrz'].get('qrz_hello_string', 'send CMD or DM me for more info.')
    train_qrz = config['qrz'].getboolean('training', True)
    
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

    # radio monitoring
    radio_detection_enabled = config['radioMon'].getboolean('enabled', False)
    rigControlServerAddress = config['radioMon'].get('rigControlServerAddress', 'localhost:4532') # default localhost:4532
    sigWatchBroadcastCh = config['radioMon'].get('sigWatchBroadcastCh', '2').split(',') # default Channel 2
    signalDetectionThreshold = config['radioMon'].getint('signalDetectionThreshold', -10) # default -10 dBm
    signalHoldTime = config['radioMon'].getint('signalHoldTime', 10) # default 10 seconds
    signalCooldown = config['radioMon'].getint('signalCooldown', 5) # default 1 second
    signalCycleLimit = config['radioMon'].getint('signalCycleLimit', 5) # default 5 cycles, used with SIGNAL_COOLDOWN

    # file monitor
    file_monitor_enabled = config['fileMon'].getboolean('filemon_enabled', False)
    file_monitor_file_path = config['fileMon'].get('file_path', 'alert.txt') # default alert.txt
    file_monitor_broadcastCh = config['fileMon'].getint('broadcastCh', 2) # default 2
    read_news_enabled = config['fileMon'].getboolean('enable_read_news', False) # default disabled
    news_file_path = config['fileMon'].get('news_file_path', 'news.txt') # default news.txt
    news_random_line_only = config['fileMon'].getboolean('news_random_line', False) # default False
    enable_runShellCmd = config['fileMon'].getboolean('enable_runShellCmd', False) # default False

    # games
    game_hop_limit = config['messagingSettings'].getint('game_hop_limit', 5) # default 3 hops
    dopewars_enabled = config['games'].getboolean('dopeWars', True)
    lemonade_enabled = config['games'].getboolean('lemonade', True)
    blackjack_enabled = config['games'].getboolean('blackjack', True)
    videoPoker_enabled = config['games'].getboolean('videoPoker', True)
    mastermind_enabled = config['games'].getboolean('mastermind', True)
    golfSim_enabled = config['games'].getboolean('golfSim', True)

    # messaging settings
    responseDelay = config['messagingSettings'].getfloat('responseDelay', 0.7) # default 0.7
    splitDelay = config['messagingSettings'].getfloat('splitDelay', 0) # default 0
    MESSAGE_CHUNK_SIZE = config['messagingSettings'].getint('MESSAGE_CHUNK_SIZE', 160) # default 160
    wantAck = config['messagingSettings'].getboolean('wantAck', False) # default False
    maxBuffer = config['messagingSettings'].getint('maxBuffer', 220) # default 220

except KeyError as e:
    print(f"System: Error reading config file: {e}")
    print(f"System: Check the config.ini against config.template file for missing sections or values.")
    print(f"System: Exiting...")
    exit(1)
