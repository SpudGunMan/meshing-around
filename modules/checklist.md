# Enhanced Check-in/Check-out System

## Overview

The enhanced checklist module provides asset tracking and accountability features with advanced safety monitoring capabilities. This system is designed for scenarios where tracking people, equipment, or assets is critical for safety, accountability, or logistics.

## Key Features

### 🔐 Basic Check-in/Check-out
- Simple interface for tracking when people or assets are checked in or out
- Automatic duration calculation
- Location tracking (GPS coordinates if available)
- Notes support for additional context

### ⏰ Safety Monitoring with Time Intervals
- Set expected check-in intervals for safety monitoring
- Automatic tracking of overdue check-ins
- Ideal for solo activities, remote work, or high-risk operations
- Get alerts when someone hasn't checked in within their expected timeframe

### ✅ Approval Workflow
- Admin approval system for check-ins
- Deny/remove unauthorized check-ins
- Maintain accountability and control

### 📍 Location Tracking
- Automatic GPS location capture when checking in/out
- View last known location in checklist
- Track movement over time

## Configuration

Add to your `config.ini`:

```ini
[checklist]
enabled = True
checklist_db = data/checklist.db
# Set to True to reverse the meaning of checkin/checkout
reverse_in_out = False
```

## Commands Reference

### Basic Commands

#### Check In
```
checkin [interval] [notes]
```

Check in to the system. Optionally specify a monitoring interval in minutes.

**Examples:**
```
checkin Arrived at base camp
checkin 30 Solo hiking on north trail
checkin 60 Working alone in tree stand
checkin Going hunting
```

#### Check Out
```
checkout [notes]
```

Check out from the system. Shows duration since check-in.

**Examples:**
```
checkout Heading back
checkout Mission complete
checkout
```

#### View Checklist
```
checklist
```

Shows all active check-ins with durations.

**Example Response:**
```
ID: Hunter1 checked-In for 01:23:45📝Solo hunting
ID: Tech2 checked-In for 00:15:30📝Equipment repair
```

#### Purge Records
```
purgein    # Delete your check-in record
purgeout   # Delete your check-out record
```

Use these to manually remove your records if needed.

### Admin Commands

#### Approve Check-in
```
checklistapprove <checkin_id>
```

Approve a pending check-in (requires admin privileges).

**Example:**
```
checklistapprove 123
```

#### Deny Check-in
```
checklistdeny <checkin_id>
```

Deny and remove a check-in (requires admin privileges).

**Example:**
```
checklistdeny 456
```

## Safety Monitoring Feature

### How Time Intervals Work

When checking in with an interval parameter, the system will track whether you check in again or check out within that timeframe.

```
checkin 60 Hunting in remote area
```

This tells the system:
- You're checking in now
- You expect to check in again or check out within 60 minutes
- If 60 minutes pass without activity, you'll be marked as overdue

### Use Cases for Time Intervals

1. **Solo Activities**: Hunting, hiking, or working alone
   ```
   checkin 30 Solo patrol north sector
   ```

2. **High-Risk Operations**: Tree work, equipment maintenance
   ```
   checkin 45 Climbing tower for antenna work
   ```

3. **Remote Work**: Working in isolated areas
   ```
   checkin 120 Survey work in remote canyon
   ```

4. **Check-in Points**: Regular status updates during long operations
   ```
   checkin 15 Descending cliff face
   ```

### Overdue Check-ins

The system tracks all check-ins with time intervals and can identify who is overdue. The module provides the `get_overdue_checkins()` function that returns a list of overdue users. 

**Note**: Automatic alerts for overdue check-ins require integration with the bot's scheduler or alert system. The checklist module provides the detection capability, but sending notifications must be configured separately through the main bot's alert features.

## Practical Examples

### Example 1: Hunting Scenario

Hunter checks in before going into the field:
```
checkin 60 Hunting deer stand #3, north 40
```

System response:
```
Checked✅In: Hunter1 (monitoring every 60min)
```

If the hunter doesn't check out or check in again within 60 minutes, they will appear on the overdue list.

When done hunting:
```
checkout Heading back to camp
```

System response:
```
Checked⌛️Out: Hunter1 duration 02:15:30
```

### Example 2: Emergency Response Team

Team leader tracks team members:

```
# Team members check in
checkin 30 Search grid A-1
checkin 30 Search grid A-2
checkin 30 Search grid A-3
```

Team leader views status:
```
checklist
```

Response shows all active searchers with their durations.

