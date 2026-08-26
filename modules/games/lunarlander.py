"""
Lunar landing simulation
https://github.com/coding-horror/basic-computer-games/blob/main/59_Lunar_LEM_Rocket/python/lunar.py
Refactored for Meshtastic Mesh Bot 2026 K7MHI
"""

import math
import random
from dataclasses import dataclass, asdict
from typing import Any, NamedTuple, Tuple, Optional, Dict

PAGE_WIDTH = 64

# Unit conversion helpers
def get_distance_display(altitude_miles: float, use_metric: bool = False) -> Tuple[float, str]:
    """
    Convert altitude to display units.
    Shows miles (or km) until under 1 mile, then switches to feet (or meters).
    
    Args:
        altitude_miles: Altitude in miles
        use_metric: If True, convert to km/m; if False, use miles/feet
    
    Returns:
        Tuple[float, str]: (value, unit_label)
    """
    if use_metric:
        # Convert miles to kilometers
        altitude_km = altitude_miles * 1.60934
        if altitude_km >= 1:
            return int(altitude_km), "km"
        else:
            m = int(altitude_km * 1000)
            return m, "m"
    else:
        # Show miles until under 1 mile, then switch to feet
        if altitude_miles >= 1:
            return int(altitude_miles), "mi"
        else:
            feet = int(altitude_miles * 5280)
            return feet, "ft"

def get_speed_display(velocity_mph: int, use_metric: bool = False) -> Tuple[int, str]:
    """
    Convert velocity to display units.
    
    Args:
        velocity_mph: Velocity in mph
        use_metric: If True, convert to m/s; if False, keep as mph
    
    Returns:
        Tuple[int, str]: (speed_value, unit_label)
    """
    if use_metric:
        # Convert mph to m/s (1 mph = 0.44704 m/s)
        velocity_ms = int(velocity_mph * 0.44704)
        return velocity_ms, "m/s"
    else:
        return velocity_mph, "mph"

COLUMN_WIDTH = 2
SECONDS_WIDTH = 4
MPH_WIDTH = 6
ALT_MI_WIDTH = 6
ALT_FT_WIDTH = 4
MPH_WIDTH = 6
FUEL_WIDTH = 8
BURN_WIDTH = 10

SECONDS_LEFT = 0
SECONDS_RIGHT = SECONDS_LEFT + SECONDS_WIDTH
ALT_LEFT = SECONDS_RIGHT + COLUMN_WIDTH
ALT_MI_RIGHT = ALT_LEFT + ALT_MI_WIDTH
ALT_FT_RIGHT = ALT_MI_RIGHT + COLUMN_WIDTH + ALT_FT_WIDTH
MPH_LEFT = ALT_FT_RIGHT + COLUMN_WIDTH
MPH_RIGHT = MPH_LEFT + MPH_WIDTH
FUEL_LEFT = MPH_RIGHT + COLUMN_WIDTH
FUEL_RIGHT = FUEL_LEFT + FUEL_WIDTH
BURN_LEFT = FUEL_RIGHT + COLUMN_WIDTH
BURN_RIGHT = BURN_LEFT + BURN_WIDTH


class PhysicalState(NamedTuple):
    velocity: float
    altitude: float


def add_rjust(line: str, s: Any, pos: int) -> str:
    """Add a new field to a line right justified to end at pos"""
    s_str = str(s)
    slen = len(s_str)
    if len(line) + slen > pos:
        new_len = pos - slen
        line = line[:new_len]
    if len(line) + slen < pos:
        spaces = " " * (pos - slen - len(line))
        line = line + spaces
    return line + s_str


def add_ljust(line: str, s: str, pos: int) -> str:
    """Add a new field to a line left justified starting at pos"""
    s = s
    if len(line) > pos:
        line = line[:pos]
    if len(line) < pos:
        spaces = " " * (pos - len(line))
        line = line + spaces
    return line + s


