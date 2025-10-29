# xtide.py - Global tide prediction using tidepredict library
# K7MHI Kelly Keeton 2025

import json
from datetime import datetime, timedelta
from modules.log import logger
import modules.settings as my_settings

try:
    from tidepredict import processdata, process_station_list, constants, timefunc
    from tidepredict.tide import Tide
    import pandas as pd
    TIDEPREDICT_AVAILABLE = True
except ImportError:
    TIDEPREDICT_AVAILABLE = False
    logger.warning("xtide: tidepredict module not installed. Install with: pip install tidepredict")

def get_nearest_station(lat, lon):
    """
    Find the nearest tide station to the given lat/lon coordinates.
    Returns station code (e.g., 'h001a') or None if not found.
    """
    if not TIDEPREDICT_AVAILABLE:
        return None
    
    try:
        # Read the station list
        try:
            stations = pd.read_csv(constants.STATIONFILE)
        except FileNotFoundError:
            # If station file doesn't exist, create it (requires network)
            logger.info("xtide: Creating station database from online source (requires network)")
            try:
                stations = process_station_list.create_station_dataframe()
            except Exception as net_error:
                logger.error(f"xtide: Failed to download station database: {net_error}")
                return None
        
        if stations.empty:
            logger.error("xtide: No stations found in database")
            return None
        
        # Calculate distance to each station
        # Using simple haversine-like calculation
        def calc_distance(row):
            try:
                # Parse lat/lon from the format like "43-36S", "172-43E"
                station_lat, station_lon = parse_station_coords(row['Lat'], row['Lon'])
                
                # Simple distance calculation (not precise but good enough)
                dlat = lat - station_lat
                dlon = lon - station_lon
                return (dlat**2 + dlon**2)**0.5
            except:
                return float('inf')
        
        stations['distance'] = stations.apply(calc_distance, axis=1)
        
        # Find the nearest station
        nearest = stations.loc[stations['distance'].idxmin()]
        
        if nearest['distance'] > 10:  # More than ~10 degrees away, might be too far
            logger.warning(f"xtide: Nearest station is {nearest['distance']:.1f}° away at {nearest['loc_name']}")
        
        station_code = "h" + nearest['stat_idx'].lower()
        logger.debug(f"xtide: Found nearest station: {nearest['loc_name']} ({station_code}) at {nearest['distance']:.2f}° away")
        
        return station_code, nearest['loc_name'], nearest['country']
    
    except Exception as e:
        logger.error(f"xtide: Error finding nearest station: {e}")
        return None

def parse_station_coords(lat_str, lon_str):
    """
    Parse station coordinates from format like "43-36S", "172-43E"
    Returns tuple of (latitude, longitude) as floats
    """
    try:
        # Parse latitude
        lat_parts = lat_str.split('-')
        lat_deg = float(lat_parts[0])
        lat_min = float(lat_parts[1][:-1])  # Remove N/S
        lat_dir = lat_parts[1][-1]  # Get N/S
        lat_val = lat_deg + lat_min/60.0
        if lat_dir == 'S':
            lat_val = -lat_val
        
        # Parse longitude
        lon_parts = lon_str.split('-')
        lon_deg = float(lon_parts[0])
        lon_min = float(lon_parts[1][:-1])  # Remove E/W
        lon_dir = lon_parts[1][-1]  # Get E/W
        lon_val = lon_deg + lon_min/60.0
        if lon_dir == 'W':
            lon_val = -lon_val
        
        return lat_val, lon_val
    except Exception as e:
        logger.debug(f"xtide: Error parsing coordinates {lat_str}, {lon_str}: {e}")
        return 0.0, 0.0

def get_tide_predictions(lat=0, lon=0, days=1):
    """
    Get tide predictions for the given location using tidepredict library.
    Returns formatted string with tide predictions.
    
    Parameters:
    - lat: Latitude
    - lon: Longitude  
    - days: Number of days to predict (default: 1)
    
    Returns:
    - Formatted string with tide predictions or error message
    """
    if not TIDEPREDICT_AVAILABLE:
        return "tidepredict library not installed"
    
    if float(lat) == 0 and float(lon) == 0:
        return "No GPS data for tide prediction"
    
    try:
        # Find nearest station
        station_info = get_nearest_station(float(lat), float(lon))
        if not station_info:
            return "No tide station found nearby. Network may be required to download station data."
        
        station_code, station_name, station_country = station_info
        
        # Load station data
        station_dict, harmfileloc = process_station_list.read_station_info_file()
        
        # Check if harmonic data exists for this station
        if station_code not in station_dict:
            logger.warning(f"xtide: No harmonic data for {station_name}.")
            return f"Tide data not available for {station_name}. Station database may need initialization."
        
        # Reconstruct tide model
        tide = processdata.reconstruct_tide_model(station_dict, station_code)
        if tide is None:
            return f"Tide model unavailable for {station_name}"
        
        # Set up time range (today only)
        now = datetime.now()
        start_time = now.strftime("%Y-%m-%d 00:00")
        end_time = (now + timedelta(days=days)).strftime("%Y-%m-%d 00:00")
        
        # Create time object
        timeobj = timefunc.Tidetime(
            st_time=start_time,
            en_time=end_time,
            station_tz=station_dict[station_code].get('tzone', 'UTC')
        )
        
        # Get predictions
        predictions = processdata.predict_plain(tide, station_dict[station_code], 't', timeobj)
        
        # Format output for mesh
        lines = predictions.strip().split('\n')
        if len(lines) > 2:
            # Skip the header lines and format for mesh display
            result = f"Tide: {station_name}\n"
            tide_lines = lines[2:]  # Skip first 2 header lines
            
            # Format each tide prediction
            for line in tide_lines[:8]:  # Limit to 8 entries
                parts = line.split()
                if len(parts) >= 4:
                    date_str = parts[0]
                    time_str = parts[1]
                    height = parts[3]
                    tide_type = ' '.join(parts[4:])
                    
                    # Convert to 12-hour format if not using zulu time
                    if not my_settings.zuluTime:
                        try:
                            time_obj = datetime.strptime(time_str, "%H%M")
                            hour = time_obj.hour
                            minute = time_obj.minute
                            if hour >= 12:
                                time_str = f"{hour-12 if hour > 12 else 12}:{minute:02d} PM"
                            else:
                                time_str = f"{hour if hour > 0 else 12}:{minute:02d} AM"
                        except:
                            pass
                    
                    result += f"{tide_type} {time_str}, {height}\n"
            
            return result.strip()
        else:
            return predictions
    
    except FileNotFoundError as e:
        logger.error(f"xtide: Station data file not found: {e}")
        return "Tide station database not initialized. Network access required for first-time setup."
    except Exception as e:
        logger.error(f"xtide: Error getting tide predictions: {e}")
        return f"Error getting tide data: {str(e)}"

def is_enabled():
    """Check if xtide/tidepredict is enabled in config"""
    return getattr(my_settings, 'useTidePredict', False) and TIDEPREDICT_AVAILABLE
