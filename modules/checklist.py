# Checkin Checkout database module for the bot
# K7MHI Kelly Keeton 2024

import sqlite3
from modules.log import logger
from modules.settings import checklist_db, reverse_in_out, bbs_ban_list, bbs_admin_list
import time

trap_list_checklist = ("checkin", "checkout", "checklist", 
                       "checklistapprove", "checklistdeny", "checklistadd", "checklistremove")

def initialize_checklist_database():
    try:
        conn = sqlite3.connect(checklist_db)
        c = conn.cursor()
        logger.debug("System: Checklist: Initializing database...")
        c.execute('''CREATE TABLE IF NOT EXISTS checkin
                     (checkin_id INTEGER PRIMARY KEY, checkin_name TEXT, checkin_date TEXT, 
                      checkin_time TEXT, location TEXT, checkin_notes TEXT, 
                      approved INTEGER DEFAULT 1, expected_checkin_interval INTEGER DEFAULT 0,
                      removed INTEGER DEFAULT 0)''')
        c.execute('''CREATE TABLE IF NOT EXISTS checkout
                     (checkout_id INTEGER PRIMARY KEY, checkout_name TEXT, checkout_date TEXT, 
                      checkout_time TEXT, location TEXT, checkout_notes TEXT,
                      checkin_id INTEGER, removed INTEGER DEFAULT 0)''')
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Checklist: Failed to initialize database: {e} Please delete old checklist database file. rm data/checklist.db")
        return False

def checkin(name, date, time, location, notes):
    location = ", ".join(map(str, location))
    # checkin a user
    conn = sqlite3.connect(checklist_db)
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO checkin (checkin_name, checkin_date, checkin_time, location, checkin_notes, removed) VALUES (?, ?, ?, ?, ?, 0)",
            (name, date, time, location, notes)
        )
    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
            initialize_checklist_database()
            c.execute(
                "INSERT INTO checkin (checkin_name, checkin_date, checkin_time, location, checkin_notes, removed) VALUES (?, ?, ?, ?, ?, 0)",
                (name, date, time, location, notes)
            )
        else:
            raise
    conn.commit()
    conn.close()
    if reverse_in_out:
        return "Checked✅Out: " + str(name)
    else:
        return "Checked✅In: " + str(name)

def checkout(name, date, time_str, location, notes, all=False, checkin_id=None):
    location = ", ".join(map(str, location))
    conn = sqlite3.connect(checklist_db)
    c = conn.cursor()
    checked_out_ids = []
    durations = []
    try:
        if checkin_id is not None:
            # Check out a specific check-in by ID
            c.execute("""
                SELECT checkin_id, checkin_time, checkin_date FROM checkin
                WHERE checkin_id = ? AND checkin_name = ?
            """, (checkin_id, name))
            row = c.fetchone()
            if row:
                c.execute("INSERT INTO checkout (checkout_name, checkout_date, checkout_time, location, checkout_notes, checkin_id) VALUES (?, ?, ?, ?, ?, ?)",
                          (name, date, time_str, location, notes, row[0]))
                checkin_time, checkin_date = row[1], row[2]
                checkin_datetime = time.strptime(checkin_date + " " + checkin_time, "%Y-%m-%d %H:%M:%S")
                time_checked_in_seconds = time.time() - time.mktime(checkin_datetime)
                durations.append(time.strftime("%H:%M:%S", time.gmtime(time_checked_in_seconds)))
                checked_out_ids.append(row[0])
        elif all:
            # Check out all active check-ins for this user
            c.execute("""
                SELECT checkin_id, checkin_time, checkin_date FROM checkin 
                WHERE checkin_name = ? 
                AND removed = 0
                AND checkin_id NOT IN (
                    SELECT checkin_id FROM checkout WHERE checkin_id IS NOT NULL
                )
            """, (name,))
            rows = c.fetchall()
            for row in rows:
                c.execute("INSERT INTO checkout (checkout_name, checkout_date, checkout_time, location, checkout_notes, checkin_id) VALUES (?, ?, ?, ?, ?, ?)",
                          (name, date, time_str, location, notes, row[0]))
                checkin_time, checkin_date = row[1], row[2]
                checkin_datetime = time.strptime(checkin_date + " " + checkin_time, "%Y-%m-%d %H:%M:%S")
                time_checked_in_seconds = time.time() - time.mktime(checkin_datetime)
                durations.append(time.strftime("%H:%M:%S", time.gmtime(time_checked_in_seconds)))
                checked_out_ids.append(row[0])
        else:
            # Default: check out the most recent active check-in
            c.execute("""
                SELECT checkin_id, checkin_time, checkin_date FROM checkin 
                WHERE checkin_name = ? 
                AND removed = 0
                AND checkin_id NOT IN (
                    SELECT checkin_id FROM checkout WHERE checkin_id IS NOT NULL
                )
                ORDER BY checkin_date DESC, checkin_time DESC 
                LIMIT 1
            """, (name,))
            row = c.fetchone()
            if row:
                c.execute("INSERT INTO checkout (checkout_name, checkout_date, checkout_time, location, checkout_notes, checkin_id) VALUES (?, ?, ?, ?, ?, ?)",
                          (name, date, time_str, location, notes, row[0]))
                checkin_time, checkin_date = row[1], row[2]
                checkin_datetime = time.strptime(checkin_date + " " + checkin_time, "%Y-%m-%d %H:%M:%S")
                time_checked_in_seconds = time.time() - time.mktime(checkin_datetime)
                durations.append(time.strftime("%H:%M:%S", time.gmtime(time_checked_in_seconds)))
                checked_out_ids.append(row[0])
    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
            conn.close()
            initialize_checklist_database()
            return checkout(name, date, time_str, location, notes, all=all, checkin_id=checkin_id)
        else:
            conn.close()
            raise
    conn.commit()
    conn.close()
    if checked_out_ids:
        if all:
            return f"Checked out {len(checked_out_ids)} check-ins for {name}. Durations: {', '.join(durations)}"
        elif checkin_id is not None:
            return f"Checked out check-in ID {checkin_id} for {name}. Duration: {durations[0]}"
        else:
            if reverse_in_out:
                return f"Checked⌛️In: {name} duration {durations[0]}"
            else:
                return f"Checked⌛️Out: {name} duration {durations[0]}"
    else:
        return f"None found for {name}"

