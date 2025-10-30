# meshing around with hamlib as a source for info to send to mesh network
# detect signal strength and frequency of active channel if appears to be in use send to mesh network
# depends on rigctld running externally as a network service
# also can use VOX detection with a microphone and vosk speech to text to send voice messages to mesh network
# requires vosk and sounddevice python modules. will auto download needed. more from https://alphacephei.com/vosk/models and unpack
# 2025 Kelly Keeton K7MHI

# WSJT-X and JS8Call UDP Monitoring
# Based on WSJT-X UDP protocol specification
# Reference: https://github.com/ckuhtz/ham/blob/main/mcast/recv_decode.py


import asyncio
import socket
import struct
import json
from modules.log import logger

# verbose debug logging for trap words function
debugVoxTmsg = False

from modules.settings import (
    radio_detection_enabled,
    rigControlServerAddress,
    signalDetectionThreshold,
    signalHoldTime,
    signalCooldown,
    signalCycleLimit,
    voxDetectionEnabled,
    useLocalVoxModel,
    localVoxModelPath,
    voxLanguage,
    voxInputDevice,
    voxTrapList,
    voxOnTrapList,
    voxEnableCmd,
    ERROR_FETCHING_DATA,
    meshagesTTS,
)

# module global variables
previousStrength = -40
signalCycle = 0

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

# --- WSJT-X and JS8Call Settings Initialization ---
wsjtxMsgQueue = []  # Queue for WSJT-X detected messages
js8callMsgQueue = []  # Queue for JS8Call detected messages
wsjtx_enabled = False
js8call_enabled = False
wsjtx_udp_port = 2237
js8call_udp_port = 2442
watched_callsigns = []
wsjtx_udp_address = '127.0.0.1'
js8call_tcp_address = '127.0.0.1'
js8call_tcp_port = 2442
# WSJT-X UDP Protocol Message Types
WSJTX_HEARTBEAT = 0
WSJTX_STATUS = 1
WSJTX_DECODE = 2
WSJTX_CLEAR = 3
WSJTX_REPLY = 4
WSJTX_QSO_LOGGED = 5
WSJTX_CLOSE = 6
WSJTX_REPLAY = 7
WSJTX_HALT_TX = 8
WSJTX_FREE_TEXT = 9
WSJTX_WSPR_DECODE = 10
WSJTX_LOCATION = 11
WSJTX_LOGGED_ADIF = 12


try:
    from modules.settings import (
        wsjtx_detection_enabled,
        wsjtx_udp_server_address,
        wsjtx_watched_callsigns,
        js8call_detection_enabled,
        js8call_server_address,
        js8call_watched_callsigns
    )
    wsjtx_enabled = wsjtx_detection_enabled
    js8call_enabled = js8call_detection_enabled

    # Use a local list to collect callsigns before assigning to watched_callsigns
    callsigns = []

    if wsjtx_enabled:
        if ':' in wsjtx_udp_server_address:
            wsjtx_udp_address, port_str = wsjtx_udp_server_address.split(':')
            wsjtx_udp_port = int(port_str)
        if wsjtx_watched_callsigns:
            callsigns.extend([cs.strip() for cs in wsjtx_watched_callsigns.split(',') if cs.strip()])

    if js8call_enabled:
        if ':' in js8call_server_address:
            js8call_tcp_address, port_str = js8call_server_address.split(':')
            js8call_tcp_port = int(port_str)
        if js8call_watched_callsigns:
            callsigns.extend([cs.strip() for cs in js8call_watched_callsigns.split(',') if cs.strip()])

    # Clean up and deduplicate callsigns, uppercase for matching
    watched_callsigns = list({cs.upper() for cs in callsigns})

except ImportError:
    logger.debug("System: RadioMon: WSJT-X/JS8Call settings not configured")
except Exception as e:
    logger.warning(f"System: RadioMon: Error loading WSJT-X/JS8Call settings: {e}")


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
        "daylight": handle_sun,
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
        print(f"System: RadioMon: Error importing VOX dependencies: {e}")
        print(f"To use VOX detection please install the vosk and sounddevice python modules")
        print(f"pip install vosk sounddevice")
        print(f"sounddevice needs pulseaudio,  apt-get install portaudio19-dev")
        voxDetectionEnabled = False
        logger.error(f"System: RadioMon: VOX detection disabled due to import error")

