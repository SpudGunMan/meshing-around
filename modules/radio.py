# meshing around with hamlib as a source for info to send to mesh network
# detect signal strength and frequency of active channel if appears to be in use send to mesh network
# depends on rigctld running externally as a network service
# also can use VOX detection with a microphone and vosk speech to text to send voice messages to mesh network
# requires vosk and sounddevice python modules. will auto download needed. more from https://alphacephei.com/vosk/models and unpack
# 2024 Kelly Keeton K7MHI

from modules.log import *
import asyncio

# verbose debug logging for trap words function
debugVoxTmsg = False


if radio_detection_enabled:
    # used by hamlib detection
    import socket

if voxDetectionEnabled:
    # methods available for trap word processing, these can be called by VOX detection when trap words are detected
    from mesh_bot import tell_joke, handle_wxc, handle_moon, handle_sun, handle_riverFlow, handle_tide, handle_satpass
    botMethods = {
        "joke": tell_joke,
        "weather": handle_wxc,
        "moon": handle_moon,
        "sun": handle_sun,
        "river": handle_riverFlow,
        "tide": handle_tide,
        "satellite": handle_satpass}
    # module global variables
    previousVoxState = False
    voxHoldTime = signalHoldTime

    try:
        import sounddevice as sd # pip install sounddevice    sudo apt install portaudio19-dev
        from vosk import Model, KaldiRecognizer # pip install vosk
        import json
        q = asyncio.Queue(maxsize=32)  # queue for audio data
        
        if useLocalVoxModel:
            voxModel = Model(lang=localVoxModelPath) # use built in model for specified language
        else:
            voxModel = Model(lang=voxLanguage) # use built in model for specified language

    except Exception as e:
        print(f"RadioMon: Error importing VOX dependencies: {e}")
        print(f"To use VOX detection please install the vosk and sounddevice python modules")
        print(f"pip install vosk sounddevice")
        print(f"sounddevice needs pulseaudio,  apt-get install portaudio19-dev")
        voxDetectionEnabled = False
        logger.error(f"RadioMon: VOX detection disabled due to import error")

FREQ_NAME_MAP = {
    462562500: "GRMS CH1",
    462587500: "GRMS CH2",
    462612500: "GRMS CH3",
    462637500: "GRMS CH4",
    462662500: "GRMS CH5",
    462687500: "GRMS CH6",
    462712500: "GRMS CH7",
    467562500: "GRMS CH8",
    467587500: "GRMS CH9",
    467612500: "GRMS CH10",
    467637500: "GRMS CH11",
    467662500: "GRMS CH12",
    467687500: "GRMS CH13",
    467712500: "GRMS CH14",
    467737500: "GRMS CH15",
    462550000: "GRMS CH16",
    462575000: "GMRS CH17",
    462600000: "GMRS CH18",
    462625000: "GMRS CH19",
    462675000: "GMRS CH20",
    462670000: "GMRS CH21",
    462725000: "GMRS CH22",
    462725500: "GMRS CH23",
    467575000: "GMRS CH24",
    467600000: "GMRS CH25",
    467625000: "GMRS CH26",
    467650000: "GMRS CH27",
    467675000: "GMRS CH28",
    467700000: "FRS CH1",
    462650000: "FRS CH5",
    462700000: "FRS CH7",
    462737500: "FRS CH16",
    146520000: "2M Simplex Calling",
    446000000: "70cm Simplex Calling",
    156800000: "Marine CH16",
    # Add more as needed
}

def get_freq_common_name(freq):
    freq = int(freq)
    name = FREQ_NAME_MAP.get(freq)
    if name:
        return name
    else:
        # Return MHz if not found
        return f"{freq/1000000} Mhz"

def get_hamlib(msg="f"):
    # get data from rigctld server
    try:
        rigControlSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        rigControlSocket.settimeout(2)
        rigControlSocket.connect((rigControlServerAddress.split(":")[0],int(rigControlServerAddress.split(":")[1])))
    except Exception as e:
        logger.error(f"RadioMon: Error connecting to rigctld: {e}")
        return ERROR_FETCHING_DATA

    try:
        build_msg = f"{msg}\n"
        MESSAGE = bytes(build_msg, "utf-8")
        rigControlSocket.sendall(MESSAGE)
        # Look for the response
        data = rigControlSocket.recv(16)
        rigControlSocket.close()
        # strip newline and return
        data = data.replace(b'\n',b'')
        return data.decode("utf-8").rstrip()
    except Exception as e:
        logger.error(f"RadioMon: Error fetching data from rigctld: {e}")
        return ERROR_FETCHING_DATA
    
