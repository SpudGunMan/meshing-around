# MeshCore Migration Plan

Migration of `meshing-around-mc` from the Meshtastic Python library to MeshCore (`meshcore` / meshcore_py).

**Source of truth for MeshCore patterns**: `../Remote-Terminal-for-MeshCore/`  
**Goal**: Keep every feature intact. Only the radio backend changes.  
**Scope**: Single radio (Serial, TCP, or BLE). DM-only response mode.

---

## Conceptual Differences to Internalize

| Concept | Meshtastic | MeshCore |
|---|---|---|
| Node identity | 32-bit integer (`2813308004`) | 64-char hex public key (`aabbcc...`) |
| Short identity | `!aabbccdd` (hex of int) | 12-char key prefix |
| Node name | `longName` / `shortName` from `interface.nodes` | `name` from contact sync |
| Event model | PyPubSub `pub.subscribe('meshtastic.receive', cb)` | `mc.subscribe(EventType.X, async_handler)` |
| Sending DM | `interface.sendText(text, destinationId=int_id)` | `await mc.commands.send_msg(pubkey_hex, text)` |
| Sending channel | `interface.sendText(text, channelIndex=ch)` | `await mc.commands.send_chan_msg(slot_idx, text)` |
| SNR / RSSI | `packet['rxSnr']`, `packet['rxRssi']` | Decoded from `RX_LOG_DATA` raw bytes |
| Hop count | Computed from `hopStart`, `hopLimit`, `hopsAway` | `path_len` from `RX_LOG_DATA` decoded path |
| GPS location | `interface.nodes[id]['position']` | `contact.lat`, `contact.lon` (from advert) |
| Channel list | `interface.getNode('^local').get_channels_with_hash()` | Managed via `mc.commands.set_channel()` |
| Connection | Sync, blocking | Async, `await MeshCore.create_*()` |

**Critical implication**: `message_from_id` changes from `int` to `str` (public key prefix). This propagates into every command handler, all game trackers, ban/admin lists, BBS, and `seenNodes`. The plan handles this explicitly in Phase 3.

---

## Phases

### Phase 0 — Dependencies & Config

**Files**: `requirements.txt`, `config.template`, `modules/settings.py`

- [ ] Remove `meshtastic` and `PyPubSub` from `requirements.txt`
- [ ] Add `meshcore` (meshcore_py) to `requirements.txt`
- [ ] Add `pycryptodome` (needed for DM decryption, already used by Remote-Terminal)
- [ ] In `config.template`, replace `[interface]` Meshtastic settings with MeshCore equivalents:
  ```ini
  [interface]
  # type: serial | tcp | ble
  type = serial
  port = /dev/ttyACM0
  # tcp: hostname = 192.168.1.1
  # tcp: port = 5000
  # ble: mac = AA:BB:CC:DD:EE:FF
  # ble: pin = 1234
  ```
- [ ] In `modules/settings.py`, update any Meshtastic-specific defaults (e.g., `publicChannel`, `wantAck`, port names)
- [ ] Verify no other module imports from `meshtastic` directly (grep: `import meshtastic`)

---

### Phase 1 — Radio Layer (`modules/system.py`)

This file owns all Meshtastic interface calls. Replace top-to-bottom.

#### 1a. Imports and connection

**Remove**:
```python
import meshtastic.serial_interface
import meshtastic.tcp_interface
import meshtastic.ble_interface
from pubsub import pub
```

**Add**:
```python
import asyncio
from meshcore import MeshCore, EventType
```

**Remove** the entire interface init loop (lines ~334–371 in system.py) that creates `interface1`–`interface9`.

**Add** a single async connect helper:
```python
_mc = None  # global MeshCore connection handle

async def connect_radio():
    global _mc
    if interface1_type == 'serial':
        _mc = await MeshCore.create_serial(port=port1 or None)
    elif interface1_type == 'tcp':
        host = hostname1.split(':')[0] if ':' in str(hostname1) else hostname1
        tcp_port = int(hostname1.split(':')[1]) if ':' in str(hostname1) else 5000
        _mc = await MeshCore.create_tcp(host=host, port=tcp_port)
    elif interface1_type == 'ble':
        _mc = await MeshCore.create_ble(address=mac1, pin=str(ble_pin1))
    return _mc
```

