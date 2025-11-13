#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# icad_tone.py - uses icad_tone_detection, for fire and EMS tone detection
# https://github.com/thegreatcodeholio/icad_tone_detection
# output to alert.txt for meshing-around bot
# 2025 K7MHI Kelly Keeton

# ---------------------------
# User Configuration Section
# ---------------------------
ALERT_FILE_PATH = "alert.txt"   # Path to alert log file, or None to disable logging
AUDIO_SOURCE = "soundcard"      # "soundcard" for mic/line-in, "http" for stream
HTTP_STREAM_URL = ""            # Set to your stream URL if using "http"
SAMPLE_RATE = 16000             # Audio sample rate (Hz)
INPUT_CHANNELS = 1              # Number of input channels (1=mono)
MIN_SAMPLES = 4096              # Minimum samples per detection window (increase for better accuracy)
STREAM_BUFFER = 32000           # Number of bytes to buffer before detection (for MP3 streams)
INPUT_DEVICE = 0             # Set to device index or name, or None for default
# ---------------------------

import sys
import time
from icad_tone_detection import tone_detect
from pydub import AudioSegment
import requests
import sounddevice as sd
import numpy as np
import argparse
import io
import warnings
warnings.filterwarnings("ignore", message="nperseg = .* is greater than input length")
def write_alert(message):
    if ALERT_FILE_PATH:
        try:
            with open(ALERT_FILE_PATH, "w") as f: # overwrite each time
                f.write(message + "\n")
        except Exception as e:
            print(f"Error writing to alert file: {e}", file=sys.stderr)

def detect_and_alert(audio_data, sample_rate):
    try:
        result = tone_detect(audio_data, sample_rate)
    except Exception as e:
        print(f"Detection error: {e}", file=sys.stderr)
        return
    # Only print if something is detected
    if result and any(getattr(result, t, []) for t in [
        "two_tone_result", "long_result", "hi_low_result", "pulsed_result", "mdc_result", "dtmf_result"
    ]):
        print("Raw detection result:", result)
        # Prepare alert summary for all relevant tone types
        summary = []
        if hasattr(result, "dtmf_result") and result.dtmf_result:
            for dtmf in result.dtmf_result:
                summary.append(f"DTMF Digit: {dtmf.get('digit', '?')} | Duration: {dtmf.get('length', '?')}s")
        if hasattr(result, "hi_low_result") and result.hi_low_result:
            for hl in result.hi_low_result:
                summary.append(
                    f"Hi/Low Alternations: {hl.get('alternations', '?')} | Duration: {hl.get('length', '?')}s"
                )
        if hasattr(result, "mdc_result") and result.mdc_result:
            for mdc in result.mdc_result:
                summary.append(
                    f"MDC UnitID: {mdc.get('unitID', '?')} | Op: {mdc.get('op', '?')} | Duration: {mdc.get('length', '?')}s"
                )
        if hasattr(result, "pulsed_result") and result.pulsed_result:
            for pl in result.pulsed_result:
                summary.append(
                    f"Pulsed Tone: {pl.get('detected', '?')}Hz | Cycles: {pl.get('cycles', '?')} | Duration: {pl.get('length', '?')}s"
                )
        if hasattr(result, "two_tone_result") and result.two_tone_result:
            for tt in result.two_tone_result:
                summary.append(
                    f"Two-Tone: {tt.get('detected', ['?','?'])[0]}Hz/{tt.get('detected', ['?','?'])[1]}Hz | Tone A: {tt.get('tone_a_length', '?')}s | Tone B: {tt.get('tone_b_length', '?')}s"
                )
        if hasattr(result, "long_result") and result.long_result:
            for lt in result.long_result:
                summary.append(
                    f"Long Tone: {lt.get('detected', '?')}Hz | Duration: {lt.get('length', '?')}s"
                )
        if summary:
            write_alert("\n".join(summary))

def get_supported_sample_rate(device, channels=1):
    # Try common sample rates
    for rate in [44100, 48000, 16000, 8000]:
        try:
            sd.check_input_settings(device=device, channels=channels, samplerate=rate)
            return rate
        except Exception:
            continue
    return None

