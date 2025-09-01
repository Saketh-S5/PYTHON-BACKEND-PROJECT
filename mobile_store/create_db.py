import sqlite3


conn = sqlite3.connect('products.db')
c = conn.cursor()


c.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        price REAL,
        image TEXT
    )
''')


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
           ]

c.executemany("INSERT OR IGNORE INTO products (name, price, image) VALUES (?, ?, ?)", products)

conn.commit()
conn.close()

print("Database updated successfully without duplicates!")
