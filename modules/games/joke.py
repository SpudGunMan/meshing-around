# This module is used to tell jokes to the user
# The emoji table of contents is used to replace words in the joke with emojis
# As a Ham, is this obsecuring the meaning of the joke? Or is it enhancing it?
from dadjokes import Dadjoke # pip install dadjokes
import random
from modules.log import logger, getPrettyTime
from modules.settings import dad_jokes_emojiJokes, dad_jokes_enabled

lameJokes = [
    "Why don't scientists trust atoms? Because they make up everything!",
    "Why did the scarecrow win an award? Because he was outstanding in his field!",
    "Why don't skeletons fight each other? They don't have the guts.",
    "What do you call fake spaghetti? An impasta!",
    "Why did the bicycle fall over? Because it was two-tired!",
    "Why did the math book look sad? Because it had too many problems.",
    "Why did the golfer bring two pairs of pants? In case he got a hole in one.",
    "Why did the coffee file a police report? It got mugged.",
    "Why did the tomato turn red? Because it saw the salad dressing!",
    "Why did the cookie go to the doctor? Because it felt crummy.",
    "Why did the computer go to the doctor? Because it had a virus!",
    "Why did the chicken join a band? Because it had the drumsticks!",
    "Why did the banana go to the doctor? Because it wasn't peeling well.",
    "Why did the cow go to space? To see the moooon!",
    "Why did the fish blush? Because it saw the ocean's bottom!",
    "Why did the elephant bring a suitcase to the zoo? Because it wanted to pack its trunk!",
    "Why did the meshtastic node go to therapy? It had too many connections to handle!",
    "Why did the meshtastic user bring a ladder to the meeting? To reach new heights in communication!",
    "Why did the meshtastic device break up with Wi-Fi? It found a better connection!",
    "Why did the meshtastic network throw a party? Because it wanted to mesh well with everyone!",
    "Why did the meshtastic node get promoted? Because it was outstanding in its field!",
    "Why did the meshtastic user bring a map? To navigate the mesh of possibilities!",
    "Why did the meshtastic device go to school? To improve its signal strength!",
    "How did the meshtastic node become a comedian? It uses mesh-bots to deliver punchlines!",
    "Chuck Norris doesn't read books. He stares them down until he gets the information he wants.",
    "When Chuck Norris enters a room, he doesn't turn the lights on. He turns the dark off.",
    "Chuck Norris can divide by zero.",
    "Chuck Norris counted to infinity. Twice.",
    "Chuck Norris can slam a revolving door.",
    "When Chuck Norris does a push-up, he isn't lifting himself up; he's pushing the Earth down.",
    "Chuck Norris can hear sign language.",
    "Death once had a near-Chuck Norris experience.",
    "Chuck Norris can unscramble an egg.",
    "Chuck Norris can win a game of Connect Four in only three moves.",
    "Chuck Norris can make a snowman out of rain.",
    "Chuck Norris can strangle you with a cordless phone.",
    "Chuck Norris can do a wheelie on a unicycle.",
    "Chuck Norris can kill two stones with one bird.",
    "Chuck Norris can speak braille.",
    "Chuck Norris can build a snowman out of rain.",
    "This is a test. A test of the Joke Brodcast System. If this had been an actual joke, you would have been amused.",
    "Chuck Norris doesn't join mesh networks. Mesh networks join Chuck's topology.",
    "Every time Chuck Norris sends a packet, it arrives before he hits 'send'",
    "Chuck Norris doesn't need LoRa. His roundhouse kick has a 15km range with zero latency.",
    "When Chuck Norris uses a node, the bandwidth doubles out of fear.",
    "Chuck Norris once pinged a device. It replied with an apology and a firmware update.",
    "Chuck Norris doesn't use AES encryption. His packets are so secure, they punch hackers in the bits.",
    "The Meshtastic protocol has a hidden mode: “Chuck Norris mode.” It only activates when he blinks.",
    "Chuck Norris doesn't need a GPS fix. Satellites triangulate themselves around him.",
    "Chuck Norris's mesh node doesn't sleep. It meditates while transmitting at full power.",
    "Chuck Norris doesn't broadcast. He declares.",
    "Chuck Norris once bridged two mesh networks using a shoelace.",
    "Chuck Norris's packets don't hop. They teleport out of respect.",
    "Chuck Norris doesn't need a repeater. Client_Mute is set to 'Always'.",
    "Chuck Norris's mesh messages are entangled. When he sends one, it's already received.",
    "Chuck Norris doesn't mesh with others. Others mesh with Chuck.",
    "Chuck Norris's node doesn't need a case. The PCB is armored with his beard hair.",
    "Chuck Norris once typed “Hello World” and the world replied 'Hello Chuck.'",
]