def approve_checkin(checkin_id):
    """Approve a pending check-in"""
    conn = sqlite3.connect(checklist_db)
    c = conn.cursor()
    try:
        c.execute("UPDATE checkin SET approved = 1 WHERE checkin_id = ?", (checkin_id,))
        if c.rowcount == 0:
            conn.close()
            return f"Check-in ID {checkin_id} not found."
        conn.commit()
        conn.close()
        return f"✅ Check-in {checkin_id} approved."
    except Exception as e:
        conn.close()
        logger.error(f"Checklist: Error approving check-in: {e}")
        return "Error approving check-in."

def deny_checkin(checkin_id):
    """Deny/delete a pending check-in"""
    conn = sqlite3.connect(checklist_db)
    c = conn.cursor()
    try:
        c.execute("DELETE FROM checkin WHERE checkin_id = ?", (checkin_id,))
        if c.rowcount == 0:
            conn.close()
            return f"Check-in ID {checkin_id} not found."
        conn.commit()
        conn.close()
        return f"❌ Check-in {checkin_id} denied and removed."
    except Exception as e:
        conn.close()
        logger.error(f"Checklist: Error denying check-in: {e}")
        return "Error denying check-in."

def set_checkin_interval(name, interval_minutes):
    """Set expected check-in interval for a user (for safety monitoring)"""
    conn = sqlite3.connect(checklist_db)
    c = conn.cursor()
    try:
        # Update the most recent active check-in for this user
        c.execute("""
            UPDATE checkin 
            SET expected_checkin_interval = ? 
            WHERE checkin_name = ? 
            AND checkin_id NOT IN (
                SELECT checkin_id FROM checkout 
                WHERE checkout_name = checkin_name 
                AND (checkout_date > checkin_date OR (checkout_date = checkin_date AND checkout_time > checkin_time))
            )
            ORDER BY checkin_date DESC, checkin_time DESC 
            LIMIT 1
        """, (interval_minutes, name))
        
        if c.rowcount == 0:
            conn.close()
            return f"No active check-in found for {name}."
        
        conn.commit()
        conn.close()
        return f"⏰ Check-in interval set to {interval_minutes} minutes for {name}."
    except Exception as e:
        conn.close()
        logger.error(f"Checklist: Error setting check-in interval: {e}")
        return "Error setting check-in interval."

