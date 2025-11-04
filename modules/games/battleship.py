#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Battleship game module Meshing Around
# 2025 K7MHI Kelly Keeton
import random
import copy
import uuid
import time

OCEAN = "~"
FIRE = "x"
HIT = "*"
SIZE = 10
SHIPS = [5, 4, 3, 3, 2]
SHIP_NAMES = ["✈️Carrier", "Battleship", "Cruiser", "Submarine", "Destroyer"]

class Session:
    def __init__(self, player1_id, player2_id=None, vs_ai=True):
        self.session_id = str(uuid.uuid4())
        self.vs_ai = vs_ai
        self.player1_id = player1_id
        self.player2_id = player2_id
        self.game = Battleship(vs_ai=vs_ai)
        self.next_turn = player1_id
        self.last_move = None
        self.shots_fired = 0
        self.start_time = time.time()

class Battleship:
    sessions = {}
    short_codes = {}

    @classmethod
    def _generate_short_code(cls):
        while True:
            code = str(random.randint(1000, 9999))
            if code not in cls.short_codes:
                return code

    @classmethod
    def new_game(cls, player_id, vs_ai=True, p2p_id=None):
        session = Session(player1_id=player_id, player2_id=p2p_id, vs_ai=vs_ai)
        cls.sessions[session.session_id] = session
        if not vs_ai:
            code = cls._generate_short_code()
            cls.short_codes[code] = session.session_id
            msg = (
                "New 🚢Battleship🚢 game started!\n"
                "Joining player goes first, waiting for them to join...\n"
                f"Share\n'battleship join {code}'"
            )
            return msg, code
        else:
            msg = (
                "New 🚢Battleship🤖 game started!\n"
                "Enter your move using coordinates: row-letter, column-number.\n"
                "Example: B5 or C,7\n"
                "Type 'exit' or 'end' to quit the game."
            )
            return msg, session.session_id

    @classmethod
    def end_game(cls, session_id):
        if session_id in cls.sessions:
            del cls.sessions[session_id]
        return "Thanks for playing 🚢Battleship🚢"

    @classmethod
    def get_session(cls, code_or_session_id):
        session_id = cls.short_codes.get(code_or_session_id, code_or_session_id)
        return cls.sessions.get(session_id)

    def __init__(self, vs_ai=True):
        if vs_ai:
            self.player_board = self._blank_board()
            self.ai_board = self._blank_board()
            self.player_radar = self._blank_board()
            self.ai_radar = self._blank_board()
            self.number_board = self._blank_board()
            self.player_alive = sum(SHIPS)
            self.ai_alive = sum(SHIPS)
            self._place_ships(self.player_board, self.number_board)
            self._place_ships(self.ai_board)
            self.ai_targets = []
            self.ai_last_hit = None
            self.ai_orientation = None
        else:
            # P2P: Each player has their own board and radar
            self.player1_board = self._blank_board()
            self.player2_board = self._blank_board()
            self.player1_radar = self._blank_board()
            self.player2_radar = self._blank_board()
            self.player1_alive = sum(SHIPS)
            self.player2_alive = sum(SHIPS)
            self._place_ships(self.player1_board)
            self._place_ships(self.player2_board)

    def _blank_board(self):
        return [[OCEAN for _ in range(SIZE)] for _ in range(SIZE)]

    def _place_ships(self, board, number_board=None):
        for idx, ship_len in enumerate(SHIPS):
            placed = False
            while not placed:
                vertical = random.choice([True, False])
                if vertical:
                    row = random.randint(0, SIZE - ship_len)
                    col = random.randint(0, SIZE - 1)
                    if all(board[row + i][col] == OCEAN for i in range(ship_len)):
                        for i in range(ship_len):
                            board[row + i][col] = str(idx)
                            if number_board is not None:
                                number_board[row + i][col] = idx
                        placed = True
                else:
                    row = random.randint(0, SIZE - 1)
                    col = random.randint(0, SIZE - ship_len)
                    if all(board[row][col + i] == OCEAN for i in range(ship_len)):
                        for i in range(ship_len):
                            board[row][col + i] = str(idx)
                            if number_board is not None:
                                number_board[row][col + i] = idx
                        placed = True

    def player_move(self, row, col):
        """Player fires at AI's board. Returns 'hit', 'miss', or 'sunk:<ship_idx>'."""
        if self.player_radar[row][col] != OCEAN:
            return "repeat"
        if self.ai_board[row][col] not in (OCEAN, FIRE, HIT):
            self.player_radar[row][col] = HIT
            ship_idx = int(self.ai_board[row][col])
            self.ai_board[row][col] = HIT
            if self._is_ship_sunk(self.ai_board, ship_idx):
                self.ai_alive -= SHIPS[ship_idx]
                return f"sunk:{ship_idx}"
            return "hit"
        else:
            self.player_radar[row][col] = FIRE
            self.ai_board[row][col] = FIRE
            return "miss"

    def ai_move(self):
        """AI fires at player's board. Returns (row, col, result or 'sunk:<ship_idx>')."""
        while True:
            row = random.randint(0, SIZE - 1)
            col = random.randint(0, SIZE - 1)
            if self.ai_radar[row][col] == OCEAN:
                break
        if self.player_board[row][col] not in (OCEAN, FIRE, HIT):
            self.ai_radar[row][col] = HIT
            ship_idx = int(self.player_board[row][col])
            self.player_board[row][col] = HIT
            if self._is_ship_sunk(self.player_board, ship_idx):
                self.player_alive -= SHIPS[ship_idx]
                return row, col, f"sunk:{ship_idx}"
            return row, col, "hit"
        else:
            self.ai_radar[row][col] = FIRE
            self.player_board[row][col] = FIRE
            return row, col, "miss"

    def p2p_player_move(self, row, col, attacker, defender, radar, defender_alive_attr):
        """P2P: attacker fires at defender's board, updates radar and defender's board."""
        if radar[row][col] != OCEAN:
            return "repeat"
        if defender[row][col] not in (OCEAN, FIRE, HIT):
            radar[row][col] = HIT
            ship_idx = int(defender[row][col])
            defender[row][col] = HIT
            if self._is_ship_sunk(defender, ship_idx):
                setattr(self, defender_alive_attr, getattr(self, defender_alive_attr) - SHIPS[ship_idx])
                return f"sunk:{ship_idx}"
            return "hit"
        else:
            radar[row][col] = FIRE
            defender[row][col] = FIRE
            return "miss"

    def _is_ship_sunk(self, board, ship_idx):
        for row in board:
            for cell in row:
                if cell == str(ship_idx):
                    return False
        return True

    def is_game_over(self, vs_ai=True):
        if vs_ai:
            return self.player_alive == 0 or self.ai_alive == 0
        else:
            return self.player1_alive == 0 or self.player2_alive == 0

    def get_player_board(self):
        return copy.deepcopy(self.player_board)

    def get_player_radar(self):
        return copy.deepcopy(self.player_radar)

    def get_ai_board(self):
        return copy.deepcopy(self.ai_board)

    def get_ai_radar(self):
        return copy.deepcopy(self.ai_radar)

    def get_ship_status(self, board):
        status = {}
        for idx in range(len(SHIPS)):
            afloat = any(str(idx) in row for row in board)
            status[idx] = "Afloat" if afloat else "Sunk"
        return status

    def display_draw_board(self, board, label="Board"):
        print(f"{label}")
        print("   " + " ".join(str(i+1).rjust(2) for i in range(SIZE)))
        for idx, row in enumerate(board):
            print(chr(ord('A') + idx) + " " + " ".join(cell.rjust(2) for cell in row))