Reference: `../Remote-Terminal-for-MeshCore/app/radio.py` — `RadioManager._connect()`

#### 1b. `get_my_node_info()`

**Remove**: `interface.getMyNodeInfo()['num']`

**Add**: Get the bot's own public key after connect:
```python
_my_public_key = None  # set after connect

async def fetch_own_identity():
    global _my_public_key
    info = await _mc.commands.get_device_info()
    _my_public_key = info.get('public_key', '')
```

Reference: `../Remote-Terminal-for-MeshCore/app/services/radio_commands.py`

#### 1c. `send_message()`

**Current signature**: `send_message(message, ch, nodeid=0, nodeInt=1, bypassChuncking=False, reply_id=None)`

- `nodeid=0` means channel send; `nodeid != 0` means DM.
- `ch` is the channel slot index.

**Replace** `interface.sendText()` / `interface.sendData()`:
```python
async def send_message(message, ch, nodeid=None, nodeInt=1, bypassChuncking=False, reply_id=None):
    if not _mc:
        logger.error("send_message: radio not connected")
        return False
    chunks = messageChunker(message) if not bypassChuncking else [message]
    if isinstance(chunks, str):
        chunks = [chunks]
    for chunk in chunks:
        try:
            if nodeid:
                await _mc.commands.send_msg(nodeid, chunk)   # DM by pubkey
            else:
                await _mc.commands.send_chan_msg(ch, chunk)  # channel by slot index
            await asyncio.sleep(splitDelay)
        except Exception as e:
            logger.error(f"send_message error: {e}")
            return False
    return True
```

> **Note**: `reply_id` threading is Meshtastic-specific. MeshCore has no equivalent. Drop it silently for now.

All callers of `send_message()` in `mesh_bot.py` must be updated to `await send_message(...)`. Because `auto_response()` returns a string and its callers send it, the callers become async (see Phase 2).

#### 1d. `send_raw_bytes()`

MeshCore has no raw portnum-based data send equivalent for bot use. This is only used by the `echo` binary mode (which is gated behind `echoBinary = False`) and by `modules/udp.py`. Mark as not-implemented stub:
```python
async def send_raw_bytes(nodeid, raw_bytes, nodeInt=1, channel=0, portnum=256, want_ack=True, reply_id=None):
    logger.warning("send_raw_bytes: not supported on MeshCore, skipping")
    return False
```

#### 1e. Contact / node lookup

**Remove**: All uses of `interface.nodes`.

**Add**: In-memory contact cache built from MeshCore events:
```python
_contacts: dict[str, dict] = {}
# key = full pubkey hex (64 chars)
# value = {'name': str, 'lat': float, 'lon': float, 'last_seen': float}
```

**Replace** `get_name_from_number(number, type, nodeInt)`:
```python
def get_name_from_number(pubkey, type='long', nodeInt=1):
    # pubkey is now a hex string (full or 12-char prefix)
    contact = _get_contact(pubkey)
    if contact:
        return contact.get('name', pubkey[:12])
    return pubkey[:12] if pubkey else '?'
```

**Replace** `get_num_from_short_name(short_name, nodeInt)`:
```python
def get_num_from_short_name(name, nodeInt=1):
    # Returns a pubkey prefix matching the name
    for pubkey, contact in _contacts.items():
        if contact.get('name', '').lower() == name.lower():
            return pubkey
    return None
```

**Replace** `decimal_to_hex(decimal_number)`:
```python
def pubkey_short(pubkey):
    """Returns the 12-char prefix used as the short public identity."""
    return pubkey[:12] if pubkey else '?'
```
> Update all call sites of `decimal_to_hex()` to use `pubkey_short()` or display the prefix directly.

**Replace** `get_node_list()`:
```python
def get_node_list(nodeInt=1):
    if not _contacts:
        return ERROR_FETCHING_DATA
    recent = sorted(_contacts.values(), key=lambda c: c.get('last_seen', 0), reverse=True)
    lines = [f"{c.get('name', '?')} SNR:{c.get('last_snr', 0)}" for c in recent[:SITREP_NODE_COUNT]]
    return "\n".join(lines)
```

