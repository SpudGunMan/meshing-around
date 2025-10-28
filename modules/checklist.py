# Checkin Checkout database module for the bot
# K7MHI Kelly Keeton 2024

import sqlite3
from modules.log import logger
from modules.settings import checklist_db, reverse_in_out, bbs_ban_list
import time

trap_list_checklist = ("checkin", "checkout", "checklist", "purgein", "purgeout", 
                       "checklistapprove", "checklistdeny", "checklistadd", "checklistremove")

def initialize_checklist_database():
    try:
        conn = sqlite3.connect(checklist_db)
        c = conn.cursor()
        # Check if the checkin table exists, and create it if it doesn't
        logger.debug("System: Checklist: Initializing database...")
        c.execute('''CREATE TABLE IF NOT EXISTS checkin
                     (checkin_id INTEGER PRIMARY KEY, checkin_name TEXT, checkin_date TEXT, 
                      checkin_time TEXT, location TEXT, checkin_notes TEXT, 
                      approved INTEGER DEFAULT 1, expected_checkin_interval INTEGER DEFAULT 0)''')
        # Check if the checkout table exists, and create it if it doesn't
        c.execute('''CREATE TABLE IF NOT EXISTS checkout
                     (checkout_id INTEGER PRIMARY KEY, checkout_name TEXT, checkout_date TEXT, 
                      checkout_time TEXT, location TEXT, checkout_notes TEXT)''')
        
        # Add new columns if they don't exist (for migration)
        try:
            c.execute("ALTER TABLE checkin ADD COLUMN approved INTEGER DEFAULT 1")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            c.execute("ALTER TABLE checkin ADD COLUMN expected_checkin_interval INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Checklist: Failed to initialize database: {e}")
        return False

def checkin(name, date, time, location, notes):
    location = ", ".join(map(str, location))
    # checkin a user
    conn = sqlite3.connect(checklist_db)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO checkin (checkin_name, checkin_date, checkin_time, location, checkin_notes) VALUES (?, ?, ?, ?, ?)", (name, date, time, location, notes))
        # # remove any checkouts that are older than the checkin
        # c.execute("DELETE FROM checkout WHERE checkout_date < ? OR (checkout_date = ? AND checkout_time < ?)", (date, date, time))
    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
            initialize_checklist_database()
            c.execute("INSERT INTO checkin (checkin_name, checkin_date, checkin_time, location, checkin_notes) VALUES (?, ?, ?, ?, ?)", (name, date, time, location, notes))
        else:
            raise
    conn.commit()
    conn.close()
    if reverse_in_out:
        return "Checked✅Out: " + str(name)
    else:
        return "Checked✅In: " + str(name)

def delete_checkin(checkin_id):
    # delete a checkin
    conn = sqlite3.connect(checklist_db)
    c = conn.cursor()
    c.execute("DELETE FROM checkin WHERE checkin_id = ?", (checkin_id,))
    conn.commit()
    conn.close()
    return "Checkin deleted." + str(checkin_id)

def checkout(name, date, time_str, location, notes):
    location = ", ".join(map(str, location))
    checkin_record = None  # Ensure variable is always defined
    conn = sqlite3.connect(checklist_db)
    c = conn.cursor()
    try:
        # Check if the user has a checkin before checking out
        c.execute("""
            SELECT checkin_id FROM checkin 
            WHERE checkin_name = ? 
            AND NOT EXISTS (
            SELECT 1 FROM checkout 
            WHERE checkout_name = checkin_name 
            AND (checkout_date > checkin_date OR (checkout_date = checkin_date AND checkout_time > checkin_time))
            )
            ORDER BY checkin_date DESC, checkin_time DESC 
            LIMIT 1
        """, (name,))
        checkin_record = c.fetchone()
        if checkin_record:
            c.execute("INSERT INTO checkout (checkout_name, checkout_date, checkout_time, location, checkout_notes) VALUES (?, ?, ?, ?, ?)", (name, date, time_str, location, notes))
            # calculate length of time checked in
            c.execute("SELECT checkin_time, checkin_date FROM checkin WHERE checkin_id = ?", (checkin_record[0],))
            checkin_time, checkin_date = c.fetchone()
            checkin_datetime = time.strptime(checkin_date + " " + checkin_time, "%Y-%m-%d %H:%M:%S")
            time_checked_in_seconds = time.time() - time.mktime(checkin_datetime)
            timeCheckedIn = time.strftime("%H:%M:%S", time.gmtime(time_checked_in_seconds))
            # # remove the checkin record older than the checkout
            # c.execute("DELETE FROM checkin WHERE checkin_date < ? OR (checkin_date = ? AND checkin_time < ?)", (date, date, time_str))
    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
            conn.close()
            initialize_checklist_database()
            # Try again after initializing
            return checkout(name, date, time_str, location, notes)
        else:
            conn.close()
            raise
    conn.commit()
    conn.close()
    if checkin_record:
        if reverse_in_out:
            return "Checked⌛️In: " + str(name) + " duration " + timeCheckedIn
        else:
            return "Checked⌛️Out: " + str(name) + " duration " + timeCheckedIn
    else:
        return "None found for " + str(name)