def get_sig_strength():
    strength = get_hamlib('l STRENGTH')
    return strength

# def vox_callback(indata, frames, time, status):
#     if status:
#         logger.warning(f"RadioMon: VOX input status: {status}")
#     q.put(bytes(indata))
def checkVoxTrapWords(text):
    try:
        if not voxOnTrapList:
            logger.debug(f"RadioMon: VOX detected: {text}")
            return text
        if text:
            traps = [voxTrapList] if isinstance(voxTrapList, str) else voxTrapList
            text_lower = text.lower()
            for trap in traps:
                trap_clean = trap.strip()
                trap_lower = trap_clean.lower()
                idx = text_lower.find(trap_lower)
                if idx != -1:
                    new_text = text[idx + len(trap_clean):].strip()
                    logger.debug(f"RadioMon: VOX detected trap word '{trap_lower}' in: '{text}' (remaining: '{new_text}')")
                    new_words = new_text.split()
                    if voxEnableCmd:
                        for word in new_words:
                            if word in botMethods:
                                logger.info(f"RadioMon: VOX action '{word}' with '{new_text}'")
                                return botMethods[word](None, None, None, vox=True)
                    logger.debug(f"RadioMon: VOX returning text after trap word '{trap_lower}': '{new_text}'")
                    return new_text
            logger.debug(f"RadioMon: VOX no trap word found in: '{text}'")
        return None
    except Exception as e:
        logger.debug(f"RadioMon: Error in checkVoxTrapWords: {e}")
        return None

async def signalWatcher():
    global previousStrength
    global signalCycle
    try:
        signalStrength = int(get_sig_strength())
        if signalStrength >= previousStrength and signalStrength > signalDetectionThreshold:
            message = f"Detected {get_freq_common_name(get_hamlib('f'))} active. S-Meter:{signalStrength}dBm"
            logger.debug(f"RadioMon: {message}. Waiting for {signalHoldTime} seconds")
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

def make_vox_callback(loop, q):
    def vox_callback(indata, frames, time, status):
        if status:
            logger.warning(f"RadioMon: VOX input status: {status}")
        try:
            loop.call_soon_threadsafe(q.put_nowait, bytes(indata))
        except asyncio.QueueFull:
            # Drop the oldest item and add the new one
            try:
                q.get_nowait()  # Remove oldest
            except asyncio.QueueEmpty:
                pass
            try:
                loop.call_soon_threadsafe(q.put_nowait, bytes(indata))
            except asyncio.QueueFull:
                # If still full, just drop this frame
                logger.debug("RadioMon: VOX queue full, dropping audio frame")
        except RuntimeError:
            # Loop may be closed
            pass
    return vox_callback
 
async def voxMonitor():
    global previousVoxState, voxMsgQueue
    try:
        model = voxModel
        device_info = sd.query_devices(voxInputDevice, 'input')
        samplerate = 16000
        logger.debug(f"RadioMon: VOX monitor started on device {device_info['name']} with samplerate {samplerate} using trap words: {voxTrapList if voxOnTrapList else 'none'}")
        rec = KaldiRecognizer(model, samplerate)
        loop = asyncio.get_running_loop()
        callback = make_vox_callback(loop, q)
        with sd.RawInputStream(
            device=voxInputDevice,
            samplerate=samplerate,
            blocksize=8000,
            dtype='int16',
            channels=1,
            callback=callback
        ):
            while True:
                data = await q.get()
                if rec.AcceptWaveform(data):
                    result = rec.Result()
                    text = json.loads(result).get("text", "")
                    # process text
                    if text and text != 'huh':
                        result = checkVoxTrapWords(text)
                        if result:
                            # If result is a function return, handle it (send to mesh, log, etc.)
                            # If it's just text, handle as a normal message
                            voxMsgQueue.append(result)

                await asyncio.sleep(0.1)
    except Exception as e:
        logger.error(f"RadioMon: Error in VOX monitor: {e}")

# end of file
