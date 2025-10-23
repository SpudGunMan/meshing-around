# Meshtastic Mesh-Bot Modules

This document provides an overview of all modules available in the Mesh-Bot project, including their features, usage, and configuration. Updated when I can. Oct-2025 "ver 1.9.8.4"

---

## Table of Contents

- [Overview](#overview)
- [Games](#games)
- [BBS (Bulletin Board System)](#bbs-bulletin-board-system)
- [Checklist](#checklist)
- [Location & Weather](#location--weather)
- [EAS & Emergency Alerts](#eas--emergency-alerts)
- [File Monitoring & News](#file-monitoring--news)
- [Radio Monitoring](#radio-monitoring)
- [Ollama LLM/AI](#ollama-llmai)
- [Wikipedia Search](#wikipedia-search)
- [Scheduler](#scheduler)
- [Other Utilities](#other-utilities)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Adding your Own](adding_more.md)

---

## Overview

Modules are Python files in the `modules/` directory that add features to the bot. Enable or disable them via `config.ini`. See [modules/adding_more.md](adding_more.md) for developer notes.

---

## Games

All games are played via DM to the bot. See [modules/games/README.md](games/README.md) for detailed rules and examples.

| Command        | Description                        |
|----------------|------------------------------------|
| `blackjack`    | Play Blackjack (Casino 21)         |
| `dopewars`     | Classic trading game               |
| `golfsim`      | 9-hole Golf Simulator              |
| `lemonstand`   | Lemonade Stand business sim        |
| `tictactoe`    | Tic-Tac-Toe vs. the bot            |
| `mastermind`   | Code-breaking game                 |
| `videopoker`   | Video Poker (five-card draw)       |
| `joke`         | Tells a dad joke                   |
| `hamtest`      | FCC/ARRL QuizBot                   |
| `hangman`      | Classic word guess game            |
| `survey`       | Take a custom survey               |
| `quiz`         | QuizMaster group quiz              |

Enable/disable games in `[games]` section of `config.ini`.

---

## BBS (Bulletin Board System)

| Command      | Description                                   |
|--------------|-----------------------------------------------|
| `bbshelp`    | Show BBS help                                 |
| `bbslist`    | List messages                                 |
| `bbsread`    | Read a message by ID                          |
| `bbspost`    | Post a message or DM                          |
| `bbsdelete`  | Delete a message                              |
| `bbsinfo`    | BBS stats (sysop)                             |
| `bbslink`    | Link messages between BBS systems             |

Enable in `[bbs]` section of `config.ini`.

---

## Checklist

| Command      | Description                                   |
|--------------|-----------------------------------------------|
| `checkin`    | Check in a node/asset                         |
| `checkout`   | Check out a node/asset                        |
| `checklist`  | Show checklist database                       |

Enable in `[checklist]` section of `config.ini`.

---

## Location & Weather

| Command      | Description                                   |
|--------------|-----------------------------------------------|
| `wx`         | Local weather forecast (NOAA/Open-Meteo)      |
| `wxc`        | Weather in metric/imperial                    |
| `wxa`        | NOAA alerts                                   |
| `wxalert`    | NOAA alerts (expanded)                        |
| `mwx`        | NOAA Coastal Marine Forecast                  |
| `tide`       | NOAA tide info                                |
| `riverflow`  | NOAA river flow info                          |
| `earthquake` | USGS earthquake info                          |
| `valert`     | USGS volcano alerts                           |
| `rlist`      | Nearby repeaters from RepeaterBook            |
| `satpass`    | Satellite pass info                           |
| `howfar`     | Distance traveled since last check            |
| `howtall`    | Calculate height using sun angle              |
| `whereami`   | Show current location                         |

Configure in `[location]` section of `config.ini`.

---

## EAS & Emergency Alerts

| Command      | Description                                   |
|--------------|-----------------------------------------------|
| `ea`/`ealert`| FEMA iPAWS/EAS alerts (USA/DE)                |

Enable in `[eas]` section of `config.ini`.

---

## File Monitoring & News

| Command      | Description                                   |
|--------------|-----------------------------------------------|
| `readnews`   | Read contents of a news file                  |
| `readrss`    | Read RSS feed                                 |
| `x:`         | Run shell command (if enabled)                |

Configure in `[fileMon]` section of `config.ini`.

---

## Radio Monitoring

| Command      | Description                                   |
|--------------|-----------------------------------------------|
| `radio`      | Monitor radio SNR via Hamlib                  |

Configure in `[radioMon]` section of `config.ini`.

## Voice Commands (VOX)

You can trigger select bot functions using voice commands with the "Hey Chirpy!" wake word. Just say "Hey Chirpy..." followed by one of the supported commands:

| Voice Command | Description                                 |
|---------------|---------------------------------------------|
| `joke`        | Tells a joke                                |
| `weather`     | Returns local weather forecast              |
| `moon`        | Returns moonrise/set and phase info         |
| `daylight`    | Returns sunrise/sunset times                |
| `river`       | Returns NOAA river flow info                |
| `tide`        | Returns NOAA tide information               |
| `satellite`   | Returns satellite pass info                 |

Enable and configure VOX features in the `[vox]` section of `config.ini`.
---

## Ollama LLM/AI

| Command      | Description                                   |
|--------------|-----------------------------------------------|
| `askai`      | Ask Ollama LLM AI                             |
| `ask:`       | Ask Ollama LLM AI (raw)                       |

Configure in `[ollama]` section of `config.ini`.

---

## Wikipedia Search

| Command      | Description                                   |
|--------------|-----------------------------------------------|
| `wiki:`      | Search Wikipedia or local Kiwix server        |

Configure in `[wikipedia]` section of `config.ini`.

---

## Scheduler

Automate messages and tasks using the scheduler module.

Configure in `[scheduler]` section of `config.ini`.  
See [modules/scheduler.py](modules/custom_scheduler.py) for advanced scheduling.

---

## Other Utilities

- `motd` — Message of the day
- `leaderboard` — Mesh telemetry stats
- `lheard` — Last heard nodes
- `history` — Command history
- `cmd`/`cmd?` — Show help message ( the bot avoids the use of saying or using help )

---

## Configuration

- Edit `config.ini` to enable/disable modules and set options.
- See `config.template` for all available settings.
- Each module section in `config.ini` has an `enabled` flag.

---

## Troubleshooting

- Use the `logger` module for debug output.
- See [modules/README.md](modules/README.md) for developer help.
- Use `etc/simulator.py` for local testing.
- Check the logs in the `logs/` directory for errors.

---

Happy meshing!