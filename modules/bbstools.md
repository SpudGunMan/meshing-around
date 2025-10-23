
---

# 📡 meshBBS: How-To & API Documentation

This document covers the Bulliten Board System or BBS componment of the meshing-around project.

## Table of Contents

1. [BBS Core Functions](#1-bbs-core-functions)
    - [Direct Messages (DMs)](#11-direct-messages-dms)
2. [BBS Database Sync: File-Based (Out-of-Band)](#1-bbs-database-sync-file-based-out-of-band)
3. [BBS Over-the-Air (OTA) Sync: Linking](#2-bbs-over-the-air-ota-sync-linking)
4. [Scheduling BBS Sync](#3-scheduling-bbs-sync)
5. [Best Practices](#4-best-practices)
6. [Example: Full Sync Workflow](#5-example-full-sync-workflow)
7. [Troubleshooting](#6-troubleshooting)
8. [API Reference: BBS Sync](#7-api-reference-bbs-sync)

## 1. **BBS Core Functions**

## 1.1 **Direct Messages (DMs)**

### **How DMs Work**
- Direct Messages (DMs) are private messages sent from one node to another.
- DMs are stored separately from public posts in `data/bbsdm.pkl`.
- Each DM entry typically includes: `[id, toNode, message, fromNode, timestamp, threadID, replytoID]`.

### **DM Delivery**
- When a DM is posted using `bbs_post_dm(toNode, message, fromNode)`, it is added to the recipient's DM database.
- DMs can be delivered in two ways:
  1. **File-Based Sync:**  
     - The `bbsdm.pkl` file is copied between nodes using SCP, rsync, or other file transfer methods.
     - After syncing, the recipient node can check for new DMs using `bbs_check_dm(toNode)`.
  2. **Over-the-Air (OTA) Sync:**  
     - DMs can be exchanged between nodes using the same OTA sync mechanism as public posts.
     - The `bbslink` command can include DMs, and the recipient node processes and stores them in `bbsdm.pkl`.
- DMs are only visible to the intended recipient node and are not listed in the public message list.

### **DM Commands**
| Command         | Description                                 |
|-----------------|---------------------------------------------|
| `bbs_post_dm`   | Send a direct message to another node       |
| `bbs_check_dm`  | Check for new DMs for your node             |
| `bbs_delete_dm` | Delete a DM after reading                   |

---


### **Message Storage**
The .. database is
- Messages are stored in `data/bbsdb.pkl` (public posts) and `data/bbsdm.pkl` (direct messages).
- Format: Each message is a list, e.g. `[id, subject, body, fromNode, timestamp, threadID, replytoID]`.


| Command      | Description                                   |
|--------------|-----------------------------------------------|
| `bbshelp`    | Show BBS help                                 |
| `bbslist`    | List messages                                 |
| `bbsread`    | Read a message by ID                          |
| `bbspost`    | Post a message or DM                          |
| `bbsdelete`  | Delete a message                              |
| `bbsinfo`    | BBS stats (sysop)                             |
| `bbslink`    | Link messages between BBS systems             |

---
Enable in `[bbs]` section of `config.ini`.

## 1. **BBS Database Sync: File-Based (Out-of-Band)**

### **Manual/Automated File Sync (e.g., SSH/SCP)**
- **Purpose:** Sync BBS data between nodes by copying `bbsdb.pkl` and `bbsdm.pkl` files.
- **How-To:**
  1. **Locate Files:**  
     - `data/bbsdb.pkl` (public posts)
     - `data/bbsdm.pkl` (direct messages)
  2. **Copy Files:**  
     Use `scp` or `rsync` to copy files between nodes:
     ```sh
     scp user@remote:/path/to/meshing-around/data/bbsdb.pkl ./data/bbsdb.pkl
     scp user@remote:/path/to/meshing-around/data/bbsdm.pkl ./data/bbsdm.pkl
     ```
  3. **Reload Database:**  
     After copying, when the "API" is enabled the watchdog will look for changes and injest.

- **Automating with Cron/Scheduler:**
  - Set up a cron job or use the bot’s scheduler to periodically pull/push files.

---

## 2. **BBS Over-the-Air (OTA) Sync: Linking**
### **How OTA Sync Works**
- Nodes can exchange BBS messages using special commands over the mesh network.
- Uses `bbslink` and `bbsack` commands for message exchange.
- Future supports compression for bandwidth efficiency.

### **Enabling BBS Linking**
- Set `bbs_link_enabled = True` in your config.
- Optionally, set `bbs_link_whitelist` to restrict which nodes can sync.

### **Manual Sync Command**
- To troubleshoot request sync from another node, send:
  ```
  bbslink <messageID> $<subject> #<body>
  ```
- The receiving node will respond with `bbsack <messageID>`.

### **Out-of-Band Channel**
- For high-reliability sync, configure a dedicated channel (not used for chat).
---

## 3. **Scheduling BBS Sync**

### **Using the Bot’s Scheduler**

- You can schedule periodic sync requests to a peer node.
- Example: Every hour, send a `bbslink` request to a peer.
see more at [Module Readme](README.md#scheduler)
---

## 4. **Best Practices**

- **Backup:** Regularly back up `bbsdb.pkl` and `bbsdm.pkl`.
- **Security:** Use SSH keys for file transfer; restrict OTA sync to trusted nodes.
- **Reliability:** Use a dedicated channel for BBS sync to avoid chat congestion.
- **Automation:** Use the scheduler for regular syncs, both file-based and OTA.

---

## 5. **Example: Full Sync Workflow**

1. **Set up a dedicated sync channel** (e.g., channel bot-admin).
2. **Configure both nodes** with `bbs_link_enabled = True` and add each other to `bbs_link_whitelist`.
3. **Schedule sync** every hour:
   - Node A sends `bbslink 0` to Node B on channel 99.
   - Node B responds with messages and `bbsack`.
4. **Optionally, use SSH/scp** to copy `bbsdb.pkl` for full out-of-band backup.

---

## 6. **Troubleshooting**

- **Messages not syncing?**
  - Check `bbs_link_enabled` and whitelist settings.
  - Ensure both nodes are on the same sync channel.
  - Check logs for errors.

- **File sync issues?**
  - Verify file permissions and paths.
  - Ensure the bot reloads the database after file copy.

## 7. **API Reference: BBS Sync**

### **Key Functions in Python**
| Function                | Purpose                                   | Usage Example                                      |
|-------------------------|-------------------------------------------|----------------------------------------------------|
| `bbs_post_message()`    | Post a new public message                 | `bbs_post_message(subject, body, fromNode)`        |
| `bbs_read_message()`    | Read a message by ID                      | `bbs_read_message(messageID)`                      |
| `bbs_delete_message()`  | Delete a message (admin/owner only)       | `bbs_delete_message(messageID, fromNode)`          |
| `bbs_list_messages()`   | List all message subjects                 | `bbs_list_messages()`                              |
| `bbs_post_dm()`         | Post a direct message                     | `bbs_post_dm(toNode, message, fromNode)`           |
| `bbs_check_dm()`        | Check for DMs for a node                  | `bbs_check_dm(toNode)`                             |
| `bbs_delete_dm()`       | Delete a DM after reading                 | `bbs_delete_dm(toNode, message)`                   |
| `get_bbs_stats()`       | Get stats on BBS and DMs                  | `get_bbs_stats()`                                  |


| Function                  | Purpose                                   |
|---------------------------|-------------------------------------------|
| `bbs_sync_posts()`        | Handles incoming/outgoing sync requests   |
| `bbs_receive_compressed()`| Handles compressed sync data              |
| `compress_data()`         | Compresses data for OTA transfer          |
| `decompress_data()`       | Decompresses received data                |


### **Handle Incoming Sync**
- The bot automatically processes incoming `bbslink` and `bbsack` commands via `bbs_sync_posts()`.

### **Compressed Sync**
Future Use
- If `useSynchCompression` is enabled, use:
  ```python
  compressed = compress_data(msg)
  send_raw_bytes(peerNode, compressed)
  ```
- Receiving node uses `bbs_receive_compressed()`.

---

---