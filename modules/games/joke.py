# This module is used to tell jokes to the user
# The emoji table of contents is used to replace words in the joke with emojis
# As a Ham, is this obsecuring the meaning of the joke? Or is it enhancing it?
from dadjokes import Dadjoke # pip install dadjokes
from modules.log import *

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
        'mango': '🥭', 'apple': '🍎', 'green apple': '🍏', 'pear': '🍐', 'peach': '🍑', 'cherries': '🍒', 'strawberry': '🍓', 'kiwi': '🥝', 'tomato': '🍅', 'coconut': '🥥', 'avocado': '🥑',
        'eggplant': '🍆', 'potato': '🥔', 'carrot': '🥕', 'corn': '🌽', 'hot pepper': '🌶️', 'cucumber': '🥒', 'leafy green': '🥬', 'broccoli': '🥦', 'garlic': '🧄', 'onion': '🧅',
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
        'school': '🏫', 'department store': '🏬', 'factory': '🏭', 'japanese castle': '🏯', 'castle': '🏰', 'wedding': '💒', 'tokyo tower': '🗼', 'statue of liberty': '🗽', 'church': '⛪', 'mosque': '🕌',
        'hindu temple': '🛕', 'synagogue': '🕍', 'shinto shrine': '⛩️', 'kaaba': '🕋', 'fountain': '⛲', 'tent': '⛺', 'foggy': '🌁', 'night with stars': '🌃', 'sunrise over mountains': '🌄', 'sunrise': '🌅',
        'cityscape at dusk': '🌆', 'sunset': '🌇', 'cityscape': '🏙️', 'bridge at night': '🌉', 'hot springs': '♨️', 'carousel horse': '🎠', 'ferris wheel': '🎡', 'roller coaster': '🎢', 'barber pole': '💈',
        'robot': '🤖', 'alien': '👽', 'ghost': '👻', 'skull': '💀', 'pumpkin': '🎃', 'clown': '🤡', 'wizard': '🧙', 'elf': '🧝', 'fairy': '🧚', 'mermaid': '🧜', 'vampire': '🧛',
        'zombie': '🧟', 'genie': '🧞', 'superhero': '🦸', 'supervillain': '🦹', 'mage': '🧙', 'knight': '🛡️', 'ninja': '🥷', 'pirate': '🏴‍☠️', 'angel': '👼', 'devil': '😈', 'dragon': '🐉',
        'unicorn': '🦄', 'phoenix': '🦅', 'griffin': '🦅', 'centaur': '🐎', 'minotaur': '🐂', 'cyclops': '👁️', 'medusa': '🐍', 'sphinx': '🦁', 'kraken': '🦑', 'yeti': '❄️', 'sasquatch': '🦧',
        'loch ness monster': '🦕', 'chupacabra': '🐐', 'banshee': '👻', 'golem': '🗿', 'djinn': '🧞', 'basilisk': '🐍', 'hydra': '🐉', 'cerberus': '🐶', 'chimera': '🐐', 'manticore': '🦁', 'wyvern': '🐉',
        'pegasus': '🦄', 'hippogriff': '🦅', 'kelpie': '🐎', 'selkie': '🦭', 'kitsune': '🦊', 'tanuki': '🦝', 'tengu': '🦅', 'oni': '👹', 'yokai': '👻', 'kappa': '🐢', 'yurei': '👻',
        'kami': '👼', 'shinigami': '💀', 'bakemono': '👹', 'tsukumogami': '🧸', 'noppera-bo': '👤', 'rokurokubi': '🧛', 'yuki-onna': '❄️', 'jorogumo': '🕷️', 'nue': '🐍', 'ubume': '👼',
        'atom': '⚛️', 'dna': '🧬', 'microscope': '🔬', 'telescope': '🔭', 'rocket': '🚀', 'satellite': '🛰️', 'spaceship': '🛸', 'planet': '🪐', 'black hole': '🕳️', 'galaxy': '🌌',
        'comet': '☄️', 'constellation': '🌠', 'lightning': '⚡', 'magnet': '🧲', 'battery': '🔋', 'computer': '💻', 'keyboard': '⌨️', 'mouse': '🖱️', 'printer': '🖨️', 'floppy disk': '💾',
        'cd': '💿', 'dvd': '📀', 'smartphone': '📱', 'tablet': '📲', 'watch': '⌚', 'camera': '📷', 'video camera': '📹', 'projector': '📽️', 'radio': '📻', 'television': '📺',
        'satellite dish': '📡', 'game controller': '🎮', 'joystick': '🕹️', 'vr headset': '🕶️', 'headphones': '🎧', 'speaker': '🔊', 'flashlight': '🔦', 'circuit': '🔌', 'chip': '💻',
        'server': '🖥️', 'database': '💾', 'cloud': '☁️', 'network': '🌐', 'code': '💻', 'bug': '🐛', 'virus': '🦠', 'bacteria': '🦠', 'lab coat': '🥼', 'safety goggles': '🥽',
        'test tube': '🧪', 'petri dish': '🧫', 'beaker': '🧪', 'bunsen burner': '🔥', 'graduated cylinder': '🧪', 'pipette': '🧪', 'scalpel': '🔪', 'syringe': '💉', 'pill': '💊',
        'stethoscope': '🩺', 'thermometer': '🌡️', 'x-ray': '🩻', 'brain': '🧠', 'heart': '❤️', 'lung': '🫁', 'bone': '🦴', 'muscle': '💪', 'robot arm': '🦾', 'robot leg': '🦿',
        'prosthetic arm': '🦾', 'prosthetic leg': '🦿', 'wheelchair': '🦽', 'crutch': '🦯', 'hearing aid': '🦻', 'glasses': '👓', 'magnifying glass': '🔍', 'circus tent': '🎪',
        'duck': '🦆', 'eagle': '🦅', 'owl': '🦉', 'bat': '🦇', 'shark': '🦈', 'butterfly': '🦋', 'snail': '🐌', 'bee': '🐝', 'beetle': '🐞', 'ant': '🐜', 'cricket': '🦗', 
        'spider': '🕷️', 'scorpion': '🦂', 'turkey': '🦃', 'peacock': '🦚', 'parrot': '🦜', 'swan': '🦢', 'flamingo': '🦩', 'dodo': '🦤', 'sloth': '🦥', 'otter': '🦦', 
        'skunk': '🦨', 'kangaroo': '🦘', 'badger': '🦡', 'beaver': '🦫', 'bison': '🦬', 'mammoth': '🦣', 'raccoon': '🦝', 'hedgehog': '🦔', 'squirrel': '🐿️', 'chipmunk': '🐿️', 
        'porcupine': '🦔', 'llama': '🦙', 'giraffe': '🦒', 'zebra': '🦓', 'hippopotamus': '🦛', 'rhinoceros': '🦏', 'gorilla': '🦍', 'orangutan': '🦧', 'elephant': '🐘', 'camel': '🐫', 
        'llama': '🦙', 'alpaca': '🦙', 'buffalo': '🐃', 'ox': '🐂', 'deer': '🦌', 'moose': '🦌', 'reindeer': '🦌', 'goat': '🐐', 'sheep': '🐑', 'ram': '🐏', 'lamb': '🐑', 'horse': '🐴', 
        'unicorn': '🦄', 'zebra': '🦓', 'cow': '🐄', 'pig': '🐖', 'boar': '🐗', 'mouse': '🐁', 'rat': '🐀', 'hamster': '🐹', 'rabbit': '🐇', 'chipmunk': '🐿️', 'beaver': '🦫', 'hedgehog': '🦔', 
        'bat': '🦇', 'bear': '🐻', 'koala': '🐨', 'panda': '🐼', 'sloth': '🦥', 'otter': '🦦', 'skunk': '🦨', 'kangaroo': '🦘', 'badger': '🦡', 'turkey': '🦃', 'chicken': '🐔', 'rooster': '🐓', 
        'peacock': '🦚', 'parrot': '🦜', 'swan': '🦢', 'flamingo': '🦩', 'dodo': '🦤', 'crocodile': '🐊', 'turtle': '🐢', 'lizard': '🦎', 'snake': '🐍', 'dragon': '🐉', 'sauropod': '🦕', 't-rex': '🦖', 
        'whale': '🐋', 'dolphin': '🐬', 'fish': '🐟', 'blowfish': '🐡', 'shark': '🦈', 'octopus': '🐙', 'shell': '🐚', 'crab': '🦀', 'lobster': '🦞', 'shrimp': '🦐', 'squid': '🦑', 'snail': '🐌', 'butterfly': '🦋', 
        'bee': '🐝', 'beetle': '🐞', 'ant': '🐜', 'cricket': '🦗', 'spider': '🕷️', 'scorpion': '🦂', 'mosquito': '🦟', 'microbe': '🦠', 'locomotive': '🚂', 'arm': '💪', 'leg': '🦵', 'sponge': '🧽',
        'toothbrush': '🪥', 'broom': '🧹', 'basket': '🧺', 'roll of paper': '🧻', 'bucket': '🪣', 'soap': '🧼', 'toilet paper': '🧻', 'shower': '🚿', 'bathtub': '🛁', 'razor': '🪒', 'lotion': '🧴',
        'letter': '✉️', 'envelope': '✉️', 'mail': '📬', 'post': '📮', 'golf': '⛳️', 'golfing': '⛳️', 'office': '🏢', 'work': '💼', 'meeting': '📅', 'presentation': '📊', 'report': '📄', 'document': '📄',
        'file': '📁', 'folder': '📂', 'sports': '🏅', 'athlete': '🏃', 'competition': '🏆', 'race': '🏁', 'tournament': '🏆', 'champion': '🏆', 'medal': '🏅', 'victory': '🏆', 'win': '🏆', 'lose': '😞',
        'draw': '🤝', 'team': '👥', 'player': '👤', 'coach': '👨‍🏫', 'referee': '🧑‍⚖️', 'stadium': '🏟️', 'arena': '🏟️', 'field': '🏟️', 'court': '🏟️', 'track': '🏟️', 'gym': '🏋️', 'fitness': '🏋️', 'exercise': '🏋️', 
        'workout': '🏋️', 'training': '🏋️', 'practice': '🏋️', 'game': '🎮', 'match': '🎮', 'score': '🏅', 'goal': '🥅', 'point': '🏅', 'basket': '🏀', 'home run': '⚾️', 'strike': '🎳', 'spare': '🎳', 'frame': '🎳', 
        'inning': '⚾️', 'quarter': '🏈', 'half': '🏈', 'overtime': '🏈', 'penalty': '⚽️', 'foul': '⚽️', 'timeout': '⏱️', 'substitute': '🔄', 'bench': '🪑', 'sideline': '🏟️', 'dugout': '⚾️', 'locker room': '🚪', 'shower': '🚿', 
        'uniform': '👕', 'jersey': '👕', 'cleats': '👟', 'helmet': '⛑️', 'pads': '🛡️', 'gloves': '🧤', 'bat': '⚾️', 'ball': '⚽️', 'puck': '🏒', 'stick': '🏒', 'net': '🥅', 'hoop': '🏀', 'goalpost': '🥅', 'whistle': '🔔', 
        'scoreboard': '📊', 'fans': '👥', 'crowd': '👥', 'cheer': '📣', 'boo': '😠', 'applause': '👏', 'celebration': '🎉', 'parade': '🎉', 'trophy': '🏆', 'medal': '🏅', 'ribbon': '🎀', 'cup': '🏆', 'championship': '🏆', 
        'league': '🏆', 'season': '🏆', 'playoffs': '🏆', 'finals': '🏆', 'champion': '🏆', 'runner-up': '🥈', 'third place': '🥉', 'snowman': '☃️', 'snowmen': '⛄️'
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

def tell_joke(nodeID=0):
    dadjoke = Dadjoke()
    renderedLaugh = sendWithEmoji(dadjoke.joke)
    return renderedLaugh

