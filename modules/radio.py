# meshing around with hamlib as a source for info to send to mesh network
# detect signal strength and frequency of active channel if appears to be in use send to mesh network
# depends on rigctld running externally as a network service
# 2024 Kelly Keeton K7MHI

import socket
import asyncio
from modules.settings import *

SIGNAL_DETECTION_THRESHOLD = -10 # dBm
SIGNAL_HOLD_TIME = 15 # seconds to hold on to signal before checking again
SIGNAL_COOLDOWN = 5 # seconds to wait between signal checks
SIGNAL_CYCLE_LIMIT = 6 # multiply by SIGNAL_COOLDOWN to get total time to wait before resetting signal strength

ERROR_FETCHING_DATA = "error fetching data"

def get_hamlib(msg="f"):
    try:
        rigControlSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        rigControlSocket.settimeout(2)
        rigControlSocket.connect((rigControlServerAddress.split(":")[0],int(rigControlServerAddress.split(":")[1])))
    except Exception as e:
        print(f"\nSystem: Error connecting to rigctld: {e}")
        return ERROR_FETCHING_DATA

    build_msg = f"{msg}\n"
    MESSAGE = bytes(build_msg, "utf-8")
    rigControlSocket.sendall(MESSAGE)
    # Look for the response
    data = rigControlSocket.recv(16)
    rigControlSocket.close()
    # strip newline and return
    data = data.replace(b'\n',b'')
    return data.decode("utf-8").rstrip()

def get_freq_common_name(freq):
    freq = int(freq)
    if freq == 462562500:
        return "GRMS CH1"
    elif freq == 462587500:
        return "GRMS CH2"
    elif freq == 462612500:
        return "GRMS CH3"
    elif freq == 462637500:
        return "GRMS CH4"
    elif freq == 462662500:
        return "GRMS CH5"
    elif freq == 462687500:
        return "GRMS CH6"
    elif freq == 462712500:
        return "GRMS CH7"
    elif freq == 462737500:
        return "GRMS CH8"
    elif freq == 462762500:
        return "GRMS CH9"
    elif freq == 462787500:
        return "GRMS CH10"
    elif freq == 462812500:
        return "GRMS CH11"
    elif freq == 462837500:
        return "GRMS CH12"
    elif freq == 462862500:
        return "GRMS CH13"
    elif freq == 462887500:
        return "GRMS CH14"
    elif freq == 462912500:
        return "GRMS CH15"
    elif freq == 462937500:
        return "GRMS CH16"
    elif freq == 462550000:
        return "FRS CH1"
    elif freq == 462575000:
        return "FRS CH2"
    elif freq == 462600000:
        return "FRS CH3"
    elif freq == 462625000:
        return "FRS CH4"
    elif freq == 462650000:
        return "FRS CH5"
    elif freq == 462675000:
        return "FRS CH6"
    elif freq == 462700000:
        return "FRS CH7"
    elif freq == 462725000:
        return "FRS CH8"
    elif freq == 462562500:
        return "FRS CH9"
    elif freq == 462587500:
        return "FRS CH10"
    elif freq == 462612500:
        return "FRS CH11"
    elif freq == 462637500:
        return "FRS CH12"
    elif freq == 462662500:
        return "FRS CH13"
    elif freq == 462687500:
        return "FRS CH14"
    elif freq == 462712500:
        return "FRS CH15"
    elif freq == 462737500:
        return "FRS CH16"
    elif freq == 146520000:
        return "2M Simplex Calling"
    else:
        #return Mhz
        freq = freq/1000000
        return f"{freq} Mhz"
    
def get_sig_strength():
    strength = get_hamlib('l STRENGTH')
    return strength

async def signalWatcher():
    global previousStrength
    global signalCycle
    try:
        signalStrength = int(get_sig_strength())
        if signalStrength >= previousStrength and signalStrength > SIGNAL_DETECTION_THRESHOLD:
            message = f"Detected {get_freq_common_name(get_hamlib('f'))} active use S:{signalStrength}"
            print (message)
            previousStrength = signalStrength
            signalCycle = 0
            await asyncio.sleep(SIGNAL_HOLD_TIME)
        else:
            signalCycle += 1
            if signalCycle >= SIGNAL_CYCLE_LIMIT:
                signalCycle = 0
                previousStrength = -40
            await asyncio.sleep(SIGNAL_COOLDOWN)
    except Exception as e:
        signalStrength = -40
        signalCycle = 0
        previousStrength = -40

# end of file