**Replace** `get_node_location(nodeID, nodeInt, channel, round_digits)`:
```python
def get_node_location(pubkey, nodeInt=1, channel=0, round_digits=2):
    contact = _get_contact(pubkey)
    if contact and contact.get('lat') and contact.get('lat') != 0.0:
        lat, lon = contact['lat'], contact['lon']
        if fuzzItAll:
            lat, lon = round(lat, round_digits), round(lon, round_digits)
        return [lat, lon]
    if fuzz_config_location:
        return [round(latitudeValue, round_digits), round(longitudeValue, round_digits)]
    return [latitudeValue, longitudeValue]
```

#### 1f. Channel cache

**Remove**: `build_channel_cache()`, `refresh_channel_cache()`, `resolve_channel_name()`, `channel_list`.

For DM-only mode, channel sends are not the primary path. Add a simple channel slot tracker:
```python
_channel_slots: dict[str, int] = {}
# key = channel name; value = slot index

async def ensure_channel_slot(channel_name: str, channel_key: str, preferred_slot: int) -> int:
    """Load a channel into a radio slot if not already loaded."""
    if channel_name in _channel_slots:
        return _channel_slots[channel_name]
    await _mc.commands.set_channel(preferred_slot, channel_name, channel_key)
    _channel_slots[channel_name] = preferred_slot
    return preferred_slot
```

Reference: `../Remote-Terminal-for-MeshCore/app/services/message_send.py` channel slot logic.

#### 1g. `onDisconnect()` / reconnect

**Remove**: `onDisconnect(interface)` (Meshtastic callback).

**Add**: Async reconnect monitor (called from `main()` as a background task):
```python
_connected = False

async def connection_monitor():
    global _mc, _connected
    while True:
        await asyncio.sleep(5)
        if _mc is None or not _connected:
            logger.warning("System: Radio disconnected, attempting reconnect...")
            try:
                await connect_radio()
                await fetch_own_identity()
                await register_event_handlers()
                _connected = True
                logger.info("System: Reconnected to radio")
            except Exception as e:
                logger.error(f"System: Reconnect failed: {e}")
                _connected = False
```

Reference: `../Remote-Terminal-for-MeshCore/app/radio.py` — `_connection_monitor()`

#### 1h. Telemetry / firmware / favorites

- `displayNodeTelemetry()`: stub — MeshCore has `get_device_info()`, but the Meshtastic telemetry fields (channelUtilization, airUtilTx) are not equivalent. Simplify to return what's available or log only.
- `getNodeFirmware()`: Use `mc.commands.get_device_info()` to get firmware version.
- `handleFavoriteNode()` / `getFavoriteNodes()`: MeshCore has no direct favorites API for the bot. Remove or stub.

---

### Phase 2 — Event Handler (`mesh_bot.py`)

#### 2a. Remove PyPubSub

**Remove**:
```python
from pubsub import pub
# and in start_rx():
pub.subscribe(onReceive, 'meshtastic.receive')
pub.subscribe(onDisconnect, 'meshtastic.connection.lost')
```

#### 2b. Replace `onReceive(packet, interface)`

The current Meshtastic `onReceive` receives a raw packet dict. Replace with two MeshCore event handlers:

**Primary path — raw packet (preferred, gives SNR/RSSI/path)**:
```python
async def on_rx_log_data(event):
    """Primary inbound path via raw RF packet."""
    # Parse SNR, RSSI, path (hop count) from raw bytes
    # See ../Remote-Terminal-for-MeshCore/app/packet_processor.py for full decode
    from modules.system import _mc, _my_public_key, _contacts
    payload = event.payload
    raw_bytes = payload.data if hasattr(payload, 'data') else bytes(payload)
    
    # Use decoder from Remote-Terminal to extract PacketInfo
    # packet_info.rssi, packet_info.snr, packet_info.path_len
    # packet_info.payload_type (PayloadType.PRIV or GroupText)
    # ... then call _dispatch_message(text, sender_key, snr, rssi, hop, is_dm)
```

**Fallback path — decoded DM (no raw packet access)**:
```python
async def on_contact_message(event):
    """Fallback DM handler when RX_LOG_DATA is not available."""
    payload = event.payload
    sender_key = payload.pubkey_prefix   # 12-char hex
    text = payload.text
    await _dispatch_dm(text, sender_key, snr=0, rssi=0, hop="Direct", is_dm=True)
```

