# Checkin Checkout database module for the bot
# K7MHI Kelly Keeton 2024

import sqlite3
from modules.log import *
import time

trap_list_checklist = ("checkin", "checkout", "checklist", "purgein", "purgeout")

def initialize_checklist_database():
    # create the database
    conn = sqlite3.connect(checklist_db)
    c = conn.cursor()
    # Check if the checkin table exists, and create it if it doesn't
    c.execute('''CREATE TABLE IF NOT EXISTS checkin
                 (checkin_id INTEGER PRIMARY KEY, checkin_name TEXT, checkin_date TEXT, checkin_time TEXT, location TEXT, checkin_notes TEXT)''')
    # Check if the checkout table exists, and create it if it doesn't
    c.execute('''CREATE TABLE IF NOT EXISTS checkout
                 (checkout_id INTEGER PRIMARY KEY, checkout_name TEXT, checkout_date TEXT, checkout_time TEXT, location TEXT, checkout_notes TEXT)''')
    conn.commit()
    conn.close()
    logger.debug("System: Ensured data/checklist.db exists with required tables")
    return True

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
    # checkout a user
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
            c.execute("SELECT checkin_time FROM checkin WHERE checkin_id = ?", (checkin_record[0],))
            checkin_time = c.fetchone()[0]
            checkin_datetime = time.strptime(date + " " + checkin_time, "%Y-%m-%d %H:%M:%S")
            time_checked_in_seconds = time.time() - time.mktime(checkin_datetime)
            timeCheckedIn = time.strftime("%H:%M:%S", time.gmtime(time_checked_in_seconds))
            # # remove the checkin record older than the checkout
            # c.execute("DELETE FROM checkin WHERE checkin_date < ? OR (checkin_date = ? AND checkin_time < ?)", (date, date, time_str))
    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
            initialize_checklist_database()
            c.execute("INSERT INTO checkout (checkout_name, checkout_date, checkout_time, location, checkout_notes) VALUES (?, ?, ?, ?, ?)", (name, date, time_str, location, notes))
        else:
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

def list_checkin():
    # list checkins
    conn = sqlite3.connect(checklist_db)
    c = conn.cursor()
    c.execute("""
        SELECT * FROM checkin
        WHERE checkin_id NOT IN (
            SELECT checkin_id FROM checkout
            WHERE checkout_date > checkin_date OR (checkout_date = checkin_date AND checkout_time > checkin_time)
        )
    """)
    rows = c.fetchall()
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
    try:
        comment = message.split(" ", 1)[1]
    except IndexError:
        comment = ""
    # handle checklist commands
    if ("checkin" in message.lower() and not reverse_in_out) or ("checkout" in message.lower() and reverse_in_out):
        return checkin(name, current_date, current_time, location, comment)
    elif ("checkout" in message.lower() and not reverse_in_out) or ("checkin" in message.lower() and reverse_in_out):
        return checkout(name, current_date, current_time, location, comment)
    elif "purgein" in message.lower():
        return delete_checkin(nodeID)
    elif "purgeout" in message.lower():
        return delete_checkout(nodeID)
    elif "?" in message.lower():
        if not reverse_in_out:
            return ("Command: checklist followed by\n"
                    "checkout to check out\n"
                    "purgeout to delete your checkout record\n"
                    "Example: checkin Arrived at park")
        else:
            return ("Command: checklist followed by\n"
                    "checkin to check out\n"
                    "purgeout to delete your checkin record\n"
                    "Example: checkout Leaving park")
    elif "checklist" in message.lower():
        return list_checkin()
    else:
        return "Invalid command."