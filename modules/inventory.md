# Inventory & Point of Sale System

## Overview

The inventory module provides a complete point-of-sale (POS) system for mesh networks, enabling inventory management, sales tracking, and cart-based transactions. This system is ideal for:

- Emergency supply management
- Event merchandise sales
- Community supply tracking
- Remote location inventory
- Asset management
- Field operations logistics

## Features

### 🏪 Complete POS System
- **Item Management**: Add, remove, and update inventory items
- **Cart System**: Build orders before completing transactions
- **Transaction Logging**: Full audit trail of all sales and returns
- **Price Tracking**: Track price changes over time
- **Location Tracking**: Optional warehouse/location field for items

### 💰 Financial Features
- **Penny Rounding**: USA cash sales support
  - Cash sales round down to nearest nickel
  - Taxed sales round up to nearest nickel
- **Daily Statistics**: Track sales performance
- **Hot Item Detection**: Identify best-selling products
- **Revenue Tracking**: Daily sales totals

### 📊 Reporting
- **Inventory Value**: Total inventory worth
- **Sales Reports**: Daily transaction summaries
- **Best Sellers**: Most popular items

## Configuration

Add to your `config.ini`:

```ini
[inventory]
enabled = True
inventory_db = data/inventory.db
# Set to True to disable penny precision and round to nickels (USA cash sales)
# When True: cash sales round down, taxed sales round up to nearest $0.05
# When False (default): normal penny precision ($0.01)
disable_penny = False
```

## Commands Reference

### Item Management

#### Add Item
```
itemadd <name> <price> <quantity> [location]
```

Adds a new item to inventory.

**Examples:**
```
itemadd Radio 149.99 5 Shelf-A
itemadd Battery 12.50 20 Warehouse
itemadd Water 1.00 100
```

#### Remove Item
```
itemremove <name>
```

Removes an item from inventory (also removes from all carts).

**Examples:**
```
itemremove Radio
itemremove "First Aid Kit"
```

#### Update Item
```
itemreset <name> [price=X] [qty=Y]
```

Updates item price and/or quantity.

**Examples:**
```
itemreset Radio price=139.99
itemreset Battery qty=50
itemreset Water price=0.95 qty=200
```

#### Quick Sale
```
itemsell <name> <quantity> [notes]
```

Sell directly without using cart (for quick transactions).

**Examples:**
```
itemsell Battery 2
itemsell Water 10 Emergency supply
itemsell Radio 1 Field unit sale
```

#### Return Transaction
```
itemreturn <transaction_id>
```

Reverse a transaction and return items to inventory.

**Examples:**
```
itemreturn 123
itemreturn 45
```

#### List Inventory
```
itemlist
```

Shows all items with prices, quantities, and total inventory value.

**Example Response:**
```
📦 Inventory:
Radio: $149.99 x 5 @ Shelf-A = $749.95
Battery: $12.50 x 20 @ Warehouse = $250.00
Water: $1.00 x 100 = $100.00

Total Value: $1,099.95
```

#### Statistics
```
itemstats
```

Shows today's sales performance.

**Example Response:**
```
📊 Today's Stats:
Sales: 15
Revenue: $423.50
Hot Item: Battery (8 sold)
```

### Cart System

#### Add to Cart
```
cartadd <name> <quantity>
```

Add items to your shopping cart.

**Examples:**
```
cartadd Radio 2
cartadd Battery 4
cartadd Water 12
```

#### Remove from Cart
```
cartremove <name>
```

Remove items from cart.

**Examples:**
```
cartremove Radio
cartremove Battery
```

#### View Cart
```
cart
cartlist
```

Display your current cart contents and total.

**Example Response:**
```
🛒 Your Cart:
Radio: $149.99 x 2 = $299.98
Battery: $12.50 x 4 = $50.00

Total: $349.98
```

#### Complete Transaction
```
cartbuy [notes]
cartsell [notes]
```

Process the cart as a transaction. Use `cartbuy` for purchases (adds to inventory) or `cartsell` for sales (removes from inventory).

**Examples:**
```
cartsell Customer purchase
cartbuy Restocking supplies
cartsell Event merchandise
```

#### Clear Cart
```
cartclear
```

Empty your shopping cart without completing a transaction.

## Use Cases

### 1. Event Merchandise Sales

Perfect for festivals, hamfests, or community events:

