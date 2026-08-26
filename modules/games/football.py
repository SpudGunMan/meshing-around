"""
Football Game Module for Mesh-Bot DE K7MHI 2026
Refactored from the classic BASIC N.F.U. Football game.
User plays against Bot with random team names and natural language command input.

Original credits:
- Ported to Python by Martin Thoma in 2022
- JavaScript version by Oscar Toledo G. (nanochess)
- https://github.com/coding-horror/basic-computer-games/tree/main/37_Football/python
"""

import random
import time
from typing import Dict, Optional, Tuple
from math import floor
from modules.log import logger


class Football:
    """Football game class for Mesh-Bot.
    User plays against Bot with random team names selected from PLAY_DATA.
    Natural language commands: run, pass, punt, field goal, score, help, end, new
    """
    
    # Play data: maps play number to offensive/defensive effectiveness
    PLAY_DATA = {
        "players": [17, 8, 4, 14, 19, 3, 10, 1, 7, 11, 15, 9, 5, 20, 13, 18, 16, 2, 12, 6,
                    20, 2, 17, 5, 8, 18, 12, 11, 1, 4, 19, 14, 10, 7, 9, 15, 6, 13, 16, 3],
        "actions": [
            "PITCHOUT", "TRIPLE REVERSE", "DRAW", "QB SNEAK", "END AROUND",
            "DOUBLE REVERSE", "LEFT SWEEP", "RIGHT SWEEP", "OFF TACKLE", "WISHBONE OPTION",
            "FLARE PASS", "SCREEN PASS", "ROLL OUT OPTION", "RIGHT CURL", "LEFT CURL",
            "WISHBONE OPTION", "SIDELINE PASS", "HALF-BACK OPTION", "RAZZLE-DAZZLE", "BOMB!!!!"
        ],
        "teams": ["Chirps", "Burps", "Quacks", "Barks", "Meows", "Hisses", "Roars", "Growls"]
    }
    
    # Natural language → play type mapping
    PLAY_COMMANDS = {
        "run": [0, 1, 2, 3, 4, 5, 6, 7, 8],  # Run plays (positions 1-9)
        "pass": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19],  # Pass plays (positions 11-20)
        "bomb": [19],  # Bomb play
        "sweep": [6, 7],  # Sweep plays
        "option": [9, 15],  # Option plays
        "screen": [11],  # Screen pass
        "curl": [13, 14],  # Curl plays
    }
    
    # Direct play name → index mapping
    PLAY_NAMES = {
        "pitchout": 0,
        "triple reverse": 1,
        "draw": 2,
        "qb sneak": 3,
        "end around": 4,
        "double reverse": 5,
        "left sweep": 6,
        "right sweep": 7,
        "off tackle": 8,
        "wishbone option": 9,
        "flare pass": 10,
        "screen pass": 11,
        "roll out option": 12,
        "right curl": 13,
        "left curl": 14,
        "sideline pass": 16,
        "half-back option": 17,
        "razzle-dazzle": 18,
        "bomb": 19,
    }
    
    def __init__(self, display_module=None):
        """Initialize Football game.
        
        Args:
            display_module: Optional display module for visual output (future use)
        """
        self.display_module = display_module
        self.game = {}  # game[nodeID] = game state dict
        self.winning_score = 20  # Default winning score
    
    def new_game(self, nodeID: int, winning_score: int = 20) -> str:
        """Start a new football game.
        
        Args:
            nodeID: User's mesh node ID
            winning_score: Points needed to win
            
        Returns:
            Welcome message with game info and initial prompt
        """
        self.winning_score = winning_score
        
        # Initialize play scramble (aa, ba, ca arrays from original)
        player_data = [num - 1 for num in self.PLAY_DATA["players"]]
        aa = [-100] * 20  # User team play indices
        ba = [-100] * 20  # Bot team play indices
        ca = [-100] * 40  # Combined scramble
        
        for i in range(40):
            index = player_data[i - 1]
            if i < 20:
                aa[index] = i
            else:
                ba[index] = i - 20
            ca[i] = index
        
        # Random coin flip for initial possession
        initial_possession = random.randint(0, 1)  # 0 = user, 1 = bot
        
        # Select random team names from PLAY_DATA
        team_names = random.sample(self.PLAY_DATA["teams"], 2)
        user_team = team_names[0]
        bot_team = team_names[1]
        
        self.game[nodeID] = {
            "nodeID": nodeID,
            "user_team": user_team,
            "bot_team": bot_team,
            "score": [0, 0],  # [User team, Bot team]
            "possession": initial_possession,  # 0=user, 1=bot
            "position": 20 if initial_possession == 0 else 50,  # Ball position (0-100), 50=midfield after kickoff
            "down": 1,
            "yards_to_go": 10,
            "position_at_drive_start": 20 if initial_possession == 0 else 50,
            "games": 1,
            "aa": aa,  # User team play indices
            "ba": ba,  # Bot team play indices
            "ca": ca,  # Combined scramble
            "turn": "user" if initial_possession == 0 else "bot",
            "last_played": time.time(),
            "game_over": False,
            "last_play_result": "",
            "waiting_for_conversion": False,  # Flag to wait for conversion type choice
        }
        
        msg = "🏈 LET'S PLAY 🏈\n"
        msg += f"{user_team} vs 🤖 {bot_team} winner at {self.winning_score} pts\n\n"
        msg += f"🪙 {user_team if initial_possession == 0 else bot_team} receives kickoff\n"
        msg += self._get_field_display(nodeID)
        msg += "\nPlay Commands: run, pass, sweep, bomb, punt, or field goal, or help.\n\n"
        
        if initial_possession == 1:  # Bot receives
            msg += self._handle_bot_kickoff(nodeID)
            msg += "\n" + self._get_field_display(nodeID)
            msg += "\n\n📍 Your Play?"
        
        return msg
    
    def play(self, nodeID: int, command: str) -> str:
        """Process user's play command.
        
        Args:
            nodeID: User's mesh node ID
            command: Natural language command (e.g., "run", "pass")
            
        Returns:
            Message with play result, field update, and next prompt
        """
        if nodeID not in self.game:
            return "Game not started. Type 'football new' to begin."
        
        game = self.game[nodeID]
        command = command.strip().lower()
        
        # Check if waiting for conversion type choice after TD
        if game.get("waiting_for_conversion", False):
            if command in ("kick", "1"):
                msg = self._score_touchdown(nodeID, "", conversion_type="kick")
            elif command in ("2pt", "2"):
                msg = self._score_touchdown(nodeID, "", conversion_type="2pt")
            else:
                return "After touchdown, choose: 'kick' for 1-point or '2pt' for 2-point conversion"
            
            game["waiting_for_conversion"] = False
            
            # Check for game over
            if self._check_game_over(nodeID):
                return msg + "\n\n" + self._end_game(nodeID)
            
            # Bot now has possession - play full drive automatically
            msg += "\n\n🔄 POSSESSION CHANGE - 🤖\n\n" + self._play_bot_full_drive(nodeID)
            # Check for game over again
            if self._check_game_over(nodeID):
                return msg + "\n\n" + self._end_game(nodeID)
            game["last_played"] = time.time()
            return msg
        
        # Handle special commands
        if command in ("end", "e", "quit", "q"):
            return self._end_game(nodeID)
        
        if command in ("score", "s"):
            msg = self._get_scores(nodeID)
            msg += "\n" + self._get_field_display(nodeID)
            msg += "\nCall Play"
            return msg
        
        if command in ("help", "h", "?"):
            return self._get_help_text(nodeID)
        
        if command in ("new", "n"):
            return self.new_game(nodeID, self.winning_score)
        
        # If bot's turn, play entire bot drive automatically
        if game["possession"] == 1:  # Bot possession
            play_result = self._play_bot_full_drive(nodeID)
            # Check for game over
            if self._check_game_over(nodeID):
                return play_result + "\n\n" + self._end_game(nodeID)
            # After bot drive, prompt user for their turn
            play_result += "\n" + self._get_field_display(nodeID)
            play_result += "\n\n📍 Your Play?"
            game["last_played"] = time.time()
            return play_result
        
        # Parse user's play command
        play_result = self._execute_user_play(nodeID, command)
        game["last_play_result"] = play_result
        
        # Check for game over
        if self._check_game_over(nodeID):
            return play_result + "\n\n" + self._end_game(nodeID)
        
        # If still user possession (didn't lose it), prompt for next play
        if game["possession"] == 0:
            play_result += "\n" + self._get_field_display(nodeID)
            play_result += "\n\n📍 Next Play?"
        else:
            # Bot gained possession, play entire bot drive automatically
            play_result += "\n\n🔄 POSSESSION CHANGE - 🤖\n\n" + self._play_bot_full_drive(nodeID)
            # Check for game over
            if self._check_game_over(nodeID):
                return play_result + "\n\n" + self._end_game(nodeID)
            # After bot drive completes, show field and prompt user
            play_result += "\n" + self._get_field_display(nodeID)
            play_result += "\n\n📍 Your Play?"
        
        game["last_played"] = time.time()
        return play_result
    
    def _execute_user_play(self, nodeID: int, command: str) -> str:
        """Execute user's offensive play.
        
        Returns play result message and updates game state.
        """
        game = self.game[nodeID]
        msg = f"\n({game['user_team']})\n\n"
        
        # Handle special 4th down scenarios
        if game["down"] == 4:
            if "punt" in command:
                return self._execute_punt(nodeID)
            elif "field" in command or "goal" in command or "fg" in command:
                return self._execute_field_goal(nodeID)
            elif "go" in command or "try" in command or "gain" in command:
                pass  # Fall through to normal play
            else:
                # Default: punt on 4th down
                return self._execute_punt(nodeID)
        
        # Parse natural language to play type
        play_type = self._parse_play_command(command)
        if play_type is None:
            return f"❓ Unknown command: '{command}'\nTry: run, pass, bomb, sweep, option, screen, or punt/field goal"
        
        # Get user's play number
        user_play_num = random.choice(play_type)
        
        # Get bot's defensive play (biased random)
        bot_play_num = self._get_bot_play(nodeID, user_play_type=play_type)
        
        # Calculate yards gained
        aa = game["aa"]
        ba = game["ba"]
        yards = self._calculate_yards(nodeID, user_play_num, bot_play_num)
        
        # Build play description
        play_name = self.PLAY_DATA["actions"][user_play_num]
        bot_defense = self.PLAY_DATA["actions"][bot_play_num]
        
        msg += f"Offense: {play_name}\n"
        msg += f"Defense (🤖 {game['bot_team']}): {bot_defense}\n"
        
        # Check for penalties before play
        penalty_result = self._check_penalties(nodeID, is_pass_play=any(p in [10, 11, 12, 13, 14, 15, 16, 17, 18, 19] for p in play_type))
        if penalty_result:
            msg += penalty_result + "\n\n"
            # Replay the down
            msg += "🔄 Same down, replay\n"
            return msg
        
        # Check for interception on pass plays (8% chance)
        is_pass_play = any(play in [10, 11, 12, 13, 14, 15, 16, 17, 18, 19] for play in play_type)
        if is_pass_play and random.random() < 0.08:
            msg += f"🔴 INTERCEPTION! {game['bot_team']} ball!\n\n"
            game["possession"] = 1
            game["down"] = 1
            game["yards_to_go"] = 10
            game["position_at_drive_start"] = game["position"]
            return msg
        
        # Check for sack on pass plays (negative yards)
        if is_pass_play and yards < 0:
            # Check for intentional grounding (QB throws away under pressure)
            if random.random() < 0.15:  # 15% chance of grounding call
                msg += f"Result: 🚫 SACK! {-yards} yard loss\n"
                msg += f"🚩 INTENTIONAL GROUNDING - 5 yard penalty from line of scrimmage\n\n"
                # Reset position and add penalty
                game["position"] = max(0, game["position"] - 5)
                game["down"] += 1
                return msg
            else:
                msg += f"Result: 🚫 SACK! {-yards} yard loss\n\n"
        else:
            msg += f"Result: +{yards}yd\n\n"
        
        # Update position
        game["position"] += yards
        
        # Check for fumble/turnover (2.5% chance)
        if random.random() < 0.025:
            msg += f"🔴 FUMBLE! {game['bot_team']} ball!\n"
            game["possession"] = 1
            game["down"] = 1
            game["yards_to_go"] = 10
            game["position_at_drive_start"] = game["position"]
            return msg
        
        # Check for touchdown
        if game["position"] >= 100:
            msg += "🏈 TOUCHDOWN! 🏈\n"
            msg += "Choose conversion: 'kick' for 1-point (95% success, 7 pts) or '2pt' for 2-point (50% success, 8 pts)"
            game["waiting_for_conversion"] = True
            return msg
        
        # Check for safety (ball at or behind own goal)
        if game["position"] <= 0:
            msg += f"⚠️ SAFETY! {game['bot_team']} scores 2 points.\n"
            game["score"][1] += 2
            game["possession"] = 1
            game["position"] = 50
            game["down"] = 1
            game["yards_to_go"] = 10
            game["position_at_drive_start"] = 50
            return msg
        
        # Update down and yards to go
        yards_gained_since_drive_start = game["position"] - game["position_at_drive_start"]
        
        if yards_gained_since_drive_start >= 10:
            msg += "📍 FIRST DOWN!\n"
            game["down"] = 1
            game["yards_to_go"] = 10
            game["position_at_drive_start"] = game["position"]
        else:
            game["down"] += 1
            game["yards_to_go"] = 10 - yards_gained_since_drive_start
        
        # Check for turnover on downs
        if game["down"] > 4:
            msg += "🔴 TURNOVER ON DOWNS!\n"
            game["possession"] = 1
            game["down"] = 1
            game["yards_to_go"] = 10
            game["position_at_drive_start"] = game["position"]
        
        return msg
    
    def _execute_punt(self, nodeID: int) -> str:
        """Execute a punt play.
        
        Returns punt result message.
        """
        game = self.game[nodeID]
        msg = f"📍 {game['user_team'].upper()} PUNTS\n"
        
        # Punt distance 25-60 yards (25% chance of bad punt)
        if random.random() < 0.25:
            punt_dist = random.randint(10, 25)
            msg += f"Bad punt! Only {punt_dist} yards.\n"
        else:
            punt_dist = random.randint(25, 60)
            msg += f"Punt: {punt_dist} yards.\n"
        
        # Move ball
        game["position"] += punt_dist
        
        # Check for out of bounds past endzone
        if game["position"] > 100:
            game["position"] = 100
            msg += "Punt went into endzone. Touchback.\n"
        
        # Possession change
        game["possession"] = 1
        game["down"] = 1
        game["yards_to_go"] = 10
        game["position_at_drive_start"] = game["position"]
        
        return msg
    
    def _execute_field_goal(self, nodeID: int) -> str:
        """Execute a field goal attempt.
        
        Returns field goal result message.
        """
        game = self.game[nodeID]
        msg = "🎯 Field Goal Attempt\n"
        
        # Field goal range depends on distance
        distance = 100 - game["position"]
        success_rate = max(0.05, 0.95 - (distance / 100))
        
        if random.random() < success_rate:
            msg += f"✅ GOOD! 3 points!\n"
            game["score"][0] += 3
        else:
            msg += f"❌ Ball went wide.\n"
        
        # Possession change
        game["possession"] = 1
        game["down"] = 1
        game["yards_to_go"] = 10
        game["position_at_drive_start"] = game["position"] if game["position"] < 20 else 20
        game["position"] = game["position_at_drive_start"]
        
        return msg
    
    def _play_bot_full_drive(self, nodeID: int) -> str:
        """Execute bot's full possession drive until they lose the ball.
        
        Loops through bot's plays until possession changes back to user (0),
        or game ends. This plays out the entire bot drive automatically.
        
        Returns accumulated message with all plays in the drive.
        """
        game = self.game[nodeID]
        full_msg = ""
        
        # Loop until bot loses possession
        while game["possession"] == 1:
            full_msg += self._play_bot_possession(nodeID)
            
            # Check if game is over (prevent infinite loops on score checks)
            if self._check_game_over(nodeID):
                break
        
        return full_msg
    
    def _play_bot_possession(self, nodeID: int) -> str:
        """Execute bot's possession turn (single play).
        
        Returns message with bot's play and any results.
        """
        game = self.game[nodeID]
        msg = f"\n🤖 {game['bot_team']}'s Turn 🤖\n\n"
        
        # Bot decides to play or kick on 4th down
        if game["down"] == 4:
            rand = random.random()
            if rand < 0.5:
                return msg + self._execute_bot_punt(nodeID)
            else:
                return msg + self._execute_bot_field_goal(nodeID)
        
        # Bot selects a play
        bot_play_num = random.randint(0, 19)
        user_defensive_play = random.randint(0, 19)
        
        # Check for bot penalties
        is_bot_pass = bot_play_num in [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
        penalty_result = self._check_penalties(nodeID, is_pass_play=is_bot_pass)
        if penalty_result:
            msg += f"{game['bot_team']} Play: {self.PLAY_DATA['actions'][bot_play_num]}\n"
            msg += penalty_result + "\n\n"
            msg += "🔄 Same down, replay\n"
            return msg
        
        # Calculate yards
        yards = self._calculate_yards(nodeID, bot_play_num, user_defensive_play)
        
        play_name = self.PLAY_DATA["actions"][bot_play_num]
        msg += f"{game['bot_team']} Play: {play_name}\n"
        msg += f"Yards Gained: {yards}\n\n"
        
        # Update position (bot moving toward 0 yardline)
        game["position"] -= yards
        
        # Check for fumble
        if random.random() < 0.025:
            msg += f"🔴 FUMBLE! {game['user_team']} recovers!\n"
            game["possession"] = 0
            game["down"] = 1
            game["yards_to_go"] = 10
            game["position_at_drive_start"] = game["position"]
            return msg
        
        # Check for touchdown (bot endzone is position 0)
        if game["position"] <= 0:
            return self._score_bot_touchdown(nodeID, msg)
        
        # Check for safety
        if game["position"] >= 100:
            msg += f"⚠️ SAFETY! {game['user_team']} scores 2 points.\n"
            game["score"][0] += 2
            game["possession"] = 0
            game["position"] = 50
            game["down"] = 1
            game["yards_to_go"] = 10
            game["position_at_drive_start"] = 50
            return msg
        
        # Update down and yards to go
        yards_gained_since_drive_start = game["position_at_drive_start"] - game["position"]
        
        if yards_gained_since_drive_start >= 10:
            msg += f"📍 {game['bot_team'].upper()} FIRST DOWN!\n"
            game["down"] = 1
            game["yards_to_go"] = 10
            game["position_at_drive_start"] = game["position"]
        else:
            game["down"] += 1
            game["yards_to_go"] = 10 - yards_gained_since_drive_start
        
        # Check for turnover on downs
        if game["down"] > 4:
            msg += f"🔴 {game['bot_team'].upper()} TURNOVER ON DOWNS! {game['user_team']}'s ball.\n"
            game["possession"] = 0
            game["down"] = 1
            game["yards_to_go"] = 10
            game["position_at_drive_start"] = game["position"]
        
        return msg
    
    def _execute_bot_punt(self, nodeID: int) -> str:
        """Bot executes a punt.
        
        Returns punt result message.
        """
        game = self.game[nodeID]
        msg = f"📍 {game['bot_team'].upper()} PUNTS\n"
        
        if random.random() < 0.25:
            punt_dist = random.randint(10, 25)
            msg += f"Bad punt! Only {punt_dist} yards.\n"
        else:
            punt_dist = random.randint(25, 60)
            msg += f"Punt: {punt_dist} yards.\n"
        
        game["position"] -= punt_dist
        
        if game["position"] < 0:
            game["position"] = 0
            msg += "Punt rolled into endzone. Touchback.\n"
        
        game["possession"] = 0
        game["down"] = 1
        game["yards_to_go"] = 10
        game["position_at_drive_start"] = game["position"]
        
        msg += f"\n{self._get_field_display(nodeID)}\n"
        msg += "Your play?"
        return msg
    
    def _execute_bot_field_goal(self, nodeID: int) -> str:
        """Bot attempts a field goal.
        
        Returns field goal result message.
        """
        game = self.game[nodeID]
        msg = f"🎯 {game['bot_team'].upper()} FIELD GOAL ATTEMPT\n"
        
        distance = game["position"]
        success_rate = max(0.05, 0.95 - (distance / 100))
        
        if random.random() < success_rate:
            msg += f"✅ GOOD! Bot scores 3!\n"
            game["score"][1] += 3
        else:
            msg += f"❌ Ball went wide.\n"
        
        game["possession"] = 0
        game["down"] = 1
        game["yards_to_go"] = 10
        game["position_at_drive_start"] = game["position"] if game["position"] < 80 else 80
        game["position"] = game["position_at_drive_start"]
        
        msg += f"\n{self._get_field_display(nodeID)}\n"
        msg += "Your play?"
        return msg
    
    def _handle_bot_kickoff(self, nodeID: int) -> str:
        """Bot receives kickoff at start of game.
        
        Returns kickoff and full bot drive result.
        """
        game = self.game[nodeID]
        msg = f"🤖 {game['bot_team']} receives kickoff at midfield (50 yard line).\n\n"
        return msg + self._play_bot_full_drive(nodeID)
    
    def _score_touchdown(self, nodeID: int, msg_prefix: str, conversion_type: str = "auto") -> str:
        """Process user touchdown.
        
        Args:
            nodeID: User's node ID
            msg_prefix: Message prefix from play result
            conversion_type: "auto" for AI choice, "kick" for 1-point, "2pt" for 2-point
        
        Returns touchdown message.
        """
        game = self.game[nodeID]
        msg = msg_prefix
        msg += "🏈 TOUCHDOWN! 🏈\n"
        
        # Let user choose conversion type on their TD
        if conversion_type == "auto":
            # For now, auto to kick (95% good, 5% blocked)
            if random.random() < 0.05:
                msg += "Extra point (1-point kick) BLOCKED. 6 points.\n"
                game["score"][0] += 6
            else:
                msg += "Extra point (1-point kick) GOOD. 7 points!\n"
                game["score"][0] += 7
        elif conversion_type == "kick":
            # 1-point extra point (95% success)
            if random.random() < 0.05:
                msg += "1-Point Kick BLOCKED. 6 points.\n"
                game["score"][0] += 6
            else:
                msg += "1-Point Kick GOOD. 7 points!\n"
                game["score"][0] += 7
        elif conversion_type == "2pt":
            # 2-point conversion (50% success)
            if random.random() < 0.5:
                msg += "2-Point Conversion GOOD. 8 points!\n"
                game["score"][0] += 8
            else:
                msg += "2-Point Conversion FAILED. 6 points.\n"
                game["score"][0] += 6
        
        # Change possession and handle kickoff
        msg += f"\n📍 KICKOFF - {game['bot_team']} receives at the 20 yard line\n"
        
        # Check for kickoff return TD (8% chance)
        if random.random() < 0.08:
            msg += f"🏈 KICKOFF RETURN FOR TOUCHDOWN! 🏈 {game['bot_team'].upper()}!\n"
            msg += "2-Point conversion attempt after return TD...\n"
            if random.random() < 0.5:
                msg += "2-Point Conversion GOOD. 8 points!\n"
                game["score"][1] += 8
            else:
                msg += "2-Point Conversion FAILED. 6 points.\n"
                game["score"][1] += 6
            # Keep possession with bot
            game["possession"] = 1
            game["position"] = 50
            game["down"] = 1
            game["yards_to_go"] = 10
            game["position_at_drive_start"] = 20
        else:
            # Normal kickoff
            game["possession"] = 1
            game["position"] = 20  # Receiving team starts at 20 yard line
            game["position_at_drive_start"] = 20
            game["down"] = 1
            game["yards_to_go"] = 10
        
        return msg
    
    def _score_bot_touchdown(self, nodeID: int, msg_prefix: str) -> str:
        """Process bot touchdown.
        
        Returns touchdown message. Bot randomly chooses conversion type.
        """
        game = self.game[nodeID]
        msg = msg_prefix
        msg += f"🏈 {game['bot_team'].upper()} TOUCHDOWN! 🏈\n"
        
        # Bot decides conversion type: 70% kick, 30% 2-point
        if random.random() < 0.7:
            # 1-point kick (95% success)
            if random.random() < 0.05:
                msg += "Extra point (1-point kick) BLOCKED. 6 points.\n"
                game["score"][1] += 6
            else:
                msg += "Extra point (1-point kick) GOOD. 7 points!\n"
                game["score"][1] += 7
        else:
            # 2-point conversion (50% success)
            if random.random() < 0.5:
                msg += "2-Point Conversion GOOD. 8 points!\n"
                game["score"][1] += 8
            else:
                msg += "2-Point Conversion FAILED. 6 points.\n"
                game["score"][1] += 6
        
        # Kickoff to user team
        msg += f"\n📍 KICKOFF - {game['user_team']} receives at the 20 yard line\n"
        
        # Check for kickoff return TD (8% chance)
        if random.random() < 0.08:
            msg += f"🏈 KICKOFF RETURN FOR TOUCHDOWN! 🏈 {game['user_team'].upper()}!\n"
            msg += "2-Point conversion attempt after return TD...\n"
            if random.random() < 0.5:
                msg += "2-Point Conversion GOOD. 8 points!\n"
                game["score"][0] += 8
            else:
                msg += "2-Point Conversion FAILED. 6 points.\n"
                game["score"][0] += 6
            # Keep possession with user
            game["possession"] = 0
            game["position"] = 50
            game["down"] = 1
            game["yards_to_go"] = 10
            game["position_at_drive_start"] = 50
        else:
            # Normal kickoff
            game["possession"] = 0
            game["position"] = 20  # User receives at 20 yard line
            game["down"] = 1
            game["yards_to_go"] = 10
            game["position_at_drive_start"] = 20
        
        return msg
    
    def _calculate_yards(self, nodeID: int, offensive_play: int, defensive_play: int) -> int:
        """Calculate yards gained based on play matchup.
        
        Yards depend on how different the plays are (classic football game logic).
        Can be negative (sack) or positive depending on matchup.
        """
        game = self.game[nodeID]
        aa = game["aa"]
        ba = game["ba"]
        
        # Get play effectiveness values
        off_val = aa[offensive_play]
        def_val = ba[defensive_play]
        
        # Calculate yards: difference in play values affects outcome
        diff = abs(off_val - def_val)
        base_yards = floor(diff / 19 * ((100 - game["position"] + 25) * random.random() - 15))
        
        # Randomize with small variance
        # Allow negative yards (sacks) now - don't cap at 0
        yards = base_yards + random.randint(-2, 2)
        
        return yards
    
    def _parse_play_command(self, command: str) -> Optional[list]:
        """Parse natural language play command to play indices.
        
        Supports:
        - Category commands: "run", "pass", "bomb", "sweep", etc.
        - Direct play numbers: "6" or "play 6"
        - Play names: "left sweep", "right sweep", etc.
        
        Args:
            command: Natural language (e.g., "run", "play 6", "left sweep")
            
        Returns:
            List of valid play indices, or None if unrecognized
        """
        import re
        
        command = command.strip().lower()
        
        # Try direct play number: "6" or "play 6"
        match = re.search(r'play\s+(\d+)|^(\d+)$', command)
        if match:
            play_num = int(match.group(1) or match.group(2))
            if 0 <= play_num <= 19:
                return [play_num]
            else:
                return None
        
        # Try specific play name
        for play_name, play_idx in self.PLAY_NAMES.items():
            if play_name in command:
                return [play_idx]
        
        # Try category command
        for key, plays in self.PLAY_COMMANDS.items():
            if key in command:
                return plays
        
        return None
    
    def _check_penalties(self, nodeID: int, is_pass_play: bool = False) -> Optional[str]:
        """Check for penalties on offense (pre-play).
        
        Returns penalty description if penalty occurred, None otherwise.
        
        Penalties:
        - False start (2% base)
        - Holding on offense (3% base, +2% if pass play)
        - Pass interference (0% on run plays, 4% on pass plays)
        """
        # False start
        if random.random() < 0.02:
            return "🚩 FALSE START on offense - 5 yard penalty"
        
        # Holding on offense
        if random.random() < 0.03 + (0.02 if is_pass_play else 0):
            return "🚩 HOLDING on offense - 10 yard penalty"
        
        # Pass interference (defense, but we'll check it here)
        if is_pass_play and random.random() < 0.04:
            return "🚩 PASS INTERFERENCE on defense - Automatic first down"
        
        return None
    
    def _get_bot_play(self, nodeID: int, user_play_type: list) -> int:
        """Get bot's defensive play number using biased random strategy.
        
        Strategy:
        - 70% random from all plays
        - 20% counter-play (if user ran, play pass defense)
        - 10% aggressive shutdown
        
        Returns play number (0-19)
        """
        rand = random.random()
        
        if rand < 0.70:
            # Random play
            return random.randint(0, 19)
        elif rand < 0.90:
            # Counter-play: if user played running plays, bot plays pass defense
            if any(play in [0, 1, 2, 3, 4, 5, 6, 7, 8] for play in user_play_type):
                # Play pass defense
                return random.choice([10, 12, 14, 16])
            else:
                # Play run defense
                return random.choice([1, 3, 5, 7])
        else:
            # Aggressive play
            return random.choice([19, 18, 17])  # Aggressive plays
    
    def _get_field_display(self, nodeID: int) -> str:
        """Get status tracker with down, yards to score, and field position.
        
        Returns formatted status string.
        """
        game = self.game[nodeID]
        pos = game["position"]
        yards_to_go = game["yards_to_go"]
        
        # Calculate yards to score (touchdown)
        if game["possession"] == 0:  # User offensive
            yards_to_score = 100 - pos
        else:  # Bot offensive
            yards_to_score = pos
        
        status = f"📊Down {game['down']}/4 | To Score: {yards_to_score}yd | To 1st: {yards_to_go}yd | Pos: {pos}"
        
        return status
    
    def _get_scores(self, nodeID: int) -> str:
        """Get current score display.
        
        Returns formatted score string.
        """
        game = self.game[nodeID]
        msg = "\n📊 SCORE\n"
        msg += f"You ({game['user_team']}): {game['score'][0]}\n"
        msg += f"🤖 Bot ({game['bot_team']}): {game['score'][1]}\n"
        return msg
    
    def _check_game_over(self, nodeID: int) -> bool:
        """Check if game is over (someone reached winning score).
        
        Returns True if game over, False otherwise.
        """
        game = self.game[nodeID]
        return game["score"][0] >= self.winning_score or game["score"][1] >= self.winning_score
    
    def _end_game(self, nodeID: int) -> str:
        """End the game and return final result.
        
        Returns end-game message with stats.
        """
        game = self.game[nodeID]
        msg = "\n🏁 GAME OVER 🏁\n"
        msg += f"Final Score:\n"
        msg += f"  You ({game['user_team']}): {game['score'][0]}\n"
        msg += f"  🤖 Bot ({game['bot_team']}): {game['score'][1]}\n\n"
        
        if game['score'][0] > game['score'][1]:
            msg += f"🎉 YOU WIN! ({game['user_team'].upper()}) Great game!\n"
        elif game['score'][1] > game['score'][0]:
            msg += f"🤖 BOT WINS ({game['bot_team'].upper()}) Better luck next time!\n"
        else:
            msg += "🤝 TIE GAME! Well played!\n"
        
        msg += "\nType 'football new' to play again."
        game["game_over"] = True
        
        return msg
    
    def _get_help_text(self, nodeID: int) -> str:
        """Get help text for game commands.
        
        Returns help message.
        """
        msg = "🏈 FOOTBALL HELP 🏈\n\n"
        msg += "Offensive Plays:\n"
        msg += "  run       - Running plays (gains 0-20 yards)\n"
        msg += "  pass      - Passing plays (8% interception risk, can get sacked)\n"
        msg += "  bomb      - Bomb pass (high risk/high reward, 8% INT)\n"
        msg += "  sweep     - Sweep around the edge\n"
        msg += "  option    - Option play (run or pass)\n"
        msg += "  screen    - Screen pass (short, safe, 8% INT)\n\n"
        msg += "Special Plays (4th Down Only):\n"
        msg += "  punt      - Punt the ball away\n"
        msg += "  fg / field goal - Attempt a field goal\n"
        msg += "  kick      - Go for 1-point after TD\n"
        msg += "  2pt       - Go for 2-point conversion after TD\n\n"
        msg += "Commands:\n"
        msg += "  score   - Show current score\n"
        msg += "  help    - This help text\n"
        msg += "  new     - Start a new game\n"
        msg += "  end     - End the current game\n\n"

        return msg

