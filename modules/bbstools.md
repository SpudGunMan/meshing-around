
---

# meshBBS: How-To & Documentation

This document covers the Bulletin Board System (BBS) component of the meshing-around bot, including the **bbslink** feature for syncing posts between two bots over the air (OTA).

## Table of Contents

1. [BBS Core Functions](#1-bbs-core-functions)
    - [Central Message Store](#11-central-message-store)
    - [Direct Mail (DM) Messages](#12-direct-mail-dm-messages)
    - [BBS Commands](#bbs-commands)
2. [BBSLink: OTA Sync Between Bots](#2-bbslink-ota-sync-between-bots)
    - [Overview](#21-overview)
    - [Prerequisites](#22-prerequisites)
    - [Configuration](#23-configuration)
    - [Finding a Peer's Pubkey Prefix](#24-finding-a-peers-pubkey-prefix)
    - [Access Modes](#25-access-modes)
    - [How the Sync Protocol Works](#26-how-the-sync-protocol-works)
    - [What to Expect](#27-what-to-expect)
3. [Automatic Sync with the Scheduler](#3-automatic-sync-with-the-scheduler)
4. [Manual Sync Trigger](#4-manual-sync-trigger)
5. [BBS Database Sync: File-Based (Out-of-Band)](#5-bbs-database-sync-file-based-out-of-band)
6. [Troubleshooting](#6-troubleshooting)
7. [API Reference](#7-api-reference)

---

## 1. BBS Core Functions

### 1.1 Central Message Store

- Shared public message board for all nodes on the mesh.
- Simple one-level message list — no threading.
- Messages are stored in `data/bbsdb.pkl`.
- Each entry: `[id, subject, body, fromNode, timestamp, threadID, replytoID]`

**Post a public message:**
```
bbspost $Subject #Message body here
```

### 1.2 Direct Mail (DM) Messages

- Private messages from one node to another, stored in `data/bbsdm.pkl`.
- When the recipient node comes online, the bot delivers the DM and removes it from storage.
- Each DM entry: `[toNode, message, fromNode]`

**Post a DM:**
```
bbspost @Username #Message body here
```

### BBS Commands

| Command      | Description                            |
|--------------|----------------------------------------|
| `bbshelp`    | Show BBS help                          |
| `bbslist`    | List all public message subjects       |
| `bbsread #N` | Read public message by ID              |
| `bbspost`    | Post a public message or send a DM     |
| `bbsdelete #N` | Delete a message (owner or admin)    |
| `bbsinfo`    | Show message and DM counts             |

---

## 2. BBSLink: OTA Sync Between Bots

### 2.1 Overview

BBSLink lets two MeshBot instances exchange their public BBS posts over the air, one post at a time, using DM messages. A sync session pulls all posts from a peer bot into your local board. Duplicate posts are silently ignored, so you can run sync repeatedly without building up duplicates.

Sync is **one-directional per session**: the initiating bot pulls from the peer. For bidirectional sync, configure both bots to pull from each other on a schedule.

### 2.2 Prerequisites

- Both bots must be running MeshCore (this feature does not work with Meshtastic).
- Both bots must have `[bbs] enabled = True` in `config.ini`.
- The **receiving** bot (the one being pulled from) must have `bbslink_enabled = True`.
- Both bots must be reachable via DM on the mesh.

### 2.3 Configuration

Add the following to the `[bbs]` section of `config.ini` on each bot:

```ini
[bbs]
enabled = True
bbslink_enabled = True

# Peer BBS bots to sync with (comma-separated pubkey prefixes, 12-char hex).
# Also acts as the inbound whitelist — only listed nodes may sync with this bot.
# Leave empty to allow any node to sync (open mode).
bbslink_peers = a1b2c3d4e5f6,b2c3d4e5f6a7
```

**Bot A config** — wants to pull from Bot B:
```ini
bbslink_enabled = True
bbslink_peers = <Bot B's pubkey prefix>
```

**Bot B config** — the source of posts:
```ini
bbslink_enabled = True
bbslink_peers = <Bot A's pubkey prefix>   # restricts inbound; omit to allow all
```

### 2.4 Finding a Peer's Pubkey Prefix

MeshCore identifies nodes by a **12-character hex pubkey prefix** (e.g. `a1b2c3d4e5f6`). This is visible in:

- The MeshCore web interface or Remote Terminal — shown in the contacts list next to a node's name.
- Bot logs — when a node sends a message, its pubkey prefix is logged: `From: a1b2c3d4e5f6`
- The `whoami` or `whois` bot command — returns identity info including the pubkey prefix.

This is **not** the same as a Meshtastic numeric node ID.

### 2.5 Access Modes

| `bbslink_peers` value | Behavior |
|-----------------------|----------|
| Empty (default)       | **Open mode** — any node can initiate a sync with this bot |
| One or more prefixes  | **Closed mode** — only listed nodes can sync; others get "BBS Link is disabled for your node" |

`bbslink_peers` serves double duty: it's both the list of peers the scheduler actively contacts, and the inbound access control list.

### 2.6 How the Sync Protocol Works

Sync is driven by a DM ping-pong exchange:

```
Initiator (Bot A)          Peer (Bot B)
─────────────────          ────────────
bbslink 0          →       (receives request)
                   ←       bbslink 0 $Subject #Body @originPrefix
bbsack 0           →       (acknowledges, peer sends next)
                   ←       bbslink 1 $Subject2 #Body2 @originPrefix2
bbsack 1           →
                   ←       bbslink 2 $...
...
bbsack N           →       (N+1 >= total messages — sync complete, no reply)
```

**Rate limiting** — the peer bot paces its replies to avoid mesh congestion:
- 5 seconds (+ `responseDelay`) between each message
- An additional 10 second pause every 5 messages

So a board with 20 posts takes roughly **2–3 minutes** to fully sync.

**Message format** (internal, not user-typed):
```
bbslink <N> $<subject> #<body> @<originPubkeyPrefix>
```

**ACK format:**
```
bbsack <N>
```

### 2.7 What to Expect

- Sync pulls **all posts from the peer's board**, starting at index 0.
- Posts already on your board with the same subject and body are silently skipped (dedup by content hash).
- The origin author of a synced post is preserved — the `@originPrefix` field in the wire format stores who originally wrote it.
- While a sync is in progress the bot remains responsive to other commands — the async delays do not block the event loop.
- Channel bbslink messages also work (for broadcast-mode discovery). The bot always replies via DM, not on the channel, to avoid spamming it.

---

## 3. Automatic Sync with the Scheduler

Use the `link` scheduler value to have the bot initiate sync automatically on a recurring schedule.

**With `bbslink_peers` configured** — sends `bbslink 0` as a DM to each peer:
```ini
[bbs]
bbslink_enabled = True
bbslink_peers = a1b2c3d4e5f6

[scheduler]
enabled = True
interface = 1
channel = 0       # channel is unused for DM mode but required
value = link
interval = 6      # every 6 hours
```

**Without `bbslink_peers`** (open/broadcast mode) — sends `bbslink MeshBot looking for peers` as a channel message. Any bot with `bbslink_enabled = True` that sees the message will respond and push its posts:
```ini
[bbs]
bbslink_enabled = True

[scheduler]
enabled = True
interface = 1
channel = 8       # dedicated mesh-admin channel recommended
value = link
interval = 12     # every 12 hours
```

The `interval` is always in **hours**.

---

## 4. Manual Sync Trigger

To manually pull all posts from a peer bot, send it a DM:
```
bbslink 0
```

The peer will begin sending its posts back to you one at a time. You do not need to send anything else — the ACKs are handled automatically by your bot.

To check if bbslink is working from the peer's side without triggering a full sync, you can also send:
```
bbslink MeshBot looking for peers
```
The peer will respond with its first post if `bbslink_enabled = True`.

---

## 5. BBS Database Sync: File-Based (Out-of-Band)

For full bulk sync or backup, copy the database files directly between hosts.

Enable the API watcher so the bot picks up externally modified files:
```ini
[bbs]
bbsAPI_enabled = True
```

**Copy files manually:**
```sh
scp user@remote:/path/to/meshing-around-mc/data/bbsdb.pkl ./data/bbsdb.pkl
scp user@remote:/path/to/meshing-around-mc/data/bbsdm.pkl ./data/bbsdm.pkl
```

When `bbsAPI_enabled = True`, the watchdog detects file changes and reloads the database automatically. Useful for a nightly cron job or rsync.

You can also inject a DM directly using `script/injectDM.py` without going over the air.

---

## 6. Troubleshooting

**Peer replies "BBS Link is disabled for your node."**
- The peer has `bbslink_peers` set and your bot's pubkey prefix is not in the list.
- Add your prefix to the peer's `bbslink_peers`, or clear the list for open mode.

**No response at all to `bbslink 0`**
- Check that the peer has `bbslink_enabled = True`.
- Confirm you are sending it as a **DM** to the peer's pubkey prefix, not as a channel message to address `0`.
- Check the peer's logs for `BBS Link is disabled` or connection errors.

**Sync starts but stops partway through**
- Normal — if the mesh drops a message, the session stalls. Restart by sending `bbslink 0` again.
- The bot resumes from the beginning (message 0), but duplicates are skipped, so restarting is safe.

**Posts appear with wrong author names**
- Author identity is stored as the pubkey prefix at time of original posting. If the name hasn't been seen on your local mesh yet, it will display as the raw prefix until that node advertises itself.

**File sync not reloading after scp**
- Ensure `bbsAPI_enabled = True`.
- Confirm the watchdog task is running (check logs for "data persistence" task).

---

## 7. API Reference

### BBS Functions (`modules/bbstools.py`)

| Function | Purpose |
|---|---|
| `bbs_post_message(subject, body, fromNode)` | Post a new public message |
| `bbs_read_message(messageID)` | Read a message by ID |
| `bbs_delete_message(messageID, fromNode)` | Delete (owner or admin only) |
| `bbs_list_messages()` | Return formatted subject list |
| `bbs_post_dm(toNode, message, fromNode)` | Queue a DM for delivery |
| `bbs_check_dm(toNode)` | Check for pending DM for a node |
| `bbs_delete_dm(toNode, message)` | Remove a delivered DM |
| `get_bbs_stats()` | Return post and DM counts |
| `bbs_sync_posts(input, peerNode, rxNode)` | Handle inbound bbslink/bbsack (async) |

### Compression (future use)

`useSynchCompression = False` in `bbstools.py`. When enabled:
- `compress_data(msg)` → zlib bytes
- `bbs_receive_compressed(data_bytes, fromNode, rxNode)` → decompress + sync

Not active in current builds.

---
