# helper functions to get HF band conditions, DRAP X-ray flux, and sunrise/sunset times
# HF code from https://github.com/Murturtle/MeshLink
# K7MHI Kelly Keeton 2024

import requests # pip install requests
import xml.dom.minidom
from datetime import datetime
import ephem # pip install pyephem
from datetime import timezone
from modules.log import logger, getPrettyTime
from modules.settings import (latitudeValue, longitudeValue, zuluTime,
                              n2yoAPIKey, urlTimeoutSeconds, use_metric,
                              ERROR_FETCHING_DATA, NO_DATA_NOGPS, NO_ALERTS)
import math

trap_list_solarconditions = ("sun", "moon", "solar", "hfcond", "satpass", "howtall")

def hf_band_conditions():
    # ham radio HF band conditions
    hf_cond = ""
    signalnoise = ""
    band_cond = requests.get("https://www.hamqsl.com/solarxml.php", timeout=urlTimeoutSeconds)
    if(band_cond.ok):
        solarxml = xml.dom.minidom.parseString(band_cond.text)
        for i in solarxml.getElementsByTagName("band"):
            hf_cond += i.getAttribute("time")[0]+i.getAttribute("name") +"="+str(i.childNodes[0].data)+"\n"
        hf_cond = hf_cond[:-1] # remove the last newline
        for i in solarxml.getElementsByTagName("solardata"):
            signalnoise = i.getElementsByTagName("signalnoise")[0].childNodes[0].data
        hf_cond += "\nQRN:" + signalnoise
    else:
        logger.error("Solar: Error fetching HF band conditions")
        hf_cond = ERROR_FETCHING_DATA
    
    return hf_cond

def solar_conditions():
    # radio related solar conditions from hamsql.com
    solar_cond = ""
    solar_cond = requests.get("https://www.hamqsl.com/solarxml.php", timeout=urlTimeoutSeconds)
    if(solar_cond.ok):
        solar_xml = xml.dom.minidom.parseString(solar_cond.text)
        for i in solar_xml.getElementsByTagName("solardata"):
            solar_a_index = i.getElementsByTagName("aindex")[0].childNodes[0].data
            solar_k_index = i.getElementsByTagName("kindex")[0].childNodes[0].data
            solar_xray = i.getElementsByTagName("xray")[0].childNodes[0].data
            solar_flux = i.getElementsByTagName("solarflux")[0].childNodes[0].data
            sunspots = i.getElementsByTagName("sunspots")[0].childNodes[0].data
            signalnoise = i.getElementsByTagName("signalnoise")[0].childNodes[0].data
        solar_cond = "A-Index: " + solar_a_index + "\nK-Index: " + solar_k_index + "\nSunspots: " + sunspots + "\nX-Ray Flux: " + solar_xray + "\nSolar Flux: " + solar_flux + "\nSignal Noise: " + signalnoise
    else:
        logger.error("Solar: Error fetching solar conditions")
        solar_cond = ERROR_FETCHING_DATA
    return solar_cond

def drap_xray_conditions():
    # DRAP X-ray flux conditions, from NOAA direct
    drap_cond = ""
    drap_cond = requests.get("https://services.swpc.noaa.gov/text/drap_global_frequencies.txt", timeout=urlTimeoutSeconds)
    if(drap_cond.ok):
        drap_list = drap_cond.text.split('\n')
        x_filter = '#  X-RAY Message :'
        for line in drap_list:
            if x_filter in line:
                xray_flux = line.split(": ")[1]
    else:
        logger.error("Error fetching DRAP X-ray flux")
        xray_flux = ERROR_FETCHING_DATA
    return xray_flux

