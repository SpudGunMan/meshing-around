# MeshCore Bot — Command Testing Checklist

Testing on MeshCore (Heltec V3, serial `/dev/ttyUSB0`).  
Status: ✅ Working | ❌ Broken | ⚠️ Partial | ⬜ Not tested | 🚫 Disabled in config

Send commands as DMs to the bot node. Check `data/syslog.txt` for errors.

---

## Core / Identity

| Status | Command | Notes |
|--------|---------|-------|
| ✅ | `ping` | Returns pong with hop count / SNR |
| ✅ | `ack` | Returns ACK-ACK |
| ✅ | `cq` / `cqcq` / `cqcqcq` | Was showing `000000000000` as bot name — fixed to use `mc.self_info.name` |
| ✅ | `test` / `testing` | Returns random testing phrase |
| ✅ | `pong` | Returns PING!! |
| ✅ | `whoami` | Shows your name, pubkey prefix, hop/SNR — needs contact to have advertised |
| ✅ | `whois <partial>` | Prefix search — 1 match = 1 reply, multiple matches = 1 DM per match |
| ⬜ | `📍` | Alias for whoami |
| ⬜ | `cmd` / `cmd?` | List available commands |
| ⬜ | `echo <text>` | Echoes back the message |

---

## Location

| Status | Command | Notes |
|--------|---------|-------|
| ✅ | `whereami` | Returns **sender's** GPS location — requires sender node to have GPS; falls back to "no GPS" message |
| ⬜ | `howfar` | Distance you've traveled since last call — requires sender to have `adv_lat`/`adv_lon` in contact cache |
| ⬜ | `howfar reset` | Reset your starting point |
| ⬜ | `howtall` | Elevation diff from bot location |
| ⬜ | `map` | Returns a map link |

---

## Node Info / Status

| Status | Command | Notes |
|--------|---------|-------|
| ⬜ | `sitrep` / `lheard` | Recently heard nodes |
| ⬜ | `sysinfo` | Bot uptime, contact count, session DM count |
| ⬜ | `leaderboard` | Best/worst RF signal and most active node — populated after receiving DMs with RSSI |
| ⬜ | `history` | Message history |
| ⬜ | `messages` | Channel message history |
| ⬜ | `motd` | Message of the day (`motd =` in `[general]`) |
| ⬜ | `path` | Repeater path + estimated distance for last received message |

---

## Weather

Location: sender GPS first (from contact cache), fallback to bot lat/lon (`lat`/`lon` in `[location]`).  
Outside US: set `UseMeteoWxAPI = True` in `[location]` — currently **True** ✅

| Status | Command | Notes |
|--------|---------|-------|
| ✅ | `wx` | `[location] UseMeteoWxAPI = True` ✅ |
| ⬜ | `wxc` | Weather in Celsius — same API as `wx` |
| ⬜ | `wxa` / `wxalert` | Weather alerts |
| 🚫 | `mwx` | Requires `[location] coastalEnabled = True` — currently **not set** (defaults False) |
| 🚫 | `tide` | Requires `[location] coastalEnabled = True` — currently **not set** (defaults False) |
| ⬜ | `riverflow` | River flow data — uses bot lat/lon |
| ⬜ | `moon` | Moon phase |
| ⬜ | `sun` | Sunrise/sunset |

---

## Solar / HF Conditions

| Status | Command | Notes |
|--------|---------|-------|
| ⬜ | `hfcond` | HF band conditions |
| ⬜ | `solar` | Solar/space weather |
| ⬜ | `satpass` | Satellite pass times |
| ⬜ | `earthquake` | Recent earthquakes |
| ⬜ | `valert` | Volcano alerts |

---

## Games

Config in `[games]` section. Missing keys default to `True` except `quiz` (defaults `False`).

| Status | Command | Config flag | Notes |
|--------|---------|-------------|-------|
| ✅ | `blackjack` | `blackjack = True` ✅ | Card game |
| ✅ | `videopoker` | `videopoker = True` ✅ | Poker game |
| ✅ | `dopewars` | `dopewars = True` ✅ | Drug market sim |
| ✅ | `lemonstand` | `lemonade = True` ✅ | Lemonade stand sim |
| ⬜ | `golfsim` | `golfSim` not in config → default **True** | Golf game |
| ⬜ | `mastermind` | `mastermind` not in config → default **True** | Code-guessing game |
| ⬜ | `hangman` | `hangman` not in config → default **True** | Word game |
| ⬜ | `tictactoe` / `tic-tac-toe` | `tictactoe` not in config → default **True** | Board display stubbed; text board doesn't render over mesh |
| 🚫 | `quiz` / `q: <answer>` | `quiz` not in config → default **False** | Enable with `[games] quiz = True` |
| ⬜ | `battleship` | `battleShip` not in config → default **True** | Naval game |
| ⬜ | `hamtest` | `hamtest` not in config → default **True** | Ham radio practice exam |
| ⬜ | `games` | — | List games |