```
# Setup inventory
itemadd Tshirt 20.00 50 Booth-A
itemadd Hat 15.00 30 Booth-A
itemadd Sticker 5.00 100 Booth-B

# Customer transaction
cartadd Tshirt 2
cartadd Hat 1
cartsell Festival sale

# Check daily performance
itemstats
```

### 2. Emergency Supply Tracking

Track supplies during disaster response:

```
# Add emergency supplies
itemadd Water 0.00 500 Warehouse-1
itemadd MRE 0.00 200 Warehouse-1
itemadd Blanket 0.00 100 Warehouse-2

# Distribute supplies
itemsell Water 50 Red Cross distribution
itemsell MRE 20 Family shelter

# Check remaining inventory
itemlist
```

### 3. Field Equipment Management

Manage tools and equipment in remote locations:

```
# Track equipment
itemadd Generator 500.00 3 Base-Camp
itemadd Radio 200.00 10 Equipment-Room
itemadd Battery 15.00 50 Supply-Closet

# Equipment checkout
itemsell Generator 1 Field deployment
itemsell Radio 5 Survey team

# Monitor inventory
itemlist
itemstats
```

### 4. Community Supply Exchange

Facilitate supply exchanges within a community:

```
# Add community items
itemadd Seeds 2.00 100 Community-Garden
itemadd Firewood 10.00 20 Storage-Shed

# Member transactions
cartadd Seeds 5
cartadd Firewood 2
cartsell Member-123 purchase
```

## Penny Rounding (USA Mode)

When `disable_penny = True` is set in the configuration, the system implements penny rounding (disabling penny precision). This follows USA practice where pennies are not commonly used in cash transactions.

### Cash Sales (Round Down)
- $10.47 → $10.45
- $10.48 → $10.45
- $10.49 → $10.45

### Taxed Sales (Round Up)
- $10.47 → $10.50
- $10.48 → $10.50
- $10.49 → $10.50

This follows common USA practice where pennies are not used in cash transactions.

## Database Schema

The system uses SQLite with four tables:

### items
```sql
CREATE TABLE items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT UNIQUE NOT NULL,
    item_price REAL NOT NULL,
    item_quantity INTEGER NOT NULL DEFAULT 0,
    location TEXT,
    created_date TEXT,
    updated_date TEXT
)
```

### transactions
```sql
CREATE TABLE transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_type TEXT NOT NULL,
    transaction_date TEXT NOT NULL,
    transaction_time TEXT NOT NULL,
    user_name TEXT,
    total_amount REAL NOT NULL,
    notes TEXT
)
```

### transaction_items
```sql
CREATE TABLE transaction_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    price_at_sale REAL NOT NULL,
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id),
    FOREIGN KEY (item_id) REFERENCES items(item_id)
)
```

### carts
```sql
CREATE TABLE carts (
    cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    added_date TEXT,
    FOREIGN KEY (item_id) REFERENCES items(item_id)
)
```

## Security Considerations

- Users on the `bbs_ban_list` cannot use inventory commands
- Each user has their own cart (identified by node ID)
- Transactions are logged with user information for accountability
- All database operations use parameterized queries to prevent SQL injection

## Tips and Best Practices

1. **Regular Inventory Checks**: Use `itemlist` regularly to monitor stock levels
2. **Descriptive Notes**: Add notes to transactions for better tracking
3. **Location Tags**: Use consistent location naming for better organization
4. **Daily Reviews**: Check `itemstats` at the end of each day
5. **Transaction IDs**: Keep track of transaction IDs for potential returns
6. **Quantity Updates**: Use `itemreset` to adjust inventory after physical counts
7. **Cart Cleanup**: Use `cartclear` if you change your mind before completing a sale

## Troubleshooting

### Item Already Exists
If you get "Item already exists" when using `itemadd`, use `itemreset` instead to update the existing item.

### Insufficient Quantity
If you see "Insufficient quantity" error, check available stock with `itemlist` before attempting the sale.

### Transaction Not Found
If `itemreturn` fails, verify the transaction ID exists. Use recent transaction logs to find valid IDs.

### Cart Not Showing Items
Each user has their own cart. Make sure you're using your own node to view your cart.

## Future Enhancements

Planned features for future releases:
- Multi-item itemsell command
- Transaction history viewing
- Inventory reports by date range
- Low stock alerts
- Price history tracking
- Barcode/QR code support
- Integration with external accounting systems

## Support

For issues or feature requests, please file an issue on the GitHub repository.