# pylint: disable=C0103, W0612
imtellingyourightnowiAmTellingYouRightNowThatMotherfErBackThereIsNotReal = ["🐦", "🦅", "🦆", "🦉", "🦜", "🐤", "🐥", "🐣", "🐔", "🐧", "🦚", "🦢", "🦩", "🦤", "🦃", "🐓"]

def tableOfContents():
    wordToEmojiMap = {
        'love': '❤️', 'heart': '❤️', 'happy': '😊', 'smile': '😊', 'sad': '😢', 'angry': '😠', 'mad': '😠', 'cry': '😢', 'laugh': '😂', 'funny': '😂', 'cool': '😎',
        'joy': '😂', 'kiss': '😘', 'hug': '🤗', 'wink': '😉', 'grin': '😁', 'bored': '😐', 'tired': '😴', 'sleepy': '😴', 'shocked': '😲', 'surprised': '😲',
        'confused': '😕', 'thinking': '🤔', 'sick': '🤢', 'party': '🎉', 'celebrate': '🎉', 'clap': '👏', 'thumbs up': '👍', 'thumbs down': '👎',
        'ok': '👌', 'wave': '👋', 'pray': '🙏', 'muscle': '💪', 'fire': '🔥', 'star': '⭐', 'sun': '☀️', 'moon': '🌙', 'rain': '🌧️', 'snow': '❄️', 'cloud': '☁️',
        'dog': '🐶', 'cat': '🐱', 'mouse': '🐭', 'rabbit': '🐰', 'fox': '🦊', 'bear': '🐻', 'panda': '🐼', 'koala': '🐨', 'tiger': '🐯', 'lion': '🦁', 'cow': '🐮',
        'pig': '🐷', 'frog': '🐸', 'monkey': '🐵', 'chicken': '🐔', 'penguin': '🐧', 'bird': '🐦', 'fish': '🐟', 'whale': '🐋', 'dolphin': '🐬', 'octopus': '🐙',
        'apple': '🍎', 'orange': '🍊', 'banana': '🍌', 'watermelon': '🍉', 'grape': '🍇', 'strawberry': '🍓', 'cherry': '🍒', 'peach': '🍑', 'pineapple': '🍍', 'mango': '🥭', 'coconut': '🥥',
        'tomato': '🍅', 'eggplant': '🍆', 'avocado': '🥑', 'broccoli': '🥦', 'cucumber': '🥒', 'corn': '🌽', 'carrot': '🥕', 'potato': '🥔', 'sweet potato': '🍠', 'chili': '🌶️', 'garlic': '🧄',
        'pizza': '🍕', 'burger': '🍔', 'fries': '🍟', 'hotdog': '🌭', 'popcorn': '🍿', 'donut': '🍩', 'cookie': '🍪', 'cake': '🎂', 'pie': '🍰', 'cupcake': '🧁', 'chocolate': '🍫',
        'candy': '🍬', 'lollipop': '🍭', 'pudding': '🍮', 'honey': '🍯', 'milk': '🍼', 'coffee': '☕', 'tea': '🍵', 'sake': '🍶', 'beer': '🍺', 'cheers': '🍻', 'champagne': '🥂',
        'wine': '🍷', 'whiskey': '🥃', 'cocktail': '🍸', 'tropical drink': '🍹', 'bottle': '🍾', 'soda': '🥤', 'chopsticks': '🥢', 'fork': '🍴', 'knife': '🔪', 'spoon': '🥄', 'kitchen knife': '🔪',
        'house': '🏠', 'home': '🏡', 'office': '🏢', 'post office': '🏣', 'hospital': '🏥', 'bank': '🏦', 'hotel': '🏨', 'love hotel': '🏩', 'convenience store': '🏪', 'school': '🏫', 'department store': '🏬',
        'factory': '🏭', 'castle': '🏯', 'palace': '🏰', 'church': '💒', 'tower': '🗼', 'statue of liberty': '🗽', 'mosque': '🕌', 'synagogue': '🕍', 'hindu temple': '🛕', 'kaaba': '🕋', 'shinto shrine': '⛩️',
        'railway': '🛤️', 'highway': '🛣️', 'map': '🗾', 'carousel': '🎠', 'ferris wheel': '🎡', 'roller coaster': '🎢', 'circus': '🎪', 'theater': '🎭', 'art': '🎨', 'slot machine': '🎰', 'dice': '🎲',
        'bowling': '🎳', 'video game': '🎮', 'dart': '🎯', 'billiard': '🎱', 'medal': '🎖️', 'trophy': '🏆', 'gold medal': '🥇', 'silver medal': '🥈', 'bronze medal': '🥉', 'soccer': '⚽', 'baseball': '⚾',
        'basketball': '🏀', 'volleyball': '🏐', 'football': '🏈', 'rugby': '🏉', 'tennis': '🎾', 'frisbee': '🥏', 'ping pong': '🏓', 'badminton': '🏸', 'boxing': '🥊', 'martial arts': '🥋',
        'goal': '🥅', 'golf': '⛳', 'skating': '⛸️', 'fishing': '🎣', 'diving': '🤿', 'running': '🎽', 'skiing': '🎿', 'sledding': '🛷', 'curling': '🥌', 'climbing': '🧗', 'yoga': '🧘',
        'surfing': '🏄', 'swimming': '🏊', 'water polo': '🤽', 'cycling': '🚴', 'mountain biking': '🚵', 'horse riding': '🏇', 'kneeling': '🧎', 'weightlifting': '🏋️', 'gymnastics': '🤸', 'wrestling': '🤼', 'handball': '🤾',
        'juggling': '🤹', 'meditation': '🧘', 'sauna': '🧖', 'rock climbing': '🧗', 'stop': '🛑', 'computer': '💻', 'phone': '📱', 'email': '📧', 'camera': '📷', 'video': '📹', 'music': '🎵',
        'guitar': '🎸', 'piano': '🎹', 'drum': '🥁', 'microphone': '🎤', 'headphone': '🎧', 'book': '📚', 'newspaper': '📰', 'magazine': '📖', 'pen': '🖊️', 'pencil': '✏️', 'paintbrush': '🖌️',
        'scissors': '✂️', 'ruler': '📏', 'globe': '🌍', 'earth': '🌎', 'star': '🌟', 'comet': '☄️', 'rocket': '🚀', 'airplane': '✈️', 'car': '🚗', 'bus': '🚌', 'train': '🚆',
        'bicycle': '🚲', 'motorcycle': '🏍️', 'boat': '🚤', 'ship': '🚢', 'helicopter': '🚁', 'tractor': '🚜', 'ambulance': '🚑', 'fire truck': '🚒', 'police car': '🚓', 'taxi': '🚕', 'truck': '🚚',
        'construction': '🚧', 'traffic light': '🚦', 'stop sign': '🛑', 'fuel': '⛽', 'battery': '🔋', 'light bulb': '💡', 'flashlight': '🔦', 'candle': '🕯️', 'lamp': '🛋️',
        'bed': '🛏️', 'sofa': '🛋️', 'chair': '🪑', 'table': '🛋️', 'toilet': '🚽', 'shower': '🚿', 'bathtub': '🛁', 'sink': '🚰', 'mirror': '🪞', 'door': '🚪', 'window': '🪟',
        'key': '🔑', 'lock': '🔒', 'hammer': '🔨', 'wrench': '🔧', 'screwdriver': '🪛', 'saw': '🪚', 'drill': '🛠️', 'toolbox': '🧰', 'paint roller': '🖌️', 'brush': '🖌️', 'broom': '🧹',
        'mop': '🧽', 'bucket': '🪣', 'vacuum': '🧹', 'washing machine': '🧺', 'dryer': '🧺', 'iron': '🧺', 'hanger': '🧺', 'laundry': '🧺', 'basket': '🧺', 'trash': '🗑️', 'recycle': '♻️',
        'plant': '🌱', 'tree': '🌳', 'flower': '🌸', 'leaf': '🍃', 'cactus': '🌵', 'mushroom': '🍄', 'herb': '🌿', 'bamboo': '🎍', 'rose': '🌹', 'tulip': '🌷', 'sunflower': '🌻',
        'hibiscus': '🌺', 'cherry blossom': '🌸', 'bouquet': '💐', 'seedling': '🌱', 'palm tree': '🌴', 'evergreen tree': '🌲', 'deciduous tree': '🌳', 'fallen leaf': '🍂', 'maple leaf': '🍁',
        'ear of rice': '🌾', 'shamrock': '☘️', 'four leaf clover': '🍀', 'grapes': '🍇', 'melon': '🍈', 'watermelon': '🍉', 'tangerine': '🍊', 'lemon': '🍋', 'banana': '🍌', 'pineapple': '🍍',
        'green apple': '🍏', 'pear': '🍐', 'peach': '🍑', 'cherries': '🍒', 'strawberry': '🍓', 'kiwi': '🥝', 'tomato': '🍅', 'coconut': '🥥', 'avocado': '🥑',
        'hot pepper': '🌶️', 'cucumber': '🥒', 'leafy green': '🥬', 'broccoli': '🥦', 'garlic': '🧄', 'onion': '🧅',
        'peanuts': '🥜', 'chestnut': '🌰', 'bread': '🍞', 'croissant': '🥐', 'baguette': '🥖', 'flatbread': '🥙', 'pretzel': '🥨', 'bagel': '🥯', 'pancakes': '🥞', 'waffle': '🧇', 'cheese': '🧀',
        'meat': '🍖', 'poultry': '🍗', 'bacon': '🥓', 'hamburger': '🍔', 'fries': '🍟', 'pizza': '🍕', 'hot dog': '🌭', 'sandwich': '🥪', 'taco': '🌮', 'burrito': '🌯', 'tamale': '🫔',
        'stuffed flatbread': '🥙', 'falafel': '🧆', 'egg': '🥚', 'fried egg': '🍳', 'shallow pan of food': '🥘', 'pot of food': '🍲', 'fondue': '🫕', 'bowl with spoon': '🥣', 'green salad': '🥗',
        'popcorn': '🍿', 'butter': '🧈', 'salt': '🧂', 'canned food': '🥫', 'bento box': '🍱', 'rice cracker': '🍘', 'rice ball': '🍙', 'cooked rice': '🍚', 'curry rice': '🍛', 'steaming bowl': '🍜',
        'spaghetti': '🍝', 'roasted sweet potato': '🍠', 'oden': '🍢', 'sushi': '🍣', 'fried shrimp': '🍤', 'fish cake': '🍥', 'moon cake': '🥮', 'dango': '🍡', 'dumpling': '🥟', 'fortune cookie': '🥠',
        'takeout box': '🥡', 'crab': '🦀', 'lobster': '🦞', 'shrimp': '🦐', 'squid': '🦑', 'oyster': '🦪', 'ice cream': '🍨', 'shaved ice': '🍧', 'ice cream cone': '🍦', 'doughnut': '🍩', 'cookie': '🍪',
        'birthday cake': '🎂', 'shortcake': '🍰', 'cupcake': '🧁', 'pie': '🥧', 'chocolate bar': '🍫', 'candy': '🍬', 'lollipop': '🍭', 'custard': '🍮', 'honey pot': '🍯', 'baby bottle': '🍼',
        'glass of milk': '🥛', 'hot beverage': '☕', 'teapot': '🫖', 'teacup without handle': '🍵', 'sake': '🍶', 'bottle with popping cork': '🍾', 'wine glass': '🍷', 'cocktail glass': '🍸', 'tropical drink': '🍹',
        'beer mug': '🍺', 'clinking beer mugs': '🍻', 'clinking glasses': '🥂', 'tumbler glass': '🥃', 'cup with straw': '🥤', 'bubble tea': '🧋', 'beverage box': '🧃', 'mate': '🧉', 'ice': '🧊',
        'chopsticks': '🥢', 'fork and knife': '🍴', 'spoon': '🥄', 'kitchen knife': '🔪', 'amphora': '🏺', 'globe showing Europe-Africa': '🌍', 'globe showing Americas': '🌎', 'globe showing Asia-Australia': '🌏',
        'globe with meridians': '🌐', 'world map': '🗺️', 'mountain': '⛰️', 'volcano': '🌋', 'mount fuji': '🗻', 'camping': '🏕️', 'beach with umbrella': '🏖️', 'desert': '🏜️', 'desert island': '🏝️',
        'national park': '🏞️', 'stadium': '🏟️', 'classical building': '🏛️', 'building construction': '🏗️', 'brick': '🧱', 'rock': '🪨', 'wood': '🪵', 'hut': '🛖', 'houses': '🏘️', 'derelict house': '🏚️',
        'house with garden': '🏡', 'office building': '🏢', 'japanese post office': '🏣', 'post office': '🏤', 'hospital': '🏥', 'bank': '🏦', 'hotel': '🏨', 'love hotel': '🏩', 'convenience store': '🏪',
        'castle': '🏰', 'wedding': '💒', 'tokyo tower': '🗼', 'statue of liberty': '🗽', 'church': '⛪', 'mosque': '🕌',
        'fountain': '⛲', 'tent': '⛺', 'foggy': '🌁', 'night with stars': '🌃', 'sunrise over mountains': '🌄', 'sunrise': '🌅',
        'cityscape at dusk': '🌆', 'sunset': '🌇', 'cityscape': '🏙️', 'bridge at night': '🌉', 'hot springs': '♨️', 'carousel horse': '🎠', 'barber pole': '💈',
        'robot': '🤖', 'alien': '👽', 'ghost': '👻', 'skull': '💀', 'pumpkin': '🎃', 'clown': '🤡', 'wizard': '🧙', 'elf': '🧝', 'fairy': '🧚', 'mermaid': '🧜', 'vampire': '🧛',
        'zombie': '🧟', 'genie': '🧞', 'superhero': '🦸', 'supervillain': '🦹', 'mage': '🧙', 'knight': '🛡️', 'ninja': '🥷', 'pirate': '🏴‍☠️', 'angel': '👼', 'devil': '😈', 'dragon': '🐉',
        'unicorn': '🦄', 'phoenix': '🦅', 'griffin': '🦅', 'centaur': '🐎', 'minotaur': '🐂', 'cyclops': '👁️', 'medusa': '🐍', 'sphinx': '🦁', 'kraken': '🦑', 'yeti': '❄️', 'sasquatch': '🦧',
        'loch ness monster': '🦕', 'chupacabra': '🐐', 'banshee': '👻', 'golem': '🗿', 'djinn': '🧞', 'basilisk': '🐍', 'hydra': '🐉', 'cerberus': '🐶', 'chimera': '🐐', 'manticore': '🦁', 'wyvern': '🐉',
        'pegasus': '🦄', 'hippogriff': '🦅', 'kelpie': '🐎', 'selkie': '🦭', 'kitsune': '🦊', 'tanuki': '🦝', 'tengu': '🦅', 'oni': '👹', 'yokai': '👻', 'kappa': '🐢', 'yurei': '👻',
        'kami': '👼', 'shinigami': '💀', 'bakemono': '👹', 'tsukumogami': '🧸', 'noppera-bo': '👤', 'rokurokubi': '🧛', 'yuki-onna': '❄️', 'jorogumo': '🕷️', 'nue': '🐍', 'ubume': '👼',
        'atom': '⚛️', 'dna': '🧬', 'microscope': '🔬', 'telescope': '🔭', 'satellite': '🛰️', 'spaceship': '🛸', 'planet': '🪐', 'black hole': '🕳️', 'galaxy': '🌌',
        'constellation': '🌠', 'lightning': '⚡', 'magnet': '🧲', 'computer': '💻', 'keyboard': '⌨️', 'mouse': '🖱️', 'printer': '🖨️', 'floppy disk': '💾',
        'cd': '💿', 'dvd': '📀', 'smartphone': '📱', 'tablet': '📲', 'watch': '⌚', 'camera': '📷', 'video camera': '📹', 'projector': '📽️', 'radio': '📻', 'television': '📺',
        'satellite dish': '📡', 'game controller': '🎮', 'joystick': '🕹️', 'vr headset': '🕶️', 'headphones': '🎧', 'speaker': '🔊', 'circuit': '🔌', 'chip': '💻',
        'server': '🖥️', 'database': '💾', 'cloud': '☁️', 'network': '🌐', 'code': '💻', 'bug': '🐛', 'virus': '🦠', 'bacteria': '🦠', 'lab coat': '🥼', 'safety goggles': '🥽',
        'test tube': '🧪', 'petri dish': '🧫', 'beaker': '🧪', 'bunsen burner': '🔥', 'graduated cylinder': '🧪', 'pipette': '🧪', 'scalpel': '🔪', 'syringe': '💉', 'pill': '💊',
        'stethoscope': '🩺', 'thermometer': '🌡️', 'x-ray': '🩻', 'brain': '🧠', 'heart': '❤️', 'lung': '🫁', 'bone': '🦴', 'muscle': '💪', 'robot arm': '🦾', 'robot leg': '🦿',
        'prosthetic arm': '🦾', 'prosthetic leg': '🦿', 'wheelchair': '🦽', 'crutch': '🦯', 'hearing aid': '🦻', 'glasses': '👓', 'magnifying glass': '🔍', 'circus tent': '🎪',
        'duck': '🦆', 'eagle': '🦅', 'owl': '🦉', 'bat': '🦇', 'shark': '🦈', 'butterfly': '🦋', 'snail': '🐌', 'bee': '🐝', 'beetle': '🐞', 'ant': '🐜', 'cricket': '🦗', 
        'spider': '🕷️', 'scorpion': '🦂', 'turkey': '🦃', 'peacock': '🦚', 'parrot': '🦜', 'swan': '🦢', 'flamingo': '🦩', 'dodo': '🦤', 'sloth': '🦥', 'otter': '🦦', 
        'skunk': '🦨', 'kangaroo': '🦘', 'badger': '🦡', 'beaver': '🦫', 'bison': '🦬', 'mammoth': '🦣', 'raccoon': '🦝', 'hedgehog': '🦔', 'squirrel': '🐿️', 'chipmunk': '🐿️', 
        'porcupine': '🦔', 'llama': '🦙', 'giraffe': '🦒', 'zebra': '🦓', 'hippopotamus': '🦛', 'rhinoceros': '🦏', 'gorilla': '🦍', 'orangutan': '🦧', 'elephant': '🐘', 'camel': '🐫', 
        'alpaca': '🦙', 'buffalo': '🐃', 'ox': '🐂', 'deer': '🦌', 'moose': '🦌', 'reindeer': '🦌', 'goat': '🐐', 'sheep': '🐑', 'ram': '🐏', 'lamb': '🐑', 'horse': '🐴', 
        'rat': '🐀', 'hedgehog': '🦔', 'chicken': '🐔', 'rooster': '🐓', 'crocodile': '🐊', 'turtle': '🐢', 'lizard': '🦎', 'dragon': '🐉', 'sauropod': '🦕', 't-rex': '🦖', 'butterfly': '🦋', 
        'mosquito': '🦟', 'microbe': '🦠', 'locomotive': '🚂', 'arm': '💪', 'leg': '🦵', 'sponge': '🧽',
        'toothbrush': '🪥', 'roll of paper': '🧻', 'soap': '🧼', 'toilet paper': '🧻', 'shower': '🚿', 'bathtub': '🛁', 'razor': '🪒', 'lotion': '🧴',
        'letter': '✉️', 'envelope': '✉️', 'mail': '📬', 'post': '📮', 'golf': '⛳️', 'golfing': '⛳️', 'meeting': '📅', 'presentation': '📊', 'report': '📄', 'document': '📄',
        'file': '📁', 'folder': '📂', 'sports': '🏅', 'athlete': '🏃', 'competition': '🏆', 'race': '🏁', 'tournament': '🏆', 'champion': '🏆', 'medal': '🏅', 'victory': '🏆', 'win': '🏆', 'lose': '😞',
        'draw': '🤝', 'team': '👥', 'player': '👤', 'coach': '👨‍🏫', 'referee': '🧑‍⚖️', 'stadium': '🏟️', 'arena': '🏟️', 'field': '🏟️', 'court': '🏟️', 'track': '🏟️', 'gym': '🏋️', 'fitness': '🏋️', 'exercise': '🏋️', 
        'workout': '🏋️', 'training': '🏋️', 'practice': '🏋️', 'game': '🎮', 'match': '🎮', 'score': '🏅', 'goal': '🥅', 'point': '🏅', 'basket': '🏀', 'home run': '⚾️', 'strike': '🎳', 'spare': '🎳', 'frame': '🎳', 
        'inning': '⚾️', 'shower': '🚿', 'uniform': '👕', 'jersey': '👕', 'cleats': '👟', 'helmet': '⛑️', 'pads': '🛡️', 'gloves': '🧤', 'bat': '⚾️', 'ball': '⚽️', 'puck': '🏒', 'stick': '🏒', 'net': '🥅', 'goalpost': '🥅',
        'scoreboard': '📊', 'fans': '👥', 'crowd': '👥', 'cheer': '📣', 'boo': '😠', 'applause': '👏', 'celebration': '🎉', 'parade': '🎉', 'trophy': '🏆', 'medal': '🏅', 'ribbon': '🎀',
        'third place': '🥉', 'snowman': '☃️', 'snowmen': '⛄️'
    }

    return wordToEmojiMap

