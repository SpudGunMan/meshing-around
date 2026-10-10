# Inventory and Point of Sale module for the bot
# K7MHI Kelly Keeton 2024
# Enhanced POS system with cart management and inventory tracking

import sqlite3
from modules.log import logger
from modules.settings import inventory_db, disable_penny, bbs_ban_list
import time
from decimal import Decimal, ROUND_HALF_UP, ROUND_DOWN

trap_list_inventory = ("item", "itemlist", "itemloan", "itemsell", "itemreturn", "itemadd", "itemremove", 
                       "itemreset", "itemstats", "cart", "cartadd", "cartremove", "cartlist",
                       "cartbuy", "cartsell", "cartclear")

def initialize_inventory_database():
    """Initialize the inventory database with all necessary tables"""
    try:
        conn = sqlite3.connect(inventory_db)
        c = conn.cursor()
        
        # Items table - stores inventory items
        logger.debug("System: Inventory: Initializing database...")
        c.execute('''CREATE TABLE IF NOT EXISTS items
                     (item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                      item_name TEXT UNIQUE NOT NULL,
                      item_price REAL NOT NULL,
                      item_quantity INTEGER NOT NULL DEFAULT 0,
                      location TEXT,
                      created_date TEXT,
                      updated_date TEXT)''')
        
        # Transactions table - stores sales/purchases
        c.execute('''CREATE TABLE IF NOT EXISTS transactions
                     (transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                      transaction_type TEXT NOT NULL,
                      transaction_date TEXT NOT NULL,
                      transaction_time TEXT NOT NULL,
                      user_name TEXT,
                      total_amount REAL NOT NULL,
                      notes TEXT)''')
        
        # Transaction items table - stores items in each transaction
        c.execute('''CREATE TABLE IF NOT EXISTS transaction_items
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      transaction_id INTEGER NOT NULL,
                      item_id INTEGER NOT NULL,
                      quantity INTEGER NOT NULL,
                      price_at_sale REAL NOT NULL,
                      FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id),
                      FOREIGN KEY (item_id) REFERENCES items(item_id))''')
        
        # Carts table - stores temporary shopping carts
        c.execute('''CREATE TABLE IF NOT EXISTS carts
                     (cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id TEXT NOT NULL,
                      item_id INTEGER NOT NULL,
                      quantity INTEGER NOT NULL,
                      added_date TEXT,
                      FOREIGN KEY (item_id) REFERENCES items(item_id))''')
        
        conn.commit()
        conn.close()
        logger.info("Inventory: Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Inventory: Failed to initialize database: {e}")
        return False

