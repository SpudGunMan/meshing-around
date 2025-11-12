#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# icad_tone.py - uses icad_tone_detection, for fire and EMS tone detection
# https://github.com/thegreatcodeholio/icad_tone_detection
# output to alert.txt for meshing-around bot
# 2025 K7MHI Kelly Keeton

ALERT_FILE_PATH = "alert.txt"
AUDIO_SOURCE = "http"  # "http" for stream, "soundcard" for microphone or line-in
HTTP_STREAM_URL = ""   # Set to your stream URL, e.g., "http://your-stream-url-here/stream.mp3"
SAMPLE_RATE = 44100
INPUT_CHANNELS = 1
CHUNK_DURATION = 2  # seconds

try:
    import sys
    import os
    import time
    from icad_tone_detection import tone_detect
    import io
    from pydub import AudioSegment
    import requests
    import sounddevice as sd
    import numpy as np
    import argparse
except ImportError as e:
    print(f"Missing required module: {e.name}. Please review the comments in program, and try again.", file=sys.stderr)
    sys.exit(1)

def write_alert(message):
    if ALERT_FILE_PATH:
        try:
            with open(ALERT_FILE_PATH, "w") as f: # overwrite existing file for each alert
                f.write(message + "\n")
        except Exception as e:
            print(f"Error writing to alert file: {e}", file=sys.stderr)

def detect_and_alert(audio_data, sample_rate):
    result = tone_detect(audio_data, sample_rate)
    print("Raw detection result:", result)  # Debugging line
    if result:
        # Print all detected tone types for debugging
        for tone_type in ["two_tone_result", "long_result", "hi_low_result", "pulsed_result", "mdc_result", "dtmf_result"]:
            tone_list = getattr(result, tone_type, [])
            if tone_list:
                print(f"{tone_type}:")
                for tone in tone_list:
                    print(tone)
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
    else:
        print("No tone detected.")

def main():
    parser = argparse.ArgumentParser(description="ICAD Tone Detection")
    parser.add_argument("--wav", type=str, help="Path to WAV file for detection")
    args = parser.parse_args()

    if args.wav:
        print(f"Processing WAV file: {args.wav}")
        try:
            audio = AudioSegment.from_file(args.wav)
            # Convert to mono if necessary
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
            for chunk in response.iter_content(chunk_size=4096):
                buffer.write(chunk)
                if buffer.tell() > SAMPLE_RATE * CHUNK_DURATION * 2:
                    buffer.seek(0)
                    audio = AudioSegment.from_file(buffer, format="mp3")
                    samples = np.array(audio.get_array_of_samples())
                    detect_and_alert(samples, audio.frame_rate)
                    buffer = io.BytesIO()
        except requests.exceptions.RequestException as e:
            print(f"Connection error: {e}", file=sys.stderr)
            sys.exit(3)
        except Exception as e:
            print(f"Error processing HTTP stream: {e}", file=sys.stderr)
            sys.exit(4)
    elif AUDIO_SOURCE == "soundcard":
        print("Listening to audio device:")
        def callback(indata, frames, time, status):
            samples = indata[:, 0]
            detect_and_alert(samples, SAMPLE_RATE)
        try:
            with sd.InputStream(samplerate=SAMPLE_RATE, channels=INPUT_CHANNELS, callback=callback):
                while True:
                    time.sleep(CHUNK_DURATION)
        except Exception as e:
            print(f"Error accessing soundcard: {e}", file=sys.stderr)
            sys.exit(5)
    else:
        print("Unknown AUDIO_SOURCE. Set to 'http' or 'soundcard'.", file=sys.stderr)
        sys.exit(6)

if __name__ == "__main__":
    main()

