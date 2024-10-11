"""
Mesh Trekker Game
Game Rules:
1. Players compete to cover the most distance over time using their Meshtastic devices.
2. The game tracks players' movements via GPS coordinates sent by their devices.
3. Total distance traveled is calculated and summed over time for each player.
4. Leaderboards show top distances for daily, weekly, and all-time periods.
5. Players can form teams, with team distances being the sum of all team members' distances.
6. Special achievements are awarded for milestones (e.g., 10km, 50km, 100km total distance).
7. The game runs continuously, allowing players to participate at their own pace.
8. Players can use the 'whereami' command to check their current location and update their position in the game.
"""

import pickle
from modules.log import *
from datetime import datetime, timedelta
from geopy.distance import geodesic

class MeshTrekkerError(Exception):
    """Base class for exceptions in this module."""
    pass

class DataLoadError(MeshTrekkerError):
    """Raised when there's an error loading data."""
    pass

class DataSaveError(MeshTrekkerError):
    """Raised when there's an error saving data."""
    pass

class InvalidGPSDataError(MeshTrekkerError):
    """Raised when invalid GPS data is provided."""
    pass

class MeshTrekker:
    def __init__(self, data_file='mesh_trekker_data.pkl'):
        self.data_file = data_file
        try:
            self.data = self.load_data()
        except DataLoadError as e:
            logger.error(f"Failed to load data: {e}")
            self.data = self.initialize_data()

    def initialize_data(self):
        return {
            'gps_data': {},
            'user_distances': {},
            'teams': {},
            'achievements': {},
        }

    def load_data(self):
        try:
            with open(self.data_file, 'rb') as f:
                return pickle.load(f)
        except (pickle.PickleError, EOFError, FileNotFoundError) as e:
            logger.info(f"Data file {self.data_file} not found. Initializing new data.")
            return self.initialize_data()

    def save_data(self):
        try:
            with open(self.data_file, 'wb') as f:
                pickle.dump(self.data, f)
        except (pickle.PickleError, IOError) as e:
            raise DataSaveError(f"Error saving data: {e}")

    def validate_gps_data(self, latitude, longitude, timestamp):
        try:
            lat = float(latitude)
            lon = float(longitude)
            if not -90 <= lat <= 90:
                raise InvalidGPSDataError(f"Invalid latitude: {latitude}")
            if not -180 <= lon <= 180:
                raise InvalidGPSDataError(f"Invalid longitude: {longitude}")
            if not isinstance(timestamp, datetime):
                raise InvalidGPSDataError(f"Invalid timestamp: {timestamp}")
        except ValueError:
            raise InvalidGPSDataError(f"Invalid GPS data: latitude={latitude}, longitude={longitude}")

    def process_gps_data(self, user_id, latitude, longitude, timestamp):
        try:
            self.validate_gps_data(latitude, longitude, timestamp)

            if user_id not in self.data['gps_data']:
                self.data['gps_data'][user_id] = []

            self.data['gps_data'][user_id].append((float(latitude), float(longitude), timestamp))

            if len(self.data['gps_data'][user_id]) > 1:
                last_lat, last_lon, last_time = self.data['gps_data'][user_id][-2]
                last_point = (last_lat, last_lon)
                new_point = (float(latitude), float(longitude))

                distance = geodesic(last_point, new_point).kilometers

                if user_id not in self.data['user_distances']:
                    self.data['user_distances'][user_id] = (0, timestamp)

                total_distance, _ = self.data['user_distances'][user_id]
                new_total_distance = total_distance + distance
                self.data['user_distances'][user_id] = (new_total_distance, timestamp)

                self.check_achievements(user_id, new_total_distance)

            self.save_data()
            return new_total_distance
        except InvalidGPSDataError as e:
            logger.error(f"Invalid GPS data for user {user_id}: {e}")
        except DataSaveError as e:
            logger.error(f"Failed to save data after processing GPS for user {user_id}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error processing GPS data for user {user_id}: {e}")
        return None

    def get_leaderboard(self, timeframe='all'):
        try:
            now = datetime.now()
            if timeframe == 'daily':
                start_time = now - timedelta(days=1)
            elif timeframe == 'weekly':
                start_time = now - timedelta(weeks=1)
            else:
                start_time = datetime.min

            leaderboard = []
            for user_id, (distance, last_updated) in self.data['user_distances'].items():
                if last_updated > start_time:
                    leaderboard.append((user_id, distance))

            return sorted(leaderboard, key=lambda x: x[1], reverse=True)[:10]
        except Exception as e:
            logger.error(f"Error generating leaderboard: {e}")
            return []

    def get_team_leaderboard(self):
        try:
            team_distances = {}
            for team_name, members in self.data['teams'].items():
                team_distance = sum(self.data['user_distances'].get(member, (0, None))[0] for member in members)
                team_distances[team_name] = team_distance

            return sorted(team_distances.items(), key=lambda x: x[1], reverse=True)[:10]
        except Exception as e:
            logger.error(f"Error generating team leaderboard: {e}")
            return []

    def get_user_stats(self, user_id):
        try:
            distance, last_updated = self.data['user_distances'].get(user_id, (0, None))
            achievements = self.data['achievements'].get(user_id, [])
            return {
                'distance': distance,
                'last_updated': last_updated,
                'achievements': achievements
            }
        except Exception as e:
            logger.error(f"Error retrieving stats for user {user_id}: {e}")
            return None

    def create_team(self, team_name, user_id):
        try:
            if team_name not in self.data['teams']:
                self.data['teams'][team_name] = [user_id]
                self.save_data()
                return True
            return False
        except DataSaveError as e:
            logger.error(f"Failed to save data after creating team {team_name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error creating team {team_name}: {e}")
            return False

    def join_team(self, team_name, user_id):
        try:
            if team_name in self.data['teams'] and user_id not in self.data['teams'][team_name]:
                self.data['teams'][team_name].append(user_id)
                self.save_data()
                return True
            return False
        except DataSaveError as e:
            logger.error(f"Failed to save data after user {user_id} joined team {team_name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error joining team {team_name} for user {user_id}: {e}")
            return False

    def check_achievements(self, user_id, total_distance):
        try:
            if user_id not in self.data['achievements']:
                self.data['achievements'][user_id] = []

            milestones = [10, 50, 100, 500, 1000]  # in km
            new_achievements = []
            for milestone in milestones:
                if total_distance >= milestone and milestone not in self.data['achievements'][user_id]:
                    self.data['achievements'][user_id].append(milestone)
                    new_achievements.append(milestone)
                    logger.info(f"User {user_id} achieved {milestone}km milestone!")
            return new_achievements
        except Exception as e:
            logger.error(f"Error checking achievements for user {user_id}: {e}")
            return []

    def get_achievements(self, user_id):
        try:
            return self.data['achievements'].get(user_id, [])
        except Exception as e:
            logger.error(f"Error retrieving achievements for user {user_id}: {e}")
            return []
        
