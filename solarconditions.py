# helper functions to get HF band conditions, DRAP X-ray flux, and sunrise/sunset times
# some code from https://github.com/Murturtle/MeshLink
# K7MHI Kelly Keeton 2024

import requests # pip install requests
import xml.dom.minidom
from datetime import datetime
import ephem # pip install pyephem

LATITUDE = 48.50
LONGITUDE = -123.0

def hf_band_conditions():
    hf_cond = ""
    band_cond = requests.get("https://www.hamqsl.com/solarxml.php", timeout=5)
    if(band_cond.ok):
        solarxml = xml.dom.minidom.parseString(band_cond.text)
        for i in solarxml.getElementsByTagName("band"):
            hf_cond += i.getAttribute("time")[0]+i.getAttribute("name") +"="+str(i.childNodes[0].data)+"\n"
    else:
        hf_cond += "error fetching"
    hf_cond = hf_cond[:-1] # remove the last newline
    return hf_cond

def solar_conditions():
    solar_cond = ""
    # get the solar conditions from the xml at "https://www.hamqsl.com/solarxml.php"
    solar_cond = requests.get("https://www.hamqsl.com/solarxml.php", timeout=5)
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
        solar_cond += "error fetching"
    return solar_cond

def drap_xray_conditions():
    drap_cond = ""
    drap_cond = requests.get("https://services.swpc.noaa.gov/text/drap_global_frequencies.txt", timeout=5)
    if(drap_cond.ok):
        drap_list = drap_cond.text.split('\n')
        x_filter = '#  X-RAY Message :'
        for line in drap_list:
            if x_filter in line:
                xray_flux = line.split(": ")[1]
    else:
        xray_flux += "error fetching"
    return xray_flux

# def get_sunrise_sunset(lat=0, lon=0):
#     from suntime import Sun, SunTimeException # pip install suntime
#     if lat != 0 and lon != 0:
#         sun = Sun(lat, lon)
#     else:
#         sun = Sun(LATITUDE, LONGITUDE)
        
#     to_zone = tz.tzlocal()
#     today_sr = sun.get_sunrise_time(datetime.now())
#     today_ss = sun.get_sunset_time(datetime.now())
#     if today_ss < today_sr: # if sunset is before sunrise, then it's tomorrow
#         today_ss = today_ss + timedelta(1)
#     todaysun = [today_sr.astimezone(to_zone).strftime('%a %d %I:%M'), today_ss.astimezone(to_zone).strftime('%a %d %I:%M')]
#     return todaysun

def get_sun(lat=0, lon=0):
    obs = ephem.Observer()
    obs.date = datetime.now()
    sun = ephem.Sun()
    if lat != 0 and lon != 0:
        obs.lat = str(lat)
        obs.lon = str(lon)
    else:
        obs.lat = str(LATITUDE)
        obs.lon = str(LONGITUDE)

    sun.compute(obs)
    sun_table = {}
    sun_table['azimuth'] = sun.az
    sun_table['altitude'] = sun.alt

    # get the next rise and set times
    local_sunrise = ephem.localtime(obs.next_rising(sun))
    local_sunset = ephem.localtime(obs.next_setting(sun))
    sun_table['rise_time'] = local_sunrise.strftime('%a %d %I:%M')
    sun_table['set_time'] = local_sunset.strftime('%a %d %I:%M')
    sun_data = f"Sun Rise: " + sun_table['rise_time'] + "\nSet: " + sun_table['set_time']
    return sun_data

def get_moon(lat=0, lon=0):
    obs = ephem.Observer()
    moon = ephem.Moon()
    if lat != 0 and lon != 0:
        obs.lat = str(lat)
        obs.lon = str(lon)
    else:
        obs.lat = str(LATITUDE)
        obs.lon = str(LONGITUDE)
    
    obs.date = datetime.now()
    moon.compute(obs)
    moon_table = {}
    moon_phase = ['New Moon', 'Waxing Crescent', 'First Quarter', 'Waxing Gibbous', 'Full Moon', 'Waning Gibbous', 'Last Quarter', 'Waning Crescent'][round(moon.phase / (2 * ephem.pi) * 8) % 8]
    moon_table['phase'] = moon_phase
    moon_table['illumination'] = moon.phase
    moon_table['azimuth'] = moon.az
    moon_table['altitude'] = moon.alt

    local_moonrise = ephem.localtime(obs.next_rising(moon))
    local_moonset = ephem.localtime(obs.next_setting(moon))
    moon_table['rise_time'] = local_moonrise.strftime('%a %d %I:%M%p')
    moon_table['set_time'] = local_moonset.strftime('%a %d %I:%M%p')

    local_next_full_moon = ephem.localtime(ephem.next_full_moon((obs.date)))
    local_next_new_moon = ephem.localtime(ephem.next_new_moon((obs.date)))
    moon_table['next_full_moon'] = local_next_full_moon.strftime('%a %b %d %I:%M%p')
    moon_table['next_new_moon'] = local_next_new_moon.strftime('%a %b %d %I:%M%p')

    moon_data = f"Moon Rise:" + moon_table['rise_time'] + "\nSet:" + moon_table['set_time'] + \
        "\nMoon Phase:" + moon_table['phase'] + " @:" + str('{0:.2f}'.format(moon_table['illumination'])) + "%" \
        + "\nNext Full Moon:" + moon_table['next_full_moon'] + "\nNext New Moon:" + moon_table['next_new_moon']
    
    return moon_data