# Tic-Tac-Toe game for Meshtastic mesh-bot
# Human is X, bot is O
# Board positions chosen by numbers 1-9
# 2025
import random

class TicTacToe:
    def __init__(self):
        self.game = {}

    def new_game(self, id):
        """Start a new game"""
        games = won = 0
        ret = ""
        if id in self.game:
            games = self.game[id]["games"]
            won = self.game[id]["won"]
            ret += f"Games:{games} Won:{won}\n"

        self.game[id] = {
            "board": [" "] * 9,  # 3x3 board as flat list
            "player": "X",       # Human is X, bot is O
            "games": games + 1,
            "won": won,
            "turn": "human"      # whose turn it is
        }
        ret += self.show_board(id)
        ret += "Pick 1-9:"
        return ret

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
                cell = b[pos] if b[pos] != " " else str(pos + 1)
                row += cell
                if j < 2:
                    row += "|"
            board_str += row
            if i < 2:
                board_str += "\n-+-+-\n"
        
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
        g["board"][pos] = "X"
        return True

    def bot_move(self, id):
        """AI makes a move"""
        g = self.game[id]
        
        # Simple AI: Try to win, block, or pick random
        move = self.find_winning_move(id, "O")  # Try to win
        if move == -1:
            move = self.find_winning_move(id, "X")  # Block player
        if move == -1:
            move = self.find_random_move(id)  # Random move
        
        if move != -1:
            g["board"][move] = "O"
        return move

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

    def find_random_move(self, id):
        """Find a random empty position"""
        g = self.game[id]
        empty = [i for i in range(9) if g["board"][i] == " "]
        return random.choice(empty) if empty else -1

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
        
        if winner == "X":
            g["won"] += 1
            return "🎉You won!"
        elif winner == "O":
            return "🤖Bot wins!"
        else:
            return "🤝Tie game!"

    def play(self, id, input_msg):
        """Main game play function"""
        if id not in self.game:
            return self.new_game(id)
        
        # If input is just "tictactoe", show current board
        if input_msg.lower().strip() == "tictactoe":
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

    def end(self, id):
        """End game completely (called by 'end' command)"""
        if id in self.game:
            del self.game[id]


# Global instances for the bot system
tictactoeTracker = []
tictactoe = TicTacToe()