import configparser

# Read the config file
config = configparser.ConfigParser() 
config_file = "config.ini"

try:
    config.read(config_file)
except Exception as e:
    print(f"System: Error reading config file: {e}")

if config.sections() == []:
    print(f"System: Error reading config file: {config_file} is empty or does not exist.")
    config['interface'] = {'type': 'serial', 'port': "/dev/ttyACM0", 'hostname': '', 'mac': ''}
    config['general'] = {'respond_by_dm_only': 'True', 'defaultChannel': '0', 'motd': 'Thanks for using MeshBOT! Have a good day!',
                         'welcome_message': 'MeshBot, here for you like a friend who is not. Try sending: ping @foo  or, cmd',
                         'DadJokes': 'True', 'StoreForward': 'True', 'StoreLimit': '3'}
    config['bbs'] = {'enabled': 'True', 'bbsdb': 'bbsdb.pkl'}
    config['location'] = {'enabled': 'True','lat': '48.50', 'lon': '-123.0'}
    config['solar'] = {'enabled': 'True'}
    config.write(open(config_file, 'w'))
    print (f"System: Config file created, check {config_file} or review the config.template")

# config.ini variables
interface_type = config['interface'].get('type', 'serial')
port = config['interface'].get('port', '')
hostname = config['interface'].get('hostname', '')
mac = config['interface'].get('mac', '')
msg_history = [] # message history for the store and forward feature
storeFlimit = config['general'].getint('StoreLimit', 3) # limit of messages to store for Store and Forward

RESPOND_BY_DM_ONLY = config['general'].getboolean('respond_by_dm_only', True)
DEFAULT_CHANNEL = config['general'].getint('defaultChannel', 0)

LATITUDE = config['location'].getfloat('lat', 48.50)
LONGITUDE = config['location'].getfloat('lon', -123.0)

try:
    if MOTD == '':
        config['general'].get('motd', 'Thanks for using MeshBOT! Have a good day!')
except NameError:
    MOTD = config['general'].get('motd', 'Thanks for using MeshBOT! Have a good day!')

welcome_message = config['general'].get('welcome_message', 'MeshBot, here for you like a friend who is not. Try sending: ping @foo  or, cmd')

solar_conditions_enabled = config['solar'].getboolean('enabled', False)
location_enabled = config['location'].getboolean('enabled', False)
bbs_enabled = config['bbs'].getboolean('enabled', False)
bbsdb = config['bbs'].get('bbsdb', 'bbsdb.pkl')
dad_jokes_enabled = config['general'].getboolean('DadJokes', False)
store_forward_enabled = config['general'].getboolean('StoreForward', False)

URL_TIMEOUT = 10 # wait time for URL requests
DAYS_OF_WEATHER = 4 # weather forecast days, the first two rows are today and tonight
# error messages
ALERT_COUNT = 2 # number of weather alerts to display
NO_DATA_NOGPS = "No location data: does your device have GPS?"
ERROR_FETCHING_DATA = "error fetching data"

bbs_ban_list = [] # list of banned nodes numbers ex: [2813308004, 4258675309]
bbs_admin_list = [] # list of admin nodes numbers ex: [2813308004, 4258675309]