# Mesh Bot for Network Testing and BBS Activities

Mesh Bot is a feature-rich Python bot designed to enhance your [Meshtastic](https://meshtastic.org/docs/introduction/) network experience. It provides powerful tools for network testing, messaging, games, and more—all via text-based message delivery. Whether you want to test your mesh, send messages, or play games, [mesh_bot.py](mesh_bot.py) has you covered.

* [Getting Started](#getting-started)


![Example Use](etc/pong-bot.jpg "Example Use")
#### TLDR
* [install.sh](INSTALL.md)
* [Configuration Guide](modules/README.md)
* [Games Help](modules/games/README.md)

## Key Features
![CodeQlBadge](https://github.com/SpudGunMan/meshing-around/actions/workflows/dynamic/github-code-scanning/codeql/badge.svg)

### Intelligent Keyword Responder
- **Automated Responses**: Detects keywords like "ping" and replies with "pong" in direct messages (DMs) or group channels.
- **Customizable Triggers**: Monitors group channels for specific keywords and sends custom responses.
- **Emergency Detection**: Watches for emergency-related keywords and alerts a wider audience.
- **New Node Greetings**: Automatically welcomes new nodes joining the mesh.

### Network Tools
- **Mesh Testing**: Use `ping` to test message delivery with realistic packets.
- **Hardware Testing**: The `test` command sends incrementally sized data to test radio buffer limits.
- **Network Monitoring**: Alerts for noisy nodes, tracks node locations, and suggests optimal relay placement.

- **Site Survey & Location Logging**: Use the `map` command to log your current GPS location with a custom description—ideal for site surveys, asset tracking, or mapping nodes locations. Entries are saved to a CSV file for later analysis or visualization.

### Multi-Radio/Node Support
- **Simultaneous Monitoring**: Observe up to nine networks at once.
- **Flexible Messaging**: Send mail and messages between networks.

### Advanced Messaging Capabilities
- **Mail Messaging**: Leave messages for other devices; delivered as DMs when the device is next seen. Use `bbspost @nodeNumber #message` or `bbspost @nodeShortName #message`.
- **Message Scheduler**: Automate messages such as weather updates or net reminders.
- **Store and Forward**: Retrieve missed messages with the `messages` command; optionally log messages to disk.
- **BBS Linking**: Connect multiple bots to expand BBS coverage.
- **E-Mail/SMS Integration**: Send mesh messages to email or SMS for broader reach.
- **New Node Greetings**: Automatically greet new nodes via text.

### Interactive AI and Data Lookup
- **Weather, Earthquake, River, and Tide Data**: Get local alerts and info from NOAA/USGS; uses Open-Meteo for areas outside NOAA coverage.
- **Wikipedia Search**: Retrieve summaries from Wikipedia.
- **Ollama LLM Integration**: Query the [Ollama](https://github.com/ollama/ollama/tree/main/docs) AI for advanced responses.
- **Satellite Passes**: Find upcoming satellite passes for your location.
- **GeoMeasuring Tools**: Calculate distances and midpoints using collected GPS data; supports Fox & Hound direction finding.

### Proximity Alerts
- **Location-Based Alerts**: Get notified when members arrive at a configured latitude/longitude—ideal for campsites, geo-fences, or remote locations. Optionally, trigger scripts, send emails, or automate actions (e.g., change node config, turn on lights, or drop an `alert.txt` file to start a survey or game).
- **Customizable Triggers**: Use proximity events for creative applications like "king of the hill" or 🧭 geocache games by adjusting the alert cycle.
- **High Flying Alerts**: Receive notifications when nodes with high altitude are detected on the mesh.
- **Voice/Command Triggers**: Activate bot functions using keywords or voice commands (see [Voice Commands](#voice-commands-vox) for "Hey Chirpy!" support).

#### Radio Frequency Monitoring
- **SNR RF Activity Alerts**: Monitor radio frequencies and receive alerts when high SNR (Signal-to-Noise Ratio) activity is detected.
- **Hamlib Integration**: Use Hamlib (rigctld) to monitor the S meter on a connected radio.
- **Speech-to-Text Broadcasting**: Convert received audio to text using [Vosk](https://alphacephei.com/vosk/models) and broadcast it to the mesh.

### Check-In / Check-Out & Asset Tracking
- **Asset Tracking**: Maintain a check-in/check-out list for nodes or assets—ideal for accountability of people and equipment (e.g., Radio-Net, FEMA, trailhead groups).

### Fun and Games
- **Built-in Games**: Play classic games like DopeWars, Lemonade Stand, BlackJack, and Video Poker directly via DM.
- **FCC ARRL QuizBot**: Practice for the ham radio exam with the integrated quiz bot.
- **Command-Based Gameplay**: Use the `games` command to view available games and start playing.
- **Telemetry Leaderboard**: Compete for fun stats like lowest battery or coldest temperature.

#### QuizMaster
- **Group Quizzes**: Admins can start and stop quiz games for groups.
- **Player Participation**: Players join with `q: join`, leave with `q: leave`, and answer questions by prefixing their answer with `q:`, e.g., `q: 42`.
- **Scoring & Leaderboards**: Check your score with `q: score` and see the top performers with `q: top`.
- **Admin Controls**: QuizMasters (from `bbs_admin_list`) can use `q: start`, `q: stop`, and `q: broadcast <message>` to manage games.

#### Survey Module
- **Custom Surveys**: Create and manage surveys by editing JSON files in `data/survey`. Multiple surveys are supported (e.g., `survey snow`).
- **User Feedback**: Users participate via DM; responses are logged for review.
- **Reporting**: Retrieve survey results with `survey report` or `survey report <surveyname>`.

### EAS Alerts
- **FEMA iPAWS/EAS Alerts**: Receive Emergency Alerts from FEMA via API on internet-connected nodes.
- **NOAA EAS Alerts**: Get Emergency Alerts from NOAA via API.
- **USGS Volcano Alerts**: Receive volcano alerts from USGS via API.
- **Offline EAS Alerts**: Report EAS alerts over the mesh using external tools, even without internet.
- **NINA Alerts (Germany)**: Receive emergency alerts from the xrepository.de feed for Germany.

### File Monitor Alerts
- **File Monitoring**: Watch a text file for changes and broadcast updates to the mesh channel.
- **News File Access**: Retrieve the contents of a news file on request; supports multiple news sources or files.
- **Shell Command Access**: Execute shell commands via DM with replay protection (admin only).

### Data Reporting
- **HTML Reports**: Visualize bot traffic and data flows with a built-in HTML generator. See [data reporting](logs/README.md) for details.
- **RSS & News Feeds**: Receive news and data from multiple sources directly on the mesh.

### Robust Message Handling
- **Automatic Message Chunking**: Messages over 160 characters are automatically split to ensure reliable delivery across multiple hops.

## Getting Started
This project is developed on Linux (specifically a Raspberry Pi) but should work on any platform where the [Meshtastic protobuf API](https://meshtastic.org/docs/software/python/cli/) modules are supported, and with any compatible [Meshtastic](https://meshtastic.org/docs/getting-started/) hardware. For pico or low-powered devices, see projects for embedding, armbian or [buildroot](https://github.com/buildroot-meshtastic/buildroot-meshtastic), also see [femtofox](https://github.com/noon92/femtofox) for running on luckfox hardware. If you need a local console consider the [firefly](https://github.com/pdxlocations/firefly) project. 

🥔 Please use responsibly and follow local rulings for such equipment. This project captures packets, logs them, and handles over the air communications which can include PII such as GPS locations.

### Quick Setup 
#### Clone the Repository
If you dont have git you will need it `sudo apt-get install git`
```sh
git clone https://github.com/spudgunman/meshing-around
```
- **Automated Installation**: [install.sh](INSTALL.md) will automate optional venv and requirements installation.
- **Launch Script**: [laynch.sh](INSTALL.md) only used in a venv install, to launch the bot and the report generator.

### Docker Installation - handy for windows
See further info on the [docker.md](script/docker/README.md)

## Full list of commands for the bot
[modules/README.md](modules/README.md)

### Games (via DM only)
[modules/games/README.md](modules/games/README.md)

### Firmware 2.6 DM Key, and 2.7 CLIENT_BASE Favorite Nodes
Firmware 2.6 introduced [PKC](https://meshtastic.org/blog/introducing-new-public-key-cryptography-in-v2_5/), enabling secure private messaging by adding necessary keys to each node. To fully utilize this feature, you should add favorite nodes—such as BBS admins—to your node’s favorites list to ensure their keys are retained. A helper script is provided to simplify this process:
- Run the helper script from the main program directory: `python3 script/addFav.py`
- By default, this script adds nodes from `bbs_admin_list` and `bbslink_whitelist`
- If using a virtual environment, run: `launch.sh addfav`
- The API will not work-fully today to set nodes this is a WIP

Additionally, you can just DM a bot to "auto favorite." If your node is set to not be messageable, DMs won't work—be advised.

To configure favorite nodes, add their numbers to your config file:
```conf
[general]
favoriteNodeList = # list of favorite nodes numbers ex: 2813308004,4258675309 used by script/addFav.py
```

### MQTT Notes
There is no direct support for MQTT in the code, however, reports from Discord are that using [meshtasticd](https://meshtastic.org/docs/hardware/devices/linux-native-hardware/) with no radio and attaching the bot to the software node, which is MQTT-linked, allows routing. Tested working fully Firmware:2.6.11 with [mosquitto](https://meshtastic.org/docs/software/integrations/mqtt/mosquitto/).

~~There also seems to be a quicker way to enable MQTT by having your bot node with the enabled [serial](https://meshtastic.org/docs/configuration/module/serial/) module with echo enabled and MQTT uplink and downlink. These two~~ 

# Recognition

I used ideas and snippets from other responder bots and want to call them out!

### Inspiration and Code Snippets
- [MeshLink](https://github.com/Murturtle/MeshLink)
- [Meshtastic Python Examples](https://github.com/pdxlocations/meshtastic-Python-Examples)
- [Meshtastic Matrix Relay](https://github.com/geoffwhittington/meshtastic-matrix-relay)

### Games Ported From
- [Lemonade Stand](https://github.com/tigerpointe/Lemonade-Stand/)
- [Drug Wars](https://github.com/Reconfirefly/drugwars)
- [BlackJack](https://github.com/Himan10/BlackJack)
- [Video Poker Terminal Game](https://github.com/devtronvarma/Video-Poker-Terminal-Game)
- [Python Mastermind](https://github.com/pwdkramer/pythonMastermind/)
- [Golf](https://github.com/danfriedman30/pythongame)
- ARRL Question Pool Data from https://github.com/russolsen/ham_radio_question_pool

### Special Thanks
- **xdep**: For the reporting tools.
- **Nestpebble**: For new ideas and enhancements.
- **mrpatrick1991**: For Docker configurations.
- **[https://github.com/A-c0rN](A-c0rN)**: Assistance with iPAWS and EAS
- **Mike O'Connell/skrrt**: For [eas_alert_parser](etc/eas_alert_parser.py) enhanced by **sheer.cold**
- **PiDiBi**: For looking at test functions and other suggestions like wxc, CPU use, and alerting ideas.
- **WH6GXZ nurse dude**: For bashing on installer, Volcano Alerts 🌋
- **Josh**: For more bashing on installer!
- **dj505**: trying it on windows!
- **mikecarper**: ideas, and testing. hamtest
- **c.merphy360**: high altitude alerts
- **Iris**: testing and finding 🐞
- **FJRPiolt**: testing bugs out!!
- **Cisien, bitflip, Woof, propstg, snydermesh, trs2982, F0X, Malice, mesb1, and Hailo1999**: For testing and feature ideas on Discord and GitHub.
- **Meshtastic Discord Community**: For tossing out ideas and testing code.

### Tools
- **Node Backup Management**: [Node Slurper](https://github.com/SpudGunMan/node-slurper)

Meshtastic® is a registered trademark of Meshtastic LLC. Meshtastic software components are released under various licenses, see GitHub for details. No warranty is provided - use at your own risk.
