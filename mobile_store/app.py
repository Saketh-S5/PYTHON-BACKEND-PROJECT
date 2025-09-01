from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secretkey"  # session secret

# ------------------ DB CONNECTION ------------------ #
def get_db_connection():
    conn = sqlite3.connect("products.db")
    conn.row_factory = sqlite3.Row
    return conn

# ------------------ HOME PAGE ------------------ #
@app.route("/")
def home():
    conn = get_db_connection()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return render_template("home.html", products=products)

# ------------------ ADD TO CART ------------------ #
@app.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):
    if "cart" not in session:
        session["cart"] = []
    session["cart"].append(product_id)
    session.modified = True
    return redirect(url_for("cart"))

# ------------------ CART ------------------ #
@app.route("/cart")
def cart():
    cart_items = []
    total = 0

    if "cart" in session:
        conn = get_db_connection()
        for pid in session["cart"]:
            product = conn.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
            if product:
                cart_items.append(product)
                total += product["price"]
        conn.close()

    return render_template("cart.html", cart=cart_items, total=total)

# ------------------ CHECKOUT ------------------ #
@app.route("/checkout")
def checkout():
    if "cart" not in session or len(session["cart"]) == 0:
        return redirect(url_for("home"))
    return render_template("checkout.html")

# ------------------ PROCESS PAYMENT ------------------ #
@app.route("/process_payment", methods=["POST"])
def process_payment():
    name = request.form["name"]
    card = request.form["card"]
    expiry = request.form["expiry"]
    cvv = request.form["cvv"]

    # Dummy payment logic (always success)
    session.pop("cart", None)  # clear cart
    return render_template("success.html", name=name)

# ------------------ MAIN ------------------ #
if __name__ == "__main__":
    app.run(debug=True)
