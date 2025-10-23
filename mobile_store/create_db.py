import sqlite3

# Connect to database (creates it if it doesn’t exist)
conn = sqlite3.connect('products.db')
c = conn.cursor()

# ------------------ CREATE TABLES ------------------ #
# Products table
c.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        price REAL,
        image TEXT
    )
''')

# Users table
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
''')

# Admin table
c.execute('''
    CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
''')

# Orders table
c.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        address TEXT NOT NULL,
        total REAL NOT NULL
    )
''')

# ------------------ ADD SAMPLE DATA ------------------ #
products = [
    ("iPhone 15 Pro", 120000, "ipn15pro.png"),
    ("Samsung Galaxy S24", 95600, "s24.jpeg"),
    ("Samsung Galaxy S24fe", 75600, "s24fe.png"),
    ("Realme GT 6", 40000, "gt6.png"),
    ("Vivo X100", 50000, "vivox100.png"),
    ("Asus ROG Phone 7", 80000, "asusrog7.jpg"),
    ("OnePlus 12", 70000, "oneplus12.jpg"),
    ("Oppo Find N2 Flip", 90000, "oppon2flip.jpg"),
    ("Google Pixel 8", 85000, "pixel8.jpg"),
    ("Xiomi 14", 65000, "xiaomi14.jpg"),
    ("Redmagic 9 pro",92000, "redmagic.jpg"),
    ("iqoo 12", 48000, "iqoo.png")

]

c.executemany("INSERT OR IGNORE INTO products (name, price, image) VALUES (?, ?, ?)", products)

# Add a default admin if not exists
c.execute("INSERT OR IGNORE INTO admin (username, password) VALUES (?, ?)", ("admin", "admin123"))

conn.commit()
conn.close()

print("✅ Database setup complete! All tables created and data inserted successfully.")
