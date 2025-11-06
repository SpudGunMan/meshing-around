# etc Directory

This folder contains supporting files and resources for the Mesh Bot project. Typical contents include:

- **Images**: Visual assets used in documentation (e.g., `pong-bot.jpg`).
- **Custom Scripts**: Example or utility scripts for advanced configuration (e.g., `custom_scheduler.py` for scheduled tasks).
- **tmp**: Temp files for install

## db_admin.py

**Purpose:**  
`db_admin.py` is a simple administrative tool for viewing the contents of the Mesh Bot’s data and high score databases. It loads and prints out messages, direct messages, email/SMS records, and game high score tables stored in the `/data` directory.

**Usage:**  
Run this script from the command line to display the current contents of the bot’s databases. This is useful for debugging, verifying data integrity, or reviewing stored messages and game scores.

```sh
python etc/db_admin.py
```

**What it does:**  
- Attempts to load various `.pkl` and `.pickle` files from the `data` directory.
- Prints out the contents of BBS messages, direct messages, email and SMS databases.
- Displays high scores for supported games (Lemonade Stand, DopeWars, BlackJack, Video Poker, Mastermind, GolfSim).
- If a file is missing, it will print a message indicating so.

**Note:**  
This tool is for administrative and debugging purposes only. It does not modify any data.

## eas_alert_parser.py

**Purpose:**  
`eas_alert_parser.py` is a utility script for processing and cleaning up output from `multimon-ng` to extract and convert Emergency Alert System (EAS) messages for further use, such as with EAS2Text.

**Usage:**  
This script is intended to be used with piped input, typically from `multimon-ng` decoding SAME/EAS messages. It filters and processes EAS lines, converts them to readable text using EAS2Text, and writes the results to `alert.txt`.

**Example usage:**
```sh
multimon-ng -a EAS ... | python etc/eas_alert_parser.py
```

**What it does:**  
- Reads input line-by-line (supports piped or redirected input).
- Filters for lines starting with `EAS:` or `EAS (part):`.
- Avoids duplicate messages and only processes new alerts.
- Uses the EAS2Text library to convert EAS codes to human-readable messages.
- Writes completed alerts to `alert.txt` for further processing or notification.

**Note:**  
This script is intended for experimental or hobbyist use and may require customization for your specific workflow.

## simulator.py

**Purpose:**  
`simulator.py` is a development and testing tool that simulates the behavior of the Mesh Bot in a controlled environment. It allows you to prototype and test handler functions without needing real hardware or a live mesh network.

**Usage:**  
Run this script from the command line to interactively test handler functions. You can input messages as if you were a mesh node, and see how your handler responds.

```sh
python etc/simulator.py
```

**What it does:**  
- Simulates node IDs, device IDs, and random GPS locations.
- Lets you specify which handler function to test (by setting `projectName`).
- Prompts for user input, passes it to the handler, and displays the response.
- Logs simulated message sending and handler output for review.
- Useful for rapid prototyping and debugging new features or message handlers.

**Note:**  
Edit the `projectName` variable to match the handler function you want to test. You can expand this script to test additional handlers or scenarios as needed.

## yolo_vision.py

**Purpose:**  
`yolo_vision.py` provides real-time object detection and movement tracking using a Raspberry Pi camera and YOLOv5. It is designed for integration with the Mesh Bot project, outputting alerts to both the console and an optional `alert.txt` file for further use (such as with Meshtastic).

**Features:**  
- Ignores specified object classes (e.g., "bed", "chair") to reduce false positives.
- Configurable detection confidence threshold and movement sensitivity.
- Tracks object movement direction (left, right, stationary).
- Fuse counter: only alerts after an object is detected for several consecutive frames.
- Optionally writes the latest alert (without timestamp) to a specified file, overwriting previous alerts.

**Configuration:**  
- `LOW_RES_MODE`: Use low or high camera resolution for CPU savings.
- `IGNORE_CLASSES`: List of object classes to ignore.
- `CONFIDENCE_THRESHOLD`: Minimum confidence for reporting detections.
- `MOVEMENT_THRESHOLD`: Minimum pixel movement to consider as "moving".
- `ALERT_FUSE_COUNT`: Number of consecutive detections before alerting.
- `ALERT_FILE_PATH`: Path to alert file (set to `None` to disable file output).

**Usage:**  
Run this script to monitor the camera feed and generate alerts for detected and moving objects. Alerts are printed to the console and, if configured, written to `alert.txt` for integration with other systems.

---