def get_noaa_scales_summary():
    """
    Show latest observed, 24-hour max, and predicted geomagnetic, storm, and blackout data.
    """
    try:
        response = requests.get("https://services.swpc.noaa.gov/products/noaa-scales.json", timeout=urlTimeoutSeconds)
        if response.ok:
            data = response.json()
            today = datetime.utcnow().date()
            latest_entry = None
            latest_dt = None
            max_g_today = None
            max_g_scale = -1
            predicted_g = None
            predicted_g_scale = -1

            # Find latest observed and 24-hour max for today
            for entry in data.values():
                date_str = entry.get("DateStamp")
                time_str = entry.get("TimeStamp")
                if date_str and time_str:
                    try:
                        dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
                        g = entry.get("G", {})
                        g_scale = int(g.get("Scale", -1)) if g.get("Scale") else -1
                        # Latest observed for today
                        if dt.date() == today:
                            if latest_dt is None or dt > latest_dt:
                                latest_dt = dt
                                latest_entry = entry
                            # 24-hour max for today
                            if g_scale > max_g_scale:
                                max_g_scale = g_scale
                                max_g_today = entry
                        # Predicted (future)
                        elif dt.date() > today:
                            if g_scale > predicted_g_scale:
                                predicted_g_scale = g_scale
                                predicted_g = entry
                    except Exception:
                        continue

            def format_entry(label, entry):
                if not entry:
                    return f"{label}: No data"
                g = entry.get("G", {})
                s = entry.get("S", {})
                r = entry.get("R", {})
                parts = [f"{label} {g.get('Text', 'N/A')} (G:{g.get('Scale', 'N/A')})"]
            
                # Only show storm if it's happening
                if s.get("Text") and s.get("Text") != "none":
                    parts.append(f"Currently:{s.get('Text')} (S:{s.get('Scale', 'N/A')})")
            
                # Only show blackout if it's not "none" or scale is not 0
                if r.get("Text") and r.get("Text") != "none" and r.get("Scale") not in [None, "0", 0]:
                    parts.append(f"RF Blackout:{r.get('Text')} (R:{r.get('Scale', 'N/A')})")
            
                return "\n".join(parts)

            output = []
            #output.append(format_entry("Latest Observed", latest_entry))
            output.append(format_entry("24hrMax:", max_g_today))
            output.append(format_entry("Predicted:", predicted_g))
            return "\n".join(output)
        else:
            logger.error("Error fetching NOAA scales")
            return None
    except Exception as e:
        logger.error(f"Error fetching NOAA scales: {e}")
        return None