### Example 3: Equipment Checkout

Track equipment loans:

```
checkin Radio #5 for field ops
```

When equipment is returned:
```
checkout Equipment returned
```

### Example 4: Site Survey

Field technicians checking in at locations:

```
# At first site
checkin 45 Site survey tower location 1

# Moving to next site (automatically checks out from first)
checkin 45 Site survey tower location 2
```

## Integration with Other Systems

### Geo-Location Awareness

The checklist system automatically captures GPS coordinates when available. This can be used for:
- Tracking last known position
- Geo-fencing applications
- Emergency response coordination
- Asset location management

### Alert Systems

The overdue check-in feature can trigger:
- Notifications to supervisors
- Emergency alerts
- Automated messages to response teams
- Email/SMS notifications (if configured)

### Scheduling Integration

Combine with the scheduler module to:
- Send reminders to check in
- Automatically generate reports
- Schedule periodic check-in requirements
- Send daily summaries

## Best Practices

### For Users

1. **Always Include Context**: Add notes when checking in
   ```
   checkin 30 North trail maintenance
   ```
   Not just:
   ```
   checkin
   ```

2. **Set Realistic Intervals**: Don't set intervals too short or too long
   - Too short: False alarms
   - Too long: Defeats safety purpose

3. **Check Out Promptly**: Always check out when done to clear your status

4. **Use Consistent Naming**: If tracking equipment, use consistent names

### For Administrators

1. **Review Checklist Regularly**: Monitor who is checked in
   ```
   checklist
   ```

2. **Respond to Overdue Situations**: Act on overdue check-ins promptly

3. **Set Clear Policies**: Establish when and how to use the system

4. **Train Users**: Ensure everyone knows how to use time intervals

5. **Test the System**: Regularly verify the system is working

## Safety Scenarios

### Scenario 1: Tree Stand Hunting
```
checkin 60 Hunting from tree stand at north plot
```
If hunter falls or has medical emergency, they'll be marked overdue after 60 minutes.

### Scenario 2: Equipment Maintenance
```
checkin 30 Generator maintenance at remote site
```
If technician encounters danger, overdue status can be detected. Note: Requires alert system integration to send notifications.

### Scenario 3: Hiking
```
checkin 120 Day hike to mountain peak
```
Longer interval for extended activity, but still provides safety net.

### Scenario 4: Watchstanding
```
checkin 240 Night watch duty
```
Regular check-ins every 4 hours ensure person is alert and safe.

## Database Schema

### checkin Table
```sql
CREATE TABLE checkin (
    checkin_id INTEGER PRIMARY KEY,
    checkin_name TEXT,
    checkin_date TEXT,
    checkin_time TEXT,
    location TEXT,
    checkin_notes TEXT,
    approved INTEGER DEFAULT 1,
    expected_checkin_interval INTEGER DEFAULT 0
)
```

### checkout Table
```sql
CREATE TABLE checkout (
    checkout_id INTEGER PRIMARY KEY,
    checkout_name TEXT,
    checkout_date TEXT,
    checkout_time TEXT,
    location TEXT,
    checkout_notes TEXT
)
```

## Reverse Mode

Setting `reverse_in_out = True` in config swaps the meaning of checkin and checkout commands. This is useful if your organization uses opposite terminology.

With `reverse_in_out = True`:
- `checkout` command performs a check-in
- `checkin` command performs a check-out

## Migration from Basic Checklist

The enhanced checklist is backward compatible with the basic version. Existing check-ins will continue to work, and new features are optional. The database will automatically upgrade to add new columns when first accessed.

## Troubleshooting

### Not Seeing Overdue Alerts
The overdue detection is built into the module, but alerts need to be configured in the main bot scheduler. Check your scheduler configuration.

### Wrong Duration Shown
Duration is calculated from check-in time to current time. If system clock is wrong, durations will be incorrect. Ensure system time is accurate.

### Can't Approve/Deny Check-ins
These are admin-only commands. Check that your node ID is in the `bbs_admin_list`.

### Location Not Showing
GPS coordinates are only captured if the node has GPS enabled and has a fix. Check node GPS settings.

## Future Enhancements

Planned features:
- Configurable alert thresholds per user
- Email/SMS notifications for overdue check-ins
- Historical check-in reports
- Check-in schedules and recurring events
- Geo-fence monitoring
- Integration with tracking systems
- Mobile app support

## Support

For issues or feature requests, please file an issue on the GitHub repository.