if meshagesTTS:
    try:
        # TTS for meshages imports
        logger.debug("System: RadioMon: Initializing TTS model for audible meshages")
        import sounddevice as sd
        from kittentts import KittenTTS
        ttsModel = KittenTTS("KittenML/kitten-tts-nano-0.2")
        available_voices = [
            'expr-voice-2-m', 'expr-voice-2-f', 'expr-voice-3-m', 'expr-voice-3-f',
            'expr-voice-4-m', 'expr-voice-4-f', 'expr-voice-5-m', 'expr-voice-5-f'
        ]
    except Exception as e:
        logger.error(f"To use Meshages TTS please review the radio.md documentation for setup instructions.")
        meshagesTTS = False

async def generate_and_play_tts(text, voice, samplerate=24000):
    """Async: Generate speech and play audio."""
    text = text.strip()
    if not text:
        return
    try:
        logger.debug(f"System: RadioMon: Generating TTS for text: {text} with voice: {voice}")
        audio = await asyncio.to_thread(ttsModel.generate, text, voice=voice)
        if audio is None or len(audio) == 0:
            return
        await asyncio.to_thread(sd.play, audio, samplerate)
        await asyncio.to_thread(sd.wait)
        del audio
    except Exception as e:
        logger.warning(f"System: RadioMon: Error in generate_and_play_tts: {e}")

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
    if "socket" not in globals():
        logger.warning("System: RadioMon: 'socket' module not imported. Hamlib disabled.")
        return ERROR_FETCHING_DATA
    try:
        rigControlSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        rigControlSocket.settimeout(2)
        rigControlSocket.connect((rigControlServerAddress.split(":")[0],int(rigControlServerAddress.split(":")[1])))
    except Exception as e:
        logger.error(f"System: RadioMon: Error connecting to rigctld: {e}")
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
        logger.error(f"System: RadioMon: Error fetching data from rigctld: {e}")
        return ERROR_FETCHING_DATA
    
def get_sig_strength():
    strength = get_hamlib('l STRENGTH')
    return strength

def checkVoxTrapWords(text):
    try:
        if not voxOnTrapList:
            logger.debug(f"System: RadioMon: VOX detected: {text}")
            return text
        if text:
            traps = [voxTrapList] if isinstance(voxTrapList, str) else voxTrapList
            text_lower = text.lower()
            for trap in traps:
                trap_clean = trap.strip()
                trap_lower = trap_clean.lower()
                idx = text_lower.find(trap_lower)
                if debugVoxTmsg:
                    logger.debug(f"System: RadioMon: VOX checking for trap word '{trap_lower}' in: '{text}' (index: {idx})")
                if idx != -1:
                    new_text = text[idx + len(trap_clean):].strip()
                    if debugVoxTmsg:
                        logger.debug(f"System: RadioMon: VOX detected trap word '{trap_lower}' in: '{text}' (remaining: '{new_text}')")
                    new_words = new_text.split()
                    if voxEnableCmd:
                        for word in new_words:
                            if word in botMethods:
                                logger.info(f"System: RadioMon: VOX action '{word}' with '{new_text}'")
                                if word == "joke":
                                    return botMethods[word](vox=True)
                                else:
                                    return botMethods[word](None, None, None, vox=True)
                    logger.debug(f"System: RadioMon: VOX returning text after trap word '{trap_lower}': '{new_text}'")
                    return new_text
            if debugVoxTmsg:
                logger.debug(f"System: RadioMon: VOX no trap word found in: '{text}'")
        return None
    except Exception as e:
        logger.debug(f"System: RadioMon: Error in checkVoxTrapWords: {e}")
        return None

async def signalWatcher():
    global previousStrength
    global signalCycle
    try:
        signalStrength = int(get_sig_strength())
        if signalStrength >= previousStrength and signalStrength > signalDetectionThreshold:
            message = f"Detected {get_freq_common_name(get_hamlib('f'))} active. S-Meter:{signalStrength}dBm"
            logger.debug(f"System: RadioMon: {message}. Waiting for {signalHoldTime} seconds")
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

