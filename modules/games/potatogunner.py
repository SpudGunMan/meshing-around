#!/usr/bin/env python3
# Potato Gunner - Potato-Themed Artillery Game for MeshBot
# Based on: https://github.com/coding-horror/basic-computer-games/blob/main/42_Gunner/python/gunner.py
# 2026 Kelly Keeton K7MHI

from math import sin, cos, radians
from random import random, randint, choice
import time
import pickle
from modules.log import logger


def saveHSPotato(nodeID, highScore):
    """Save the game high_score to pickle."""
    highScore = {'nodeID': nodeID, 'highScore': highScore}
    try:
        with open('data/potatogunner_hs.pkl', 'wb') as file:
            pickle.dump(highScore, file)
    except FileNotFoundError:
        logger.debug("System: PotatoGunner: Creating new data/potatogunner_hs.pkl file")
        with open('data/potatogunner_hs.pkl', 'wb') as file:
            pickle.dump(highScore, file)


def loadHSPotato():
    """Load the game high_score from pickle."""
    try:
        with open('data/potatogunner_hs.pkl', 'rb') as file:
            highScore = pickle.load(file)
            return highScore
    except FileNotFoundError:
        logger.debug("System: PotatoGunner: Creating new data/potatogunner_hs.pkl file")
        highScore = {'nodeID': 0, 'highScore': 0}
        with open('data/potatogunner_hs.pkl', 'wb') as file:
            pickle.dump(highScore, file)
        return highScore


