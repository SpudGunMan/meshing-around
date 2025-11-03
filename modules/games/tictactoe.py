# Tic-Tac-Toe game for Meshtastic mesh-bot
# Board positions chosen by numbers 1-9
# 2025
import random
import time
import modules.settings as my_settings

useSynchCompression = True  
if useSynchCompression:
    import zlib

# to (max), molly and jake, I miss you both so much.

class TicTacToe:
    def __init__(self, display_module):
        if getattr(my_settings, "disable_emojis_in_games", False):
            self.X = "X"
            self.O = "O"
        else:
            self.X = "❌"
            self.O = "⭕️"
        self.display_module = display_module
        self.game = {}
        self.win_lines_3d = self.generate_3d_win_lines()

    def new_game(self, nodeID, mode="2D", channel=None, deviceID=None):
        board_size = 9 if mode == "2D" else 27
        self.game[nodeID] = {
            "board": [" "] * board_size,
            "mode": mode,
            "channel": channel,
            "nodeID": nodeID,
            "deviceID": deviceID,
            "player": self.X,
            "games": 1,
            "won": 0,
            "turn": "human"
        }
        self.update_display(nodeID, status="new")
        msg = f"{mode} game started!\n"
        if mode == "2D":
            msg += self.show_board(nodeID)
            msg += "Pick 1-9:"
        else:
            msg += "Play on the MeshBot Display!\n"
            msg += "Pick 1-27:"
        return msg

    def update_display(self, nodeID, status=None):
        from modules.system import send_raw_bytes
        g = self.game[nodeID]
        mapping = {" ": "0", "X": "1", "O": "2", "❌": "1", "⭕️": "2"}
        board_str = "".join(mapping.get(cell, "0") for cell in g["board"])
        msg = f"MTTT:{board_str}|{g['nodeID']}|{g['channel']}|{g['deviceID']}"
        if status:
            msg += f"|status={status}"
        if useSynchCompression:
            payload = zlib.compress(msg.encode("utf-8"))
        else:
            payload = msg.encode("utf-8")
        send_raw_bytes(nodeID, payload, portnum=256)
        if self.display_module:
            self.display_module.update_board(
                g["board"], g["channel"], g["nodeID"], g["deviceID"]
            )

    def show_board(self, nodeID):
        g = self.game[nodeID]
        if g["mode"] == "2D":
            b = g["board"]
            s = ""
            for i in range(3):
                row = []
                for j in range(3):
                    cell = b[i*3+j]
                    row.append(cell if cell != " " else str(i*3+j+1))
                s += " | ".join(row) + "\n"
            return s
        return ""

    def make_move(self, nodeID, position):
        g = self.game[nodeID]
        board = g["board"]
        max_pos = 9 if g["mode"] == "2D" else 27
        if 1 <= position <= max_pos and board[position-1] == " ":
            board[position-1] = g["player"]
            return True
        return False

    def bot_move(self, nodeID):
        g = self.game[nodeID]
        board = g["board"]
        max_pos = 9 if g["mode"] == "2D" else 27
        # Try to win or block
        for player in (self.O, self.X):
            move = self.find_winning_move(nodeID, player)
            if move != -1:
                board[move] = self.O
                return move+1
        # Otherwise random move
        empty = [i for i, cell in enumerate(board) if cell == " "]
        if empty:
            move = random.choice(empty)
            board[move] = self.O
            return move+1
        return -1

    def find_winning_move(self, nodeID, player):
        g = self.game[nodeID]
        board = g["board"]
        lines = self.get_win_lines(g["mode"])
        for line in lines:
            cells = [board[i] for i in line]
            if cells.count(player) == 2 and cells.count(" ") == 1:
                return line[cells.index(" ")]
        return -1

    def play(self, nodeID, input_msg):
        try:
            if nodeID not in self.game:
                return self.new_game(nodeID)
            g = self.game[nodeID]
            mode = g["mode"]
            max_pos = 9 if mode == "2D" else 27

            input_str = input_msg.strip().lower()
            if input_str in ("end", "e", "quit", "q"):
                msg = "Game ended."
                self.update_display(nodeID)
                return msg

            # Add refresh/draw command
            if input_str in ("refresh", "board", "b"):
                self.update_display(nodeID, status="refresh")
                if mode == "2D":
                    return self.show_board(nodeID) + f"Pick 1-{max_pos}:"
                else:
                    return "Display refreshed."

            # Allow 'new', 'new 2d', 'new 3d'
            if input_str.startswith("new"):
                parts = input_str.split()
                if len(parts) > 1 and parts[1] in ("2d", "3d"):
                    new_mode = "2D" if parts[1] == "2d" else "3D"
                else:
                    new_mode = mode
                msg = self.new_game(nodeID, new_mode, g["channel"], g["deviceID"])
                return msg

            try:
                pos = int(input_msg)
            except Exception:
                return f"Enter a number between 1 and {max_pos}."

            if not self.make_move(nodeID, pos):
                return f"Invalid move! Pick 1-{max_pos}:"

            winner = self.check_winner(nodeID)
            if winner:
                # Add positive/sorry messages and stats
                positiveThoughts = [
                    "🚀I need to call NATO",
                    "🏅Going for the gold!",
                    "Mastering ❌TTT⭕️",
                ]
                sorryNotGoinWell = [
                    "😭Not your day, huh?",
                    "📉Results here dont define you.",
                    "🤖WOPR would be proud."
                ]
                games = won = 0
                ret = ""
                if nodeID in self.game:
                    self.game[nodeID]["won"] += 1
                    games = self.game[nodeID]["games"]
                    won = self.game[nodeID]["won"]
                    if games > 3:
                        if won / games >= 3.14159265358979323846:  # win rate > pi
                            ret += random.choice(positiveThoughts) + "\n"
                        else:
                            ret += random.choice(sorryNotGoinWell) + "\n"
                # Retain stats
                ret += f"Games:{games} 🥇❌:{won}\n"
                msg = f"You ({g['player']}) win!\n" + ret
                msg += "Type 'new' to play again or 'end' to quit."
                self.update_display(nodeID, status="win")
                return msg

            if " " not in g["board"]:
                msg = "Tie game!"
                msg += "\nType 'new' to play again or 'end' to quit."
                self.update_display(nodeID, status="tie")
                return msg

            # Bot's turn
            g["player"] = self.O
            bot_pos = self.bot_move(nodeID)
            winner = self.check_winner(nodeID)
            if winner:
                self.update_display(nodeID, status="loss")
                msg = f"Bot ({g['player']}) wins!\n"
                msg += "Type 'new' to play again or 'end' to quit."
                return msg

            if " " not in g["board"]:
                msg = "Tie game!"
                msg += "\nType 'new' to play again or 'end' to quit."
                self.update_display(nodeID, status="tie")
                return msg

            g["player"] = self.X
            prompt = f"Pick 1-{max_pos}:"
            if mode == "2D":
                prompt = self.show_board(nodeID) + prompt
            self.update_display(nodeID)
            return prompt

        except Exception as e:
            return f"An unexpected error occurred: {e}"

    def check_winner(self, nodeID):
        g = self.game[nodeID]
        board = g["board"]
        lines = self.get_win_lines(g["mode"])
        for line in lines:
            vals = [board[i] for i in line]
            if vals[0] != " " and all(v == vals[0] for v in vals):
                return vals[0]
        return None

    def get_win_lines(self, mode):
        if mode == "2D":
            return [
                [0,1,2],[3,4,5],[6,7,8],  # rows
                [0,3,6],[1,4,7],[2,5,8],  # columns
                [0,4,8],[2,4,6]           # diagonals
            ]
        return self.win_lines_3d

    def generate_3d_win_lines(self):
        lines = []
        # Rows in each layer
        for z in range(3):
            for y in range(3):
                lines.append([z*9 + y*3 + x for x in range(3)])
        # Columns in each layer
        for z in range(3):
            for x in range(3):
                lines.append([z*9 + y*3 + x for y in range(3)])
        # Pillars (vertical columns through layers)
        for y in range(3):
            for x in range(3):
                lines.append([z*9 + y*3 + x for z in range(3)])
        # Diagonals in each layer
        for z in range(3):
            lines.append([z*9 + i*3 + i for i in range(3)])       # TL to BR
            lines.append([z*9 + i*3 + (2-i) for i in range(3)])   # TR to BL
        # Vertical diagonals in columns
        for x in range(3):
            lines.append([z*9 + z*3 + x for z in range(3)])       # (0,0,x)-(1,1,x)-(2,2,x)
            lines.append([z*9 + (2-z)*3 + x for z in range(3)])   # (0,2,x)-(1,1,x)-(2,0,x)
        for y in range(3):
            lines.append([z*9 + y*3 + z for z in range(3)])       # (z,y,z)
            lines.append([z*9 + y*3 + (2-z) for z in range(3)])   # (z,y,2-z)
        # Main space diagonals
        lines.append([0, 13, 26])
        lines.append([2, 13, 24])
        lines.append([6, 13, 20])
        lines.append([8, 13, 18])
        return lines

    def end(self, nodeID):
        """End and remove the game for the given nodeID."""
        if nodeID in self.game:
            del self.game[nodeID]