def main():
    print("="*80)
    print("                  iCAD Tone Decoder for Meshing-Around Booting Up!")
    if AUDIO_SOURCE == "soundcard":
        try:
            if INPUT_DEVICE is not None:
                sd.default.device = INPUT_DEVICE
                device_info = sd.query_devices(INPUT_DEVICE, kind='input')
            else:
                device_info = sd.query_devices(sd.default.device, kind='input')
            device_name = device_info['name']
            # Detect supported sample rate
            detected_rate = get_supported_sample_rate(sd.default.device, INPUT_CHANNELS)
            if detected_rate:
                SAMPLE_RATE = detected_rate
            else:
                print("No supported sample rate found, using default.", file=sys.stderr)
        except Exception:
            device_name = "Unknown"
        print(f"  Mode: Soundcard | Device: {device_name} | Sample Rate: {SAMPLE_RATE} Hz | Channels: {INPUT_CHANNELS}")
    elif AUDIO_SOURCE == "http":
        print(f"  Mode: HTTP Stream | URL: {HTTP_STREAM_URL} | Buffer: {STREAM_BUFFER} bytes")
    else:
        print(f"  Mode: {AUDIO_SOURCE}")
    print("="*80)
    time.sleep(1)

    parser = argparse.ArgumentParser(description="ICAD Tone Detection")
    parser.add_argument("--wav", type=str, help="Path to WAV file for detection")
    args = parser.parse_args()

    if args.wav:
        print(f"Processing WAV file: {args.wav}")
        try:
            audio = AudioSegment.from_file(args.wav)
            if audio.channels > 1:
                audio = audio.set_channels(1)
            print(f"AudioSegment: channels={audio.channels}, frame_rate={audio.frame_rate}, duration={len(audio)}ms")
            detect_and_alert(audio, audio.frame_rate)
        except Exception as e:
            print(f"Error processing WAV file: {e}", file=sys.stderr)
        return

    print("Starting ICAD Tone Detection...")

    if AUDIO_SOURCE == "http":
        if not HTTP_STREAM_URL or HTTP_STREAM_URL.startswith("http://your-stream-url-here"):
            print("ERROR: Please set a valid HTTP_STREAM_URL or provide a WAV file using --wav option.", file=sys.stderr)
            sys.exit(2)
        print(f"Listening to HTTP stream: {HTTP_STREAM_URL}")
        try:
            response = requests.get(HTTP_STREAM_URL, stream=True, timeout=10)
            buffer = io.BytesIO()
            try:
                for chunk in response.iter_content(chunk_size=4096):
                    buffer.write(chunk)
                    # Use STREAM_BUFFER for detection window
                    if buffer.tell() > STREAM_BUFFER:
                        buffer.seek(0)
                        audio = AudioSegment.from_file(buffer, format="mp3")
                        if audio.channels > 1:
                            audio = audio.set_channels(1)
                        # --- Simple audio level detection ---
                        samples = np.array(audio.get_array_of_samples())
                        if samples.dtype != np.float32:
                            samples = samples.astype(np.float32) / 32767.0  # Normalize to -1..1
                        rms = np.sqrt(np.mean(samples**2))
                        if rms > 0.01:
                            print(f"Audio detected! RMS: {rms:.3f}      ", end='\r')
                        if rms > 0.5:
                            print(f"WARNING: Audio too loud! RMS: {rms:.3f}      ", end='\r')
                        # --- End audio level detection ---
                        detect_and_alert(audio, audio.frame_rate)
                        buffer = io.BytesIO()
            except KeyboardInterrupt:
                print("\nStopped by user.")
                sys.exit(0)
        except requests.exceptions.RequestException as e:
            print(f"Connection error: {e}", file=sys.stderr)
            sys.exit(3)
        except Exception as e:
            print(f"Error processing HTTP stream: {e}", file=sys.stderr)
            sys.exit(4)
    elif AUDIO_SOURCE == "soundcard":
        print("Listening to audio device:")
        buffer = np.array([], dtype=np.float32)
        min_samples = MIN_SAMPLES  # Use configured minimum samples

        def callback(indata, frames, time_info, status):
            nonlocal buffer
            try:
                samples = indata[:, 0]
                buffer = np.concatenate((buffer, samples))
                # --- Simple audio level detection ---
                rms = np.sqrt(np.mean(samples**2))
                if rms > 0.01:
                    print(f"Audio detected! RMS: {rms:.3f}      ", end='\r')
                if rms > 0.5:
                    print(f"WARNING: Audio too loud! RMS: {rms:.3f}      ", end='\r')
                # --- End audio level detection ---
                # Only process when buffer is large enough
                while buffer.size >= min_samples:
                    int_samples = np.int16(buffer[:min_samples] * 32767)
                    audio = AudioSegment(
                        data=int_samples.tobytes(),
                        sample_width=2,
                        frame_rate=SAMPLE_RATE,
                        channels=1
                    )
                    detect_and_alert(audio, SAMPLE_RATE)
                    buffer = buffer[min_samples:]  # keep remainder for next window
            except Exception as e:
                print(f"Callback error: {e}", file=sys.stderr)
        try:
            with sd.InputStream(samplerate=SAMPLE_RATE, channels=INPUT_CHANNELS, dtype='float32', callback=callback):
                print("Press Ctrl+C to stop.")
                import signal
                signal.pause()  # Wait for Ctrl+C, keeps CPU usage minimal
        except KeyboardInterrupt:
            print("Stopped by user.")
        except Exception as e:
            print(f"Error accessing soundcard: {e}", file=sys.stderr)
            sys.exit(5)
    else:
        print("Unknown AUDIO_SOURCE. Set to 'http' or 'soundcard'.", file=sys.stderr)
        sys.exit(6)

if __name__ == "__main__":
    main()