class PotatoGunner:
    """
    Silly potato-themed artillery game. Players fire spuds at moving targets
    with wind, chaos events, and powerups. Multi-round tournament format.
    """
    
    def __init__(self):
        self.games = {}  # {nodeID: game_state_dict}
    
    @staticmethod
    def format_yards(value):
        """Format yardage with comma separators for readability."""
        return f"{int(value):,d}"
    
    def new_game(self, nodeID, difficulty='normal'):
        """Start a new tournament session."""
        # Load existing highscore
        hs_data = loadHSPotato()
        high_score = hs_data.get('highScore', 0)
        
        self.games[nodeID] = {
            'round': 1,
            'score': 0,
            'rounds_won': 0,
            'total_shots': 0,
            'total_hits': 0,
            'accuracy_streak': 0,
            'powerups': {
                'super_spud': 0,
                'homing_spud': 0,
                'lucky_potato': 0,
                'potato_shield': 0
            },
            'powerups_used': {
                'super_spud': 0,
                'homing_spud': 0,
                'lucky_potato': 0,
                'potato_shield': 0
            },
            'difficulty': difficulty,
            'chaos_event': None,
            'last_accuracy': 0.0,
            'start_time': time.time(),
            'high_score': high_score
        }
        
        # intro
        intro = f"🏆 High Score: {high_score} pts\n"
        intro += "💣 Fire spuds at targets!\n"
        intro += " Angle: 0-90° | Power: 0-100 PSI\n"
        intro += " Commands: hint, stats, exit\n"
        
        return intro + self._display_round_intro(nodeID)
    
    def play(self, nodeID, input_msg):
        """Process a single shot/action in the game."""
        try:
            if nodeID not in self.games:
                return self.new_game(nodeID)
            
            g = self.games[nodeID]
            input_str = input_msg.strip().lower()
            
            # Handle quit commands
            if input_str in ('end', 'e', 'quit', 'q', 'exit'):
                return self.end(nodeID)
            
            # Handle stats command
            if input_str in ('stats', 's', 'score'):
                return self._display_stats(nodeID)
            
            # Handle hint command
            if input_str in ('hint', 'h', 'help', 'examples'):
                return self._show_launch_hints(nodeID)
            elevation = None
            power = 50  # Default power if not specified
            
            hints = {
                'low': 15, 'min': 10, 'ground': 5,
                'mid': 45, 'medium': 45, 'normal': 45,
                'high': 70, 'max': 80, 'steep': 85
            }
            
            try:
                # Check if format is "angle,power" (numeric or hint word)
                if ',' in input_str:
                    parts = input_str.split(',')
                    if len(parts) != 2:
                        return "⚠️ Format: elevation,power (e.g., 45,60 or high,30)"
                    
                    # Try numeric first, then hint words
                    elevation_str = parts[0].strip()
                    try:
                        elevation = float(elevation_str)
                    except ValueError:
                        # Check if it's a hint word
                        if elevation_str in hints:
                            elevation = hints[elevation_str]
                        else:
                            return f"⚠️ '{elevation_str}' not recognized. Use angle (0-90) or hint: {', '.join(hints.keys())}"
                    
                    try:
                        power = float(parts[1].strip())
                    except ValueError:
                        return "⚠️ Power must be 0-100 PSI (e.g., high,30)"
                else:
                    # Just elevation (no power specified)
                    try:
                        elevation = float(input_str)
                    except ValueError:
                        # Check if it's a hint word
                        if input_str in hints:
                            elevation = hints[input_str]
                            power = 50  # Default power
                        else:
                            return "⚠️ Enter: angle (0-90°) or angle,power (e.g., 45,60)\nHints: low, mid, high, max\nCommands: hint, stats, e"
                    else:
                        power = 50  # Default power if numeric angle only
                
                # Validate elevation
                if elevation < 0 or elevation > 90:
                    return "⚠️ Elevation must be 0-90 degrees. Try again!"
                
                # Validate power
                if power < 0 or power > 100:
                    return "⚠️ Power must be 0-100 PSI. Try again!"
                    
            except ValueError:
                return "⚠️ Error parsing input. Use: angle,power (e.g., 45,60 or high,30)"
            
            # Process the shot
            return self._fire_spud(nodeID, elevation, power)
        
        except Exception as e:
            return f"⚠️ Error: {e}"
    
    def _fire_spud(self, nodeID, elevation, power=50):
        """Fire a spud at the target and calculate hit."""
        g = self.games[nodeID]
        
        # Get/create round state if needed
        if 'current_round_state' not in g:
            g['current_round_state'] = self._generate_round_state(nodeID)
        
        rs = g['current_round_state']
        g['total_shots'] += 1
        
        # Enhanced physics: calculate spud distance with better ballistics
        # Using realistic projectile motion: range = (v₀² * sin(2θ)) / g
        # Power scales from 0-100 PSI, affecting velocity
        elevation_rad = radians(elevation)
        
        # Base distance calculation with power scaling
        gravity = 9.81
        # Scale velocity based on power (0-100 PSI) where 50 PSI = base 100 m/s
        # Formula: velocity = (power / 50) * 100, so 50 PSI = 100 m/s, 100 PSI = 200 m/s, 10 PSI = 20 m/s
        base_velocity = (power / 50.0) * 100  # m/s (scales with PSI)
        base_distance = (base_velocity ** 2 * sin(2 * elevation_rad)) / gravity
        base_distance = base_distance * 100  # Convert to yards (roughly)
        
        # Apply chaos effects to the trajectory
        wind_factor = rs.get('wind', 0)
        
        # Check if Lucky Potato should be used (automatic on chaos survival)
        lucky_active = False
        if rs['chaos_event'] and g['powerups']['lucky_potato'] > 0:
            # Auto-use lucky potato to skip chaos effect
            g['powerups']['lucky_potato'] -= 1
            g['powerups_used']['lucky_potato'] += 1
            lucky_active = True
            wind_factor = 0  # Nullify chaos effect
        else:
            # Handle specific chaos events with their effects
            if rs['chaos_event'] == 'earthquake':
                wind_factor += randint(-100, 100)  # Adds randomness
            elif rs['chaos_event'] == 'inverse_wind':
                wind_factor = -wind_factor
            elif rs['chaos_event'] == 'ricochet':
                # Spud might bounce unexpectedly
                ricochet_chance = random()
                if ricochet_chance > 0.7:  # 30% chance of crazy ricochet
                    base_distance += randint(-500, 500)
            elif rs['chaos_event'] == 'gravity_flip':
                # Inverted gravity means opposite trajectory behavior
                base_distance = base_distance * -0.5
        
        actual_distance = base_distance + wind_factor
        actual_distance = max(0, actual_distance)  # Can't be negative
        
        # Apply powerup: homing spud (auto-correction toward target)
        powerup_correction = 0
        if g['powerups']['homing_spud'] > 0:
            powerup_correction = (rs['target_distance'] - actual_distance) * 0.15  # 15% auto-correct
            actual_distance += powerup_correction
        
        # Calculate proximity and accuracy
        proximity = abs(actual_distance - rs['target_distance'])
        
        # Accuracy radius scales with powerups and difficulty
        base_accuracy_radius = 670  # Yards
        if g['powerups']['super_spud'] > 0:
            base_accuracy_radius += 60  # +60 accuracy improvement
        if rs['chaos_event'] and not lucky_active:
            base_accuracy_radius -= 30  # Chaos makes it harder (unless Lucky saved you)
        
        accuracy_radius = max(50, base_accuracy_radius)  # Min 50 yard radius
        
        # Build response message
        msg = f"🥔FIRED AT🚀 {elevation}° with {int(power)} PSI\n"
        msg += f"Distance calc: {self.format_yards(base_distance)}yd"
        if powerup_correction != 0:
            msg += f" (homing: {int(powerup_correction):+d}yd)"
        msg += "\n"
        msg += f"Velocity: {int(base_velocity)}m/s | Wind effect: {int(wind_factor):+d}yd\n"
        msg += f"Actual distance: {self.format_yards(actual_distance)}yd | Target: {self.format_yards(rs['target_distance'])}yd\n"
        msg += f"Missed by: {self.format_yards(proximity)}yd\n"
        
        # Add chaos event narrative if present
        if rs['chaos_event']:
            chaos_info = self._get_chaos_description(rs['chaos_event'])
            msg += f"\n{chaos_info['title']} {chaos_info['flavor']}\n"
            if lucky_active:
                msg += "🍀 Lucky Potato activated! Chaos effect negated!\n"
        
        msg += "\n"
        
        # Determine hit or miss
        if proximity <= accuracy_radius:
            # HIT!
            msg += "🎯 DIRECT HIT! 🥔💥\n"
            g['total_hits'] += 1
            g['rounds_won'] += 1
            g['accuracy_streak'] += 1
            
            # Calculate points with multiple modifiers
            accuracy_bonus = max(0, int((accuracy_radius - proximity) / accuracy_radius * 100))
            combo_bonus = min(75, g['accuracy_streak'] * 15)  # +15 per streak, max 75
            round_multiplier = 1.0 + (g['round'] - 1) * 0.05  # 5% per round
            
            powerup_bonus = 0
            if g['powerups']['super_spud'] > 0:
                powerup_bonus += 50  # Increased from 25
                g['powerups']['super_spud'] -= 1
                g['powerups_used']['super_spud'] += 1
                msg += "⚡ Super Spud activated!\n"
            
            if g['powerups']['homing_spud'] > 0:
                powerup_bonus += 30
                g['powerups']['homing_spud'] -= 1
                g['powerups_used']['homing_spud'] += 1
                msg += "🎯 Homing Spud guided you to victory!\n"
            
            chaos_bonus = 0
            if rs['chaos_event']:
                chaos_bonus = 60  # Higher bonus for chaos survival
                chaos_name = rs['chaos_event'].replace('_', ' ').title()
                msg += f"🎊 Survived chaos ({chaos_name}): +{chaos_bonus} bonus!\n"
            
            # Calculate total points
            base_points = 100
            total_points = int((base_points + accuracy_bonus + combo_bonus + powerup_bonus + chaos_bonus) * round_multiplier)
            
            g['score'] += total_points
            g['last_accuracy'] = min(100, (accuracy_radius - proximity)) / accuracy_radius
            
            msg += f"\n✨ +{total_points} points!\n"
            msg += f"  Base: {base_points} | Accuracy: +{accuracy_bonus} | "
            msg += f"Streak: +{combo_bonus} | Round×{round_multiplier:.2f}\n"
            
            # Award powerups on successful hit
            powerup_msg = self._award_powerups(nodeID)
            if powerup_msg:
                msg += f"\n{powerup_msg}"
            
            msg += f"\n📊 Session: {g['score']} pts | Accuracy: {g['total_hits']}/{g['total_shots']} "
            msg += f"({100*g['total_hits']//max(1, g['total_shots'])}%)"
        else:
            # MISS
            msg += "❌ MISS! ⚠️\n"
            if actual_distance < rs['target_distance']:
                msg += f"Short by {self.format_yards(proximity)} yards\n"
            else:
                msg += f"Over by {self.format_yards(proximity)} yards\n"
            
            g['accuracy_streak'] = 0
            
            msg += f"\n📊 Session: {g['score']} pts | Accuracy: {g['total_hits']}/{g['total_shots']} "
            msg += f"({100*g['total_hits']//max(1, g['total_shots'])}%)"
        
        # Clear round state and auto-advance to next round
        del g['current_round_state']
        msg += "\n" + self._start_round(nodeID)
        
        return msg
    
    def _award_powerups(self, nodeID):
        """Determine and award powerups on successful hit based on performance."""
        g = self.games[nodeID]
        msg = ""
        awarded = []
        
        # Accuracy-based powerups
        if g['last_accuracy'] >= 0.75:  # 75% accuracy or better
            if g['total_hits'] > 0:  # Make sure we have actual hits
                g['powerups']['homing_spud'] += 1
                awarded.append("🎯 Homing Spud (auto-aim next round)")
        
        if g['last_accuracy'] >= 0.50:  # 50% accuracy or better
            if g['total_hits'] > 0:
                g['powerups']['super_spud'] += 1
                awarded.append("⚡ Super Spud (+40% accuracy)")
        
        # Streak-based powerup
        if g['accuracy_streak'] >= 3:
            g['powerups']['potato_shield'] = min(2, g['powerups'].get('potato_shield', 0) + 1)
            awarded.append("🛡️ Potato Shield (free miss next round)")
        
        # Chaos survival powerup
        if g.get('current_round_state', {}).get('chaos_event'):
            # 20% chance to get lucky potato on chaos survival
            if random() < 0.2:
                g['powerups']['lucky_potato'] = min(1, g['powerups'].get('lucky_potato', 0) + 1)
                awarded.append("🍀 Lucky Potato (skip chaos)")
        
        if awarded:
            msg = "\n🎁 Powerups Earned:\n"
            for pup in awarded:
                msg += f"  • {pup}\n"
        
        return msg
    
    def _get_chaos_description(self, chaos_event):
        """Get detailed silly description for chaos events."""
        descriptions = {
            'wind_gust': {
                'title': '🌪️ WIND GUST!',
                'flavor': 'A sudden gust catches your spud mid-flight!',
                'effect': 'Trajectory unpredictable!',
            },
            'earthquake': {
                'title': '🌍 EARTHQUAKE!',
                'flavor': 'The ground shakes violently beneath the artillery range!',
                'effect': 'Everything shifts unexpectedly!',
            },
            'rain': {
                'title': '🌧️ HEAVY RAIN!',
                'flavor': 'Torrential downpour obscures the target!',
                'effect': 'Visibility severely reduced!',
            },
            'meteor': {
                'title': '☄️ METEOR SHOWER!',
                'flavor': 'Meteorites crash nearby, creating shockwaves!',
                'effect': 'Field distorted by impacts!',
            },
            'alien': {
                'title': '👽 ALIEN ABDUCTION!',
                'flavor': 'A UFO hovers overhead, messing with gravity!',
                'effect': 'Physics go haywire!',
            },
            'squirrel': {
                'title': '🐿️ SQUIRREL ATTACK!',
                'flavor': 'A mischievous squirrel steals a spud from the launcher!',
                'effect': 'Target distracted but launcher disrupted!',
            },
            'birds': {
                'title': '🦅 BIRD STRIKE!',
                'flavor': 'A flock of birds interferes with your trajectory!',
                'effect': 'Unpredictable interference patterns!',
            },
            'farmer': {
                'title': '👨‍🌾 FARMER IN FIELD!',
                'flavor': 'The farmer wanders into the firing zone!',
                'effect': 'Must avoid hitting him! (Or get penalty)',
            },
            'gravity_flip': {
                'title': '⬆️ GRAVITY FLIPPED!',
                'flavor': 'A mysterious force inverts gravity in the field!',
                'effect': 'Spuds fly in weird trajectories!',
            },
            'inverse_wind': {
                'title': '💨 WIND REVERSAL!',
                'flavor': 'The wind suddenly switches direction!',
                'effect': 'Expect opposite effects!',
            },
            'ricochet': {
                'title': '🔀 RICOCHET MODE!',
                'flavor': 'Mysterious bouncy energy permeates the range!',
                'effect': 'Spuds might bounce unpredictably!',
            },
            'slowmo': {
                'title': '🐌 SLOW-MOTION!',
                'flavor': 'Time slows down mysteriously...',
                'effect': 'Everything moves in slow-mo!',
            },
        }
        
        return descriptions.get(chaos_event, {
            'title': '⚡ CHAOS!',
            'flavor': 'Something weird is happening!',
            'effect': 'Unknown chaos detected!',
        })
    
    def _generate_round_state(self, nodeID):
        """Generate round difficulty, chaos event, target, etc. with scaling difficulty."""
        g = self.games[nodeID]
        round_num = g['round']
        score = g['score']
        
        # Dynamic difficulty based on round AND score
        # Early rounds are easier, later rounds harder
        if round_num <= 2:
            base_distance_range = (28000, 38000)
            wind_max = 15
            chaos_chance = 0.20
            chaos_intensity = 'gentle'
        elif round_num <= 4:
            base_distance_range = (22000, 38000)
            wind_max = 30
            chaos_chance = 0.35
            chaos_intensity = 'moderate'
        elif round_num <= 6:
            base_distance_range = (18000, 40000)
            wind_max = 40
            chaos_chance = 0.45
            chaos_intensity = 'wild'
        else:
            base_distance_range = (15000, 45000)
            wind_max = 50 + (round_num - 6) * 5  # Escalate further
            chaos_chance = 0.55 + (round_num - 6) * 0.05
            chaos_intensity = 'insane'
        
        # If player is doing well, bump up difficulty slightly
        if score > 500:
            wind_max += 10
            chaos_chance += 0.05
        if score > 1500:
            wind_max += 15
            chaos_chance += 0.10
        
        base_distance = randint(base_distance_range[0], base_distance_range[1])
        
        # More realistic wind: comes in gusts (can be positive or negative)
        wind_bias = (random() - 0.5) * 2  # Bias wind -1 to +1
        wind_magnitude = random() * wind_max
        wind_factor = wind_bias * wind_magnitude
        
        # Chaos event selection - weighted based on intensity
        chaos_event = None
        if random() < chaos_chance:
            if chaos_intensity == 'gentle':
                # Mostly environmental, not too harsh
                chaos_event = choice(['wind_gust', 'rain', 'birds'])
            elif chaos_intensity == 'moderate':
                # Mix of environmental and character
                chaos_event = choice([
                    'wind_gust', 'rain', 'birds', 'squirrel', 'earthquake', 'farmer'
                ])
            elif chaos_intensity == 'wild':
                # Include rule mutations
                chaos_event = choice([
                    'wind_gust', 'earthquake', 'rain', 'alien',
                    'squirrel', 'birds', 'farmer',
                    'gravity_flip', 'inverse_wind', 'ricochet'
                ])
            else:  # insane
                # All chaos types available
                chaos_event = choice([
                    'wind_gust', 'earthquake', 'rain', 'meteor', 'alien',
                    'squirrel', 'birds', 'farmer',
                    'gravity_flip', 'inverse_wind', 'ricochet', 'slowmo'
                ])
            
            # Apply chaos event effects
            if chaos_event == 'wind_gust':
                wind_factor *= 2.5  # Sudden wind increase
            elif chaos_event == 'earthquake':
                base_distance += randint(-1000, 1000)
                wind_factor += randint(-50, 50)
            elif chaos_event == 'rain':
                # Rain adds unpredictability
                wind_factor += (random() - 0.5) * 200
            elif chaos_event == 'meteor':
                # Meteor strikes can create shockwaves
                base_distance += randint(-2000, 2000)
                wind_factor *= 1.5
            elif chaos_event == 'inverse_wind':
                wind_factor = -wind_factor
            elif chaos_event == 'gravity_flip':
                # Reduced effectiveness for gravity flip
                pass  # Applied in _fire_spud
            elif chaos_event == 'ricochet':
                # Ricochet is handled in _fire_spud
                pass
        
        # Ensure distance remains positive
        base_distance = max(5000, base_distance)
        
        return {
            'target_distance': base_distance,
            'wind': wind_factor,
            'chaos_event': chaos_event,
            'chaos_intensity': chaos_intensity,
            'created_at': time.time()
        }
    
    def _start_round(self, nodeID):
        """Start a new round."""
        g = self.games[nodeID]
        g['round'] += 1
        if 'current_round_state' in g:
            del g['current_round_state']
        return self._display_round_intro(nodeID)
    
    def _display_round_intro(self, nodeID):
        """Display introduction to a round with detailed info."""
        g = self.games[nodeID]
        rs = self._generate_round_state(nodeID)
        g['current_round_state'] = rs
        
        msg = f"\n🥔 ROUND {g['round']} 🥔\n"
        msg += f"Score: {g['score']} | Wins: {g['rounds_won']}/{g['round']}\n"
        
        # Calculate and display stats
        if g['total_shots'] > 0:
            accuracy_pct = 100 * g['total_hits'] // g['total_shots']
            msg += f"Hit Rate: {accuracy_pct}%"
            if g['accuracy_streak'] > 0:
                msg += f" | 🔥 Streak: {g['accuracy_streak']}"
            msg += "\n\n"
        
        # Target info
        msg += f"🎯 Target: ~{self.format_yards(rs['target_distance'])}yd\n"
        if rs['wind'] != 0:
            msg += f"💨 Wind: {int(rs['wind']):+d}yd\n"
        
        # Chaos event announcement
        if rs['chaos_event']:
            chaos_info = self._get_chaos_description(rs['chaos_event'])
            msg += f"\n⚠️ {chaos_info['title']} ⚠️\n"
            msg += f"   {chaos_info['flavor']}\n"
            msg += f"   → {chaos_info['effect']}\n"
        
        pups = []
        if g['powerups']['super_spud'] > 0:
            pups.append(f" ⚡ Super Spud ×{g['powerups']['super_spud']}")
        if g['powerups']['homing_spud'] > 0:
            pups.append(f" 🎯 Homing ×{g['powerups']['homing_spud']}")
        if g['powerups']['lucky_potato'] > 0:
            pups.append(f" 🍀 Lucky ×{g['powerups']['lucky_potato']}")
        if g['powerups']['potato_shield'] > 0:
            pups.append(f" 🛡️ Shield ×{g['powerups']['potato_shield']}")
        
        if pups:
            msg += f"\n💪 Powerups:\n"
            msg += "\n".join(pups) + "\n"
        
        msg += "\n🔫 Angle,Power?"
        return msg
    
    def _display_stats(self, nodeID):
        """Display current session statistics."""
        if nodeID not in self.games:
            return "No active game session."
        
        g = self.games[nodeID]
        accuracy_pct = 100 * g['total_hits'] // max(1, g['total_shots'])
        
        msg = "📊 STATS 📊\n"
        msg += f"Round: {g['round']} | Score: {g['score']} | Wins: {g['rounds_won']}/{g['round']}\n"
        msg += f"Shots: {g['total_shots']} | Hits: {g['total_hits']} ({accuracy_pct}%) | Streak: {g['accuracy_streak']}\n"
        
        
        if (g['powerups']['super_spud'] + g['powerups']['homing_spud'] + 
            g['powerups']['lucky_potato'] + g['powerups']['potato_shield']) > 0:
            msg += "💪 Active Powerups:\n"
            if g['powerups']['super_spud'] > 0:
                msg += f"  ⚡ Super Spud ×{g['powerups']['super_spud']}\n"
            if g['powerups']['homing_spud'] > 0:
                msg += f"  🎯 Homing ×{g['powerups']['homing_spud']}\n"
            if g['powerups']['lucky_potato'] > 0:
                msg += f"  🍀 Lucky ×{g['powerups']['lucky_potato']}\n"
            if g['powerups']['potato_shield'] > 0:
                msg += f"  🛡️ Shield ×{g['powerups']['potato_shield']}\n"
        
        msg += "\nFire away! Angle,Power (e.g., 45,60)"
        return msg
    
    def _show_launch_hints(self, nodeID):
        """Show example launches with different angle/power combinations."""
        if nodeID not in self.games:
            return "No active game session."
        
        g = self.games[nodeID]
        rs = g.get('current_round_state')
        if not rs:
            rs = self._generate_round_state(nodeID)
        
        target = rs['target_distance']
        
        msg = "🎯 **LAUNCH EXAMPLES** 🎯\n"
        if rs['wind'] != 0:
            msg += f"Target: {self.format_yards(target)}yd | Wind: {int(rs['wind']):+d}yd\n\n"
        else:
            msg += f"Target: {self.format_yards(target)}yd\n\n"
        
        # Calculate 3 example launches with different strategies
        examples = [
            ("Low & Slow", 15, 30),
            ("Mid Balanced", 45, 50),
            ("High & Fast", 70, 80),
        ]
        
        for name, angle, power in examples:
            # Quick physics calculation
            elevation_rad = radians(angle)
            gravity = 9.81
            base_velocity = (power / 50.0) * 100
            base_distance = (base_velocity ** 2 * sin(2 * elevation_rad)) / gravity
            base_distance = base_distance * 100
            wind_factor = rs.get('wind', 0)
            actual_distance = base_distance + wind_factor
            actual_distance = max(0, actual_distance)
            proximity = abs(actual_distance - target)
            
            # Show result
            accuracy_emoji = "🎯" if proximity < 500 else "⚡" if proximity < 1000 else "📍"
            msg += f"{accuracy_emoji} {name}: {angle}°,{power}PSI → {self.format_yards(actual_distance)}yd"
            if proximity < 500:
                msg += " (Close!)"
            msg += "\n"
        
        msg += "\nTry: 45,60  or  high,40  or just  low"
        return msg
    
    def end(self, nodeID):
        """End the game and display final score."""
        if nodeID not in self.games:
            return "No active game."
        
        g = self.games[nodeID]
        
        # Calculate performance rating
        accuracy_pct = (100 * g['total_hits']) // max(1, g['total_shots'])
        if accuracy_pct >= 75:
            rating = "🏆 SHARPSHOOTER 🏆"
        elif accuracy_pct >= 60:
            rating = "⭐ EXPERT ⭐"
        elif accuracy_pct >= 45:
            rating = "👍 DECENT 👍"
        elif accuracy_pct >= 30:
            rating = "🥔 SPUD-SLINGER 🥔"
        else:
            rating = "🎪 CHAOS CREATOR 🎪"
        
        # Check if new highscore
        is_high_score = g['score'] > g['high_score']
        if is_high_score:
            saveHSPotato(nodeID, g['score'])
        
        msg = "\n🏁 TOURNAMENT COMPLETE! 🏁\n"
        msg += f"Rating: {rating}\n\n"
        msg += "📊 FINAL STATISTICS:\n"
        msg += f"  Final Score: {g['score']} pts"
        if is_high_score:
            msg += " 🎉 NEW HIGH SCORE! 🎉"
        elif g['high_score'] > 0:
            msg += f" (High Score: {g['high_score']})"
        msg += "\n"
        msg += f"  Rounds: {g['round']} completed\n"
        msg += f"  Wins: {g['rounds_won']}/{g['round']} rounds ({100*g['rounds_won']//max(1, g['round'])}%)\n"
        msg += f"  Accuracy: {g['total_hits']}/{g['total_shots']} ({accuracy_pct}%)\n"
        msg += f"  Longest Streak: {g['accuracy_streak']} hits\n\n"
        
        # Powerup usage stats
        used_any = any(g['powerups_used'].values())
        if used_any:
            msg += "💪 POWERUPS USED:\n"
            if g['powerups_used']['super_spud'] > 0:
                msg += f"  ⚡ Super Spuds: {g['powerups_used']['super_spud']}x\n"
            if g['powerups_used']['homing_spud'] > 0:
                msg += f"  🎯 Homing Spuds: {g['powerups_used']['homing_spud']}x\n"
            if g['powerups_used']['lucky_potato'] > 0:
                msg += f"  🍀 Lucky Potatoes: {g['powerups_used']['lucky_potato']}x\n"
            if g['powerups_used']['potato_shield'] > 0:
                msg += f"  🛡️ Shields: {g['powerups_used']['potato_shield']}x\n"
            msg += "\n"
        
        # Fun facts
        msg += "📈 SESSION HIGHLIGHTS:\n"
        if g['score'] > 2000:
            msg += "  🌟 LEGENDARY PERFORMANCE!\n"
        elif g['score'] > 1500:
            msg += "  🎊 IMPRESSIVE WORK!\n"
        elif g['score'] > 1000:
            msg += "  👏 SOLID EFFORT!\n"
        else:
            msg += "  🌱 PRACTICE MAKES PERFECT!\n"
        
        if accuracy_pct >= 75:
            msg += "  💯 EXCEPTIONAL ACCURACY!\n"
        if g['accuracy_streak'] >= 5:
            msg += f"  🔥 HOT HAND: {g['accuracy_streak']} HIT STREAK!\n"
        if g['round'] >= 10:
            msg += "  🎯 WENT THE DISTANCE!\n"
        
        msg += "\n🥔 Thanks for playing! Type 'potato' to play again."
        
        # Clean up
        if nodeID in self.games:
            del self.games[nodeID]
        
        return msg


# Singleton instance for bot integration
potatogunner = PotatoGunner()