Reference: `../Remote-Terminal-for-MeshCore/app/event_handlers.py` — `on_contact_message()`  
Reference: `../Remote-Terminal-for-MeshCore/app/packet_processor.py` — `process_raw_packet()`

#### 2c. `_dispatch_dm()` — the new core dispatcher

Extract the DM-handling logic from the current monolithic `onReceive()` into a focused async function:
```python
async def _dispatch_dm(text, sender_key, snr, rssi, hop, channel_number=0, device_id=1):
    global seenNodes, cmdHistory
    
    # Update seenNodes (now keyed on pubkey string)
    _update_seen_nodes(sender_key, channel_number)

    # BBS DM mail delivery
    if bbs_enabled:
        msg = bbs_check_dm(sender_key)
        if msg:
            await send_message(f"Mail: {msg[1]}  From: {get_name_from_number(msg[2])}", 0, sender_key, device_id)
            bbs_delete_dm(msg[0], msg[1])

    # Ban check
    if str(sender_key) in bbs_ban_list or str(sender_key) in autoBanlist:
        return

    # Safety check
    if not stringSafeCheck(text, sender_key):
        return

    # Ignore own messages
    if sender_key == _my_public_key or sender_key.startswith(_my_public_key[:12]):
        return

    # Dispatch to auto_response
    if messageTrap(text) or (games_enabled and checkPlayingGame(sender_key, text, device_id, channel_number)):
        response = auto_response(text, snr, rssi, hop, (False, sender_key), sender_key, channel_number, device_id, True)
        if response:
            await send_message(response, 0, sender_key, device_id)
    elif llm_enabled and llmReplyToNonCommands:
        response = handle_llm(sender_key, channel_number, device_id, text, publicChannel)
        if response:
            await send_message(response, 0, sender_key, device_id)
    else:
        # Welcome / help
        if not any(n['nodeID'] == sender_key and n.get('welcome') for n in seenNodes):
            await send_message(welcome_message, 0, sender_key, device_id)
            for n in seenNodes:
                if n['nodeID'] == sender_key:
                    n['welcome'] = True
```

#### 2d. Register event handlers

```python
async def register_event_handlers():
    _mc.subscribe(EventType.RX_LOG_DATA, on_rx_log_data)
    _mc.subscribe(EventType.CONTACT_MSG_RECV, on_contact_message)
    _mc.subscribe(EventType.ACK, on_ack)
    logger.debug("System: Event handlers registered")
```

Also subscribe to contact events to build the `_contacts` cache:
```python
async def on_contact_update(event):
    contact = event.payload
    pubkey = contact.public_key or contact.pubkey_prefix
    _contacts[pubkey] = {
        'name': contact.name or pubkey[:12],
        'lat': getattr(contact, 'lat', 0.0),
        'lon': getattr(contact, 'lon', 0.0),
        'last_seen': time.time(),
        'last_snr': getattr(contact, 'last_snr', 0),
    }
```

Reference: `../Remote-Terminal-for-MeshCore/app/event_handlers.py` — contact upsert logic.

#### 2e. Replace `start_rx()`

**Remove**:
```python
async def start_rx():
    pub.subscribe(onReceive, 'meshtastic.receive')
    pub.subscribe(onDisconnect, 'meshtastic.connection.lost')
    while True:
        await asyncio.sleep(0.5)
```

**Replace with** event-driven startup in `main()`:
```python
async def main():
    await connect_radio()
    await fetch_own_identity()
    await register_event_handlers()
    # sync contacts on startup
    await _mc.commands.get_contacts()
    # ... then create background tasks as before
```

---

### Phase 3 — Node Identity Adaptation

This is the widest-touching change. Every place the code uses `message_from_id` as an integer node number must accept a string public key.

#### 3a. `seenNodes`

**Before**: `{'nodeID': 2813308004, 'rxInterface': 1, 'channel': 0, 'welcome': False, ...}`  
**After**: `{'nodeID': 'aabbccdd1234', 'rxInterface': 1, 'channel': 0, 'welcome': False, ...}`

The `nodeID` key value changes from `int` to `str` (12-char pubkey prefix). No structural change needed.

#### 3b. Game trackers

