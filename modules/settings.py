import configparser

# messages
NO_DATA_NOGPS = "No location data: does your device have GPS?"
ERROR_FETCHING_DATA = "error fetching data"
WELCOME_MSG = 'MeshBot, here for you like a friend who is not. Try sending: ping @foo  or, cmd'
MOTD = 'Thanks for using MeshBOT! Have a good day!'
NO_ALERTS = "No weather alerts found."

# setup the global variables
MESSAGE_CHUNK_SIZE = 160 # message chunk size for sending at high success rate
SITREP_NODE_COUNT = 3 # number of nodes to report in the sitrep
msg_history = [] # message history for the store and forward feature
bbs_ban_list = [] # list of banned users
bbs_admin_list = [] # list of admin users
repeater_channels = [] # list of channels to listen on for repeater mode
antiSpam = True # anti-spam feature to prevent flooding public channel
ping_enabled = True # ping feature to respond to pings, ack's etc.
sitrep_enabled = True # sitrep feature to respond to sitreps
lastHamLibAlert = 0 # last alert from hamlib

# Read the config file, if it does not exist, create basic config file
config = configparser.ConfigParser() 
config_file = "config.ini"

try:
    config.read(config_file)
except Exception as e:
    print(f"System: Error reading config file: {e}")

if config.sections() == []:
    print(f"System: Error reading config file: {config_file} is empty or does not exist.")
    config['interface'] = {'type': 'serial', 'port': "/dev/ttyACM0", 'hostname': '', 'mac': ''}
    config['general'] = {'respond_by_dm_only': 'True', 'defaultChannel': '0', 'motd': MOTD,
                         'welcome_message': WELCOME_MSG, 'zuluTime': 'False'}
    config.write(open(config_file, 'w'))
    print (f"System: Config file created, check {config_file} or review the config.template")

# interface1 settings
interface1_type = config['interface'].get('type', 'serial')
port1 = config['interface'].get('port', '')
hostname1 = config['interface'].get('hostname', '')
mac1 = config['interface'].get('mac', '')

# interface2 settings
if 'interface2' in config:
    interface2_type = config['interface2'].get('type', 'serial')
    port2 = config['interface2'].get('port', '')
    hostname2 = config['interface2'].get('hostname', '')
    mac2 = config['interface2'].get('mac', '')
    interface2_enabled = config['interface2'].getboolean('enabled', False)
else:
    interface2_enabled = False

# variables
try:
    storeFlimit = config['general'].getint('StoreLimit', 3) # default 3 messages for S&F
    useDMForResponse = config['general'].getboolean('respond_by_dm_only', True)
    publicChannel = config['general'].getint('defaultChannel', 0) # the meshtastic public channel
    location_enabled = config['location'].getboolean('enabled', False)
    latitudeValue = config['location'].getfloat('lat', 48.50)
    longitudeValue = config['location'].getfloat('lon', -123.0)
    zuluTime = config['general'].getboolean('zuluTime', False)
    welcome_message = config['general'].get(f'welcome_message', WELCOME_MSG)
    welcome_message = (f"{welcome_message}").replace('\\n', '\n') # allow for newlines in the welcome message
    solar_conditions_enabled = config['solar'].getboolean('enabled', False)
    bbs_enabled = config['bbs'].getboolean('enabled', False)
    bbsdb = config['bbs'].get('bbsdb', 'bbsdb.pkl')
    dad_jokes_enabled = config['general'].getboolean('DadJokes', False)
    store_forward_enabled = config['general'].getboolean('StoreForward', False)
    config['general'].get('motd', MOTD)
    urlTimeoutSeconds = config['general'].getint('URL_TIMEOUT', 10) # default 10 seconds
    forecastDuration = config['general'].getint('DAYS_OF_WEATHER', 4) # default days of weather
    numWxAlerts = config['general'].getint('ALERT_COUNT', 2) # default 2 alerts
    bbs_ban_list = config['bbs'].get('bbs_ban_list', '').split(',')
    bbs_admin_list = config['bbs'].get('bbs_admin_list', '').split(',')
    repeater_enabled = config['repeater'].getboolean('enabled', False)
    repeater_channels = config['repeater'].get('repeater_channels', '').split(',')
    radio_dectection_enabled = config['radioMon'].getboolean('enabled', False)
    rigControlServerAddress = config['radioMon'].get('rigControlServerAddress', 'localhost:4532') # default localhost:4532
    sigWatchBrodcastCh = config['radioMon'].get('sigWatchBrodcastCh', '2').split(',') # default Channel 2
    signalDetectionThreshold = config['radioMon'].getint('signalDetectionThreshold', -10) # default -10 dBm
    signalHoldTime = config['radioMon'].getint('signalHoldTime', 10) # default 10 seconds
    signalCooldown = config['radioMon'].getint('signalCooldown', 5) # default 1 second
    signalCycleLimit = config['radioMon'].getint('signalCycleLimit', 5) # default 5 cycles, used with SIGNAL_COOLDOWN
except KeyError as e:
    print(f"System: Error reading config file: {e}")
    print(f"System: Check the config.ini against config.template file for missing sections or values.")
    print(f"System: Exiting...")
    exit(1)