def sendWithEmoji(message):
    # this will take a string of text and replace any word or phrase that is in the word list with the corresponding emoji
    wordToEmojiMap = tableOfContents()
    # type format to clean it up
    words = message.split()
    i = 0
    while i < len(words):
        for phrase in sorted(wordToEmojiMap.keys(), key=len, reverse=True):
            phrase_words = phrase.split()
            # Strip punctuation from the words
            stripped_words = [word.lower().strip('.,!?') for word in words[i:i+len(phrase_words)]]
            if stripped_words == phrase_words:
                logger.debug(f"System: Replaced the phrase '{phrase}' with '{wordToEmojiMap[phrase]}'")
                words[i:i+len(phrase_words)] = [wordToEmojiMap[phrase]]
                i += len(phrase_words) - 1
                break
            # Check for plural forms
            elif stripped_words == [word + 's' for word in phrase_words]:
                logger.debug(f"System: Replaced the plural phrase '{' '.join([word + 's' for word in phrase_words])}' with '{wordToEmojiMap[phrase]}'")
                words[i:i+len(phrase_words)] = [wordToEmojiMap[phrase]]
                i += len(phrase_words) - 1
                break
        i += 1
    return ' '.join(words)

def tell_joke(nodeID=0, vox=False, test=False):
    dadjoke = Dadjoke()
    if test:
        return sendWithEmoji(dadjoke.joke)
    try:
        if dad_jokes_emojiJokes:
            renderedLaugh = sendWithEmoji(dadjoke.joke)
        else:
            renderedLaugh = dadjoke.joke
        return renderedLaugh
    except Exception as e:
        return random.choice(lameJokes)