All game trackers use `nodeID` as a key (or `userID` for DopeWars):
- `dwPlayerTracker`: `{'userID': sender_key, ...}`
- `jackTracker`, `vpTracker`, `lemonadeTracker`, `golfTracker`, `hangmanTracker`, `hamtestTracker`, `tictactoeTracker`, `mindTracker`, `battleshipTracker`, `surveyTracker`: `{'nodeID': sender_key, ...}`

No structural changes needed — the keys become strings instead of ints, which Python handles naturally.

#### 3c. Admin and ban lists

`bbs_admin_list` and `bbs_ban_list` are loaded from `config.ini` as comma-separated values. Users will need to provide **12-char public key prefixes** (or full keys) instead of Meshtastic node numbers.

Update `config.template`:
```ini
[bbs]
# bbs_admin_list: comma-separated MeshCore public key prefixes (12 hex chars)
# example: bbs_admin_list = aabbccdd1234,112233445566
bbs_admin_list =
bbs_ban_list =
```

Update `isNodeAdmin()` and `isNodeBanned()`:
```python
def isNodeAdmin(pubkey):
    pubkey_prefix = str(pubkey)[:12].lower()
    for admin in bbs_admin_list:
        if admin.strip().lower() == pubkey_prefix or str(pubkey).lower().startswith(admin.strip().lower()):
            return True
    return False
```

#### 3d. BBS system (`modules/bbstools.py`)

BBS stores messages and DMs keyed on node identifiers. Audit `bbstools.py` for any `int()` casts or numeric-only assumptions on node IDs. Change storage key to string pubkey prefix.

#### 3e. `handle_whoami()` display

**Before**: Shows integer ID, longName, shortName, `!hex` format  
**After**: Shows pubkey prefix, name from contact cache
```python
def handle_whoami(message_from_id, deviceID, hop, snr, rssi, pkiStatus):
    name = get_name_from_number(message_from_id)
    prefix = message_from_id[:12] if message_from_id else '?'
    msg = f"You are {name} key:{prefix}\n"
    msg += f"SNR:{snr} RSSI:{rssi} {hop}"
    loc = get_node_location(message_from_id, deviceID)
    if loc != [latitudeValue, longitudeValue]:
        msg += f"\nGPS: {loc[0]}, {loc[1]}"
    return msg
```

#### 3f. `handle_whois()`

**Before**: Looks up by short name or `!hex` integer  
**After**: Looks up by name in `_contacts` or by pubkey prefix

---

### Phase 4 — Signal Info (SNR / RSSI / Hop)

#### 4a. SNR and RSSI from raw packets

MeshCore delivers SNR and RSSI via `RX_LOG_DATA`. The decoder in Remote-Terminal extracts them:

Reference: `../Remote-Terminal-for-MeshCore/app/decoder.py` — `parse_packet()` returns `PacketInfo` with `rssi: int`, `snr: float`.

For the bot, either:
1. **Copy the relevant decoder function** from `Remote-Terminal-for-MeshCore/app/decoder.py` into `modules/decoder.py` (minimal subset).
2. **Or** fall back to `snr=0, rssi=0` from `CONTACT_MSG_RECV` and only populate them when `RX_LOG_DATA` provides them.

#### 4b. Hop count

**Before**: Computed from `hopStart`, `hopLimit`, `hopsAway` fields in the Meshtastic packet.  
**After**: `path_len` from `PacketInfo` (from `parse_packet()` on `RX_LOG_DATA`).

Map:
- `path_len == 0` → `"Direct"` (direct RF)
- `path_len == 1` → `"1 Hop"`
- `path_len > 1` → `"N Hops"`

The `handle_ping()` response format (`[RF]`, `[F]`, `[GW]`) maps to:
- `"Direct"` → `[RF]`
- `"N Hops"` → `[F]` (flooded)
- Gateway/MQTT cases are less common in MeshCore — default to `[F]`

---

### Phase 5 — Async Propagation

The current `send_message()` is synchronous and uses `time.sleep()`. After Phase 1 makes it async, every caller must `await` it.

**Callers to update** (all in `mesh_bot.py`):
- `onReceive()` body → `_dispatch_dm()` (already async in Phase 2)
- All `handle_*()` functions that call `send_message()` directly (not via `auto_response()`) — e.g., `handle_emergency()`, `handleBattleship()` (P2P notify), `quizHandler()` (broadcast)
- Background tasks: `handleAlertBroadcast()`, `handleMultiPing()`, scheduler loop

