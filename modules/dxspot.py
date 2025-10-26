# meshing-around modules/dxspot.py - Handles DX Spotter integration
# Fetches DX spots from Spothole API based on user commands
# 2025 K7MHI Kelly Keeton
import requests
import datetime
from modules.log import logger

trap_list_dxspotter = ["dx"]

def handledxcluster(message, nodeID, deviceID):
    from modules.dxspot import get_spothole_spots
    if "DX" in message.upper():
        logger.debug(f"System: DXSpotter: Device:{deviceID} Handler: DX Spot Request Received from Node {nodeID}")
        band = None
        mode = None
        source = None
        dx_call = None
        parts = message.split()
        for part in parts:
            if part.lower().startswith("band="):
                band = part.split("=")[1]
            elif part.lower().startswith("mode="):
                mode = part.split("=")[1]
            elif part.lower().startswith("ota="):
                source = part.split("=")[1]
            elif part.lower().startswith("of="):
                dx_call = part.split("=")[1]
        # Build params dict
        params = {}
        if source:
            params["source"] = source.upper()
        if band:
            params["band"] = band.lower()
        if mode:
            params["mode"] = mode.upper()
        if dx_call:
            params["dx_call"] = dx_call.upper()

        # Fetch spots
        spots = get_spothole_spots(**params)
        if spots:
            response_lines = []
            for spot in spots[:5]:
                callsign = spot.get('dx_call', spot.get('callsign', 'N/A'))
                freq_hz = spot.get('freq', spot.get('frequency', None))
                frequency = f"{float(freq_hz)/1e6:.3f} MHz" if freq_hz else "N/A"
                mode_val = spot.get('mode', 'N/A')
                comment = spot.get('comment', '')
                if len(comment) > 111: # Truncate comment to 111 chars
                    comment = comment[:111] + '...'
                sig = spot.get('sig', '')
                de_grid = spot.get('de_grid', '')
                de_call = spot.get('de_call', '')
                sig_ref_name = spot.get('sig_refs_names', [''])[0] if spot.get('sig_refs_names') else ''
                line = f"{callsign} @{frequency} {mode_val} {sig} {sig_ref_name} by:{de_call} {de_grid} {comment}"
                response_lines.append(line)
            response = "\n".join(response_lines)
        else:
            response = "No DX spots found."
        return response
    return "Error: No DX command found."

def get_spothole_spots(source=None, band=None, mode=None, date=None, dx_call=None, de_continent=None, de_location=None):
    """
    Fetches spots from https://spothole.app/api/v1/spots with optional filters.
    Returns a list of spot dicts.
    """
    url = "https://spothole.app/api/v1/spots"
    params = {}
    

    # Add administrative filters if provided
    qrt = False  # Always fetch active spots
    needs_sig = False # Always need spots wth a group ike Xota
    limit = 4
    dedupe = True

    params["dedupe"] = str(dedupe).lower()
    params["limit"] = limit
    params["qrt"] = str(qrt).lower()
    params["needs_sig"] = str(needs_sig).lower()
    params["needs_sig_ref"] = 'true'
    # Only get spots from last 9 hours
    received_since_dt = datetime.datetime.utcnow() - datetime.timedelta(hours=9)
    received_since = int(received_since_dt.timestamp())
    params["received_since"] = received_since
    
    # Add spot filters if provided
    if source:
        params["source"] = source
    if band:
        params["band"] = band
    if mode:
        params["mode"] = mode
    if date:
        # date should be a string in YYYY-MM-DD or datetime.date
        if isinstance(date, datetime.date):
            params["date"] = date.isoformat()
        else:
            params["date"] = date
    
    try:
        headers = {"User-Agent": "meshing-around-dxspotter/1.0"}
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        spots = response.json()
    except Exception as e:
        logger.debug(f"Error fetching spots: {e}")
        spots = []

    # Admin Filters done via config.ini
    de_grid = None  # e.g., "EM00"
    de_latitude = None  # e.g., 34.05
    de_longitude = None  # e.g., -118.25
    de_dxcc_id = None  # e.g., "291"
    de_call = None  # e.g., "K7MHI"

    dx_itu_zone = None  # e.g., "3"
    dx_cq_zone = None  # e.g., "4"
    dx_dxcc_id = None  # e.g., "291"

    # spotter
    if de_latitude is not None and de_longitude is not None:
        lat_range = (de_latitude - 1.0, de_latitude + 1.0)
        lon_range = (de_longitude - 1.0, de_longitude + 1.0)
        spots = [spot for spot in spots if lat_range[0] <= spot.get('de_latitude', 0) <= lat_range[1] and
                 lon_range[0] <= spot.get('de_longitude', 0) <= lon_range[1]]
    if de_grid:
        spots = [spot for spot in spots if spot.get('de_grid', '').upper() == de_grid.upper()]
    if de_dxcc_id:
        spots = [spot for spot in spots if str(spot.get('de_dxcc_id', '')) == str(de_dxcc_id)]
    if de_call:
        spots = [spot for spot in spots if spot.get('de_call', '').upper() == de_call.upper()]
    # DX
    if dx_itu_zone:
        spots = [spot for spot in spots if str(spot.get('dx_itu_zone', '')) == str(dx_itu_zone)]
    if dx_cq_zone:
        spots = [spot for spot in spots if str(spot.get('dx_cq_zone', '')) == str(dx_cq_zone)]
    if dx_dxcc_id:
        spots = [spot for spot in spots if str(spot.get('dx_dxcc_id', '')) == str(dx_dxcc_id)]

    # User Filters

    # Filter by dx_call if provided
    if dx_call:
        spots = [spot for spot in spots if spot.get('dx_call', '').upper() == dx_call.upper()]

    # Filter by de_continent if provided
    if de_continent:
        spots = [spot for spot in spots if spot.get('de_continent', '').upper() == de_continent.upper()]

    # Filter by de_location if provided
    if de_location:
        spots = [spot for spot in spots if spot.get('de_location', '').upper() == de_location.upper()]

    return 

def handle_post_dxspot():
    time = int(datetime.datetime.utcnow().timestamp())
    freq = 14200000  # 14 MHz
    comment = "Test spot please ignore"
    de_spot = "N0CALL"
    dx_spot = "N0CALL"
    spot = {"dx_call": dx_spot, "time": time, "freq": freq, "comment": comment, "de_call": de_spot}
    try:
        success = post_spothole_spot(spot)
        if success:
            return "Spot posted successfully."
        else:
            return "Failed to post spot."
    except Exception as e:
        logger.debug(f"Error in handle_post_dxspot: {e}")
        return "Error occurred while posting spot."

def post_spothole_spot(spot):
    """
    Posts a new spot to https://spothole.app/api/v1/spot.
    """
    url = "https://spothole.app/api/v1/spot"
    headers = {"Content-Type": "application/json", "User-Agent": "meshing-around-dxspotter/1.0"}
    try:
        response = requests.post(url, json=spot, headers=headers, timeout=10)
        response.raise_for_status()
        logger.debug(f"Spot posted successfully: {response.json()}")
        return True
    except Exception as e:
        logger.debug(f"Error posting spot: {e}")
        return False