def get_short_name(node_id):
    from mesh_bot import battleshipTracker
    entry = next((e for e in battleshipTracker if e['nodeID'] == node_id), None)
    return entry['short_name'] if entry and 'short_name' in entry else str(node_id)

def playBattleship(message, nodeID, deviceID, session_id=None):
    if not session_id or session_id not in Battleship.sessions:
        return Battleship.new_game(nodeID, vs_ai=True)

    session = Battleship.get_session(session_id)
    game = session.game

    # Check for game over
    if not session.vs_ai and game.is_game_over(vs_ai=False):
        winner = None
        if game.player1_alive == 0:
            winner = get_short_name(session.player2_id)
        elif game.player2_alive == 0:
            winner = get_short_name(session.player1_id)
        else:
            winner = "Nobody"
        elapsed = int(time.time() - session.start_time)
        mins, secs = divmod(elapsed, 60)
        time_str = f"{mins}m {secs}s" if mins else f"{secs}s"
        shots = session.shots_fired
        return (
            f"Game over! {winner} wins! 🚢🏆\n"
            f"Game finished in {shots} shots and {time_str}.\n"
        )

    if not session.vs_ai and session.player2_id is None:
        code = next((k for k, v in Battleship.short_codes.items() if v == session.session_id), None)
        return (
            f"Waiting for another player to join.\n"
            f"Share this code: {code}\n"
            "Type 'end' to cancel this P2P game."
        )

    if nodeID != session.next_turn:
        return "It's not your turn!"

    msg = message.strip().lower()
    if msg.startswith("battleship"):
        msg = msg[len("battleship"):].strip()
    if msg.startswith("b:"):
        msg = msg[2:].strip()
    msg = msg.replace(" ", "")

    x = y = None
    if "," in msg:
        parts = msg.split(",")
        if len(parts) == 2 and len(parts[0]) == 1 and parts[0].isalpha() and parts[1].isdigit():
            y = ord(parts[0]) - ord('a')
            x = int(parts[1]) - 1
        else:
            return "Invalid coordinates. Use format A2 or A,2 (row letter, column number)."
    elif len(msg) >= 2 and msg[0].isalpha() and msg[1:].isdigit():
        y = ord(msg[0]) - ord('a')
        x = int(msg[1:]) - 1
    else:
        return "Invalid command. Use format A2 or A,2 (row letter, column number)."

    if x is None or y is None or not (0 <= x < SIZE and 0 <= y < SIZE):
        return "Coordinates out of range."

    ai_row = ai_col = ai_result = None
    over = False

    if session.vs_ai:
        result = game.player_move(y, x)
        ai_row, ai_col, ai_result = game.ai_move()
        over = game.is_game_over(vs_ai=True)
    else:
        # P2P: determine which player is moving and fire at the other player's board
        if nodeID == session.player1_id:
            attacker = "player1"
            defender = "player2"
            result = game.p2p_player_move(
                y, x,
                game.player1_board, game.player2_board,
                game.player1_radar, "player2_alive"
            )
        else:
            attacker = "player2"
            defender = "player1"
            result = game.p2p_player_move(
                y, x,
                game.player2_board, game.player1_board,
                game.player2_radar, "player1_alive"
            )
        over = game.is_game_over(vs_ai=False)
        coord_str = f"{chr(y+65)}{x+1}"
        session.last_move = (nodeID, coord_str, result)

    # --- DEBUG DISPLAY ---
    DEBUG = False
    if DEBUG:
        if session.vs_ai:
            game.display_draw_board(game.player_board, label=f"Player Board ({session.player1_id})")
            game.display_draw_board(game.player_radar, label="Player Radar")
            game.display_draw_board(game.ai_board, label="AI Board")
            game.display_draw_board(game.ai_radar, label="AI Radar")
        else:
            p1_id = session.player1_id
            p2_id = session.player2_id if session.player2_id else "Waiting"
            game.display_draw_board(game.player1_board, label=f"Player 1 Board ({p1_id})")
            game.display_draw_board(game.player1_radar, label="Player 1 Radar")
            game.display_draw_board(game.player2_board, label=f"Player 2 Board ({p2_id})")
            game.display_draw_board(game.player2_radar, label="Player 2 Radar")

    # Format radar as a 4x4 grid centered on the player's move
    if session.vs_ai:
        radar = game.get_player_radar()
    else:
        radar = game.player1_radar if nodeID == session.player1_id else game.player2_radar

    window_size = 4
    half_window = window_size // 2
    min_row = max(0, min(y - half_window, SIZE - window_size))
    max_row = min(SIZE, min_row + window_size)
    min_col = max(0, min(x - half_window, SIZE - window_size))
    max_col = min(SIZE, min_col + window_size)

    radar_str = "🗺️" + " ".join(str(i+1) for i in range(min_col, max_col)) + "\n"
    for idx in range(min_row, max_row):
        radar_str += chr(ord('A') + idx) + "  " + " ".join(radar[idx][j] for j in range(min_col, max_col)) + "\n"

    def format_ship_status(status_dict):
        afloat = 0
        for idx, state in status_dict.items():
            if state == "Afloat":
                afloat += 1
        return f"{afloat}/{len(SHIPS)} afloat"

    if session.vs_ai:
        ai_status_str = format_ship_status(game.get_ship_status(game.ai_board))
        player_status_str = format_ship_status(game.get_ship_status(game.player_board))
    else:
        ai_status_str = format_ship_status(game.get_ship_status(game.player2_board))
        player_status_str = format_ship_status(game.get_ship_status(game.player1_board))

    def move_result_text(res, is_player=True):
        if res.startswith("sunk:"):
            idx = int(res.split(":")[1])
            name = SHIP_NAMES[idx]
            return f"Sunk🎯 {name}!"
        elif res == "hit":
            return "💥Hit!"
        elif res == "miss":
            return "missed"
        elif res == "repeat":
            return "📋already targeted"
        else:
            return res

    # After a valid move, switch turns
    if session.vs_ai:
        session.next_turn = nodeID
    else:
        session.next_turn = session.player2_id if nodeID == session.player1_id else session.player1_id

    # Increment shots fired
    session.shots_fired += 1

    # Waste of ammo comment
    funny_comment = ""
    if session.shots_fired % 50 == 0:
        funny_comment = f"\n🥵shoCaptain, that's {session.shots_fired} rounds! The barrels are getting warm!"

    # Output message
    if session.vs_ai:
        msg_out = (
            f"Your move: {move_result_text(result)}\n"
            f"AI ships: {ai_status_str}\n"
            f"Radar:\n{radar_str}"
            f"AI move: {chr(ai_row+65)}{ai_col+1} ({move_result_text(ai_result, False)})\n"
            f"Your ships: {player_status_str}"
            f"{funny_comment}"
        )
    else:
        my_name = get_short_name(nodeID)
        opponent_id = session.player2_id if nodeID == session.player1_id else session.player1_id
        opponent_short_name = get_short_name(opponent_id) if opponent_id else "Waiting"
        opponent_label = f"{opponent_short_name}:"
        my_move_result_str = f"Your move: {move_result_text(result)}\n"
        last_move_str = ""
        if session.last_move and session.last_move[0] != nodeID:
            last_player_short_name = get_short_name(session.last_move[0])
            last_coord = session.last_move[1]
            last_result = move_result_text(session.last_move[2])
            last_move_str = f"Last move by {last_player_short_name}: {last_coord} ({last_result})\n"
        if session.next_turn == nodeID:
            turn_prompt = f"Your turn, {my_name}! Enter your move:"
        else:
            turn_prompt = f"Waiting for {opponent_short_name}..."
        msg_out = (
            f"{my_move_result_str}"
            f"{last_move_str}"
            f"{opponent_label} {ai_status_str}\n"
            f"Radar:\n{radar_str}"
            f"Your ships: {player_status_str}\n"
            f"{turn_prompt}"
            f"{funny_comment}"
        )

    if over:
        elapsed = int(time.time() - session.start_time)
        mins, secs = divmod(elapsed, 60)
        time_str = f"{mins}m {secs}s" if mins else f"{secs}s"
        shots = session.shots_fired
        if session.vs_ai:
            if game.player_alive == 0:
                winner = "AI 🤖"
                msg_out += f"\nGame over! {winner} wins! Better luck next time.\n"
            else:
                winner = get_short_name(nodeID)
                msg_out += (
                    f"\nGame over! {winner} wins! You sank all the AI's ships! 🎉\n"
                    f"Took {shots} shots in {time_str}.\n"
                )
        else:
            # P2P: Announce winner by short name
            if game.player1_alive == 0:
                winner = get_short_name(session.player2_id)
            elif game.player2_alive == 0:
                winner = get_short_name(session.player1_id)
            else:
                winner = "Nobody"
            msg_out += (
                f"\nGame over! {winner} wins! 🚢🏆\n"
                f"Game finished in {shots} shots and {time_str}.\n"
            )
        msg_out += "Type 'battleship' to start a new game."

    return msg_out