def format_line_for_report(
    t: Any,
    miles: Any,
    feet: Any,
    velocity: Any,
    fuel: Any,
    burn_rate: str,
    is_header: bool,
) -> str:
    line = add_rjust("", t, SECONDS_RIGHT)
    line = add_rjust(line, miles, ALT_MI_RIGHT)
    line = add_rjust(line, feet, ALT_FT_RIGHT)
    line = add_rjust(line, velocity, MPH_RIGHT)
    line = add_rjust(line, fuel, FUEL_RIGHT)
    if is_header:
        line = add_rjust(line, burn_rate, BURN_RIGHT)
    else:
        line = add_ljust(line, burn_rate, BURN_LEFT)
    return line


class SimulationClock:
    def __init__(self, elapsed_time: float, time_until_next_prompt: float) -> None:
        self.elapsed_time = elapsed_time
        self.time_until_next_prompt = time_until_next_prompt

    def time_for_prompt(self) -> bool:
        return self.time_until_next_prompt < 1e-3

    def advance(self, delta_t: float) -> None:
        self.elapsed_time += delta_t
        self.time_until_next_prompt -= delta_t

    def to_dict(self) -> Dict[str, float]:
        """Serialize clock state for storage"""
        return {
            "elapsed_time": self.elapsed_time,
            "time_until_next_prompt": self.time_until_next_prompt,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> "SimulationClock":
        """Deserialize clock state from storage"""
        return cls(data["elapsed_time"], data["time_until_next_prompt"])


@dataclass
class Capsule:
    altitude: float = 120  # in miles above the surface
    velocity: float = 1  # downward
    m: float = 33000  # mass_with_fuel
    n: float = 16500  # mass_without_fuel
    g: float = 1e-3
    z: float = 1.8
    fuel_per_second: float = 0
    engine_temp: float = 0  # 0-100% (0=cold, 100=failure)

    def remaining_fuel(self) -> float:
        return self.m - self.n

    def is_out_of_fuel(self) -> bool:
        return self.remaining_fuel() < 0.1

    def update_state(
        self, sim_clock: SimulationClock, delta_t: float, new_state: PhysicalState
    ) -> None:
        sim_clock.advance(delta_t)
        self.m = self.m - delta_t * self.fuel_per_second
        # Clamp fuel to not go negative
        if self.m < self.n:
            self.m = self.n
            # Fuel is now empty, stop burning
            self.fuel_per_second = 0
        self.altitude = new_state.altitude
        self.velocity = new_state.velocity

    def fuel_time_remaining(self) -> float:
        # extrapolates out how many seconds we have at the current fuel burn rate
        assert self.fuel_per_second > 0
        return self.remaining_fuel() / self.fuel_per_second

    def predict_motion(self, delta_t: float) -> PhysicalState:
        # Perform an Euler's Method numerical integration of the equations of motion.

        q = delta_t * self.fuel_per_second / self.m

        # new velocity
        new_velocity = (
            self.velocity
            + self.g * delta_t
            + self.z * (-q - q**2 / 2 - q**3 / 3 - q**4 / 4 - q**5 / 5)
        )

        # new altitude
        new_altitude = (
            self.altitude
            - self.g * delta_t**2 / 2
            - self.velocity * delta_t
            + self.z
            * delta_t
            * (q / 2 + q**2 / 6 + q**3 / 12 + q**4 / 20 + q**5 / 30)
        )

        return PhysicalState(altitude=new_altitude, velocity=new_velocity)

    def make_state_display_string(self, sim_clock: SimulationClock, use_metric: bool = False) -> str:
        seconds = sim_clock.elapsed_time
        velocity = int(3600 * self.velocity)  # mph (always calculated)
        fuel = int(self.remaining_fuel())
        
        # Get distance and speed in proper units
        alt_value, alt_label = get_distance_display(self.altitude, use_metric)
        speed, speed_label = get_speed_display(velocity, use_metric)
        
        # Build engaging status display
        alt_str = f"{alt_value} {alt_label}"
        msg = f"⏱️ T+{seconds:>6.0f}s \n 🌍 {alt_str:>10} \n 📉 {speed:>5}{speed_label}\n"
        msg += f"⛽ Fuel: {fuel:>6}lbs "
        
        if self.fuel_per_second > 0:
            fuel_seconds = self.fuel_time_remaining()
            msg += f"| 🔥 {self.fuel_per_second:>5.0f}lbs/s ({fuel_seconds:>4.0f}s left)"
        
        # Add engine temp indicator if burning
        if self.engine_temp > 0:
            msg += f" | 🌡️ {self.engine_temp:.0f}%"
        
        # Add status indicator
        msg += "\n"
        
        # Engine temp warnings take priority
        if self.engine_temp > 90:
            msg += "🔴 CRITICAL: ENGINE OVERHEAT! Reduce burn NOW!"
        elif self.engine_temp > 70:
            msg += "🟠 WARNING: Engine temp rising - watch it!"
        elif speed > (3000 if not use_metric else int(3000 * 0.44704)):
            msg += "🚨 CRITICAL: Falling fast! Burn harder NOW!"
        elif speed > (1500 if not use_metric else int(1500 * 0.44704)):
            msg += "⚠️  WARNING: High descent rate - increase burn"
        elif speed > (500 if not use_metric else int(500 * 0.44704)):
            msg += "⚡ Descent rate: steady, watch it"
        elif speed > (100 if not use_metric else int(100 * 0.44704)):
            msg += "✅ Descent rate: controlled"
        else:
            msg += "🎯 Descent rate: excellent"
        
        return msg

    def to_dict(self) -> Dict[str, float]:
        """Serialize capsule state for storage"""
        return {
            "altitude": self.altitude,
            "velocity": self.velocity,
            "m": self.m,
            "n": self.n,
            "g": self.g,
            "z": self.z,
            "fuel_per_second": self.fuel_per_second,
            "engine_temp": self.engine_temp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> "Capsule":
        """Deserialize capsule state from storage"""
        return cls(
            altitude=data["altitude"],
            velocity=data["velocity"],
            m=data["m"],
            n=data["n"],
            g=data["g"],
            z=data["z"],
            fuel_per_second=data["fuel_per_second"],
            engine_temp=data.get("engine_temp", 0),
        )




def format_engine_failure(sim_clock: SimulationClock, capsule: Capsule) -> str:
    """Format engine failure outcome"""
    mission_time = sim_clock.elapsed_time
    altitude_at_failure = capsule.altitude
    velocity_at_failure = int(3600 * capsule.velocity)
    
    result = f"\n💥 ENGINE FAILURE AT T+{mission_time:.1f}s\n"
    result += f"📍 Altitude: {int(altitude_at_failure)}mi\n"
    result += f"📉 Velocity: {velocity_at_failure} mph (uncontrolled descent!)\n\n"
    result += "🔥 Thrusters shut down! Overheating caused catastrophic failure!\n"
    result += "☠️  MISSION FAILED - Uncontrolled impact imminent! 💀\n"
    
    return result

def format_landing_result(sim_clock: SimulationClock, capsule: Capsule) -> str:
    """Format landing outcome as a string with fun descriptions"""
    w = 3600 * capsule.velocity  # impact velocity in mph
    mission_time = sim_clock.elapsed_time
    fuel_used = 16500 - capsule.remaining_fuel()
    
    result = f"\n🌙 LUNAR TOUCHDOWN AT T+{mission_time:.1f}s\n"
    result += f"💥 Impact Velocity: {w:.1f} MPH\n"
    result += f"⛽ Fuel Used: {fuel_used:.0f} lbs\n\n"
    
    if w < 0.5:
        result += "🎯 PERFECT! Textbook landing! NASA wants to hire you! 🏆"
    elif w < 2:
        result += "✨ FLAWLESS DESCENT! Gentle as a feather on the lunar surface! 🌟"
    elif w < 10:
        result += "✅ NICE LANDING! Crew is happy, minimal scratches on hull."
    elif w < 30:
        result += "⚠️  ROUGH LANDING! Crew is shaken but safe. Some hull damage reported."
    elif w < 60:
        result += "💔 CRASH LANDING! Cabin pressure dropping... crew wounded but alive! 🏥"
    elif w < 100:
        result += "☠️  KABOOM! You hit harder than a meteor! New crater created! 💀"
    else:
        crater_size = w * 0.227
        result += f"☠️  CATASTROPHIC FAILURE! You blasted a {crater_size:.0f} FOOT CRATER!\nMission: FAILED 💀"
    
    return result


def show_landing(sim_clock: SimulationClock, capsule: Capsule) -> str:
    """Return landing result and mark game as ended"""
    return format_landing_result(sim_clock, capsule)


def show_out_of_fuel(sim_clock: SimulationClock, capsule: Capsule) -> str:
    """Return out of fuel message and calculate final landing"""
    msg = f"FUEL OUT AT {int(sim_clock.elapsed_time)} SECONDS\n"
    delta_t = (
        -capsule.velocity
        + math.sqrt(capsule.velocity**2 + 2 * capsule.altitude * capsule.g)
    ) / capsule.g
    capsule.velocity += capsule.g * delta_t
    sim_clock.advance(delta_t)
    msg += show_landing(sim_clock, capsule)
    return msg


def process_final_tick(
    delta_t: float, sim_clock: SimulationClock, capsule: Capsule
) -> str:
    """Process final tick when landing and return result"""
    # When we extrapolated our position based on our velocity
    # and delta_t, we overshot the surface. For better
    # accuracy, we will back up and do shorter time advances.

    while True:
        if delta_t < 5e-3:
            return show_landing(sim_clock, capsule)
        # line 35
        average_vel = (
            capsule.velocity
            + math.sqrt(
                capsule.velocity**2
                + 2
                * capsule.altitude
                * (capsule.g - capsule.z * capsule.fuel_per_second / capsule.m)
            )
        ) / 2
        delta_t = capsule.altitude / average_vel
        new_state = capsule.predict_motion(delta_t)
        capsule.update_state(sim_clock, delta_t, new_state)
        
        # Prevent infinite loop - if we're still above surface, landing result
        if new_state.altitude <= 0:
            return show_landing(sim_clock, capsule)


def handle_flyaway(sim_clock: SimulationClock, capsule: Capsule) -> bool:
    """
    The user has started flying away from the moon. Since this is a
    lunar LANDING simulation, we wait until the capsule's velocity is
    positive (downward) before prompting for more input.

    Returns True if landed, False if simulation should continue.
    """

    while True:
        w = (1 - capsule.m * capsule.g / (capsule.z * capsule.fuel_per_second)) / 2
        delta_t = (
            capsule.m
            * capsule.velocity
            / (
                capsule.z
                * capsule.fuel_per_second
                * math.sqrt(w**2 + capsule.velocity / capsule.z)
            )
        ) + 0.05

        new_state = capsule.predict_motion(delta_t)

        if new_state.altitude <= 0:
            # have landed
            return True

        capsule.update_state(sim_clock, delta_t, new_state)

        if (new_state.velocity > 0) or (capsule.velocity <= 0):
            # return to normal sim
            return False



def check_engine_failure(burn_rate: float, engine_temp: float, burn_duration: float) -> Tuple[bool, float]:
    """
    Check if engine fails during burn.
    
    Args:
        burn_rate: Current burn rate (lbs/sec)
        engine_temp: Current engine temperature (0-100%)
        burn_duration: How long to burn (seconds)
    
    Returns:
        Tuple[bool, float]: (engine_failed, new_temp)
        - engine_failed: True if engine failure occurs
        - new_temp: Updated engine temperature
    """
    
    # If not burning, apply cooling from previous burn
    if burn_rate == 0:
        # Cooling rates based on last burn intensity
        # We estimate from current temp: if hot, we burned hard recently
        if engine_temp > 50:
            cooling = 15  # Was burning hard, cool slowly
        elif engine_temp > 20:
            cooling = 30  # Was burning moderately, cool faster
        else:
            cooling = 50  # Was barely burning or not, cool rapidly
        
        return False, max(0, engine_temp - cooling)
    
    # Calculate temp increase based on burn rate (heating while burning)
    # 0-300 = safe, 300-450 = risky, >450 = very risky
    # At 300 lbs/sec: minimal heating (0.5% per second max)
    if burn_rate <= 100:
        temp_increase = (burn_rate / 100) * 0.2  # 0-0.2% per second
    elif burn_rate <= 300:
        temp_increase = 0.2 + ((burn_rate - 100) / 200) * 0.3  # 0.2-0.5% per second
    elif burn_rate <= 450:
        temp_increase = 0.5 + ((burn_rate - 300) / 150) * 4.5  # 0.5-5% per second
    else:
        temp_increase = 5 + ((burn_rate - 450) / 100) * 25  # 5%+ per second
    
    # Calculate total temp increase over burn duration
    new_temp = engine_temp + (temp_increase * burn_duration)
    
    # Random failure chance if overheating during the burn
    if new_temp > 100:
        # Guaranteed failure above 100%
        return True, 100.0
    elif new_temp > 80:
        # 50% failure chance above 80%
        if random.random() < 0.5:
            return True, new_temp
    
    # Return heated temp (cooling happens on next free-fall turn)
    return False, new_temp

def trigger_random_event(capsule: Capsule, sim_clock: SimulationClock) -> Tuple[str, float, float]:
    """
    Randomly trigger space hazards or helpful aliens.
    
    Returns:
        Tuple[str, float, float]: (event_message, fuel_delta, altitude_delta)
    """
    event_chance = random.random()
    
    # 5-10% chance of event
    if event_chance > 0.92:  # 8% base chance
        event_roll = random.random()
        
        if event_roll < 0.15:  # O-ring failure
            msg = "🔴 O-RING FAILURE! Thrust reduced to 50% this burn!"
            return msg, 0, 0
        
        elif event_roll < 0.35:  # Meteor shower
            altitude_loss = random.uniform(5, 15)
            msg = f"☄️  METEOR SHOWER! Lost {altitude_loss:.0f} miles altitude!"
            return msg, 0, -altitude_loss
        
        elif event_roll < 0.50:  # Solar flare
            msg = "⚡ SOLAR FLARE! Instruments blinded for this turn..."
            return msg, 0, 0
        
        elif event_roll < 0.70:  # Hostile aliens drain fuel
            fuel_drain = random.uniform(500, 2000)
            msg = f"👽 ALIENS! They drained {fuel_drain:.0f} lbs of fuel! 😱"
            return msg, -fuel_drain, 0
        
        elif event_roll < 0.85:  # Helpful aliens add fuel
            fuel_gain = random.uniform(500, 1500)
            msg = f"👽 ALIENS! Wait... they're helping? Gave us {fuel_gain:.0f} lbs! 💚"
            return msg, fuel_gain, 0
        
        else:  # Micro-meteorite fuel leak
            fuel_leak = random.uniform(100, 500)
            msg = f"💥 MICRO-METEORITE! Hull breach! {fuel_leak:.0f} lbs fuel leaking!"
            return msg, -fuel_leak, 0
    
    # No event
    return "", 0, 0


def update_game_state(
    capsule: Capsule, sim_clock: SimulationClock, burn_rate: float, burn_duration: float = 10
) -> Tuple[bool, Optional[str]]:
    """
    Update game state for one simulation cycle.
    
    Args:
        capsule: Current capsule state
        sim_clock: Current simulation clock
        burn_rate: Burn rate in lbs/sec (0-200)
        burn_duration: How long to burn in seconds (default 10)
    
    Returns:
        Tuple[bool, Optional[str]]: (game_ended, outcome_message)
        - game_ended: True if landed or out of fuel
        - outcome_message: Result string if game ended, None otherwise
    """
    
    # Check for engine failure
    engine_failed, new_temp = check_engine_failure(burn_rate, capsule.engine_temp, burn_duration)
    capsule.engine_temp = new_temp
    
    if engine_failed:
        return True, format_engine_failure(sim_clock, capsule)
    
    # Set the burn rate for this cycle
    if burn_rate < 0:
        return False, None  # Invalid input
    
    # Allow overspeed burn at player's risk
    capsule.fuel_per_second = burn_rate
    sim_clock.time_until_next_prompt = burn_duration

    # Simulate one cycle (up to next prompt or landing)
    while sim_clock.time_until_next_prompt > 0:
        if capsule.is_out_of_fuel():
            outcome = show_out_of_fuel(sim_clock, capsule)
            return True, outcome

        # clock advance is the shorter of the time to the next prompt,
        # or when we run out of fuel.
        if capsule.fuel_per_second > 0:
            delta_t = min(
                sim_clock.time_until_next_prompt, capsule.fuel_time_remaining()
            )
        else:
            delta_t = sim_clock.time_until_next_prompt

        new_state = capsule.predict_motion(delta_t)

        if new_state.altitude <= 0:
            outcome = process_final_tick(delta_t, sim_clock, capsule)
            return True, outcome

        if capsule.velocity > 0 and new_state.velocity < 0:
            if handle_flyaway(sim_clock, capsule):
                outcome = process_final_tick(delta_t, sim_clock, capsule)
                return True, outcome
        else:
            capsule.update_state(sim_clock, delta_t, new_state)
        
        # If we ran out of fuel during this tick, end the turn immediately
        if capsule.is_out_of_fuel() and sim_clock.time_until_next_prompt > 0:
            sim_clock.time_until_next_prompt = 0

    # Simulation cycle complete, get ready for next prompt
    return False, None


def get_status_message(capsule: Capsule, sim_clock: SimulationClock, use_metric: bool = False) -> str:
    """Get current game status as a formatted string for display"""
    return capsule.make_state_display_string(sim_clock, use_metric)


class LunarLander:
    """Mesh Bot compatible Lunar Lander game handler"""
    
    def __init__(self):
        """Initialize the game"""
        pass
    
    def new_game(self) -> Tuple[Dict, str]:
        """
        Start a new game with randomized difficulty.
        
        Returns:
            Tuple[Dict, str]: (game_state_dict, welcome_message)
        """
        # Randomize starting conditions for variety
        # Altitude: mostly mid-range but can be high or low
        altitude = random.uniform(60, 180)
        
        # Velocity: usually gentle descent, occasionally steeper
        # Biased toward easier starts for fun gameplay
        # NOTE: Must convert mph to miles/second for internal physics!
        velocity_mph = random.choices(
            [random.uniform(0.3, 0.8), random.uniform(0.8, 1.5)],
            weights=[70, 30]  # 70% gentle, 30% challenging
        )[0]
        velocity = velocity_mph / 3600  # Convert mph to miles/second
        
        # Fuel: mostly normal with occasional scarcity
        # 0.8-1.3 multiplier gives good playability range
        # Biased toward having enough fuel
        fuel_mult = random.choices(
            [random.uniform(0.85, 1.15), random.uniform(0.75, 0.95)],
            weights=[80, 20]  # 80% normal+ fuel, 20% tight fuel
        )[0]
        
        mass_with_fuel = 16500 + (16500 * fuel_mult)
        
        capsule = Capsule(
            altitude=altitude,
            velocity=velocity,
            m=mass_with_fuel,
            n=16500,  # Base mass stays constant
        )
        sim_clock = SimulationClock(0, 10)
        
        game_state = {
            "capsule": capsule.to_dict(),
            "clock": sim_clock.to_dict(),
            "turn_count": 0,
            "result": None,
        }
        
        welcome = (
            "🚀 LUNAR LANDER 🚀\n"
            "Your onboard computer crashed (Boeing made it 😬)\n"
            "YOU must land this capsule manually!\n\n"
            "💡 Enter: burn_rate [duration_sec]\n"
            "📊 Examples: '100' (10s default) or '150 5'\n"
            "⏱️ Watch descent & fuel! Type 'help' for more\n\n"
        )
        
        status = get_status_message(capsule, sim_clock, use_metric=False)
        return game_state, welcome + status + "\n\n→ Enter burn rate:"
    
    def play(self, game_state: Dict, burn_input: str, use_metric: bool = False) -> Tuple[Dict, str, bool]:
        """
        Process player input and return updated state.
        
        Args:
            game_state: Current game state dict
            burn_input: Player input (burn rate or command)
            use_metric: If True, display in metric units (km, m/s); if False, imperial (mi, ft, mph)
            
        Returns:
            Tuple[Dict, str, bool]: (updated_state, response_message, game_ended)
        """
        burn_rate = None
        burn_duration = None
        
        # Check if confirming overheat warning
        if 'pending_burn' in game_state:
            burn_input_lower = burn_input.strip().lower()
            if burn_input_lower in ('y', 'yes'):
                burn_rate, burn_duration = game_state['pending_burn']
                del game_state['pending_burn']
                # Proceed with high burn - skip to execution below
            elif burn_input_lower in ('n', 'no'):
                del game_state['pending_burn']
                capsule = Capsule.from_dict(game_state['capsule'])
                sim_clock = SimulationClock.from_dict(game_state['clock'])
                msg = "❌ Burn cancelled. Engine temp cooling...\n\n"
                msg += get_status_message(capsule, sim_clock, use_metric)
                msg += "\n\n→ Enter burn rate:"
                return (game_state, msg, False)
            else:
                return (game_state, "Enter 'y' to proceed or 'n' to cancel:", False)
        
        # Only parse if we don't already have burn_rate from pending_burn confirmation
        if burn_rate is None:
            # Handle commands
            burn_input = burn_input.strip().lower()
            if burn_input in ("quit", "end", "exit"):
                return game_state, "🚀 Mission aborted. Safe travels! Type 'lunarlander' to try again.", True
            if burn_input in ("help", "?", "h"):
                help_msg = (
                    "📖 CONTROLS:\n"
                    "• Burn rate: 0-300 lbs/sec\n"
                    "• Duration: 1-240 seconds (default 10)\n"
                    "• Format: '100' or '100 5'\n\n"
                    "Examples:\n"
                    "  100 → Burn at 100 for 10s (default)"
                    "  150 5 → Burn at 150 for 5s"
                    "  0 → FREE FALL (no burn)\n\n"
                    "💡 Quick burn = less fuel, longer = more control!"
                )
                return (game_state, help_msg, False)
            
            # Parse burn rate and optional duration
            burn_rate = 0
            burn_duration = 10  # default
            
            try:
                parts = burn_input.split()
                burn_rate = float(parts[0])
                if len(parts) > 1:
                    burn_duration = float(parts[1])
                
                # Validate burn rate (allow > 300 but warn about risk)
                if burn_rate < 0:
                    capsule = Capsule.from_dict(game_state['capsule'])
                    sim_clock = SimulationClock.from_dict(game_state['clock'])
                    error_msg = f"❌ Burn rate cannot be negative!\nUse 0-300 safe, higher = risky!\n\n"
                    error_msg += get_status_message(capsule, sim_clock, use_metric)
                    error_msg += "\n\n→ Try again (e.g., '100' or '100 5'):"
                    return (game_state, error_msg, False)
                
                if burn_rate > 300:
                    # Warn about overheat risk
                    capsule = Capsule.from_dict(game_state['capsule'])
                    sim_clock = SimulationClock.from_dict(game_state['clock'])
                    warn_msg = f"⚠️  CAUTION: Burn rate {burn_rate} exceeds safe limit (300)!\n"
                    warn_msg += f"🔥 Engine temp will rise rapidly - risk of failure!\n\n"
                    warn_msg += get_status_message(capsule, sim_clock, use_metric)
                    warn_msg += f"\n\n→ Proceed with {burn_rate} lbs/sec? (y/n):"
                    # Store pending action
                    game_state['pending_burn'] = (burn_rate, burn_duration)
                    return (game_state, warn_msg, False)
                
                # Validate duration
                if burn_duration < 1 or burn_duration > 240:
                    capsule = Capsule.from_dict(game_state['capsule'])
                    sim_clock = SimulationClock.from_dict(game_state['clock'])
                    error_msg = f"❌ Duration '{burn_duration}' out of range!\nUse 1-240 seconds (default 10)\n\n"
                    error_msg += get_status_message(capsule, sim_clock, use_metric)
                    error_msg += "\n\n→ Try again (e.g., '100' or '100 5'):"
                    return (game_state, error_msg, False)
                    
            except (ValueError, IndexError):
                capsule = Capsule.from_dict(game_state['capsule'])
                sim_clock = SimulationClock.from_dict(game_state['clock'])
                error_msg = f"❌ '{burn_input}' invalid format!\nEnter: burn_rate [duration]\n\n"
                error_msg += get_status_message(capsule, sim_clock, use_metric)
                error_msg += "\n\n→ Try again (e.g., '100' or '100 5'):"
                return (game_state, error_msg, False)
        
        # Restore game state
        capsule = Capsule.from_dict(game_state["capsule"])
        sim_clock = SimulationClock.from_dict(game_state["clock"])
        
        # Check for random space events (5-10% chance)
        event_msg, fuel_delta, altitude_delta = trigger_random_event(capsule, sim_clock)
        
        # Apply event effects
        if event_msg:
            capsule.m = max(capsule.n, capsule.m + fuel_delta)  # Cap at base mass minimum
            capsule.altitude = max(0, capsule.altitude + altitude_delta)
            
            # Check for O-ring failure - reduce thrust
            if "O-RING" in event_msg:
                burn_rate = burn_rate * 0.5
        
        # Update game with burn rate and duration
        game_ended, outcome = update_game_state(capsule, sim_clock, burn_rate, burn_duration)
        
        # Save updated state
        game_state["capsule"] = capsule.to_dict()
        game_state["clock"] = sim_clock.to_dict()
        game_state["turn_count"] += 1
        game_state["result"] = outcome if game_ended else None
        
        # Generate response
        if game_ended:
            response = outcome + "\n\n🔄 Type 'lunarlander' to play again"
        else:
            event_display = event_msg + "\n\n" if event_msg else ""
            status = get_status_message(capsule, sim_clock, use_metric)
            response = event_display + status + "\n\n→ Next burn rate:"
        
        return game_state, response, game_ended


def run_simulation() -> None:
    """Legacy function for standalone play - kept for backwards compatibility"""
    print()
    print(
        format_line_for_report("SEC", "MI", "FT", "MPH", "LB FUEL", "BURN RATE", True)
    )
    print("(This is a legacy mode - use mesh_bot.py for mesh integration)")


def main() -> None:
    """Legacy main for standalone play"""
    print("LUNAR")
    print("CREATIVE COMPUTING  MORRISTOWN, NEW JERSEY\n\n\n")
    print("THIS IS A COMPUTER SIMULATION OF AN APOLLO LUNAR")
    print("LANDING CAPSULE.\n\n")
    print("THE ON-BOARD COMPUTER HAS FAILED (IT WAS MADE BY")
    print("XEROX) SO YOU HAVE TO LAND THE CAPSULE MANUALLY.\n")
    print("SET BURN RATE OF RETRO ROCKETS TO ANY VALUE BETWEEN")
    print("0 (FREE FALL) AND 300 (MAXIMUM BURN) POUNDS PER SECOND.")
    print("SET NEW BURN RATE EVERY 10 SECONDS.\n")
    print("CAPSULE WEIGHT 32,500 LBS; FUEL WEIGHT 16,000 LBS.\n\n\n")
    print("GOOD LUCK\n")
    print("(Converted to mesh bot - see mesh_bot.py for integration)")


if __name__ == "__main__":
    main()