def get_overdue_checkins():
    """Get list of users who haven't checked in within their expected interval"""
    conn = sqlite3.connect(checklist_db)
    c = conn.cursor()
    current_time = time.time()
    
    try:
        c.execute("""
            SELECT checkin_id, checkin_name, checkin_date, checkin_time, expected_checkin_interval, location, checkin_notes
            FROM checkin
            WHERE expected_checkin_interval > 0
            AND approved = 1
            AND checkin_id NOT IN (
                SELECT checkin_id FROM checkout
                WHERE checkout_name = checkin_name
                AND (checkout_date > checkin_date OR (checkout_date = checkin_date AND checkout_time > checkin_time))
            )
        """)
        
        active_checkins = c.fetchall()
        conn.close()
        
        overdue_list = []
        for checkin_id, name, date, time_str, interval, location, notes in active_checkins:
            checkin_datetime = time.mktime(time.strptime(f"{date} {time_str}", "%Y-%m-%d %H:%M:%S"))
            time_since_checkin = (current_time - checkin_datetime) / 60  # in minutes
            
            if time_since_checkin > interval:
                overdue_minutes = int(time_since_checkin - interval)
                overdue_list.append({
                    'id': checkin_id,
                    'name': name,
                    'location': location,
                    'overdue_minutes': overdue_minutes,
                    'interval': interval,
                    'checkin_notes': notes
                })
        
        return overdue_list
    except sqlite3.OperationalError as e:
        conn.close()
        if "no such table" in str(e):
            initialize_checklist_database()
            return get_overdue_checkins()
        logger.error(f"Checklist: Error getting overdue check-ins: {e}")
        return []

def format_overdue_alert():
    header = "⚠️ OVERDUE CHECK-INS:\n"
    alert = ""
    try:
        """Format overdue check-ins as an alert message"""
        overdue = get_overdue_checkins()
        if overdue:
            logger.debug(f"Overdue check-ins: {overdue}")
        if not overdue:
            return None
        for entry in overdue:
            hours = entry['overdue_minutes'] // 60
            minutes = entry['overdue_minutes'] % 60
            if hours > 0:
                alert += f"{entry['name']}: {hours}h {minutes}m overdue"
            else:
                alert += f"{entry['name']}: {minutes}m overdue"
            # if entry['location']:
            #     alert += f" @ {entry['location']}"
            if entry['checkin_notes']:
                alert += f" 📝{entry['checkin_notes']}"
            alert += "\n"
        if alert:
            return header + alert.rstrip()
    except Exception as e:
        logger.error(f"Checklist: Error formatting overdue alert: {e}")
        return None