def round_price(amount, is_taxed_sale=False):
    """Round price based on penny rounding settings"""
    if not disable_penny:
        return float(Decimal(str(amount)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
    
    # Penny rounding logic
    decimal_amount = Decimal(str(amount))
    if is_taxed_sale:
        # Round up for taxed sales
        return float(decimal_amount.quantize(Decimal('0.05'), rounding=ROUND_HALF_UP))
    else:
        # Round down for cash sales
        return float(decimal_amount.quantize(Decimal('0.05'), rounding=ROUND_DOWN))

def add_item(name, price, quantity=0, location=""):
    """Add a new item to inventory"""
    conn = sqlite3.connect(inventory_db)
    c = conn.cursor()
    current_date = time.strftime("%Y-%m-%d")
    
    try:
        # Check if item already exists
        c.execute("SELECT item_id FROM items WHERE item_name = ?", (name,))
        existing = c.fetchone()
        if existing:
            conn.close()
            return f"Item '{name}' already exists. Use itemreset to update."
        
        c.execute("""INSERT INTO items (item_name, item_price, item_quantity, location, created_date, updated_date)
                     VALUES (?, ?, ?, ?, ?, ?)""",
                  (name, price, quantity, location, current_date, current_date))
        conn.commit()
        conn.close()
        return f"✅ Item added: {name} - ${price:.2f} - Qty: {quantity}"
    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
            initialize_inventory_database()
            return add_item(name, price, quantity, location)
        else:
            conn.close()
            logger.error(f"Inventory: Error adding item: {e}")
            return "Error adding item."
    except Exception as e:
        conn.close()
        logger.error(f"Inventory: Error adding item: {e}")
        return "Error adding item."

def remove_item(name):
    """Remove an item from inventory"""
    conn = sqlite3.connect(inventory_db)
    c = conn.cursor()
    
    try:
        c.execute("DELETE FROM items WHERE item_name = ?", (name,))
        if c.rowcount == 0:
            conn.close()
            return f"Item '{name}' not found."
        conn.commit()
        conn.close()
        return f"🗑️ Item removed: {name}"
    except Exception as e:
        conn.close()
        logger.error(f"Inventory: Error removing item: {e}")
        return "Error removing item."

def reset_item(name, price=None, quantity=None):
    """Update item price or quantity"""
    conn = sqlite3.connect(inventory_db)
    c = conn.cursor()
    current_date = time.strftime("%Y-%m-%d")
    
    try:
        # Check if item exists
        c.execute("SELECT item_price, item_quantity FROM items WHERE item_name = ?", (name,))
        item = c.fetchone()
        if not item:
            conn.close()
            return f"Item '{name}' not found."
        
        updates = []
        params = []
        
        if price is not None:
            updates.append("item_price = ?")
            params.append(price)
        
        if quantity is not None:
            updates.append("item_quantity = ?")
            params.append(quantity)
        
        if not updates:
            conn.close()
            return "No updates specified."
        
        updates.append("updated_date = ?")
        params.append(current_date)
        params.append(name)
        
        query = f"UPDATE items SET {', '.join(updates)} WHERE item_name = ?"
        c.execute(query, params)
        conn.commit()
        conn.close()
        
        update_msg = []
        if price is not None:
            update_msg.append(f"Price: ${price:.2f}")
        if quantity is not None:
            update_msg.append(f"Qty: {quantity}")
        
        return f"🔄 Item updated: {name} - {' - '.join(update_msg)}"
    except Exception as e:
        conn.close()
        logger.error(f"Inventory: Error resetting item: {e}")
        return "Error updating item."

def sell_item(name, quantity, user_name="", notes=""):
    """Sell an item (remove from inventory and record transaction)"""
    conn = sqlite3.connect(inventory_db)
    c = conn.cursor()
    current_date = time.strftime("%Y-%m-%d")
    current_time = time.strftime("%H:%M:%S")
    
    try:
        # Get item details
        c.execute("SELECT item_id, item_price, item_quantity FROM items WHERE item_name = ?", (name,))
        item = c.fetchone()
        if not item:
            conn.close()
            return f"Item '{name}' not found."
        
        item_id, price, current_qty = item
        
        if current_qty < quantity:
            conn.close()
            return f"Insufficient quantity. Available: {current_qty}"
        
        # Calculate total with rounding
        total = round_price(price * quantity, is_taxed_sale=True)
        
        # Create transaction
        c.execute("""INSERT INTO transactions (transaction_type, transaction_date, transaction_time, 
                     user_name, total_amount, notes)
                     VALUES (?, ?, ?, ?, ?, ?)""",
                  ("SALE", current_date, current_time, user_name, total, notes))
        transaction_id = c.lastrowid
        
        # Add transaction item
        c.execute("""INSERT INTO transaction_items (transaction_id, item_id, quantity, price_at_sale)
                     VALUES (?, ?, ?, ?)""",
                  (transaction_id, item_id, quantity, price))
        
        # Update inventory
        c.execute("UPDATE items SET item_quantity = item_quantity - ?, updated_date = ? WHERE item_id = ?",
                  (quantity, current_date, item_id))
        
        conn.commit()
        conn.close()
        return f"💰 Sale: {quantity}x {name} - Total: ${total:.2f}"
    except Exception as e:
        conn.close()
        logger.error(f"Inventory: Error selling item: {e}")
        return "Error processing sale."

def return_item(transaction_id):
    """Return items from a transaction (reverse the sale or loan)"""
    conn = sqlite3.connect(inventory_db)
    c = conn.cursor()
    current_date = time.strftime("%Y-%m-%d")
    
    try:
        # Get transaction details
        c.execute("SELECT transaction_type FROM transactions WHERE transaction_id = ?", (transaction_id,))
        transaction = c.fetchone()
        if not transaction:
            conn.close()
            return f"Transaction {transaction_id} not found."
        transaction_type = transaction[0]
        
        # Get items in transaction
        c.execute("""SELECT ti.item_id, ti.quantity, i.item_name 
                     FROM transaction_items ti
                     JOIN items i ON ti.item_id = i.item_id
                     WHERE ti.transaction_id = ?""", (transaction_id,))
        items = c.fetchall()
        
        if not items:
            conn.close()
            return f"No items found for transaction {transaction_id}."
        
        # Return items to inventory
        for item_id, quantity, item_name in items:
            c.execute("UPDATE items SET item_quantity = item_quantity + ?, updated_date = ? WHERE item_id = ?",
                      (quantity, current_date, item_id))
        
        # Remove transaction and transaction_items
        c.execute("DELETE FROM transactions WHERE transaction_id = ?", (transaction_id,))
        c.execute("DELETE FROM transaction_items WHERE transaction_id = ?", (transaction_id,))
        
        conn.commit()
        conn.close()
        if transaction_type == "LOAN":
            return f"↩️ Loan {transaction_id} returned. Item(s) back in inventory."
        else:
            return f"↩️ Transaction {transaction_id} reversed. Items returned to inventory."
    except Exception as e:
        conn.close()
        logger.error(f"Inventory: Error returning item: {e}")
        return "Error processing return."

def loan_item(name, user_name="", note=""):
    """Loan an item (checkout/loan to someone, record transaction)"""
    conn = sqlite3.connect(inventory_db)
    c = conn.cursor()
    current_date = time.strftime("%Y-%m-%d")
    current_time = time.strftime("%H:%M:%S")

    try:
        # Get item details
        c.execute("SELECT item_id, item_price, item_quantity FROM items WHERE item_name = ?", (name,))
        item = c.fetchone()
        if not item:
            conn.close()
            return f"Item '{name}' not found."
        item_id, price, current_qty = item

        if current_qty < 1:
            conn.close()
            return f"Insufficient quantity. Available: {current_qty}"

        # Create loan transaction (quantity always 1 for now)
        c.execute("""INSERT INTO transactions (transaction_type, transaction_date, transaction_time, 
                     user_name, total_amount, notes)
                     VALUES (?, ?, ?, ?, ?, ?)""",
                  ("LOAN", current_date, current_time, user_name, 0.0, note))
        transaction_id = c.lastrowid

        # Add transaction item
        c.execute("""INSERT INTO transaction_items (transaction_id, item_id, quantity, price_at_sale)
                     VALUES (?, ?, ?, ?)""",
                  (transaction_id, item_id, 1, price))

        # Update inventory
        c.execute("UPDATE items SET item_quantity = item_quantity - 1, updated_date = ? WHERE item_id = ?",
                  (current_date, item_id))

        conn.commit()
        conn.close()
        return f"🔖 Loaned: {name} (note: {note}) [Transaction #{transaction_id}]"
    except Exception as e:
        conn.close()
        logger.error(f"Inventory: Error loaning item: {e}")
        return "Error processing loan."

def get_loans_for_items():
    """Return a dict of item_name -> list of loan notes for currently loaned items"""
    conn = sqlite3.connect(inventory_db)
    c = conn.cursor()
    try:
        # Find all active loans (not returned)
        c.execute("""
            SELECT i.item_name, t.notes
            FROM transactions t
            JOIN transaction_items ti ON t.transaction_id = ti.transaction_id
            JOIN items i ON ti.item_id = i.item_id
            WHERE t.transaction_type = 'LOAN'
        """)
        rows = c.fetchall()
        conn.close()
        loans = {}
        for item_name, note in rows:
            loans.setdefault(item_name, []).append(note)
        return loans
    except Exception as e:
        conn.close()
        logger.error(f"Inventory: Error fetching loans: {e}")
        return {}

def list_items():
    """List all items in inventory, with loan info if any"""
    conn = sqlite3.connect(inventory_db)
    c = conn.cursor()
    try:
        c.execute("SELECT item_name, item_price, item_quantity, location FROM items ORDER BY item_name")
        items = c.fetchall()
        conn.close()

        if not items:
            return "No items in inventory."

        # Get loan info
        loans = get_loans_for_items()

        result = "📦 Inventory:\n"
        total_value = 0
        for name, price, qty, location in items:
            value = price * qty
            total_value += value
            loc_str = f" @ {location}" if location else ""
            loan_str = ""
            if name in loans:
                for note in loans[name]:
                    loan_str += f" [loan: {note}]"
            result += f"{name}: ${price:.2f} x {qty}{loc_str} = ${value:.2f}{loan_str}\n"

        result += f"\nTotal Value: ${total_value:.2f}"
        return result.rstrip()
    except Exception as e:
        conn.close()
        logger.error(f"Inventory: Error listing items: {e}")
        return "Error listing items."

def get_stats():
    """Get sales statistics"""
    conn = sqlite3.connect(inventory_db)
    c = conn.cursor()
    
    try:
        current_date = time.strftime("%Y-%m-%d")
        
        # Get today's sales
        c.execute("""SELECT COUNT(*), SUM(total_amount) 
                     FROM transactions 
                     WHERE transaction_type = 'SALE' AND transaction_date = ?""",
                  (current_date,))
        today_stats = c.fetchone()
        today_count = today_stats[0] or 0
        today_total = today_stats[1] or 0
        
        # Get hot item (most sold today)
        c.execute("""SELECT i.item_name, SUM(ti.quantity) as total_qty
                     FROM transaction_items ti
                     JOIN transactions t ON ti.transaction_id = t.transaction_id
                     JOIN items i ON ti.item_id = i.item_id
                     WHERE t.transaction_date = ? AND t.transaction_type = 'SALE'
                     GROUP BY i.item_name
                     ORDER BY total_qty DESC
                     LIMIT 1""", (current_date,))
        hot_item = c.fetchone()
        
        conn.close()
        
        result = f"📊 Today's Stats:\n"
        result += f"Sales: {today_count}\n"
        result += f"Revenue: ${today_total:.2f}\n"
        if hot_item:
            result += f"Hot Item: {hot_item[0]} ({hot_item[1]} sold)"
        else:
            result += "Hot Item: None"
        
        return result
    except Exception as e:
        conn.close()
        logger.error(f"Inventory: Error getting stats: {e}")
        return "Error getting stats."

def add_to_cart(user_id, item_name, quantity):
    """Add item to user's cart"""
    conn = sqlite3.connect(inventory_db)
    c = conn.cursor()
    current_date = time.strftime("%Y-%m-%d")
    
    try:
        # Get item details
        c.execute("SELECT item_id, item_quantity FROM items WHERE item_name = ?", (item_name,))
        item = c.fetchone()
        if not item:
            conn.close()
            return f"Item '{item_name}' not found."
        
        item_id, available_qty = item
        
        # Check if item already in cart
        c.execute("SELECT quantity FROM carts WHERE user_id = ? AND item_id = ?", (user_id, item_id))
        existing = c.fetchone()
        
        if existing:
            new_qty = existing[0] + quantity
            if new_qty > available_qty:
                conn.close()
                return f"Insufficient quantity. Available: {available_qty}"
            c.execute("UPDATE carts SET quantity = ? WHERE user_id = ? AND item_id = ?",
                      (new_qty, user_id, item_id))
        else:
            if quantity > available_qty:
                conn.close()
                return f"Insufficient quantity. Available: {available_qty}"
            c.execute("INSERT INTO carts (user_id, item_id, quantity, added_date) VALUES (?, ?, ?, ?)",
                      (user_id, item_id, quantity, current_date))
        
        conn.commit()
        conn.close()
        return f"🛒 Added to cart: {quantity}x {item_name}"
    except Exception as e:
        conn.close()
        logger.error(f"Inventory: Error adding to cart: {e}")
        return "Error adding to cart."

def remove_from_cart(user_id, item_name):
    """Remove item from user's cart"""
    conn = sqlite3.connect(inventory_db)
    c = conn.cursor()
    
    try:
        c.execute("""DELETE FROM carts 
                     WHERE user_id = ? AND item_id = (SELECT item_id FROM items WHERE item_name = ?)""",
                  (user_id, item_name))
        if c.rowcount == 0:
            conn.close()
            return f"Item '{item_name}' not in cart."
        
        conn.commit()
        conn.close()
        return f"🗑️ Removed from cart: {item_name}"
    except Exception as e:
        conn.close()
        logger.error(f"Inventory: Error removing from cart: {e}")
        return "Error removing from cart."

def list_cart(user_id):
    """List items in user's cart"""
    conn = sqlite3.connect(inventory_db)
    c = conn.cursor()
    
    try:
        c.execute("""SELECT i.item_name, i.item_price, c.quantity
                     FROM carts c
                     JOIN items i ON c.item_id = i.item_id
                     WHERE c.user_id = ?""", (user_id,))
        items = c.fetchall()
        conn.close()
        
        if not items:
            return "🛒 Cart is empty."
        
        result = "🛒 Your Cart:\n"
        total = 0
        for name, price, qty in items:
            subtotal = price * qty
            total += subtotal
            result += f"{name}: ${price:.2f} x {qty} = ${subtotal:.2f}\n"
        
        total = round_price(total, is_taxed_sale=True)
        result += f"\nTotal: ${total:.2f}"
        return result
    except Exception as e:
        conn.close()
        logger.error(f"Inventory: Error listing cart: {e}")
        return "Error listing cart."

def checkout_cart(user_id, user_name="", transaction_type="SALE", notes=""):
    """Process cart as a transaction"""
    conn = sqlite3.connect(inventory_db)
    c = conn.cursor()
    current_date = time.strftime("%Y-%m-%d")
    current_time = time.strftime("%H:%M:%S")
    
    try:
        # Get cart items
        c.execute("""SELECT i.item_id, i.item_name, i.item_price, c.quantity, i.item_quantity
                     FROM carts c
                     JOIN items i ON c.item_id = i.item_id
                     WHERE c.user_id = ?""", (user_id,))
        cart_items = c.fetchall()
        
        if not cart_items:
            conn.close()
            return "Cart is empty."
        
        # Verify all items have sufficient quantity
        for item_id, name, price, cart_qty, stock_qty in cart_items:
            if stock_qty < cart_qty:
                conn.close()
                return f"Insufficient quantity for '{name}'. Available: {stock_qty}"
        
        # Calculate total
        total = sum(price * qty for _, _, price, qty, _ in cart_items)
        total = round_price(total, is_taxed_sale=(transaction_type == "SALE"))
        
        # Create transaction
        c.execute("""INSERT INTO transactions (transaction_type, transaction_date, transaction_time,
                     user_name, total_amount, notes)
                     VALUES (?, ?, ?, ?, ?, ?)""",
                  (transaction_type, current_date, current_time, user_name, total, notes))
        transaction_id = c.lastrowid
        
        # Process each item
        for item_id, name, price, quantity, _ in cart_items:
            # Add to transaction items
            c.execute("""INSERT INTO transaction_items (transaction_id, item_id, quantity, price_at_sale)
                         VALUES (?, ?, ?, ?)""",
                      (transaction_id, item_id, quantity, price))
            
            # Update inventory (subtract for SALE, add for BUY)
            if transaction_type == "SALE":
                c.execute("UPDATE items SET item_quantity = item_quantity - ?, updated_date = ? WHERE item_id = ?",
                          (quantity, current_date, item_id))
            else:  # BUY
                c.execute("UPDATE items SET item_quantity = item_quantity + ?, updated_date = ? WHERE item_id = ?",
                          (quantity, current_date, item_id))
        
        # Clear cart
        c.execute("DELETE FROM carts WHERE user_id = ?", (user_id,))
        
        conn.commit()
        conn.close()
        
        emoji = "💰" if transaction_type == "SALE" else "📦"
        return f"{emoji} Transaction #{transaction_id} completed: ${total:.2f}"
    except Exception as e:
        conn.close()
        logger.error(f"Inventory: Error processing cart: {e}")
        return "Error processing cart."

def clear_cart(user_id):
    """Clear user's cart"""
    conn = sqlite3.connect(inventory_db)
    c = conn.cursor()
    
    try:
        c.execute("DELETE FROM carts WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
        return "🗑️ Cart cleared."
    except Exception as e:
        conn.close()
        logger.error(f"Inventory: Error clearing cart: {e}")
        return "Error clearing cart."

def process_inventory_command(nodeID, message, name="none"):
    """Process inventory and POS commands"""
    # Check ban list
    if str(nodeID) in bbs_ban_list:
        logger.warning("System: Inventory attempt from the ban list")
        return "Unable to process command"
    
    message_lower = message.lower()
    parts = message.split()
    
    try:
        # Help command
        if "?" in message_lower:
            return get_inventory_help()
        
        # Item management commands
        if message_lower.startswith("itemadd "):
            # itemadd <name> <qty> [price] [location]
            if len(parts) < 3:
                return "Usage: itemadd <name> <qty> [price] [location]"
            item_name = parts[1]
            try:
                quantity = int(parts[2])
            except ValueError:
                return "Invalid quantity."
            price = 0.0
            location = ""
            if len(parts) > 3:
                try:
                    price = float(parts[3])
                    location = " ".join(parts[4:]) if len(parts) > 4 else ""
                except ValueError:
                    # If price is omitted, treat parts[3] as location
                    price = 0.0
                    location = " ".join(parts[3:])
            return add_item(item_name, price, quantity, location)
        
        elif message_lower.startswith("itemremove "):
            item_name = " ".join(parts[1:])
            return remove_item(item_name)
        
        elif message_lower.startswith("itemreset "):
            # itemreset name [price=X] [quantity=Y]
            if len(parts) < 2:
                return "Usage: itemreset <name> [price=X] [quantity=Y]"
            item_name = parts[1]
            price = None
            quantity = None
            for part in parts[2:]:
                if part.startswith("price="):
                    try:
                        price = float(part.split("=")[1])
                    except ValueError:
                        return "Invalid price value."
                elif part.startswith("quantity=") or part.startswith("qty="):
                    try:
                        quantity = int(part.split("=")[1])
                    except ValueError:
                        return "Invalid quantity value."
            return reset_item(item_name, price, quantity)
        
        elif message_lower.startswith("itemsell "):
            # itemsell name quantity [notes]
            if len(parts) < 3:
                return "Usage: itemsell <name> <quantity> [notes]"
            item_name = parts[1]
            try:
                quantity = int(parts[2])
                notes = " ".join(parts[3:]) if len(parts) > 3 else ""
                return sell_item(item_name, quantity, name, notes)
            except ValueError:
                return "Invalid quantity."
        
        elif message_lower.startswith("itemreturn "):
            # itemreturn transaction_id
            if len(parts) < 2:
                return "Usage: itemreturn <transaction_id>"
            try:
                transaction_id = int(parts[1])
                return return_item(transaction_id)
            except ValueError:
                return "Invalid transaction ID."
        
        elif message_lower.startswith("itemloan "):
            # itemloan <name> <note>
            if len(parts) < 3:
                return "Usage: itemloan <name> <note>"
            item_name = parts[1]
            note = " ".join(parts[2:])
            return loan_item(item_name, name, note)
        
        elif message_lower == "itemlist":
            return list_items()
        
        elif message_lower == "itemstats":
            return get_stats()
        
        # Cart commands
        elif message_lower.startswith("cartadd "):
            # cartadd name quantity
            if len(parts) < 3:
                return "Usage: cartadd <name> <quantity>"
            item_name = parts[1]
            try:
                quantity = int(parts[2])
                return add_to_cart(str(nodeID), item_name, quantity)
            except ValueError:
                return "Invalid quantity."
        
        elif message_lower.startswith("cartremove "):
            item_name = " ".join(parts[1:])
            return remove_from_cart(str(nodeID), item_name)
        
        elif message_lower == "cartlist" or message_lower == "cart":
            return list_cart(str(nodeID))
        
        elif message_lower.startswith("cartbuy") or message_lower.startswith("cartsell"):
            transaction_type = "BUY" if "buy" in message_lower else "SALE"
            notes = " ".join(parts[1:]) if len(parts) > 1 else ""
            return checkout_cart(str(nodeID), name, transaction_type, notes)
        
        elif message_lower == "cartclear":
            return clear_cart(str(nodeID))
        
        else:
            return "Invalid command. Send 'item?' for help."
    
    except Exception as e:
        logger.error(f"Inventory: Error processing command: {e}")
        return "Error processing command."

def get_inventory_help():
    """Return help text for inventory commands"""
    return (
        "📦 Inventory Commands:\n"
        "  itemadd <name> <qty> [price] [loc]\n"
        "  itemremove <name>\n"
        "  itemreset name> <qty> [price] [loc]\n"
        "  itemsell <name> <qty> [notes]\n"
        "  itemloan <name> <note>\n"
        "  itemreturn <transaction_id>\n"
        "  itemlist\n"
        "  itemstats\n"
        "\n"
        "🛒 Cart Commands:\n"
        "  cartadd <name> <qty>\n"
        "  cartremove <name>\n"
        "  cartlist\n"
        "  cartbuy/cartsell [notes]\n"
        "  cartclear\n"
    )
