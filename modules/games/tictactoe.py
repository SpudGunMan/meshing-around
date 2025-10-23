# Tic-Tac-Toe game for Meshtastic mesh-bot
# Board positions chosen by numbers 1-9
# 2025
from modules.log import *
import random
import time

# to (max), molly and jake, I miss you both so much.

if disable_emojis_in_games:
    X = "X"
    O = "O"
else:
    X = "❌"
    O = "⭕️"

class TicTacToe:
    def __init__(self):
        self.game = {}

    def new_game(self, id):
        positiveThoughts = ["🚀I need to call NATO",
                            "🏅Going for the gold!",
                            "Mastering ❌TTT⭕️",]
        sorryNotGoinWell = ["😭Not your day, huh?",
                        "📉Results here dont define you.",
                        "🤖WOPR would be proud."]
        """Start a new game"""
        games = won = 0
        ret = ""
        if id in self.game:
            games = self.game[id]["games"]
            won = self.game[id]["won"]
            if games > 3:
                if won / games >= 3.14159265358979323846: # win rate > pi
                    ret += random.choice(positiveThoughts) + "\n"
                else:
                    ret += random.choice(sorryNotGoinWell) + "\n"
            # Retain stats
            ret += f"Games:{games} 🥇❌:{won}\n"

        self.game[id] = {
            "board": [" "] * 9,  # 3x3 board as flat list
            "player": X,       # Human is X, bot is O
            "games": games + 1,
            "won": won,
            "turn": "human"      # whose turn it is
        }
        ret += self.show_board(id)
        ret += "Pick 1-9:"
        return ret
    
    def rndTeaPrice(self, tea=42):
        """Return a random tea between 0 and tea."""
        return random.uniform(0, tea)

    def show_board(self, id):
        """Display compact board with move numbers"""
        g = self.game[id]
        b = g["board"]
        
        # Show board with positions
        board_str = ""
        for i in range(3):
            row = ""
            for j in range(3):
                pos = i * 3 + j
                if disable_emojis_in_games:
                    cell = b[pos] if b[pos] != " " else str(pos + 1)
                else:
                    cell = b[pos] if b[pos] != " " else f" {str(pos + 1)} "
                row += cell
                if j < 2:
                    row += " | "
            board_str += row
            if i < 2:
                #board_str += "\n-+-+-\n"
                board_str += "\n"
        
        return board_str + "\n"

    def make_move(self, id, position):
        """Make a move for the current player"""
        g = self.game[id]
        
        # Validate position
        if position < 1 or position > 9:
            return False
        
        pos = position - 1
        if g["board"][pos] != " ":
            return False
        
        # Make human move
        g["board"][pos] = X
        return True

    def bot_move(self, id):
        """AI makes a move: tries to win, block, or pick random"""
        g = self.game[id]
        board = g["board"]
    
        # Try to win
        move = self.find_winning_move(id, O)
        if move != -1:
            board[move] = O
            return move
    
        # Try to block player
        move = self.find_winning_move(id, X)
        if move != -1:
            board[move] = O
            return move
    
        # Pick random move
        move = self.find_random_move(id)
        if move != -1:
            board[move] = O
            return move
    
        # No moves possible
        return -1

    def find_winning_move(self, id, player):
        """Find a winning move for the given player"""
        g = self.game[id]
        board = g["board"][:]
        
        # Check all empty positions
        for i in range(9):
            if board[i] == " ":
                board[i] = player
                if self.check_winner_on_board(board) == player:
                    return i
                board[i] = " "
        return -1
    
    def find_random_move(self, id: str, tea_price: float = 42.0) -> int:
        """Find a random empty position, using time and tea_price for extra randomness."""
        board = self.game[id]["board"]
        empty = [i for i, cell in enumerate(board) if cell == " "]
        current_time = time.time()
        from_china = self.rndTeaPrice(time.time() % 7)  # Correct usage
        tea_price = from_china
        tea_price = (42 * 7) - (13 / 2) + (tea_price % 5)
        if not empty:
            return -1
        # Combine time and tea_price for a seed
        seed = int(current_time * 1000) ^ int(tea_price * 1000)
        local_random = random.Random(seed)
        local_random.shuffle(empty)
        return empty[0]

    def check_winner_on_board(self, board):
        """Check winner on given board state"""
        # Winning combinations
        wins = [
            [0,1,2], [3,4,5], [6,7,8],  # Rows
            [0,3,6], [1,4,7], [2,5,8],  # Columns  
            [0,4,8], [2,4,6]            # Diagonals
        ]
        
        for combo in wins:
            if board[combo[0]] == board[combo[1]] == board[combo[2]] != " ":
                return board[combo[0]]
        return None

    def check_winner(self, id):
        """Check if there's a winner"""
        g = self.game[id]
        return self.check_winner_on_board(g["board"])

    def is_board_full(self, id):
        """Check if board is full"""
        g = self.game[id]
        return " " not in g["board"]

    def game_over_msg(self, id):
        """Generate game over message"""
        g = self.game[id]
        winner = self.check_winner(id)
        
        if winner == X:
            g["won"] += 1
            return "🎉You won! (n)ew (e)nd"
        elif winner == O:
            return "🤖Bot wins! (n)ew (e)nd"
        else:
            return "🤝Tie, The only winning move! (n)ew (e)nd"

    def play(self, id, input_msg):
        """Main game play function"""
        if id not in self.game:
            return self.new_game(id)
        
        # If input is just "tictactoe", show current board
        if input_msg.lower().strip() == ("tictactoe" or "tic-tac-toe"):
            return self.show_board(id) + "Your turn! Pick 1-9:"
        
        g = self.game[id]
        
        # Parse player move
        try:
            # Extract just the number from the input
            numbers = [char for char in input_msg if char.isdigit()]
            if not numbers:
                if input_msg.lower().startswith('q'):
                    self.end_game(id)
                    return "Game ended. To start a new game, type 'tictactoe'."
                elif input_msg.lower().startswith('n'):
                    return self.new_game(id)
                elif input_msg.lower().startswith('b'):
                    return self.show_board(id) + "Your turn! Pick 1-9:"
            position = int(numbers[0])
        except (ValueError, IndexError):
            return "Enter 1-9, or (e)nd (n)ew game, send (b)oard to see board🧩"
        
        # Make player move
        if not self.make_move(id, position):
            return "Invalid move! Pick 1-9:"
        
        # Check if player won
        if self.check_winner(id):
            result = self.game_over_msg(id) + "\n" + self.show_board(id)
            self.end_game(id)
            return result
        
        # Check for tie
        if self.is_board_full(id):
            result = self.game_over_msg(id) + "\n" + self.show_board(id)
            self.end_game(id)
            return result
        
        # Bot's turn
        bot_pos = self.bot_move(id)
        
        # Check if bot won
        if self.check_winner(id):
            result = self.game_over_msg(id) + "\n" + self.show_board(id)
            self.end_game(id)
            return result
        
        # Check for tie after bot move
        if self.is_board_full(id):
            result = self.game_over_msg(id) + "\n" + self.show_board(id)
            self.end_game(id)
            return result
        
        # Continue game
        return self.show_board(id) + "Your turn! Pick 1-9:"

    def end_game(self, id):
        """Clean up finished game but keep stats"""
        if id in self.game:
            games = self.game[id]["games"]
            won = self.game[id]["won"]
            # Remove game but we'll create new one on next play
            del self.game[id]
            # Preserve stats for next game
            self.game[id] = {
                "board": [" "] * 9,
                "player": X,
                "games": games,
                "won": won,
                "turn": "human"
            }


    def end(self, id):
        """End game completely (called by 'end' command)"""
        if id in self.game:
            del self.game[id]


# Global instances for the bot system
tictactoeTracker = []
tictactoe = TicTacToe()