async def make_vox_callback(loop, q):
    def vox_callback(indata, frames, time, status):
        if status:
            logger.warning(f"System: RadioMon: VOX input status: {status}")
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
                logger.debug("System: RadioMon: VOX queue full, dropping audio frame")
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
        logger.debug(f"System: RadioMon: VOX monitor started on device {device_info['name']} with samplerate {samplerate} using trap words: {voxTrapList if voxOnTrapList else 'none'}")
        rec = KaldiRecognizer(model, samplerate)
        loop = asyncio.get_running_loop()
        callback = await make_vox_callback(loop, q)
        with sd.RawInputStream(
            device=voxInputDevice,
            samplerate=samplerate,
            blocksize=4000,
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
        logger.warning(f"System: RadioMon: Error in VOX monitor: {e}")

def decode_wsjtx_packet(data):
    """Decode WSJT-X UDP packet according to the protocol specification"""
    try:
        # WSJT-X uses Qt's QDataStream format (big-endian)
        magic = struct.unpack('>I', data[0:4])[0]
        if magic != 0xADBCCBDA:
            return None
        
        schema_version = struct.unpack('>I', data[4:8])[0]
        msg_type = struct.unpack('>I', data[8:12])[0]
        
        offset = 12
        
        # Helper to read Qt QString (4-byte length + UTF-8 data)
        def read_qstring(data, offset):
            if offset + 4 > len(data):
                return "", offset
            length = struct.unpack('>I', data[offset:offset+4])[0]
            offset += 4
            if length == 0xFFFFFFFF:  # Null string
                return "", offset
            if offset + length > len(data):
                return "", offset
            text = data[offset:offset+length].decode('utf-8', errors='ignore')
            return text, offset + length
        
        # Decode DECODE message (type 2)
        if msg_type == WSJTX_DECODE:
            # Read fields according to WSJT-X protocol
            wsjtx_id, offset = read_qstring(data, offset)
            
            # Read other decode fields: new, time, snr, delta_time, delta_frequency, mode, message
            if offset + 1 > len(data):
                return None
            new = struct.unpack('>?', data[offset:offset+1])[0]
            offset += 1
            
            if offset + 4 > len(data):
                return None
            time_val = struct.unpack('>I', data[offset:offset+4])[0]
            offset += 4
            
            if offset + 4 > len(data):
                return None
            snr = struct.unpack('>i', data[offset:offset+4])[0]
            offset += 4
            
            if offset + 8 > len(data):
                return None
            delta_time = struct.unpack('>d', data[offset:offset+8])[0]
            offset += 8
            
            if offset + 4 > len(data):
                return None
            delta_frequency = struct.unpack('>I', data[offset:offset+4])[0]
            offset += 4
            
            mode, offset = read_qstring(data, offset)
            message, offset = read_qstring(data, offset)
            
            return {
                'type': 'decode',
                'id': wsjtx_id,
                'new': new,
                'time': time_val,
                'snr': snr,
                'delta_time': delta_time,
                'delta_frequency': delta_frequency,
                'mode': mode,
                'message': message
            }
        
        # Decode QSO_LOGGED message (type 5)
        elif msg_type == WSJTX_QSO_LOGGED:
            wsjtx_id, offset = read_qstring(data, offset)
            
            # Read QSO logged fields
            if offset + 8 > len(data):
                return None
            date_off = struct.unpack('>Q', data[offset:offset+8])[0]
            offset += 8
            
            if offset + 8 > len(data):
                return None
            time_off = struct.unpack('>Q', data[offset:offset+8])[0]
            offset += 8
            
            dx_call, offset = read_qstring(data, offset)
            dx_grid, offset = read_qstring(data, offset)
            
            return {
                'type': 'qso_logged',
                'id': wsjtx_id,
                'dx_call': dx_call,
                'dx_grid': dx_grid
            }
            
        return None
        
    except Exception as e:
        logger.debug(f"System: RadioMon: Error decoding WSJT-X packet: {e}")
        return None

def check_callsign_match(message, callsigns):
    """Check if any watched callsign appears in the message
    
    Uses word boundary matching to avoid false positives like matching
    'K7' when looking for 'K7MHI'. Callsigns are expected to be
    separated by spaces or be at the start/end of the message.
    """
    if not callsigns:
        return True  # If no filter, accept all
    
    message_upper = message.upper()
    # Split message into words for exact matching
    words = message_upper.split()
    
    for callsign in callsigns:
        callsign_upper = callsign.upper()
        # Pre-compute patterns for portable/mobile suffixes
        callsign_with_slash = callsign_upper + '/'
        callsign_with_dash = callsign_upper + '-'
        slash_callsign = '/' + callsign_upper
        dash_callsign = '-' + callsign_upper
        
        # Check if callsign appears as a complete word
        if callsign_upper in words:
            return True
        
        # Check for callsigns in compound forms like "K7MHI/P" or "K7MHI-7"
        for word in words:
            if (word.startswith(callsign_with_slash) or 
                word.startswith(callsign_with_dash) or
                word.endswith(slash_callsign) or 
                word.endswith(dash_callsign)):
                return True
    
    return False

async def wsjtxMonitor():
    """Monitor WSJT-X UDP broadcasts for decode messages"""
    if not wsjtx_enabled:
        logger.warning("System: RadioMon: WSJT-X monitoring called but not enabled")
        return
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((wsjtx_udp_address, wsjtx_udp_port))
        sock.setblocking(False)
        
        logger.info(f"System: RadioMon: WSJT-X UDP listener started on {wsjtx_udp_address}:{wsjtx_udp_port}")
        if watched_callsigns:
            logger.info(f"System: RadioMon: Watching for callsigns: {', '.join(watched_callsigns)}")
        
        while True:
            try:
                data, addr = sock.recvfrom(4096)
                decoded = decode_wsjtx_packet(data)
                
                if decoded and decoded['type'] == 'decode':
                    message = decoded['message']
                    mode = decoded['mode']
                    snr = decoded['snr']
                    
                    # Check if message contains watched callsigns
                    if check_callsign_match(message, watched_callsigns):
                        msg_text = f"WSJT-X {mode}: {message} (SNR: {snr:+d}dB)"
                        logger.info(f"System: RadioMon: {msg_text}")
                        wsjtxMsgQueue.append(msg_text)
                        
            except BlockingIOError:
                # No data available
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.debug(f"System: RadioMon: Error in WSJT-X monitor loop: {e}")
                await asyncio.sleep(1)
                
    except Exception as e:
        logger.warning(f"System: RadioMon: Error starting WSJT-X monitor: {e}")

async def js8callMonitor():
    """Monitor JS8Call TCP API for messages"""
    if not js8call_enabled:
        logger.warning("System: RadioMon: JS8Call monitoring called but not enabled")
        return
    
    try:
        logger.info(f"System: RadioMon: JS8Call TCP listener connecting to {js8call_tcp_address}:{js8call_tcp_port}")
        if watched_callsigns:
            logger.info(f"System: RadioMon: Watching for callsigns: {', '.join(watched_callsigns)}")
        
        while True:
            try:
                # Connect to JS8Call TCP API
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect((js8call_tcp_address, js8call_tcp_port))
                sock.setblocking(False)
                
                logger.info("System: RadioMon: Connected to JS8Call API")
                
                buffer = ""
                while True:
                    try:
                        data = sock.recv(4096)
                        if not data:
                            logger.warning("System: RadioMon: JS8Call connection closed")
                            break
                        
                        buffer += data.decode('utf-8', errors='ignore')
                        
                        # Process complete JSON messages (newline delimited)
                        while '\n' in buffer:
                            line, buffer = buffer.split('\n', 1)
                            if not line.strip():
                                continue
                                
                            try:
                                msg = json.loads(line)
                                msg_type = msg.get('type', '')
                                
                                # Handle RX.DIRECTED and RX.ACTIVITY messages
                                if msg_type in ['RX.DIRECTED', 'RX.ACTIVITY']:
                                    params = msg.get('params', {})
                                    text = params.get('TEXT', '')
                                    from_call = params.get('FROM', '')
                                    snr = params.get('SNR', 0)
                                    
                                    if text and check_callsign_match(text, watched_callsigns):
                                        msg_text = f"JS8Call from {from_call}: {text} (SNR: {snr:+d}dB)"
                                        logger.info(f"System: RadioMon: {msg_text}")
                                        js8callMsgQueue.append(msg_text)
                                        
                            except json.JSONDecodeError:
                                logger.debug(f"System: RadioMon: Invalid JSON from JS8Call: {line[:100]}")
                            except Exception as e:
                                logger.debug(f"System: RadioMon: Error processing JS8Call message: {e}")
                                
                    except BlockingIOError:
                        await asyncio.sleep(0.1)
                    except socket.timeout:
                        await asyncio.sleep(0.1)
                    except Exception as e:
                        logger.debug(f"System: RadioMon: Error in JS8Call receive loop: {e}")
                        break
                        
                sock.close()
                logger.warning("System: RadioMon: JS8Call connection lost, reconnecting in 5s...")
                await asyncio.sleep(5)
                
            except socket.timeout:
                logger.warning("System: RadioMon: JS8Call connection timeout, retrying in 5s...")
                await asyncio.sleep(5)
            except Exception as e:
                logger.warning(f"System: RadioMon: Error connecting to JS8Call: {e}")
                await asyncio.sleep(10)
                
    except Exception as e:
        logger.warning(f"System: RadioMon: Error starting JS8Call monitor: {e}")

# end of file