def get_sun(lat=0, lon=0):
    # get sunrise and sunset times using callers location or default
    obs = ephem.Observer()
    obs.date = datetime.now(timezone.utc)
    sun = ephem.Sun()
    if lat != 0 and lon != 0:
        obs.lat = str(lat)
        obs.lon = str(lon)
    else:
        obs.lat = str(latitudeValue)
        obs.lon = str(longitudeValue)

    sun.compute(obs)
    sun_table = {}

    # get the sun azimuth and altitude
    sun_table['azimuth'] = sun.az
    sun_table['altitude'] = sun.alt

    # sun is up include altitude
    if sun_table['altitude'] > 0:
        sun_table['altitude'] = sun.alt
    else:
        sun_table['altitude'] = 0

    # get the next rise and set times
    local_sunrise = ephem.localtime(obs.next_rising(sun))
    local_sunset = ephem.localtime(obs.next_setting(sun))
    if zuluTime:
        sun_table['rise_time'] = local_sunrise.strftime('%a %d %H:%M')
        sun_table['set_time'] = local_sunset.strftime('%a %d %H:%M')
    else:
        sun_table['rise_time'] = local_sunrise.strftime('%a %d %I:%M%p')
        sun_table['set_time'] = local_sunset.strftime('%a %d %I:%M%p')
    
    # if sunset is before sunrise, then data will be for tomorrow format sunset first and sunrise second
    if local_sunset < local_sunrise:
        sun_data = "SunSet: " + sun_table['set_time'] + "\nRise: " + sun_table['rise_time']
    else:
        sun_data = "SunRise: " + sun_table['rise_time'] + "\nSet: " + sun_table['set_time']

    sun_data += "\nDaylight: " + str((local_sunset - local_sunrise).seconds // 3600) + "h " + str(((local_sunset - local_sunrise).seconds // 60) % 60) + "m"
    
    if sun_table['altitude'] > 0:
        sun_data += "\nRemaining: " + str((local_sunset - datetime.now()).seconds // 3600) + "h " + str(((local_sunset - datetime.now()).seconds // 60) % 60) + "m"
    
    sun_data += "\nAzimuth: " + str('{0:.2f}'.format(sun_table['azimuth'] * 180 / ephem.pi)) + "°"
    if sun_table['altitude'] > 0:
        sun_data += "\nAltitude: " + str('{0:.2f}'.format(sun_table['altitude'] * 180 / ephem.pi)) + "°"
    return sun_data

def get_moon(lat=0, lon=0):
    # get moon phase and rise/set times using callers location or default
    obs = ephem.Observer()
    moon = ephem.Moon()
    if lat != 0 and lon != 0:
        obs.lat = str(lat)
        obs.lon = str(lon)
    else:
        obs.lat = str(latitudeValue)
        obs.lon = str(longitudeValue)
    
    obs.date = datetime.now(timezone.utc)
    moon.compute(obs)
    moon_table = {}
    illum = moon.phase  # 0 = new, 50 = first/last quarter, 100 = full
    
    if illum < 1.0:
        moon_phase = 'New Moon🌑'
    elif illum < 49:
        moon_phase = 'Waxing Crescent 🌒'
    elif 49 <= illum < 51:
        moon_phase = 'First Quarter 🌓'
    elif illum < 99:
        moon_phase = 'Waxing Gibbous 🌔'
    elif illum >= 99:
        moon_phase = 'Full Moon🌕'
    elif illum > 51:
        moon_phase = 'Waning Gibbous 🌖'
    elif 51 >= illum > 49:
        moon_phase = 'Last Quarter 🌗'
    else:
        moon_phase = 'Waning Crescent 🌘'
    
    moon_table['phase'] = moon_phase
    moon_table['illumination'] = moon.phase
    moon_table['azimuth'] = moon.az
    moon_table['altitude'] = moon.alt

    local_moonrise = ephem.localtime(obs.next_rising(moon))
    local_moonset = ephem.localtime(obs.next_setting(moon))
    if zuluTime:
        moon_table['rise_time'] = local_moonrise.strftime('%a %d %H:%M')
        moon_table['set_time'] = local_moonset.strftime('%a %d %H:%M')
    else:
        moon_table['rise_time'] = local_moonrise.strftime('%a %d %I:%M%p')
        moon_table['set_time'] = local_moonset.strftime('%a %d %I:%M%p')

    local_next_full_moon = ephem.localtime(ephem.next_full_moon((obs.date)))
    local_next_new_moon = ephem.localtime(ephem.next_new_moon((obs.date)))
    if zuluTime:
        moon_table['next_full_moon'] = local_next_full_moon.strftime('%a %b %d %H:%M')
        moon_table['next_new_moon'] = local_next_new_moon.strftime('%a %b %d %H:%M')
    else:
        moon_table['next_full_moon'] = local_next_full_moon.strftime('%a %b %d %I:%M%p')
        moon_table['next_new_moon'] = local_next_new_moon.strftime('%a %b %d %I:%M%p')

    moon_data = "MoonRise: " + moon_table['rise_time'] + "\nSet: " + moon_table['set_time'] + \
        "\nPhase: " + moon_table['phase'] + " @: " + str('{0:.2f}'.format(moon_table['illumination'])) + "%" \
        + "\nFullMoon: " + moon_table['next_full_moon'] + "\nNewMoon: " + moon_table['next_new_moon']
    
    # if moon is in the sky, add azimuth and altitude
    if moon_table['altitude'] > 0:
        moon_data += "\nAz: " + str('{0:.2f}'.format(moon_table['azimuth'] * 180 / ephem.pi)) + "°" + \
            "\nAlt: " + str('{0:.2f}'.format(moon_table['altitude'] * 180 / ephem.pi)) + "°"
    
    return moon_data

def getNextSatellitePass(satellite, lat=0, lon=0):
    pass_data = ''
    # get the next satellite pass for a given satellite
    visualPassAPI = "https://api.n2yo.com/rest/v1/satellite/visualpasses/"
    if lat == 0 and lon == 0:
        lat = latitudeValue
        lon = longitudeValue
    # API URL
    if n2yoAPIKey == '':
        logger.error("System: Missing API key free at https://www.n2yo.com/login/")
        return "not configured, bug your sysop"
    url = visualPassAPI + str(satellite) + "/" + str(lat) + "/" + str(lon) + "/0/2/300/" + "&apiKey=" + n2yoAPIKey
    # get the next pass data
    try:
        if not int(satellite):
            raise Exception("Invalid satellite number")
        next_pass_data = requests.get(url, timeout=urlTimeoutSeconds)
        if(next_pass_data.ok):
            pass_json = next_pass_data.json()
            if 'info' in pass_json and 'passescount' in pass_json['info'] and pass_json['info']['passescount'] > 0:
                satname = pass_json['info']['satname']
                pass_time = pass_json['passes'][0]['startUTC']
                pass_duration = pass_json['passes'][0]['duration']
                pass_maxEl = pass_json['passes'][0]['maxEl']
                pass_rise_time = datetime.fromtimestamp(pass_time).strftime('%a %d %I:%M%p')
                pass_startAzCompass = pass_json['passes'][0]['startAzCompass']
                pass_set_time = datetime.fromtimestamp(pass_time + pass_duration).strftime('%a %d %I:%M%p')
                pass__endAzCompass = pass_json['passes'][0]['endAzCompass']
                pass_data = f"{satname} @{pass_rise_time} Az: {pass_startAzCompass} for{getPrettyTime(pass_duration)}, MaxEl: {pass_maxEl}° Set @{pass_set_time} Az: {pass__endAzCompass}"
            elif pass_json['info']['passescount'] == 0:
                satname = pass_json['info']['satname']
                pass_data = f"{satname} has no upcoming passes"
        else:
            logger.error(f"System: Error fetching satellite pass data {satellite}")
            pass_data = ERROR_FETCHING_DATA
    except Exception as e:
        logger.warning(f"System: User supplied value {satellite} unknown or invalid")
        pass_data = "Provide NORAD# example use: 🛰️satpass 25544,33591"
    return pass_data

def measureHeight(lat=0, lon=0, shadow=0):
    # measure height of a given location using sun angle and shadow length
    if lat == 0 and lon == 0:
        return NO_DATA_NOGPS
    if shadow == 0:
        return NO_ALERTS
    obs = ephem.Observer()
    obs.lat = str(lat)
    obs.lon = str(lon)
    obs.date = datetime.now(timezone.utc)
    sun = ephem.Sun()
    sun.compute(obs)
    sun_altitude = sun.alt * 180 / ephem.pi
    if sun_altitude <= 0:
        return "☀️Sun is below horizon, I dont belive your shadow measurement"
    try:
        if use_metric:
            height = float(shadow) * math.tan(sun.alt)
            return f"📏Object Height: {height:.2f} m (Shadow: {shadow} m, 📐Sun Alt: {sun_altitude:.2f}°)"
        else:
            # Assume shadow is in feet if imperial, otherwise convert from meters to feet
            shadow_ft = float(shadow)
            height_ft = shadow_ft * math.tan(sun.alt)
            return f"📏Object Height: {height_ft:.2f} ft (Shadow: {shadow_ft} ft, 📐Sun Alt: {sun_altitude:.2f}°)"
    except Exception as e:
        logger.error(f"Space: Error calculating height: {e}")
        return NO_ALERTS