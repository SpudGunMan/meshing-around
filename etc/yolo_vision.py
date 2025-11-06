#!/usr/bin/env python3
# YOLOv5 Object Detection with Movement Tracking using Raspberry Pi AI Camera
# Adapted from Ultralytics YOLOv5 and Picamera2 examples
# Requirements: torch, torchvision, pillow, picamera2, numpy
# Adjust settings below as needed, indended for meshing-around alert.txt output to meshtastic
# 2025 K7MHI Kelly Keeton
import torch
from PIL import Image
import numpy as np
import time
from picamera2 import Picamera2
import warnings
import sys
import datetime

# Suppress FutureWarnings from libraries
warnings.filterwarnings("ignore", category=FutureWarning)

# Load YOLOv5 model, other options include 'yolov5m', 'yolov5l', 'yolov5x'
model = torch.hub.load("ultralytics/yolov5", "yolov5s")

LOW_RES_MODE = 0  # 1 for low res (320x240), 0 for high res (640x480)
IGNORE_CLASSES = ["bed", "chair"]  # Add object names to ignore
CONFIDENCE_THRESHOLD = 0.8  # Only show detections above this confidence
MOVEMENT_THRESHOLD = 50     # Pixels to consider as movement (adjust as needed)
IGNORE_STATIONARY = True   # Whether to ignore stationary objects in output
ALERT_FUSE_COUNT = 5  # Number of consecutive detections before alerting
ALERT_FILE_PATH = "alert.txt"  # e.g., "/opt/meshing-around/alert.txt" or None for no file output

picam2 = Picamera2()
if LOW_RES_MODE:
    picam2.preview_configuration.main.size = (320, 240)
else:
    picam2.preview_configuration.main.size = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")
picam2.start()

print("="*40)
print("  Sentinal Vision 3000 Booting Up!")
print("="*40)
time.sleep(1)

def alert_output(msg, alert_file_path=ALERT_FILE_PATH):
    print(msg)
    if alert_file_path:
        # Remove timestamp for file output
        msg_no_time = " ".join(msg.split("] ")[1:]) if "] " in msg else msg
        with open(alert_file_path, "w") as f:  # Use "a" to append instead of overwrite
            f.write(msg_no_time + "\n")

try:
    i = 0 # Frame counter if zero will be infinite
    system_normal_printed = False # system nominal flag, if true disables printing
    while True:
        i += 1
        frame = picam2.capture_array()
        img = Image.fromarray(frame)

        results = model(img)
        df = results.pandas().xyxy[0]
        df = df[df['confidence'] >= CONFIDENCE_THRESHOLD]  # Filter by confidence
        df = df[~df['name'].isin(IGNORE_CLASSES)]          # Filter out ignored classes
        counts = df['name'].value_counts()
        if counts.empty:
            if not system_normal_printed:
                print("System nominal: No objects detected.")
                system_normal_printed = True
            continue  # Skip the rest of the loop if nothing detected
        if counts.sum() > ALERT_FUSE_COUNT:
            system_normal_printed = False  # Reset flag if something is detected

        # Movement tracking
        if not hasattr(__builtins__, 'prev_centers'):
            __builtins__.prev_centers = {}
        if not hasattr(__builtins__, 'stationary_reported'):
            __builtins__.stationary_reported = set()
        if not hasattr(__builtins__, 'fuse_counters'):
            __builtins__.fuse_counters = {}

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_centers = {}
        detected_this_frame = set()

        for idx, row in df.iterrows():
            obj_id = f"{row['name']}_{idx}"
            x_center = (row['xmin'] + row['xmax']) / 2
            current_centers[obj_id] = x_center
            detected_this_frame.add(obj_id)

            prev_x = __builtins__.prev_centers.get(obj_id)
            direction = ""
            count = counts[row['name']]

            # Fuse logic
            fuse_counters = __builtins__.fuse_counters
            if obj_id not in fuse_counters:
                fuse_counters[obj_id] = 1
            else:
                fuse_counters[obj_id] += 1

            if fuse_counters[obj_id] < ALERT_FUSE_COUNT:
                continue  # Don't alert yet

            if prev_x is not None:
                delta = x_center - prev_x
                if abs(delta) < MOVEMENT_THRESHOLD:
                    direction = "stationary"
                    if IGNORE_STATIONARY:
                        if obj_id not in __builtins__.stationary_reported:
                            alert_output(f"[{timestamp}] {count} {row['name']} {direction}")
                            __builtins__.stationary_reported.add(obj_id)
                    else:
                        alert_output(f"[{timestamp}] {count} {row['name']} {direction}")
                else:
                    direction = "moving right" if delta > 0 else "moving left"
                    alert_output(f"[{timestamp}] {count} {row['name']} {direction}")
                    __builtins__.stationary_reported.discard(obj_id)
            else:
                direction = "detected"
                alert_output(f"[{timestamp}] {count} {row['name']} {direction}")

        # Reset fuse counters for objects not detected in this frame
        for obj_id in list(__builtins__.fuse_counters.keys()):
            if obj_id not in detected_this_frame:
                __builtins__.fuse_counters[obj_id] = 0

        __builtins__.prev_centers = current_centers

        time.sleep(1)  # Adjust frame rate as needed
except KeyboardInterrupt:
    print("\nInterrupted by user. Shutting down...")
except Exception as e:
    print(f"\nAn error occurred: {e}", file=sys.stderr)
finally:
    picam2.close()
    print("Camera closed. Goodbye!")