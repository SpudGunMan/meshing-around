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
                callsign = spot.get('dx_call', spot.get('callsign', ''))
                freq_hz = spot.get('freq', spot.get('frequency', None))
                frequency = f"{float(freq_hz)/1e6:.3f} MHz" if freq_hz else ""
                mode_val = spot.get('mode', '')
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
    if de_continent:
        params["de_continent"] = de_continent
    if de_location:
        params["de_location"] = de_location
    if source:
        params["source"] = source
    if band:
        params["band"] = band
    if mode:
        params["mode"] = mode
    if dx_call:
        params["dx_call"] = dx_call
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
    return spots