def delete_checkout(checkout_id):
    # delete a checkout
    conn = sqlite3.connect(checklist_db)
    c = conn.cursor()
    c.execute("DELETE FROM checkout WHERE checkout_id = ?", (checkout_id,))
    conn.commit()
    conn.close()
    return "Checkout deleted." + str(checkout_id)

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
            SELECT checkin_id, checkin_name, checkin_date, checkin_time, expected_checkin_interval, location
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
        for checkin_id, name, date, time_str, interval, location in active_checkins:
            checkin_datetime = time.mktime(time.strptime(f"{date} {time_str}", "%Y-%m-%d %H:%M:%S"))
            time_since_checkin = (current_time - checkin_datetime) / 60  # in minutes
            
            if time_since_checkin > interval:
                overdue_minutes = int(time_since_checkin - interval)
                overdue_list.append({
                    'id': checkin_id,
                    'name': name,
                    'location': location,
                    'overdue_minutes': overdue_minutes,
                    'interval': interval
                })
        
        return overdue_list
    except Exception as e:
        conn.close()
        logger.error(f"Checklist: Error getting overdue check-ins: {e}")
        return []

def format_overdue_alert():
    """Format overdue check-ins as an alert message"""
    overdue = get_overdue_checkins()
    if not overdue:
        return None
    
    alert = "⚠️ OVERDUE CHECK-INS:\n"
    for entry in overdue:
        hours = entry['overdue_minutes'] // 60
        minutes = entry['overdue_minutes'] % 60
        alert += f"{entry['name']}: {hours}h {minutes}m overdue"
        if entry['location']:
            alert += f" @ {entry['location']}"
        alert += "\n"
    
    return alert.rstrip()

def list_checkin():
    # list checkins
    conn = sqlite3.connect(checklist_db)
    c = conn.cursor()
    try:
        c.execute("""
            SELECT * FROM checkin
            WHERE checkin_id NOT IN (
                SELECT checkin_id FROM checkout
                WHERE checkout_date > checkin_date OR (checkout_date = checkin_date AND checkout_time > checkin_time)
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
            logger.error(f"Checklist: Error listing checkins: {e}")
            return "Error listing checkins."
    conn.close()
    timeCheckedIn = ""
    checkin_list = ""
    for row in rows:
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
        checkin_list += "ID: " + row[1] + " checked-In for " + timeCheckedIn
        if row[5] != "":
            checkin_list += "📝" + row[5]
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
        return checkout(name, current_date, current_time, location, comment)
    
    elif "purgein" in message_lower:
        return delete_checkin(nodeID)
    
    elif "purgeout" in message_lower:
        return delete_checkout(nodeID)
    
    elif message_lower.startswith("checklistapprove "):
        try:
            checkin_id = int(parts[1])
            return approve_checkin(checkin_id)
        except (ValueError, IndexError):
            return "Usage: checklistapprove <checkin_id>"
    
    elif message_lower.startswith("checklistdeny "):
        try:
            checkin_id = int(parts[1])
            return deny_checkin(checkin_id)
        except (ValueError, IndexError):
            return "Usage: checklistdeny <checkin_id>"
    
    elif "?" in message_lower:
        if not reverse_in_out:
            return ("Command: checklist followed by\n"
                    "checkin [interval] [note] - check in (optional interval in minutes)\n"
                    "checkout [note] - check out\n"
                    "purgein - delete your checkin\n"
                    "purgeout - delete your checkout\n"
                    "checklistapprove <id> - approve checkin\n"
                    "checklistdeny <id> - deny checkin\n"
                    "Example: checkin 60 Hunting in tree stand")
        else:
            return ("Command: checklist followed by\n"
                    "checkout [interval] [note] - check out (optional interval)\n"
                    "checkin [note] - check in\n"
                    "purgeout - delete your checkout\n"
                    "purgein - delete your checkin\n"
                    "Example: checkout 60 Leaving park")
    
    elif "checklist" in message_lower:
        return list_checkin()
    
    else:
        return "Invalid command."