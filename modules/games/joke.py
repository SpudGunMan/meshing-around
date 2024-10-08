from dadjokes import Dadjoke # pip install dadjokes
from modules.log import *



def sendWithEmoji(message):
    # this will take a string of text and replace any word or phrase that is in the word list with the corresponding emoji
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
        'juggling': '🤹', 'meditation': '🧘', 'sauna': '🧖', 'rock climbing': '🧗', 'stop': '🛑'
    }
    # type format to clean it up
    words = message.lower().split()
    i = 0
    while i < len(words):
        for phrase in sorted(wordToEmojiMap.keys(), key=len, reverse=True):
            phrase_words = phrase.split()
            # Strip punctuation from the words
            stripped_words = [word.strip('.,!?') for word in words[i:i+len(phrase_words)]]
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