**Strategy**: Make `auto_response()` return a string as before (it does not call `send_message()` itself). Only the callers of `send_message()` outside of `auto_response()` need to become async. There are ~10 such places.

**Replace** all `time.sleep(splitDelay)` → `await asyncio.sleep(splitDelay)` in async contexts.

---

### Phase 6 — Reconnect & Watchdog

#### 6a. Watchdog task

The current `watchdog()` in `mesh_bot.py` handles periodic tasks (multi-ping, alert broadcasts, memory cleanup, scheduler checks). Keep this structure. Replace the interface-check logic:

**Before**:
```python
# Check if interfaces are alive (Meshtastic-specific)
for i in range(1, 10):
    if interface[i] and not interface[i].isConnected():
        ...
```

**After**:
```python
# Check MeshCore connection
if not _connected:
    logger.warning("Watchdog: Radio not connected")
    # connection_monitor() task handles reconnect
```

#### 6b. Connection monitor

Already defined in Phase 1g. Add it as a named asyncio task in `main()`:
```python
tasks.append(asyncio.create_task(connection_monitor(), name="connection_monitor"))
```

---

### Phase 7 — Pong Bot (`pong_bot.py`)

`pong_bot.py` is a stripped-down version of `mesh_bot.py`. Apply the same changes:
- Remove `pub.subscribe`
- Replace `onReceive` with MeshCore event handlers
- Replace `interface.sendText()` with `await mc.commands.send_msg()`
- Remove interface init loop

Because the pong bot is simpler, tackle it after `mesh_bot.py` is working.

---

### Phase 8 — Scheduler Module (`modules/scheduler.py`)

The scheduler calls `send_message()` to broadcast timed messages. After Phase 5, update calls to `await send_message()`. Scheduler must run inside the asyncio event loop (it already does via `run_scheduler_loop()` task).

---

### Phase 9 — Testing

- [ ] Run `python3 -m pytest modules/test_bot.py -v` — module import tests should still pass (no radio needed)
- [ ] Connect a MeshCore radio and run `mesh_bot.py` — verify DM receive and respond
- [ ] Test `ping` command: verify SNR/RSSI/hop display
- [ ] Test `whoami`: verify pubkey prefix display
- [ ] Test BBS: `bbspost`, `bbsread`, `bbslist`
- [ ] Test a game: `blackjack`
- [ ] Test admin command with a key in `bbs_admin_list`

---

## Files Changed Summary

| File | Change |
|---|---|
| `requirements.txt` | Remove `meshtastic`, `PyPubSub`; add `meshcore`, `pycryptodome` |
| `config.template` | Update `[interface]` section; update admin/ban list format |
| `modules/system.py` | Full radio layer rewrite (Phases 1a–1h) |
| `modules/settings.py` | Remove Meshtastic-specific defaults |
| `mesh_bot.py` | Replace event subscription and onReceive (Phase 2); async propagation (Phase 5) |
| `pong_bot.py` | Same as mesh_bot.py, simpler (Phase 7) |
| `modules/scheduler.py` | Await send_message (Phase 8) |
| `modules/bbstools.py` | String node IDs (Phase 3d) |
| `modules/decoder.py` | New file — minimal decoder for SNR/RSSI/hop from RX_LOG_DATA (Phase 4) |
| `modules/test_bot.py` | Update for new identity model (Phase 9) |

**Files that do NOT change**: All game modules, weather modules, LLM, BBS logic, wiki, RSS, etc. The feature layer is untouched.

---

## Reference Checklist (grep targets before starting each phase)

```bash
# All Meshtastic imports
grep -rn "import meshtastic" meshing-around-mc/

# All pubsub uses
grep -rn "from pubsub\|pub.subscribe" meshing-around-mc/

# All interface object uses (beyond system.py)
grep -rn "interface\." meshing-around-mc/modules/

# All send_message calls (to update to await)
grep -rn "send_message(" meshing-around-mc/

# All decimal_to_hex calls (to replace with pubkey_short)
grep -rn "decimal_to_hex" meshing-around-mc/

# All get_name_from_number calls
grep -rn "get_name_from_number" meshing-around-mc/

# All isNodeAdmin / isNodeBanned calls
grep -rn "isNodeAdmin\|isNodeBanned" meshing-around-mc/
```
