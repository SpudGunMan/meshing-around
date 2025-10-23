#python word of the day game module for meshing-around bot
from modules.log import *
import random
import json
import os
import time
from itertools import product

class WordOfTheDayGame:
    def __init__(self):
        default_word_list = [
            {'word': 'serendipity', 'meta': 'The occurrence of events by chance in a happy or beneficial way.'},
            {'word': 'ephemeral', 'meta': 'Lasting for a very short time.'},
            {'word': 'sonder', 'meta': 'The realization that each passerby has a life as vivid and complex as your own.'},
            {'word': 'petrichor', 'meta': 'A pleasant smell that frequently accompanies the first rain after a long period of warm, dry weather.'},
        ]
        json_path = os.path.join('data', 'wotd.json')
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r') as f:
                    self.word_list = json.load(f)
            except FileNotFoundError:
                logger.debug("System: WoTd: Failed to load data/wotd.json, using default word list.")
                self.word_list = default_word_list
            except json.JSONDecodeError:
                logger.warning("System: WoTd: JSON decode error in data/wotd.json, example format: [{\"word\": \"example\", \"definition\": \"An example definition.\"}]")
                self.word_list = default_word_list
        else:
            logger.debug("System: WoTd: data/wotd.json not found, using default word list.")
            self.word_list = default_word_list

        # Load bingo card words from JSON if available
        default_bingo_card = [
            "dog", "cat", "fish", "bird", "hamster", "rabbit", "turtle", "lizard", "snake", "frog",
            "horse", "cow", "pig", "sheep", "goat", "chicken", "duck", "turkey", "peacock", "parrot",
            "elephant", "lion", "tiger", "bear", "wolf", "fox", "deer", "moose", "zebra", "giraffe",
            "monkey", "ape", "chimpanzee", "gorilla", "orangutan", "kangaroo", "koala", "panda",
            "whale", "dolphin", "shark", "octopus", "crab", "lobster", "jellyfish", "seahorse",
            "ant", "bee", "butterfly", "dragonfly", "spider", "ladybug"
        ]
        bingo_json_path = os.path.join('data', 'bingo.json')
        if os.path.exists(bingo_json_path):
            try:
                with open(bingo_json_path, 'r') as f:
                    bingoCard = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                logger.debug("System: WoTd: Failed to load data/bingo.json, using default bingo card. example format: [\"word1\", \"word2\", ...]")
                bingoCard = default_bingo_card
        else:
            logger.debug("System: WoTd: data/bingo.json not found, using default bingo card.")
            bingoCard = default_bingo_card

        # Create a set for faster lookup
        self.bingoCardSet = set(bingoCard)

        self.leet_dict = {
            'a': ['4', '@'],
            'b': ['8'],
            'e': ['3'],
            'i': ['1', '!', '|'],
            'l': ['1', '|', '7'],
            'o': ['0'],
            's': ['5', '$'],
            't': ['7', '+'],
            'g': ['9', '6'],
        }
        # Initialize the word of the day
        self.word_of_the_day_entry = random.choice(self.word_list)
        logger.debug(f"System: WoTd: Initialized with word of the day '{self.word_of_the_day_entry['word']}'.")
        # Initialize bingo card
        self.generate_bingo_card(3)
        logger.debug("System: BINGO: " + ". ".join(" | ".join(row) for row in self.bingo_card))

    def get_emoji_type(self, emoji, randomReturn=False):
        smileys = "😀😁😂🤣😃😄😅😆😉😊😋😎😍😘🥰😗😙😚🙂🤗🤩🤔🤨😐😑😶🙄😏😣😥😮🤐😯😪😫😴😌😛😜😝🤤😒😓😔😕🙃🤑😲☹️🙁😖😞😟😤😢😭😦😧😨😩🤯😬😰😱🥵🥶😳🤪😵😡😠🤬😷🤒🤕🤢🤮🤧😇🥳🥺🤠"
        animals = "🐶🐱🐭🐹🐰🦊🐻🐼🐨🐯🦁🐮🐷🐽🐸🐵🙈🙉🙊🐒🐔🐧🐦🐤🐣🐥🦆🦅🦉🦇🐺🐗🐴🦄🐝🐛🦋🐌🐞🐜🦟🦗🕷️🕸️🐢🐍🦎🦂🦀🦞🦐🦑🐙🦑🐠🐟🐡🐬🦈🐳🐋🐊🐅🐆🦓🦍🦧🐘🦛🦏🐪🐫🦒🦘🐃🐂🐄🐎🐖🐏🐑🦙🐐🦌🐕🐩🦮🐕‍🦺🐈🐓🦃🦚🦜🦢🦩🕊️🐇🦝🦨🦡🦦🦥🐁🐀🐿️🦔"
        fruit = "🍎🍊🍌🍉🍇🍓🍒🍑🥭🍍🥥🥝🍅🥑🍆🥔🥕🌽🌶️🥒🥬🥦🧄🧅🍄🥜🌰"
        categories = {'smileys': smileys, 'animals': animals, 'fruit': fruit}
        if randomReturn:
            cat = random.choice(list(categories))
            return random.choice(categories[cat])
        for cat, chars in categories.items():
            if emoji in chars:
                return cat
        return False

    def reset_word_of_the_day(self):
        logger.debug("System: WoTd: Resetting Word of the Day.")
        self.word_of_the_day_entry = random.choice(self.word_list)

    def generate_leet_variants(self, word):
        chars = []
        for c in word.lower():
            if c in self.leet_dict:
                chars.append([c] + self.leet_dict[c])
            else:
                chars.append([c])
        variants = set()
        for combo in product(*chars):
            variant = ''.join(combo)
            variants.add(variant)
            if len(variants) > 128:
                break
        return variants

    def did_it_happen(self, string_of_text=''):
        """
        Check if the current word of the day (or its leet variants) appears in the text.
        Also check for a bingo win.
        Returns:
            (wotd_found, old_entry, new_entry, bingo_win, bingo_message)
        """
        text = string_of_text.lower()
        words_in_text = set(text.split())
        word = self.word_of_the_day_entry['word'].lower()
        variants = self.generate_leet_variants(word)
        wotd_found = False
        old_entry = None
        new_entry = None
    
        for variant in variants:
            if variant in words_in_text:
                old_entry = self.word_of_the_day_entry
                self.reset_word_of_the_day()
                new_entry = self.word_of_the_day_entry
                wotd_found = True
                break
    
        bingo_win, bingo_message = self.b_i_n_g_o(string_of_text)
        return wotd_found, old_entry, new_entry, bingo_win, bingo_message
    
    def generate_bingo_card(self, size=9):
        """
        Generate a random bingo card of given size (size x size) from the bingoCardSet.
        Returns a 2D list representing the bingo card.
        """
        words = random.sample(list(self.bingoCardSet), size * size)
        card = [words[i*size:(i+1)*size] for i in range(size)]
        self.bingo_card = card
        self.bingo_card_matches = [[False]*size for _ in range(size)]
        return card

    def b_i_n_g_o(self, string_of_text=''):
        """
        Check if any words in the text match the bingo card.
        If a row, column, or diagonal is fully matched, return True and the winning line.
        Otherwise, return False and None.
        """
        if not hasattr(self, 'bingo_card'):
            logger.debug("System: WoTd: Generating new bingo card.")
            self.generate_bingo_card(3)

        words_in_text = set(string_of_text.lower().split())
        size = len(self.bingo_card)
        # Mark matches
        for i in range(size):
            for j in range(size):
                if self.bingo_card[i][j].lower() in words_in_text:
                    self.bingo_card_matches[i][j] = True

        # Check rows
        for i in range(size):
            if all(self.bingo_card_matches[i]):
                winning_row = self.bingo_card[i]
                logger.debug("System: BINGO achieved, generating new bingo card.")
                self.generate_bingo_card(size)  # Reset board after win
                return True, f"BINGO! Row {i+1}: {winning_row}"

        # Check columns
        for j in range(size):
            if all(self.bingo_card_matches[i][j] for i in range(size)):
                col = [self.bingo_card[i][j] for i in range(size)]
                return True, f"BINGO! Column {j+1}: {col}"

        # Check diagonals
        if all(self.bingo_card_matches[i][i] for i in range(size)):
            diag = [self.bingo_card[i][i] for i in range(size)]
            return True, f"BINGO! Diagonal: {diag}"
        if all(self.bingo_card_matches[i][size-1-i] for i in range(size)):
            diag = [self.bingo_card[i][size-1-i] for i in range(size)]
            return True, f"BINGO! Diagonal: {diag}"

        return False, None
    
    def extract_emojis(self, text):
        emojis = []
        for char in text:
            cp = ord(char)
            # Common emoji Unicode ranges
            if (
                0x1F600 <= cp <= 0x1F64F or  # Emoticons
                0x1F300 <= cp <= 0x1F5FF or  # Symbols & pictographs
                0x1F680 <= cp <= 0x1F6FF or  # Transport & map symbols
                0x1F1E6 <= cp <= 0x1F1FF or  # Regional indicator symbols
                0x2600  <= cp <= 0x26FF  or  # Misc symbols
                0x2700  <= cp <= 0x27BF  or  # Dingbats
                0x1F900 <= cp <= 0x1F9FF or  # Supplemental symbols & pictographs
                0x1FA70 <= cp <= 0x1FAFF or  # Symbols & pictographs extended-A
                0x2B50  == cp or             # Star
                0x2B55  == cp                # Heavy large circle
            ):
                emojis.append(char)
        return emojis
    
    def emojiMiniGame(self, string_of_text='', nodeID=0, nodeInt=1, emojiSeen=False):
        from modules.system import meshLeaderboard
        """
        Track emoji usage, Returns a string if the mini-game is won, else None.
        If emojiSeen is False, only update mostMessages leaderboard and skip emoji logic.
        """

        # --- Always update mostMessages leaderboard ---
        if 'nodeMessageCounts' in meshLeaderboard and meshLeaderboard['nodeMessageCounts']:
            max_node = max(meshLeaderboard['nodeMessageCounts'], key=meshLeaderboard['nodeMessageCounts'].get)
            meshLeaderboard['mostMessages'] = {
                'nodeID': max_node,
                'value': meshLeaderboard['nodeMessageCounts'][max_node],
                'timestamp': time.time()
            }

        
        emoji = None  # Placeholder: extract emoji from string_of_text if needed
        emojis = self.extract_emojis(string_of_text)
        if not emojiSeen and not emojis:
            return None
        logger.debug(f"System: WoTd: Emoji mini-game processing for nodeID {nodeID} with emojis: {emojis}")
        # --- 1. Update meshLeaderboard for emoji usage ---
        if 'emojiCounts' not in meshLeaderboard:
            meshLeaderboard['emojiCounts'] = {}
        if 'emojiTypeCounts' not in meshLeaderboard:
            meshLeaderboard['emojiTypeCounts'] = {}

        meshLeaderboard['emojiCounts'].setdefault(nodeID, {})
        for emoji in emojis:
            meshLeaderboard['emojiCounts'][nodeID][emoji] = meshLeaderboard['emojiCounts'][nodeID].get(emoji, 0) + 1

        # --- Update the leaderboard record for most emojis ---
        # Flatten per-node emoji counts to total per node
        emoji_totals = {nid: sum(emojicounts.values()) for nid, emojicounts in meshLeaderboard['emojiCounts'].items() if isinstance(emojicounts, dict)}
        if emoji_totals:
            max_node = max(emoji_totals, key=emoji_totals.get)
            meshLeaderboard['mostEmojis'] = {
                'nodeID': max_node,
                'value': emoji_totals[max_node],
                'timestamp': time.time()
            }
        
        # --- 2. Track most used of a type (e.g., smileys, animals, etc.) ---
        emoji_type = self.get_emoji_type(emoji)
        meshLeaderboard['emojiTypeCounts'].setdefault(emoji_type, {})
        meshLeaderboard['emojiTypeCounts'][emoji_type][emoji] = meshLeaderboard['emojiTypeCounts'][emoji_type].get(emoji, 0) + 1

        # --- 3. Slot machine mini-game ---
        if 'emojiSlotWindow' not in meshLeaderboard:
            meshLeaderboard['emojiSlotWindow'] = []
        meshLeaderboard['emojiSlotWindow'].append(emoji)
        # Randomize jackpot length after each win
        if not hasattr(self, 'slot_jackpot_length'):
            self.slot_jackpot_length = random.choice([3,4,5])  # JackPot length can be 3, 4, or 5
        if len(meshLeaderboard['emojiSlotWindow']) > self.slot_jackpot_length:
            meshLeaderboard['emojiSlotWindow'].pop(0)

        # --- 3a. Detect spam of 3 identical emojis in a row ---
        if len(meshLeaderboard['emojiSlotWindow']) >= 5:
            last_three = meshLeaderboard['emojiSlotWindow'][-3:]
            if len(set(last_three)) == 1:
                # Option: Randomly add an emoji to break the spam
                random_emoji = self.get_emoji_type('', randomReturn=True)
                meshLeaderboard['emojiSlotWindow'].append(random_emoji)
                logger.debug(f"System: WoTd: Detected emoji spam, added random emoji '{random_emoji}' to slot window.")
                # Optionally, you can still scramble or pop as well if you want
                random.shuffle(meshLeaderboard['emojiSlotWindow'])
                meshLeaderboard['emojiSlotWindow'].pop()

        # # Debug: Show slot window status before jackpot check
        # logger.debug(
        #     f"Emoji Slot Window: {meshLeaderboard['emojiSlotWindow']} | "
        #     f"Jackpot Length: {self.slot_jackpot_length} | "
        #     f"Unique: {set(meshLeaderboard['emojiSlotWindow'])} | "
        #     f"Needed: {self.slot_jackpot_length - len(meshLeaderboard['emojiSlotWindow'])}"
        # )

        # Jackpot: all emojis in window are the same
        if (
            len(meshLeaderboard['emojiSlotWindow']) == self.slot_jackpot_length and
            len(set(meshLeaderboard['emojiSlotWindow'])) == 1
        ):
            winner_msg = f"🎰 JACKPOT! {emoji * self.slot_jackpot_length}"
            meshLeaderboard['emojiSlotWindow'] = []
            self.slot_jackpot_length = random.choice([3, 4, 5])  # Randomize jackpot length after win
            return winner_msg

        return None

# Example usage:
# theWordOfTheDay = WordOfTheDayGame()
# happened, entry = theWordOfTheDay.did_it_happen("I love serendipity!")
# if happened:
#     print(f"Found the word of the day: {entry['word']} - {entry['meta']}")