def list_checkin():
    # list checkins
    conn = sqlite3.connect(checklist_db)
    c = conn.cursor()
    try:
        c.execute("""
            SELECT * FROM checkin
            WHERE removed = 0
            AND NOT EXISTS (
                SELECT 1 FROM checkout
                WHERE checkout.checkin_id = checkin.checkin_id
            )
        """)
        rows = c.fetchall()
    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
            conn.close()
            initialize_checklist_database()
            return list_checkin()
        else:
            conn.close()
            initialize_checklist_database()
            return "Error listing checkins."
    conn.close()

    # Get overdue info
    overdue = {entry['id']: entry for entry in get_overdue_checkins()}

    checkin_list = ""
    for row in rows:
        checkin_id = row[0]
        # Calculate length of time checked in, including days
        total_seconds = time.time() - time.mktime(time.strptime(row[2] + " " + row[3], "%Y-%m-%d %H:%M:%S"))
        days = int(total_seconds // 86400)
        hours = int((total_seconds % 86400) // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        if days > 0:
            timeCheckedIn = f"{days}d {hours:02}:{minutes:02}:{seconds:02}"
        else:
            timeCheckedIn = f"{hours:02}:{minutes:02}:{seconds:02}"

        # Add ⏰ if routine check-ins are required
        routine = ""
        if len(row) > 7 and row[7] and int(row[7]) > 0:
            routine = f" ⏰({row[7]}m)"

        # Check if overdue
        if checkin_id in overdue:
            overdue_minutes = overdue[checkin_id]['overdue_minutes']
            overdue_hours = overdue_minutes // 60
            overdue_mins = overdue_minutes % 60
            if overdue_hours > 0:
                overdue_str = f"overdue by {overdue_hours}h {overdue_mins}m"
            else:
                overdue_str = f"overdue by {overdue_mins}m"
            status = f"{row[1]} {overdue_str}{routine}"
        else:
            status = f"{row[1]} checked-In for {timeCheckedIn}{routine}"

        checkin_list += f"ID: {checkin_id} {status}"
        if row[5] != "":
            checkin_list += " 📝" + row[5]
        if row != rows[-1]:
            checkin_list += "\n"
    # if empty list
    if checkin_list == "":
        return "No data to display."
    return checkin_list

def process_checklist_command(nodeID, message, name="none", location="none"):
    current_date = time.strftime("%Y-%m-%d")
    current_time = time.strftime("%H:%M:%S")
    # if user on bbs_ban_list reject command
    if str(nodeID) in bbs_ban_list:
        logger.warning("System: Checklist attempt from the ban list")
        return "unable to process command"
    is_admin = False
    if str(nodeID) in bbs_admin_list:
        is_admin = True
    
    message_lower = message.lower()
    parts = message.split()
    
    try:
        comment = message.split(" ", 1)[1] if len(parts) > 1 else ""
    except IndexError:
        comment = ""
    
    # handle checklist commands
    if ("checkin" in message_lower and not reverse_in_out) or ("checkout" in message_lower and reverse_in_out):
        # Check if interval is specified: checkin 60 comment
        interval = 0
        actual_comment = comment
        if comment and parts[1].isdigit():
            interval = int(parts[1])
            actual_comment = " ".join(parts[2:]) if len(parts) > 2 else ""
        
        result = checkin(name, current_date, current_time, location, actual_comment)
        
        # Set interval if specified
        if interval > 0:
            set_checkin_interval(name, interval)
            result += f" (monitoring every {interval}min)"
        
        return result
    
    elif ("checkout" in message_lower and not reverse_in_out) or ("checkin" in message_lower and reverse_in_out):
        # Support: checkout all, checkout <id>, or checkout [note]
        all_flag = False
        checkin_id = None
        actual_comment = comment
    
        # Split the command into parts after the keyword
        checkout_args = parts[1:] if len(parts) > 1 else []
    
        if checkout_args:
            if checkout_args[0].lower() == "all":
                all_flag = True
                actual_comment = " ".join(checkout_args[1:]) if len(checkout_args) > 1 else ""
            elif checkout_args[0].isdigit():
                checkin_id = int(checkout_args[0])
                actual_comment = " ".join(checkout_args[1:]) if len(checkout_args) > 1 else ""
            else:
                actual_comment = " ".join(checkout_args)
    
        return checkout(name, current_date, current_time, location, actual_comment, all=all_flag, checkin_id=checkin_id)
    
    # elif "purgein" in message_lower:
    #     return mark_checkin_removed_by_name(name)
    
    # elif "purgeout" in message_lower:
    #     return mark_checkout_removed_by_name(name)
    
    elif message_lower.startswith("checklistapprove ") and is_admin:
        try:
            checkin_id = int(parts[1])
            return approve_checkin(checkin_id)
        except (ValueError, IndexError):
            return "Usage: checklistapprove <checkin_id>"
    
    elif message_lower.startswith("checklistdeny ") and is_admin:
        try:
            checkin_id = int(parts[1])
            return deny_checkin(checkin_id)
        except (ValueError, IndexError):
            return "Usage: checklistdeny <checkin_id>"
    
    elif "?" in message_lower:
        if not reverse_in_out:
            return ("Command: checklist followed by\n"
                    "checkin [interval] [note]\n"
                    "checkout [all] [note]\n"
                    "checklistapprove <id>\n"
                    "checklistdeny <id>\n"
                    "Example: checkin 60 Leaving for a hike")
        else:
            return ("Command: checklist followed by\n"
                    "checkout [all] [interval] [note]\n"
                    "checkin [note]\n"
                    "Example: checkout 60 Leaving for a hike")
    
    elif "checklist" in message_lower:
        return list_checkin()
    
    else:
        return "Invalid command."

def mark_checkin_removed_by_name(name):
    conn = sqlite3.connect(checklist_db)
    c = conn.cursor()
    c.execute("UPDATE checkin SET removed = 1 WHERE checkin_name = ?", (name,))
    affected = c.rowcount
    conn.commit()
    conn.close()
    return f"Marked {affected} check-in(s) as removed for {name}."

def mark_checkout_removed_by_name(name):
    conn = sqlite3.connect(checklist_db)
    c = conn.cursor()
    c.execute("UPDATE checkout SET removed = 1 WHERE checkout_name = ?", (name,))
    affected = c.rowcount
    conn.commit()
    conn.close()
    return f"Marked {affected} checkout(s) as removed for {name}."