# Custom Trigger Words and User Statistics Features

## Overview
This implementation adds two major features to meshing-around:

### 1. Custom Trigger Words (Localization Support)
Allows mesh operators to configure custom trigger words in any language that behave like the built-in "ping" and "test" commands.

### 2. User Statistics and Leaderboards
Automatically tracks user activity and provides competitive leaderboards to encourage mesh participation.

## Configuration

### Custom Trigger Words
Add to your `config.ini` under `[general]`:

```ini
# Custom trigger words for ping-like responses
customPingWords = hola,привет,bonjour,ciao

# Custom trigger words for test-like responses  
customTestWords = prueba,テスト,testen,测试
```

**How it works:**
- Words are case-insensitive
- Multiple words can be added (comma-separated)
- Each word triggers the same response as "ping" or "test"
- Works in both mesh_bot.py and pong_bot.py

### User Statistics Tracking
Enable/disable in your `config.ini` under `[general]`:

```ini
enableStatsTracking = True
```

**What is tracked:**
- Message count per user
- Command usage per user
- Battery levels (from telemetry)
- Uptime (from telemetry)
- Last seen timestamp
- First seen timestamp

**Data storage:**
Statistics are persisted in `data/user_stats.json` and automatically saved during the cleanup cycle.

## Using the Leaderboard

### Basic Commands
- `top` or `leaderboard` - Show top 10 message senders
- `top messages` - Top message senders (explicit)
- `top commands` - Top command users
- `top battery` - Lowest battery levels (who needs a charge)
- `top online` - Most recently active users

### Limiting Results
Add a number to limit results:
- `top 5` - Show only top 5
- `top messages 3` - Show top 3 message senders

### Help
- `top?` - Show help for the top command

## Example Usage

### Custom Trigger Words
```
User: hola
Bot: 🏓PONG
SNR:8.5 RSSI:-95

User: prueba 3
Bot: 🎙Testing 1,2,3
SNR:7.0 RSSI:-98
```

### Leaderboards
```
User: top messages
Bot: 🏆 Most Messages:
1. KC7MHI: 142
2. KB7YEG: 98
3. KF7XYZ: 76
4. N7ABC: 52
5. W7DEF: 41

User: top battery 3
Bot: 🏆 Lowest Battery (3):
1. KC7MHI: 15%
2. N7ABC: 28%
3. KB7YEG: 45%

User: top online
Bot: 🏆 Most Recently Active:
1. KC7MHI: 2m ago
2. W7DEF: 15m ago
3. KB7YEG: 1h ago
```

## Implementation Details

### Files Modified
- `config.template` - Added new config options
- `modules/settings.py` - Read config values
- `modules/system.py` - Added custom words to trap_list, integrated stats saving
- `modules/stats.py` - New module for statistics tracking
- `mesh_bot.py` - Added custom word support, top command handler, stats tracking
- `pong_bot.py` - Added custom word support
- `data/trigger_words.json` - Example localization file (currently unused, for future expansion)

### Architecture
1. **Trigger Detection**: Custom words are added to `trap_list` during initialization
2. **Command Handling**: Custom words are dynamically added to command_handler dictionaries
3. **Response Logic**: `handle_ping()` checks for custom words in addition to built-in ones
4. **Stats Tracking**: 
   - Messages tracked in TEXT_MESSAGE_APP handler
   - Commands tracked in auto_response
   - Telemetry tracked in consumeMetadata
   - Periodic save via cleanup_memory

## Future Enhancements
- Time-based leaderboards (daily, weekly, monthly)
- Team/group statistics
- Achievement system
- Export leaderboards to HTML report
- Load trigger words from JSON file
- Per-node custom responses
