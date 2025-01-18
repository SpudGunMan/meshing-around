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
    return "Checked in: " + str(name)

def delete_checkin(checkin_id):
    # delete a checkin
    conn = sqlite3.connect(checklist_db)
    c = conn.cursor()
    c.execute("DELETE FROM checkin WHERE checkin_id = ?", (checkin_id,))
    conn.commit()
    conn.close()
    return "Checkin deleted." + str(checkin_id)

def checkout(name, date, time, location, notes):
    location = ", ".join(map(str, location))
    # checkout a user
    conn = sqlite3.connect(checklist_db)
    c = conn.cursor()
    try:
        # Check if the user has a checkin before checking out
        c.execute("SELECT checkin_id FROM checkin WHERE checkin_name = ? ORDER BY checkin_date DESC, checkin_time DESC LIMIT 1", (name,))
        checkin_record = c.fetchone()
        if checkin_record:
            c.execute("INSERT INTO checkout (checkout_name, checkout_date, checkout_time, location, checkout_notes) VALUES (?, ?, ?, ?, ?)", (name, date, time, location, notes))
        else:
            logger.error("User: " + name + " attempted to checkout without checking in first.")
    except sqlite3.OperationalError as e:
        logger.error("User: " + name + " attempted to checkout without checking in first.")
    conn.commit()
    conn.close()
    return "Checked out: " + str(name)

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
        #calculate length of time checked in
        timeCheckedIn = time.strftime("%H:%M:%S", time.gmtime(time.time() - time.mktime(time.strptime(row[2] + " " + row[3], "%Y-%m-%d %H:%M:%S"))))
        checkin_list += "ID: " + row[1] + " has been checked in for " + timeCheckedIn
        if row[5] != "":
            checkin_list += " note: " + row[5]
        if row != rows[-1]:
            checkin_list += "\n"
    # if empty list
    if checkin_list == "":
        return "No data to display."
    return checkin_list

def process_checklist_command(nodeID, message, name="none", location="none"):
    current_date = time.strftime("%Y-%m-%d")
    current_time = time.strftime("%H:%M:%S")
    try:
        comment = message.split(" ", 1)[1]
    except IndexError:
        comment = ""
    # handle checklist commands
    if "checkin" in message.lower():
        return checkin(name, current_date, current_time, location, comment)
    elif "checkout" in message.lower():
        return checkout(name, current_date, current_time, location, comment)
    elif "purgein" in message.lower():
        return delete_checkin(nodeID)
    elif "purgeout" in message.lower():
        return delete_checkout(nodeID)
    elif "checklist" in message.lower():
        return list_checkin()
    else:
        return "Invalid command."