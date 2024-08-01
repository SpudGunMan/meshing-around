# meshing around with hamlib as a source for info to send to mesh network
# detect signal strength and frequency of active channel if appears to be in use send to mesh network
# depends on rigctld running externally as a network service
# 2024 Kelly Keeton K7MHI

import socket
import asyncio
from modules.settings import *

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
    elif freq == 467562500:
        return "GRMS CH8"
    elif freq == 467587500:
        return "GRMS CH9"
    elif freq == 467612500:
        return "GRMS CH10"
    elif freq == 467637500:
        return "GRMS CH11"
    elif freq == 467662500:
        return "GRMS CH12"
    elif freq == 467687500:
        return "GRMS CH13"
    elif freq == 467712500:
        return "GRMS CH14"
    elif freq == 467737500:
        return "GRMS CH15"
    elif freq == 462550000:
        return "GRMS CH16"
    elif freq == 462575000:
        return "GMRS CH17"
    elif freq == 462600000:
        return "GMRS CH18"
    elif freq == 462625000:
        return "GMRS CH19"
    elif freq == 462675000:
        return "GMRS CH20"
    elif freq == 462670000:
        return "GMRS CH21"
    elif freq == 462725000:
        return "GMRS CH22"
    elif freq == 462725500:
        return "GMRS CH23"
    elif freq == 467575000:
        return "GMRS CH24"
    elif freq == 467600000:
        return "GMRS CH25"
    elif freq == 467625000:
        return "GMRS CH26"
    elif freq == 467650000:
        return "GMRS CH27"
    elif freq == 467675000:
        return "GMRS CH28"
    elif freq == 467700000:
        return "FRS CH1"
    elif freq == 462575000:
        return "FRS CH2"
    elif freq == 462600000:
        return "FRS CH3"
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
    elif freq == 446000000:
        return "70cm Simplex Calling"
    elif freq == 156800000:
        return "Marine CH16"
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
        if signalStrength >= previousStrength and signalStrength > signalDetectionThreshold:
            message = f"Detected {get_freq_common_name(get_hamlib('f'))} active use S-Meter:{signalStrength}dBm"
            previousStrength = signalStrength
            signalCycle = 0
            await asyncio.sleep(signalHoldTime)
            return message
        else:
            signalCycle += 1
            if signalCycle >= signalCycleLimit:
                signalCycle = 0
                previousStrength = -40
            await asyncio.sleep(signalCooldown)
            return None
    except Exception as e:
        signalStrength = -40
        signalCycle = 0
        previousStrength = -40

# end of file