## Word of the Day Game — Rules & Features

- **Word of the Day:**  
  Each day, a new word is chosen from `data/wotd.json` (or a default list if missing). Mention the word (or its leet/1337 variants) in chat to win and trigger a new word.
- **Bingo Mini-Game:**  
  A random 3x3 bingo card of words, drawn from `data/bingo.json` (or a default list if missing). Mention words from the card in chat. Complete a row, column, or diagonal to win BINGO and get a new card.
- **Emoji Mini-Game:**  
  Use emojis in chat to:
  - Play a slot machine: send the same emoji several times in a row to hit the JACKPOT!
- **Data Files:**
  - `data/wotd.json`: List of words and definitions for the Word of the Day.
[
  {
    "word": "serendipity",
    "meta": "The occurrence of events by chance in a happy or beneficial way."
  },
  {
    "word": "ephemeral",
    "meta": "Lasting for a very short time."
  },
  {
    "word": "sonder",
    "meta": "The realization that each passerby has a life as vivid and complex as your own."
  }
]
  - `data/bingo.json`: List of animal words for bingo cards.  
[
  "dog",
  "cat",
  "fish",
  "bird",
  "hamster",
  "rabbit",
  "turtle",
  "lizard",
  "snake"
]