# Initialize the game
game = MeshTrekker()

def handle_meshtrekker(user_id, deviceID, channel_number, location_info=(0,0)):
    # Process GPS data from Meshtastic devices
    latitude, longitude = location_info.split(": ")[1].split(", ")
    
    current_time = datetime.now()
    new_distance = game.process_gps_data(user_id, latitude, longitude, current_time)


    # # Create and join teams
    # game.create_team("Team A", "user1")
    # game.join_team("Team A", "user2")

    # # Get individual leaderboard
    # print("\nAll-time individual leaderboard:")
    # for user, distance in game.get_leaderboard():
    #     print(f"{user}: {distance:.2f} km")

    # # Get team leaderboard
    # print("\nTeam leaderboard:")
    # for team, distance in game.get_team_leaderboard():
    #     print(f"{team}: {distance:.2f} km")

    # # Get user stats
    # user_stats = game.get_user_stats("user1")
    # print(f"\nUser1 stats: {user_stats}")

    # # Get achievements
    # achievements = game.get_achievements("user1")
    # print(f"User1 achievements: {achievements}")

    
    if new_distance is not None:
        new_achievements = game.check_achievements(user_id, new_distance)
        response = f"{location_info}\nTotal distance: {new_distance:.2f} km"
        if new_achievements:
            response += f"\nNew achievements: {', '.join([f'{a}km' for a in new_achievements])}"
    else:
        response = f"{location_info}\nFailed to update distance. Please try again."
    
    return response

