from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secretkey"
DB_PATH = "products.db"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create required tables and add sample products if empty."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            price REAL,
            image TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            name TEXT,
            phone TEXT,
            address TEXT,
            total REAL
        )
    ''')

    # Insert sample products only if table is empty
    cur = c.execute("SELECT COUNT(*) FROM products")
    count = cur.fetchone()[0]
    if count == 0:
        products = [
            ("Asus ROG Phone 7", 80000, "asusrog7.jpg"),
            ("Realme GT 6t", 40000, "gt6.png"),
            ("iPhone 15 Pro", 120000, "ipn15pro.png"),
            ("OnePlus 12", 70000, "oneplus12.jpg"),
            ("Samsung Galaxy S24", 95600, "s24.jpeg"),
            ("Samsung Galaxy S24fe", 75600, "s24fe.png"),
            ("Vivo X100", 50000, "vivox100.png"),
            ("Oppo Find N2 Flip", 90000, "oppon2flip.jpg"),
            ("Google Pixel 8", 85000, "pixel8.jpg"),
            ("Xiomi 14", 65000, "xiaomi14.jpg"),
            ("Redmagic 9 pro",92000, "redmagic.jpg"),
            ("iqoo 12", 48000, "iqoo.png")
        ]
        c.executemany("INSERT OR IGNORE INTO products (name, price, image) VALUES (?, ?, ?)", products)
    conn.commit()
    conn.close()


@app.route("/")
def index():
    # always show login first (unless already logged in)
    if "user" in session:
        return redirect(url_for("home"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if not username or not password:
            flash("Enter username and password.", "danger")
            return redirect(url_for("register"))

        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username already exists. Choose another.", "danger")
        finally:
            conn.close()
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
        conn.close()
        if user:
            session["user"] = username
            session.permanent = False  # expires when browser is closed
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password.", "danger")
    return render_template("login.html")

# ------------------ ADMIN LOGIN ------------------ #
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        conn = get_db_connection()
        admin = conn.execute("SELECT * FROM admin WHERE username=? AND password=?", (username, password)).fetchone()
        conn.close()
        if admin:
            session["admin"] = username
            flash("Admin login successful!", "success")
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid admin credentials.", "danger")
    return render_template("admin_login.html")

# ------------------ ADMIN DASHBOARD ------------------ #
@app.route("/admin_dashboard")
def admin_dashboard():
    if "admin" not in session:
        flash("Please log in as admin.", "warning")
        return redirect(url_for("admin_login"))
    # Example: show all orders
    conn = get_db_connection()
    orders = conn.execute("SELECT * FROM orders").fetchall()
    conn.close()
    return render_template("admin_dashboard.html", orders=orders, admin=session["admin"])

# ------------------ ADMIN LOGOUT ------------------ #
@app.route("/admin_logout")
def admin_logout():
    session.pop("admin", None)
    flash("Admin logged out.", "info")
    return redirect(url_for("admin_login"))


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/home")
def home():
    if "user" not in session:
        flash("Please log in.", "warning")
        return redirect(url_for("login"))
    conn = get_db_connection()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return render_template("home.html", products=products, user=session["user"])


@app.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):
    if "user" not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))
    if "cart" not in session:
        session["cart"] = []
    session["cart"].append(product_id)
    session.modified = True
    flash("Added to cart.", "success")
    return redirect(url_for("cart"))


@app.route("/cart")
def cart():
    if "user" not in session:
        return redirect(url_for("login"))
    cart_items = []
    total = 0
    if "cart" in session and session["cart"]:
        conn = get_db_connection()
        for pid in session["cart"]:
            p = conn.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
            if p:
                cart_items.append(p)
                total += p["price"]
        conn.close()
    return render_template("cart.html", cart=cart_items, total=total)


@app.route("/checkout")
def checkout():
    if "user" not in session:
        return redirect(url_for("login"))
    if "cart" not in session or len(session["cart"]) == 0:
        flash("Cart is empty.", "warning")
        return redirect(url_for("home"))
    # Get cart products for display
    cart_items = []
    if "cart" in session and session["cart"]:
        conn = get_db_connection()
        for pid in session["cart"]:
            p = conn.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
            if p:
                cart_items.append(p)
        conn.close()
    return render_template("checkout.html", cart=cart_items)


@app.route("/process_payment", methods=["POST"])
def process_payment():
    if "user" not in session:
        return redirect(url_for("login"))

    name = request.form.get("name", "")
    card = request.form.get("card", "")
    expiry = request.form.get("expiry", "")
    phone = request.form.get("phone", "")
    address = request.form.get("address", "")

    conn = get_db_connection()
    total = 0
    products = []
    if "cart" in session:
        for pid in session["cart"]:
            p = conn.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
            if p:
                total += p["price"]
                products.append(p)
    conn.execute("INSERT INTO orders (username, name, phone, address, total) VALUES (?, ?, ?, ?, ?)",
                 (session["user"], name, phone, address, total))
    conn.commit()
    conn.close()

    session.pop("cart", None)
    return render_template("success.html", name=name, address=address, products=products)


if __name__ == "__main__":
    init_db()# ensure DB + sample data exist
    app.run(debug=True)# restart app manually to clear any previous state if needed