---

## BBS (`[bbs] enabled = True` ✅)

| Status | Command | Notes |
|--------|---------|-------|
| ⬜ | `bbslist` | List all public messages |
| ⬜ | `bbspost $subject #body` | Post a public message |
| ⬜ | `bbspost @ShortName #body` | Leave an offline DM for another node |
| ⬜ | `bbsread #<id>` | Read a message by ID |
| ⬜ | `bbsdelete #<id>` | Delete your own message (or any if admin) |
| ⬜ | `bbshelp` | BBS command help |
| ⬜ | `bbsinfo` | Message count and pending DMs |
| ⬜ | `bbsack` / `bbslink` | BBS sync between two bots — requires `[bbs] bbs_link_enabled = True` |
| ⬜ | `bannode add/remove/list <prefix>` | Admin only — ban a node from BBS |

---

## Messaging / SMS / Email

| Status | Command | Notes |
|--------|---------|-------|
| 🚫 | `sms: <node> <msg>` | Requires `[smtp] enablesmtp = True` — currently **False** |
| 🚫 | `setsms <number>` | Same SMTP requirement |
| 🚫 | `clearsms` | Same SMTP requirement |
| 🚫 | `email: <addr> <msg>` | Requires `[smtp] enablesmtp = True` — currently **False** |
| 🚫 | `setemail <addr>` | Same SMTP requirement |

---

## Info Lookups

| Status | Command | Notes |
|--------|---------|-------|
| 🚫 | `wiki <topic>` | No `[wiki]` section in config.ini |
| ⬜ | `readrss <url>` | RSS feed reader |
| ⬜ | `latest` / `readnews` | News headlines |
| 🚫 | `dx` | No `[dxspot]` section in config.ini |
| ⬜ | `rlist` | Repeater lookup |
| ⬜ | `verse` | Bible verse |
| ⬜ | `🐝` | Bee file |
| 🚫 | `joke` | `[general] DadJokes = False` — set to `True` to enable |

---

## AI / LLM

| Status | Command | Notes |
|--------|---------|-------|
| 🚫 | `ask: <question>` | No `[llm]` section in config.ini |
| 🚫 | `askai <question>` | No `[llm]` section in config.ini |

---

## Emergency

| Status | Command | Notes |
|--------|---------|-------|
| 🚫 | `911` / `112` / `999` | `[emergencyHandler] enabled = False` |
| 🚫 | `emergency` / `fire` / `police` / `ambulance` / `rescue` | `[emergencyHandler] enabled = False` |
| 🚫 | `ea` / `ealert` | `[emergencyHandler] enabled = False` |

---

## Checklist / Inventory (disabled in config)

| Status | Command | Notes |
|--------|---------|-------|
| 🚫 | `checkin` / `checkout` / `checklist` | `[checklist] enabled = False` |
| 🚫 | `item` / `itemadd` / `itemlist` / etc. | `[inventory] enabled = False` |
| 🚫 | `cart` / `cartadd` / `cartbuy` / etc. | `[inventory] enabled = False` |

---

## Misc

| Status | Command | Notes |
|--------|---------|-------|
| ⬜ | `globalthermonuclearwar` | Easter egg |
| ⬜ | `chess` | Redirects to external game |
| ⬜ | `🔔` | Alert bell |
| ⬜ | `x: <cmd>` | Shell command exec (sysop only) |

---

## Known Issues / Notes

- **`sysinfo`** — now shows uptime, contact count, and session DM count (Meshtastic TX/RX packet counters were always 0 and have been removed).
- **`tictactoe` board** — visual board display is stubbed; the raw-bytes draw method isn't ported yet.
- **`howfar`** — requires the sender's node to have GPS and to have advertised position (`adv_lat`/`adv_lon` in contact). If sender has no GPS → returns "No GPS location available".
- **`whereami`** — returns sender's GPS, not the bot's location. Returns error if sender has no GPS.
- **`leaderboard`** — only Best RF, Worst RF (from RSSI on RX_LOG_DATA events), and Most Messages (DM count) are populated in MeshCore. Meshtastic telemetry fields (battery, voltage, etc.) remain empty.
- **`mwx` / `tide`** — gated by `[location] coastalEnabled = True`; not set in config so these commands are not registered.
- **Contact names** — populated from `CONTACTS` / `NEW_CONTACT` events at startup. If a node hasn't advertised yet, its pubkey prefix is used as the name.
- **Scheduler** — `[scheduler] enabled = False`; `send_message()` calls inside it are not `await`-ed (not urgent while disabled).
- **Weather location** — all weather commands use sender GPS first (from contact cache `adv_lat`/`adv_lon`), falling back to bot `lat`/`lon` from `[location]`. Outside US requires `UseMeteoWxAPI = True`.
