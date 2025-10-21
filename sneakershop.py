import json
import os
import random
import re
import string
import sqlite3
import ssl
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename 

SENDER_EMAIL = "help.manoysneaks@gmail.com"
SENDER_PASSWORD = "jjuc srpw easo tpvv" 

def send_order_confirmation_email(recipient_email, tracking_number, checkout_data, cart_items):
    """Sends a purchase confirmation email using Gmail's SMTP server."""
    
    if SENDER_EMAIL == "your_store_email@gmail.com":
        app.logger.warning("Email not sent: SENDER_EMAIL is not configured.")
        return

    full_name = f"{checkout_data['first_name']} {checkout_data['last_name']}"
    
    item_rows = ""
    for item in cart_items:
        item_rows += f"""
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;">{item['name']} ({item['size']})</td>
            <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{item['quantity']}</td>
            <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">₱{item['price'] * item['quantity']:.2f}</td>
        </tr>
        """
        
    subtotal = sum(item['price'] * item['quantity'] for item in cart_items)
    shipping = 150.00
    tax = subtotal * 0.12
    total_amount = subtotal + shipping + tax

    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="max-width: 600px; margin: auto; border: 1px solid #eee; padding: 20px;">
            <h2 style="color: #3498db;">Order Confirmation - #{tracking_number}</h2>
            <p>Hi {full_name},</p>
            <p>Thank you for your purchase from our store! Your order has been placed and is now *Pending* processing. Details of your order are below:</p>
            
            <h3 style="border-bottom: 1px solid #eee; padding-bottom: 5px;">Order Summary</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background-color: #f2f2f2;">
                        <th style="padding: 8px; border: 1px solid #ddd; text-align: left;">Item</th>
                        <th style="padding: 8px; border: 1px solid #ddd; text-align: center;">Qty</th>
                        <th style="padding: 8px; border: 1px solid #ddd; text-align: right;">Price</th>
                    </tr>
                </thead>
                <tbody>
                    {item_rows}
                </tbody>
            </table>

            <h3 style="margin-top: 20px; border-bottom: 1px solid #eee; padding-bottom: 5px;">Totals</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 5px 0;">Subtotal:</td>
                    <td style="padding: 5px 0; text-align: right;">₱{subtotal:.2f}</td>
                </tr>
                <tr>
                    <td style="padding: 5px 0;">Shipping:</td>
                    <td style="padding: 5px 0; text-align: right;">₱{shipping:.2f}</td>
                </tr>
                <tr>
                    <td style="padding: 5px 0;">Tax (12%):</td>
                    <td style="padding: 5px 0; text-align: right;">₱{tax:.2f}</td>
                </tr>
                <tr>
                    <td style="padding: 5px 0; font-weight: bold;">Total Paid:</td>
                    <td style="padding: 5px 0; text-align: right; font-weight: bold;">₱{total_amount:.2f}</td>
                </tr>
            </table>

            <h3 style="margin-top: 20px; border-bottom: 1px solid #eee; padding-bottom: 5px;">Shipping Details</h3>
            <p>
                Tracking Number: {tracking_number}<br>
                Recipient: {full_name}<br>
                Address: {checkout_data['address']}, {checkout_data['barangay']}, {checkout_data['city']}, {checkout_data['province']}, {checkout_data['postal_code']}<br>
                Payment Method: {checkout_data['payment_method']}
            </p>

            <p style="margin-top: 30px;">You can track your order status on our website using your tracking number.</p>
            <p>Sincerely,<br>The Sneaker Shop Team</p>
        </div>
    </body>
    </html>
    """

    msg = EmailMessage()
    msg.set_content(f"Your order #{tracking_number} has been confirmed. Please view the full details on our website.")
    msg.add_alternative(html_content, subtype='html')
    msg['Subject'] = f"Your Order Confirmation - ManoySneaks #{tracking_number}"
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient_email

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
            app.logger.info(f"Confirmation email sent to {recipient_email} for order {tracking_number}")
    except Exception as e:
        app.logger.error(f"Failed to send email for order {tracking_number}. Error: {e}")

def send_subscription_confirmation_email(recipient_email):
    """Sends a newsletter subscription confirmation email."""
    
    if SENDER_EMAIL == "your_store_email@gmail.com":
        app.logger.warning("Email not sent: SENDER_EMAIL is not configured.")
        return

    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="max-width: 600px; margin: auto; border: 1px solid #eee; padding: 20px;">
            <h2 style="color: #000;">Welcome to the ManoySneaks Crew! 👟</h2>
            <p>Hi there,</p>
            <p>Thank you for subscribing to the ManoySneaks newsletter! You are now officially part of our community and will be the first to know about:</p>
            <ul>
                <li>🔥 New sneaker releases</li>
                <li>🏷️ Exclusive discounts and sales</li>
                <li>📰 Sneaker news and style guides</li>
            </ul>
            <p>We promise not to flood your inbox. Get ready for some fresh kicks!</p>
            <p style="margin-top: 30px;">Happy Sneaker Hunting,</p>
            <p>The ManoySneaks Team</p>
        </div>
    </body>
    </html>
    """

    msg = EmailMessage()
    msg.set_content(f"You have successfully subscribed to the ManoySneaks newsletter.")
    msg.add_alternative(html_content, subtype='html')
    msg['Subject'] = f"Subscription Confirmed: Welcome to ManoySneaks!"
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient_email

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
            app.logger.info(f"Subscription email sent to {recipient_email}")
            return True
    except Exception as e:
        app.logger.error(f"Failed to send subscription email to {recipient_email}. Error: {e}")
        return False

def send_contact_form_email(client_name, client_email, subject, message_body):
    """Sends the client's contact message to the store's help email address (SENDER_EMAIL)."""
    
    recipient_email = SENDER_EMAIL 

    if SENDER_EMAIL == "your_store_email@gmail.com":
        app.logger.warning("Contact email not sent: SENDER_EMAIL is not configured.")
        return False

    msg = EmailMessage()
    msg['To'] = recipient_email
    msg['From'] = SENDER_EMAIL
    msg['Subject'] = f"[CONTACT FORM] New Message from {client_name}: {subject}"

    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
            <div style="max-width: 600px; margin: auto; border: 1px solid #eee; padding: 20px; border-radius: 8px;">
                <h2 style="color: #000; border-bottom: 2px solid #eee; padding-bottom: 10px;">New Customer Inquiry</h2>
                <p>A new message has been received through the 'Contact Us' page.</p>
                
                <h3 style="color: #e74c3c; margin-top: 20px;">Sender Details:</h3>
                <p><strong>Name:</strong> {client_name}</p>
                <p><strong>Email:</strong> <a href="mailto:{client_email}">{client_email}</a></p>
                <p><strong>Subject:</strong> {subject}</p>

                <h3 style="color: #e74c3c; margin-top: 20px;">Message:</h3>
                <div style="padding: 15px; background-color: #f8f8f8; border-radius: 6px; border-left: 5px solid #e74c3c;">
                    <p style="white-space: pre-wrap; margin: 0;">{message_body}</p>
                </div>
                
                <p style="margin-top: 30px; font-size: 0.9em; color: #999;">This message was automatically generated by the contact form submission.</p>
            </div>
        </body>
    </html>
    """
    msg.set_content(f"New contact message received from {client_name} ({client_email}). Subject: {subject}. Check HTML content for details.")
    msg.add_alternative(body, subtype='html')

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        app.logger.info(f"Contact form email successfully sent to {recipient_email} from {client_email}.")
        return True
    except Exception as e:
        app.logger.error(f"Error sending contact form email from {client_email}: {e}")
        return False

LOCATION_DATA = {
    "Laguna": {
        "San Pedro": [
            "Bagong Silang", "Calendola", "Chrysanthemum", "Cuyab", "G.S.I.S.", "Landayan", "Langgam", "Maharlika", 
            "Magsaysay", "Narra", "Nueva", "Pacita 1", "Pacita 2", "Poblacion", "Riverside", "Rosario", 
            "San Antonio", "San Roque", "Santo Niño", "United Bayanihan"
        ],
        "Biñan": [
            "Bungahan", "Canlalay", "De La Paz", "Ganado", "Langkiwa", "Loma", "Malaban", "Malamig", "Mampalasan",
            "Platero", "Poblacion", "San Antonio", "San Francisco", "San Jose", "San Vicente", "Santo Domingo",
            "Santo Niño", "Santo Tomas", "Soro-Soro", "Timbao", "Tubigan", "Zapote"
        ],
        "Santa Rosa": [
            "Aplaya", "Balibago", "Caingin", "Dila", "Dita", "Don Jose", "Ibaba", "Kanluran", "Labas",
            "Malitlit", "Malusak", "Market Area", "Pook", "Pulong Santa Cruz", "Sinalhan", "Tagapo"
        ],
        "Cabuyao": [
            "Baclaran", "Banay-Banay", "Banlic", "Bigaa", "Butong", "Casile", "Diezmo", "Gulod", "Mamatid",
            "Marinig", "Niugan", "Pittland", "Pulo", "Sala", "San Isidro", "Tres Cruses",
            "Poblacion Uno", "Poblacion Dos", "Poblacion Tres"
        ],
        "Calamba": [
            "Bagong Kalsada", "Bañadero", "Banlic", "Barandal", "Barangay 1", "Barangay 2", "Barangay 3", "Barangay 4",
            "Barangay 5", "Barangay 6", "Barangay 7", "Bubuyan", "Bucal", "Bunggo", "Burol", "Camaligan", "Canlubang",
            "Halang", "Hornalan", "Kay-Anlog", "La Mesa", "Laguerta", "Lecheria", "Lingga", "Looc", "Mabato",
            "Majada Labas", "Makiling", "Mapagong", "Masili", "Maunong", "Mayapa", "Paciano Rizal", "Palingon",
            "Palo-Alto", "Pansol", "Parian", "Prinza", "Punta", "Puting Lupa", "Real", "Saimsim", "Sampiruhan",
            "San Cristobal", "San Jose", "San Juan", "San Vicente", "Santa Cruz", "Santo Tomas", "Sucol",
            "Turbina", "Ulat", "Uwisan"
        ]
    }
}

def generate_tracking_number():
    """Generates a unique tracking number in the format MNS-YYYYMMDD-XXXXX."""
    date_part = datetime.now().strftime("%Y%m%d")
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return f"MNS-{date_part}-{random_part}"

class OrderContainer:
    """A simple data container that allows dot notation access to its dictionary items."""
    def __init__(self, data_dict):
        self.__dict__.update(data_dict)

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    con = sqlite3.connect("orders.db")
    con.row_factory = sqlite3.Row  
    return con

def save_contact_message(contact_data):
    """Save contact form message to database."""
    con = get_db_connection()
    try:
        cur = con.cursor()
        cur.execute(
            "INSERT INTO contact_messages(name,email,phone,subject,message,created_at,attachment_url) VALUES(?,?,?,?,?,?,?);",
            (contact_data["name"], contact_data["email"], contact_data["phone"],
             contact_data["subject"], contact_data["message"], datetime.now().isoformat(), contact_data.get("attachment_url")),
        )
        con.commit()
    except sqlite3.Error as e:
        con.rollback()
        app.logger.error(f"Database error in save_contact_message: {e}")
        raise
    finally:
        con.close()

def get_all_contact_messages():
    """Retrieves all contact messages from the database."""
    con = get_db_connection()
    messages = []
    try:
        cur = con.cursor()
        cur.execute("SELECT * FROM contact_messages ORDER BY created_at DESC;")
        messages = cur.fetchall()
    except sqlite3.Error as e:
        app.logger.error(f"Database error in get_all_contact_messages: {e}")
    finally:
        con.close()
    return [dict(msg) for msg in messages]

def get_user_contact_messages(user_email):
    """Retrieves all contact messages for a specific user email."""
    con = get_db_connection()
    messages = []
    try:
        cur = con.cursor()
        cur.execute("SELECT * FROM contact_messages WHERE email = ? ORDER BY created_at DESC;", (user_email,))
        messages = cur.fetchall()
    except sqlite3.Error as e:
        app.logger.error(f"Database error in get_user_contact_messages: {e}")
    finally:
        con.close()
    return [dict(msg) for msg in messages]

def save_checkout_info(checkout_data, cart_items, user_id=None):
    """
    MODIFIED: Save checkout info, including payment details, and decrease product quantity.
    Returns the generated tracking number.
    """
    con = get_db_connection()
    cur = con.cursor()
    
    tracking_number = generate_tracking_number()
    now = datetime.now()
    estimated_delivery_date = now + timedelta(days=5)

    try:
        cur.execute(
            """
            INSERT INTO checkouts (
                user_id, tracking_number, first_name, last_name, email, phone, address, city, barangay, province, postal_code,
                landmark, save_address, payment_method, notes, total_amount, created_at, status, estimated_delivery_date,
                card_name, card_number, card_expiry, card_cvv, gcash_name, gcash_number, gcash_reference
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                tracking_number,
                checkout_data["first_name"], checkout_data["last_name"], checkout_data["email"],
                checkout_data["phone"], checkout_data["address"], checkout_data["city"],
                checkout_data["barangay"], checkout_data["province"], checkout_data["postal_code"],
                checkout_data["landmark"],
                checkout_data["save_address"], checkout_data["payment_method"],
                checkout_data["notes"], checkout_data["total_amount"], now.isoformat(),
                "Pending",
                estimated_delivery_date.isoformat(),
                checkout_data.get("card_name"), checkout_data.get("card_number"), 
                checkout_data.get("card_expiry"), checkout_data.get("card_cvv"),
                checkout_data.get("gcash_name"), checkout_data.get("gcash_number"),
                checkout_data.get("gcash_reference")
            )
        )
        checkout_id = cur.lastrowid

        for item in cart_items:
            cur.execute(
                "INSERT INTO order_items (checkout_id, item_name, item_size, item_price, item_quantity, item_image_url) VALUES (?, ?, ?, ?, ?, ?)",
                (checkout_id, item["name"], item["size"], item["price"], item["quantity"], item["image"])
            )
            cur.execute(
                "UPDATE product_sizes SET quantity = quantity - ? WHERE product_id = ? AND size = ?",
                (item['quantity'], item['product_id'], item['size'])
            )
        
        con.commit()
        return tracking_number
    except sqlite3.Error as e:
        con.rollback()
        app.logger.error(f"Database error in save_checkout_info: {e}")
        raise
    finally:
        con.close()

def get_user(username):
    """Retrieves a user from the database by username."""
    con = get_db_connection()
    user = None
    try:
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?;", (username,))
        user = cur.fetchone()
    except sqlite3.Error as e:
        app.logger.error(f"Database error in get_user: {e}")
    finally:
        con.close()
    return user

def read_menu(filename):
    """Reads menu items from a text file."""
    try:
        with open(filename, 'r') as f:
            temp = f.readlines()
        result = []
        for item in temp:
            new_item = item.strip()
            if new_item:
                result.append(new_item)
        return result
    except FileNotFoundError:
        return []

def save_review(review_data):
    """Saves a new review to the database."""
    con = get_db_connection()
    try:
        cur = con.cursor()
        cur.execute(
            "INSERT INTO reviews (user_name, rating, comment, image_url, created_at) VALUES (?, ?, ?, ?, ?)",
            (review_data["user_name"], review_data["rating"], review_data["comment"], review_data.get("image_url"), datetime.now().isoformat())
        )
        con.commit()
    except sqlite3.Error as e:
        con.rollback()
        app.logger.error(f"Database error in save_review: {e}")
        raise
    finally:
        con.close()

def get_all_reviews():
    """Retrieves all reviews from the database, ordered by most recent."""
    con = get_db_connection()
    reviews = []
    try:
        cur = con.cursor()
        cur.execute("SELECT * FROM reviews ORDER BY created_at DESC;")
        reviews = cur.fetchall()
    except sqlite3.Error as e:
        app.logger.error(f"Database error in get_all_reviews: {e}")
    finally:
        con.close()
    return [dict(review) for review in reviews]

def delete_review(review_id):
    """Deletes a review from the database by its ID."""
    con = get_db_connection()
    try:
        cur = con.cursor()
        cur.execute("DELETE FROM reviews WHERE id = ?;", (review_id,))
        con.commit()
    except sqlite3.Error as e:
        con.rollback()
        app.logger.error(f"Database error in delete_review: {e}")
        raise
    finally:
        con.close()

def initialize_database():
    """Initializes the database and ensures the schema is up-to-date."""
    con = get_db_connection()
    try:
        cur = con.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                is_admin BOOLEAN DEFAULT 0,
                first_name TEXT,
                last_name TEXT,
                email TEXT,
                phone TEXT,
                address TEXT,
                city TEXT,
                barangay TEXT,
                province TEXT,
                postal_code TEXT,
                landmark TEXT
            )
        """)
        
        try:
            cur.execute("ALTER TABLE users ADD COLUMN barangay TEXT;")
        except sqlite3.OperationalError: pass
        try:
            cur.execute("ALTER TABLE users ADD COLUMN landmark TEXT;")
        except sqlite3.OperationalError: pass

        cur.execute("SELECT * FROM users WHERE username = 'admin';")
        if not cur.fetchone():
            cur.execute("INSERT INTO users(username, password, is_admin, first_name, last_name, email, phone, address, city, barangay, province, postal_code, landmark) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?);",
                        ("admin", "adminpass", 1, "Admin", "User", "admin@example.com", "1234567890", "Admin Street 1", "Admin City", "Admin Barangay", "Admin Province", "12345", "Near Admin Office"))
            con.commit()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS contact_messages(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                subject TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        
        try:
            cur.execute("ALTER TABLE contact_messages ADD COLUMN attachment_url TEXT;")
        except sqlite3.OperationalError: pass
        try:
            cur.execute("ALTER TABLE contact_messages ADD COLUMN reply_message TEXT;")
        except sqlite3.OperationalError: pass
        try:
            cur.execute("ALTER TABLE contact_messages ADD COLUMN replied_at TEXT;")
        except sqlite3.OperationalError: pass

        cur.execute("""
            CREATE TABLE IF NOT EXISTS checkouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                tracking_number TEXT UNIQUE,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                address TEXT NOT NULL,
                city TEXT NOT NULL,
                barangay TEXT NOT NULL,
                province TEXT NOT NULL,
                postal_code TEXT NOT NULL,
                landmark TEXT,
                save_address INTEGER,
                payment_method TEXT NOT NULL,
                notes TEXT,
                total_amount REAL NOT NULL,
                created_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending',
                estimated_delivery_date TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
            )
        """)

        try: cur.execute("ALTER TABLE checkouts ADD COLUMN barangay TEXT;")
        except sqlite3.OperationalError: pass
        try: cur.execute("ALTER TABLE checkouts ADD COLUMN landmark TEXT;")
        except sqlite3.OperationalError: pass
        try: cur.execute("ALTER TABLE checkouts ADD COLUMN tracking_number TEXT UNIQUE;")
        except sqlite3.OperationalError: pass
        try: cur.execute("ALTER TABLE checkouts ADD COLUMN estimated_delivery_date TEXT;")
        except sqlite3.OperationalError: pass
        try: cur.execute("ALTER TABLE checkouts ADD COLUMN card_name TEXT;")
        except sqlite3.OperationalError: pass
        try: cur.execute("ALTER TABLE checkouts ADD COLUMN card_number TEXT;")
        except sqlite3.OperationalError: pass
        try: cur.execute("ALTER TABLE checkouts ADD COLUMN card_expiry TEXT;")
        except sqlite3.OperationalError: pass
        try: cur.execute("ALTER TABLE checkouts ADD COLUMN card_cvv TEXT;")
        except sqlite3.OperationalError: pass
        try: cur.execute("ALTER TABLE checkouts ADD COLUMN gcash_name TEXT;")
        except sqlite3.OperationalError: pass
        try: cur.execute("ALTER TABLE checkouts ADD COLUMN gcash_number TEXT;")
        except sqlite3.OperationalError: pass
        try: cur.execute("ALTER TABLE checkouts ADD COLUMN gcash_reference TEXT;")
        except sqlite3.OperationalError: pass

        cur.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                checkout_id INTEGER,
                item_name TEXT NOT NULL,
                item_size TEXT,
                item_price REAL NOT NULL,
                item_quantity INTEGER NOT NULL DEFAULT 1,
                item_image_url TEXT,
                FOREIGN KEY (checkout_id) REFERENCES checkouts (id) ON DELETE CASCADE
            )
        """)
        try:
            cur.execute("ALTER TABLE order_items ADD COLUMN item_quantity INTEGER NOT NULL DEFAULT 1;")
        except sqlite3.OperationalError:
            pass

        cur.execute("""
            CREATE TABLE IF NOT EXISTS products(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                brand TEXT NOT NULL,
                price REAL NOT NULL,
                original_price REAL,
                image_url TEXT,
                colors TEXT,
                category TEXT NOT NULL,
                gender TEXT, 
                on_sale BOOLEAN DEFAULT 0,
                description TEXT 
            )
        """)

        try:
            cur.execute("ALTER TABLE products ADD COLUMN description TEXT;")
        except sqlite3.OperationalError:
            pass


        cur.execute("""
            CREATE TABLE IF NOT EXISTS product_sizes(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                size TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE,
                UNIQUE(product_id, size)
            )
        """)
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT NOT NULL,
                rating INTEGER NOT NULL,
                comment TEXT NOT NULL,
                image_url TEXT,
                created_at TEXT NOT NULL
            )
        """)
        
        try:
            cur.execute("ALTER TABLE reviews ADD COLUMN rating INTEGER NOT NULL DEFAULT 3;")
        except sqlite3.OperationalError:
            pass
        
        try:
            cur.execute("ALTER TABLE reviews ADD COLUMN reply_message TEXT;")
        except sqlite3.OperationalError: pass
        try:
            cur.execute("ALTER TABLE reviews ADD COLUMN replied_at TEXT;")
        except sqlite3.OperationalError: pass

        con.commit()

        cur.execute("SELECT COUNT(*) FROM products;")
        if cur.fetchone()[0] == 0:
            sample_products = [
                ("Nike Sabrina 2 EP x TITAN 'Make Space'", "NIKE", 8095.00, None, 'img/sabrina-2-titan.png', json.dumps(["#667eea", "#ffffff"]), "sneakers", "men", 0, "Engineered for the court, the Sabrina 2 provides the perfect blend of style and performance, helping you make space and create plays."),
                ("Nike Sabrina 2 EP 'Apricot Gate'", "NIKE", 8095.00, None, 'img/sabrina-2-apricot.png', json.dumps(["#ffb347", "#ffffff"]), "sneakers", "women", 0, "Featuring a vibrant colorway, the 'Apricot Gate' is designed for players who want to stand out while demanding top-tier support and comfort."),
                ("Jordan 4 Retro 'White Cement'", "JORDAN", 11495.00, None, 'img/jordan-4-white-cement.png', json.dumps(["#ffffff", "#808080"]), "sneakers", "men", 0, "A timeless classic, the Jordan 4 'White Cement' returns with its iconic speckled details and premium materials, a must-have for any collector."),
                ("Jordan 4 Retro 'Bred Reimagined'", "JORDAN", 11495.00, None, 'img/jordan-4-bred-reimagined.png', json.dumps(["#000000", "#e74c3c"]), "sneakers", "men", 0, "The 'Bred' colorway is reimagined with new materials for a fresh take on one of the most beloved sneakers of all time."),
                ("Nike Kobe 4 Protro 'Mambacita'", "NIKE", 5995.00, 9895.00, 'img/kobe-4-mambacita.png', json.dumps(["#ffc0cb", "#000000"]), "sneakers", "women", 1, "Honoring Gigi Bryant, the 'Mambacita' is a symbol of strength and passion for the game, featuring personal touches and performance-ready tech."),
                ("Nike Kobe 6 Protro 'Sail'", "NIKE", 6995.00, 9895.00, 'img/kobe-6-sail.png', json.dumps(["#f5f5dc", "#8b4513"]), "sneakers", "men", 1, "Kobe's comeback from a torn Achilles inspired generations of past, present and future hoopers to keep fighting. This Kobe IX brings back the shoe that supported the Black Mamba during his triumphant return to the floor and gives it an upgrade. An engineered mesh upper complements a Lunarlon midsole for a lightweight, responsive ride."),
                ("Nike Dunk Low Retro 'Panda'", "NIKE", 2995.00, 5895.00, 'img/dunk-low-panda.png', json.dumps(["#ffffff", "#000000"]), "sneakers", "unisex", 1, "The ultimate versatile sneaker, the 'Panda' Dunk Low features a clean black and white color block that pairs with any outfit."),
                ("Nike Dunk Low Retro 'Grey'", "NIKE", 2995.00, 5895.00, 'img/dunk-low-grey.png', json.dumps(["#808080", "#ffffff"]), "sneakers", "unisex", 1, "A subtle and clean take on the classic Dunk Low, the 'Grey' colorway offers a minimalist aesthetic without sacrificing style.")
            ]
            for p_data in sample_products:
                cur.execute(
                    "INSERT INTO products(name, brand, price, original_price, image_url, colors, category, gender, on_sale, description) VALUES(?,?,?,?,?,?,?,?,?,?)", p_data)
                product_id = cur.lastrowid
                gender = p_data[7]
                sizes_for_gender = SIZE_MAPPING.get(gender, [])
                for size in sizes_for_gender:
                    cur.execute("INSERT INTO product_sizes(product_id, size, quantity) VALUES (?,?,?)", (product_id, size, 10))
            con.commit()
    except sqlite3.Error as e:
        app.logger.error(f"Database error during initialization: {e}")
    finally:
        con.close()

def get_all_products():
    """Fetches all products from the database, including size-based stock."""
    con = get_db_connection()
    products = []
    try:
        cur = con.cursor()
        cur.execute("SELECT * FROM products ORDER BY id DESC;")
        products_rows = cur.fetchall()
        
        for p_row in products_rows:
            p_dict = dict(p_row)
            p_dict['colors'] = json.loads(p_dict['colors']) if p_dict['colors'] else []
            
            cur.execute("SELECT size, quantity FROM product_sizes WHERE product_id = ? ORDER BY size", (p_dict['id'],))
            sizes_rows = cur.fetchall()
            p_dict['sizes'] = {row['size']: row['quantity'] for row in sizes_rows}
            p_dict['total_quantity'] = sum(p_dict['sizes'].values())
            
            products.append(p_dict)
    except sqlite3.Error as e:
        app.logger.error(f"Database error in get_all_products: {e}")
    finally:
        con.close()
    return products

def get_product_by_id(product_id):
    """Fetches a single product by its ID, including size-based stock."""
    con = get_db_connection()
    product = None
    try:
        cur = con.cursor()
        cur.execute("SELECT * FROM products WHERE id = ?;", (product_id,))
        product_row = cur.fetchone()
        
        if not product_row:
            return None
            
        product = dict(product_row)
        product['colors'] = json.loads(product['colors']) if product['colors'] else []
        
        cur.execute("SELECT size, quantity FROM product_sizes WHERE product_id = ? ORDER BY size", (product['id'],))
        sizes_rows = cur.fetchall()
        product['sizes'] = {row['size']: row['quantity'] for row in sizes_rows}
        product['total_quantity'] = sum(product['sizes'].values())
    except sqlite3.Error as e:
        app.logger.error(f"Database error in get_product_by_id: {e}")
    finally:
        con.close()
    return product

def add_product(product_data):
    """Adds a new product and initializes its size-based stock."""
    con = get_db_connection()
    try:
        cur = con.cursor()
        
        cur.execute(
            """
            INSERT INTO products(name, brand, price, original_price, image_url, colors, category, gender, on_sale, description)
            VALUES(?,?,?,?,?,?,?,?,?,?)
            """,
            (product_data["name"], product_data["brand"], product_data["price"],
             product_data.get("original_price"), product_data["image_url"],
             json.dumps(product_data.get("colors", [])), product_data["category"],
             product_data["gender"], product_data.get("on_sale", False), product_data.get("description", ""))
        )
        product_id = cur.lastrowid
        
        initial_quantity = product_data.get("quantity", 0)
        gender = product_data.get("gender")
        sizes_for_gender = SIZE_MAPPING.get(gender, [])
        
        for size in sizes_for_gender:
            cur.execute(
                "INSERT INTO product_sizes (product_id, size, quantity) VALUES (?, ?, ?)",
                (product_id, size, initial_quantity)
            )
            
        con.commit()
    except sqlite3.Error as e:
        con.rollback()
        app.logger.error(f"Database error in add_product: {e}")
        raise
    finally:
        con.close()

def update_product(product_id, product_data):
    """Updates an existing product's details and syncs sizes if gender changes."""
    con = get_db_connection()
    try:
        cur = con.cursor()

        cur.execute("SELECT gender FROM products WHERE id = ?", (product_id,))
        old_gender_row = cur.fetchone()
        old_gender = old_gender_row['gender'] if old_gender_row else None
        new_gender = product_data.get("gender")

        cur.execute(
            """
            UPDATE products
            SET name = ?, brand = ?, price = ?, original_price = ?, image_url = ?, colors = ?, category = ?, gender = ?, on_sale = ?, description = ?
            WHERE id = ?
            """,
            (product_data["name"], product_data["brand"], product_data["price"],
             product_data.get("original_price"), product_data["image_url"],
             json.dumps(product_data.get("colors", [])), product_data["category"],
             new_gender, product_data.get("on_sale", False), product_data.get("description", ""), product_id)
        )

        if old_gender and new_gender and old_gender != new_gender:
            cur.execute("DELETE FROM product_sizes WHERE product_id = ?", (product_id,))

            sizes_for_new_gender = SIZE_MAPPING.get(new_gender, [])
            for size in sizes_for_new_gender:
                cur.execute(
                    "INSERT INTO product_sizes (product_id, size, quantity) VALUES (?, ?, ?)",
                    (product_id, size, 0)
                )
            flash(f"Product gender changed for '{product_data['name']}'. Stock quantities for all new sizes have been reset to 0. Please update them accordingly.", "warning")

        con.commit()
    except sqlite3.Error as e:
        con.rollback()
        app.logger.error(f"Database error in update_product: {e}")
        raise
    finally:
        con.close()


def delete_product(product_id):
    """Deletes a product from the database by its ID."""
    con = get_db_connection()
    try:
        cur = con.cursor()
        cur.execute("DELETE FROM products WHERE id = ?;", (product_id,))
        con.commit()
    except sqlite3.Error as e:
        con.rollback()
        app.logger.error(f"Database error in delete_product: {e}")
        raise
    finally:
        con.close()

def get_order_by_id(order_id):
    """
    Fetches a single checkout record and its items by its integer ID.
    Returns an OrderContainer object.
    """
    con = get_db_connection()
    order = None
    try:
        cur = con.cursor()
        cur.execute("SELECT * FROM checkouts WHERE id = ?;", (order_id,))
        order_row = cur.fetchone()

        if order_row:
            order_data = dict(order_row)
            try:
                dt = datetime.fromisoformat(order_data['created_at'])
                order_data['created_at_formatted'] = dt.strftime('%B %d, %Y')
            except (ValueError, TypeError):
                 order_data['created_at_formatted'] = order_data['created_at'].split('T')[0]
                 
            cur.execute("SELECT *, item_quantity FROM order_items WHERE checkout_id = ?;", (order_data['id'],))
            items = cur.fetchall()
            order_data['items'] = [dict(item) for item in items]

            subtotal = sum(item['item_price'] * item['item_quantity'] for item in order_data['items'])
            tax = subtotal * 0.12
            shipping = 150.00 if subtotal > 0 else 0
            
            order_data['subtotal'] = subtotal
            order_data['tax'] = tax
            order_data['shipping'] = shipping
            
            order = OrderContainer(order_data)
    except sqlite3.Error as e:
        app.logger.error(f"Database error in get_order_by_id: {e}")
    finally:
        con.close()
    return order

def get_order_by_tracking_number(tracking_number):
    """
    Fetches a single checkout record and its items by tracking number.
    Returns an OrderContainer object.
    """
    con = get_db_connection()
    order = None
    try:
        cur = con.cursor()
        cur.execute("SELECT * FROM checkouts WHERE tracking_number = ?;", (tracking_number,))
        order_row = cur.fetchone()

        if order_row:
            order_data = dict(order_row)
            cur.execute("SELECT *, item_quantity FROM order_items WHERE checkout_id = ?;", (order_data['id'],))
            items = cur.fetchall()
            order_data['items'] = [dict(item) for item in items]
            order = OrderContainer(order_data)
    except sqlite3.Error as e:
        app.logger.error(f"Database error in get_order_by_tracking_number: {e}")
    finally:
        con.close()
    return order

def get_all_checkouts_with_items():
    """
    Fetches all checkout records with their associated order items.
    Returns a list of OrderContainer objects.
    """
    con = get_db_connection()
    result = []
    try:
        cur = con.cursor()
        cur.execute("SELECT * FROM checkouts ORDER BY created_at DESC;")
        checkouts = cur.fetchall()
        
        for checkout in checkouts:
            checkout_dict = dict(checkout)
            cur.execute("SELECT *, item_quantity FROM order_items WHERE checkout_id = ?;", (checkout['id'],))
            items = cur.fetchall()
            checkout_dict['items'] = [dict(item) for item in items]
            result.append(OrderContainer(checkout_dict))
    except sqlite3.Error as e:
        app.logger.error(f"Database error in get_all_checkouts_with_items: {e}")
    finally:
        con.close()
    return result

def get_user_orders(user_id):
    """
    MODIFIED: Fetches all checkout records for a specific user, with item details
    and dates formatted for the 'my_account' template.
    Returns a list of OrderContainer objects.
    """
    con = get_db_connection()
    result = []
    try:
        cur = con.cursor()
        cur.execute("SELECT * FROM checkouts WHERE user_id = ? ORDER BY created_at DESC;", (user_id,))
        orders = cur.fetchall()
        
        for order in orders:
            order_dict = dict(order)
            
            if order_dict.get('created_at'):
                try:
                    dt = datetime.fromisoformat(order_dict['created_at'])
                    order_dict['created_at'] = dt.strftime('%Y-%m-%d')
                except (ValueError, TypeError):
                    order_dict['created_at'] = order_dict['created_at'].split('T')[0]
            
            if order_dict.get('estimated_delivery_date'):
                try:
                    dt = datetime.fromisoformat(order_dict['estimated_delivery_date'])
                    order_dict['estimated_delivery'] = dt.strftime('%B %d, %Y')
                except (ValueError, TypeError):
                    order_dict['estimated_delivery'] = order_dict['estimated_delivery_date'].split('T')[0]
                del order_dict['estimated_delivery_date']
            else:
                 order_dict['estimated_delivery'] = None

            cur.execute("SELECT * FROM order_items WHERE checkout_id = ?;", (order['id'],))
            items_rows = cur.fetchall()
            
            items_list = []
            for item_row in items_rows:
                item_dict = dict(item_row)
                items_list.append({
                    'product_name': item_dict.get('item_name'),
                    'quantity': item_dict.get('item_quantity'),
                    'size': item_dict.get('item_size'),
                    'price': item_dict.get('item_price'),
                    'image_url': item_dict.get('item_image_url')
                })
            order_dict['items'] = items_list
            
            result.append(OrderContainer(order_dict))
    except sqlite3.Error as e:
        app.logger.error(f"Database error in get_user_orders: {e}")
    finally:
        con.close()
    return result

def update_checkout_status(checkout_id, new_status):
    """Updates the status of a checkout order."""
    con = get_db_connection()
    try:
        cur = con.cursor()
        cur.execute("UPDATE checkouts SET status = ? WHERE id = ?;", (new_status, checkout_id))
        con.commit()
    except sqlite3.Error as e:
        con.rollback()
        app.logger.error(f"Database error in update_checkout_status: {e}")
        raise
    finally:
        con.close()

def delete_checkout(checkout_id):
    """Deletes a specific order."""
    con = get_db_connection()
    try:
        cur = con.cursor()
        cur.execute("DELETE FROM checkouts WHERE id = ?;", (checkout_id,))
        con.commit()
    except sqlite3.Error as e:
        con.rollback()
        app.logger.error(f"Database error in delete_checkout: {e}")
        raise
    finally:
        con.close()
        
def get_all_users():
    """Retrieves all users from the database."""
    con = get_db_connection()
    users = []
    try:
        cur = con.cursor()
        cur.execute("SELECT id, username, is_admin, first_name, last_name, email, phone, address, city, barangay, province, postal_code, landmark FROM users;")
        users = cur.fetchall()
    except sqlite3.Error as e:
        app.logger.error(f"Database error in get_all_users: {e}")
    finally:
        con.close()
    return [dict(user) for user in users]

def get_user_by_id(user_id):
    """Retrieves a user from the database by ID."""
    con = get_db_connection()
    user = None
    try:
        cur = con.cursor()
        cur.execute("SELECT id, username, is_admin, first_name, last_name, email, phone, address, city, barangay, province, postal_code, landmark FROM users WHERE id = ?;", (user_id,))
        user = cur.fetchone()
    except sqlite3.Error as e:
        app.logger.error(f"Database error in get_user_by_id: {e}")
    finally:
        con.close()
    return dict(user) if user else None

def get_user_with_password_by_id(user_id):
    """Retrieves a user, including password, from the database by ID for verification."""
    con = get_db_connection()
    user = None
    try:
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE id = ?;", (user_id,))
        user = cur.fetchone()
    except sqlite3.Error as e:
        app.logger.error(f"Database error in get_user_with_password_by_id: {e}")
    finally:
        con.close()
    return user

def update_user_password(user_id, new_password):
    """Updates a user's password in the database."""
    con = get_db_connection()
    try:
        cur = con.cursor()
        cur.execute("UPDATE users SET password = ? WHERE id = ?;", (new_password, user_id))
        con.commit()
    except sqlite3.Error as e:
        con.rollback()
        app.logger.error(f"Database error in update_user_password: {e}")
        raise
    finally:
        con.close()

def add_user(username, password, is_admin=False, first_name="", last_name="", email="", phone="", address="", city="", barangay="", province="", postal_code="", landmark=""):
    """Adds a new user to the database with more details."""
    con = get_db_connection()
    try:
        cur = con.cursor()
        cur.execute("INSERT INTO users(username, password, is_admin, first_name, last_name, email, phone, address, city, barangay, province, postal_code, landmark) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?);",
                    (username, password, 1 if is_admin else 0, first_name, last_name, email, phone, address, city, barangay, province, postal_code, landmark))
        con.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    except sqlite3.Error as e:
        con.rollback()
        app.logger.error(f"Database error in add_user: {e}")
        raise
    finally:
        con.close()

def delete_user(user_id):
    """Deletes a user from the database by ID."""
    con = get_db_connection()
    try:
        cur = con.cursor()
        cur.execute("DELETE FROM users WHERE id = ?;", (user_id,))
        con.commit()
    except sqlite3.Error as e:
        con.rollback()
        app.logger.error(f"Database error in delete_user: {e}")
        raise
    finally:
        con.close()

def update_user_info(user_id, first_name, last_name, email, phone):
    """Updates a user's first name, last_name, email, and phone in the database."""
    con = get_db_connection()
    try:
        cur = con.cursor()
        cur.execute(
            """
            UPDATE users
            SET first_name = ?, last_name = ?, email = ?, phone = ?
            WHERE id = ?
            """,
            (first_name, last_name, email, phone, user_id)
        )
        con.commit()
    except sqlite3.Error as e:
        con.rollback()
        app.logger.error(f"Database error in update_user_info: {e}")
        raise
    finally:
        con.close()

def update_user_address(user_id, first_name, last_name, email, phone, address, city, barangay, province, postal_code, landmark):
    """Updates a user's address and related contact details in the database."""
    con = get_db_connection()
    try:
        cur = con.cursor()
        cur.execute(
            """
            UPDATE users
            SET first_name = ?, last_name = ?, email = ?, phone = ?,
                address = ?, city = ?, barangay = ?, province = ?, postal_code = ?, landmark = ?
            WHERE id = ?
            """,
            (first_name, last_name, email, phone, address, city, barangay, province, postal_code, landmark, user_id)
        )
        con.commit()
    except sqlite3.Error as e:
        con.rollback()
        app.logger.error(f"Database error in update_user_address: {e}")
        raise
    finally:
        con.close()

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

brand = read_menu("brands.txt")
gender = read_menu("gender.txt")
men_sizes = read_menu("men_sizes.txt")
women_sizes = read_menu("women_sizes.txt")

SIZE_MAPPING = {
    'men': men_sizes,
    'women': women_sizes,
    'unisex': sorted(list(set(men_sizes + women_sizes)), key=lambda x: float(x) if x.replace('.', '', 1).isdigit() else float('inf'))
}

initialize_database()

def login_required(f):
    """Decorator to require login for certain routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin privileges for certain routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        
        if not session.get('is_admin'):
            flash('You do not have administrative privileges to access this page.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def index():
    """Renders the home page with new arrivals and sale products."""
    all_products = get_all_products()
    
    processed_products = []
    for p in all_products:
        product_gender = p.get('gender', 'unisex')
        p['available_sizes'] = SIZE_MAPPING.get(product_gender, [])
        processed_products.append(p)

    new_arrivals = [p for p in processed_products if not p['on_sale']][:4]
    sale_products = [p for p in processed_products if p['on_sale']][:4]
    return render_template("home.html", new_arrivals=new_arrivals, sale_products=sale_products)

@app.route("/home")
def home():
    """Redirects to the index route to ensure a single source for the home page."""
    return redirect(url_for('index'))

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/size_chart")
def size_chart():
    return render_template("size_chart.html", men_sizes=men_sizes, women_sizes=women_sizes)

@app.route("/store_locator")
def store_locator():
    return render_template("store_locator.html")

@app.route("/reviews", methods=["GET", "POST"])
def reviews():
    """Handles displaying and submitting customer reviews."""
    if request.method == "POST":
        if 'user_id' not in session:
            flash("You must be logged in to leave a review.", "error")
            return redirect(url_for('login'))

        review_data = {
            "user_name": session.get('username', 'Anonymous'),
            "rating": request.form.get("rating"),
            "comment": request.form.get("user-comment", "").strip(),
            "image_url": None
        }

        if not all([review_data["rating"], review_data["comment"]]):
            flash("Please provide a rating and a comment.", "error")
            return redirect(url_for('reviews'))

        if 'user-image' in request.files:
            file = request.files['user-image']
            if file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
                review_data["image_url"] = url_for('static', filename=f'uploads/{unique_filename}')
            elif file.filename != '':
                flash('Invalid file type for image. Allowed types are: png, jpg, jpeg, gif.', 'error')
                return redirect(url_for('reviews'))

        try:
            save_review(review_data)
            flash("Thank you for your review!", "success")
        except Exception as e:
            flash("There was an error submitting your review. Please try again.", "error")
            app.logger.error(f"Error saving review: {e}")

        return redirect(url_for('reviews'))

    all_reviews = get_all_reviews()
    return render_template("reviews.html", reviews=all_reviews)

@app.route("/contact", methods=["GET", "POST"])
def contact():
    """
    Handles displaying the contact page and processing the contact form submission.
    """
    if request.method == "POST":
        contact_data = {
            "name": request.form.get("name"),
            "email": request.form.get("email"),
            "phone": request.form.get("phone", ""), 
            "subject": request.form.get("subject"),
            "message": request.form.get("message"),
            "attachment_url": None 
        }
        
        if not all([contact_data["name"], contact_data["email"], contact_data["subject"], contact_data["message"]]):
            flash("Please fill out all required fields: Name, Email, Subject, and Message.", "error")
            return redirect(url_for('contact'))
        
        try:
            save_contact_message(contact_data)
            
            email_success = send_contact_form_email(
                contact_data["name"],
                contact_data["email"],
                contact_data["subject"],
                contact_data["message"]
            )

            if email_success:
                flash("Success! Your message has been sent. We will get back to you shortly.", "success")
            else:
                flash("Your message was saved, but there was an issue sending the immediate email notification. We'll manually check the database.", "warning")

        except Exception as e:
            app.logger.error(f"Failed to process contact form: {e}")
            flash("An unexpected error occurred. Please try again later.", "error")
            
        return redirect(url_for('contact'))
    
    return render_template("contact_us.html")

@app.route("/policy")
def policy():
    """Renders the return and exchange policy page."""
    return render_template("policy.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Handles user login."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Please enter both username and password.", "error")
            return render_template("login.html")

        user = get_user(username)
        if user and user['password'] == password: 
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = bool(user['is_admin'])
            flash(f"Welcome back, {username}!", "success")
            if session['is_admin']:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password.", "error")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Handles user registration."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        if not username or not password or not confirm_password:
            flash("All fields are required.", "error")
            return render_template("register.html")

        if len(password) < 4:
            flash("Password must be at least 4 characters long.", "error")
            return render_template("register.html")

        if not re.match(r'^[A-Za-z0-9]+$', password):
            flash("Password can only contain letters and numbers.", "error")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("register.html")

        if get_user(username):
            flash("Username already exists. Please choose a different one.", "error")
            return render_template("register.html")

        if add_user(username, password):
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('login'))
        else:
            flash("Registration failed. Please try again.", "error")
            
    return render_template("register.html")

@app.route("/logout")
def logout():
    """Logs out the current user."""
    session.clear()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for('index'))

@app.route("/shop")
def shop():
    """Route for the shop page, fetching products and their sizes."""
    all_products = get_all_products()
    
    processed_products = []
    for p in all_products:
        product_gender = p.get('gender', 'unisex')
        p['available_sizes'] = SIZE_MAPPING.get(product_gender, [])
        processed_products.append(p)

    return render_template("shop.html", products_data=processed_products)

@app.route("/product/<int:product_id>")
def product_detail(product_id):
    """Renders the detailed page for a single product."""
    product = get_product_by_id(product_id)
    if not product:
        flash("Product not found.", "error")
        return redirect(url_for('shop'))
    
    if product.get("original_price"):
        product['sale_price'] = product['price']
        product['price'] = product['original_price']
    else:
        product['sale_price'] = None

    product_gender = product.get('gender', 'unisex')
    available_sizes = SIZE_MAPPING.get(product_gender, [])
    
    return render_template("product_detail.html", product=product, available_sizes=available_sizes)

@app.route("/cart")
def cart():
    """Route for the shopping cart page."""
    if 'cart' not in session:
        session['cart'] = []
    else:
        for item in session['cart']:
            if 'quantity' not in item:
                item['quantity'] = 1
        session.modified = True

    subtotal = sum(item['price'] * item['quantity'] for item in session['cart'])
    shipping = 0.00
    if subtotal > 0:
        shipping = 150.00
    tax = subtotal * 0.12
    total_amount = subtotal + shipping + tax
    
    return render_template("cart.html", cart_items=session['cart'], subtotal=subtotal, shipping=shipping, tax=tax, total_amount=total_amount)

@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    """Adds an item with a specific size and quantity to the cart."""
    item_name = request.form.get("item_name")
    item_size = request.form.get("item_size")
    try:
        item_quantity = int(request.form.get("item_quantity", 1))
        if item_quantity < 1:
            item_quantity = 1
    except (ValueError, TypeError):
        item_quantity = 1
    
    if not item_name:
        flash("Could not add item to cart. Product name is missing.", "error")
        return redirect(request.referrer or url_for('shop'))
    
    if not item_size:
        flash("Please select a size.", "error")
        return redirect(request.referrer or url_for('shop'))

    con = get_db_connection()
    try:
        product = con.execute("SELECT * FROM products WHERE name = ?", (item_name,)).fetchone()
        if not product:
            flash(f"Could not find a product named '{item_name}'.", "error")
            return redirect(request.referrer or url_for('shop'))
        
        product_id = product['id']
        
        stock_row = con.execute("SELECT quantity FROM product_sizes WHERE product_id = ? AND size = ?", (product_id, item_size)).fetchone()
        available_stock = stock_row['quantity'] if stock_row else 0
        
        if 'cart' not in session:
            session['cart'] = []

        existing_item_index = -1
        for i, item in enumerate(session['cart']):
            if item['product_id'] == product_id and item['size'] == item_size:
                existing_item_index = i
                break
        
        total_quantity_needed = item_quantity
        if existing_item_index != -1:
            total_quantity_needed += session['cart'][existing_item_index]['quantity']
            
        if total_quantity_needed > available_stock:
            flash(f"Not enough stock for '{item_name}' (Size: {item_size}). Only {available_stock} available.", "error")
            return redirect(request.referrer or url_for('shop'))
            
        if existing_item_index != -1:
            session['cart'][existing_item_index]['quantity'] += item_quantity
            flash(f"Updated quantity for '{item_name}' (Size: {item_size}) in your cart!", "success")
        else:
            session['cart'].append({
                "product_id": product_id,
                "name": item_name,
                "size": item_size,
                "price": product['price'],
                "image": product['image_url'],
                "quantity": item_quantity
            })
            flash(f"'{item_name}' (Size: {item_size}) added to cart!", "success")

        session.modified = True
    except sqlite3.Error as e:
        app.logger.error(f"Database error fetching product for cart: {e}")
        flash("An error occurred while adding to cart. Please try again.", "error")
    finally:
        con.close()

    return redirect(url_for('cart'))

@app.route("/remove_from_cart/<int:item_index>", methods=["POST"])
def remove_from_cart(item_index):
    """Route to remove an item from the shopping cart."""
    if 'cart' in session and 0 <= item_index < len(session['cart']):
        item_name = session['cart'][item_index]['name']
        session['cart'].pop(item_index)
        session.modified = True
        flash(f"{item_name} removed from cart.", "success")
    return redirect(url_for('cart'))

@app.route("/update_cart/<int:item_index>", methods=["POST"])
def update_cart(item_index):
    """Updates the quantity of an item in the cart."""
    if 'cart' not in session or not (0 <= item_index < len(session['cart'])):
        flash("Invalid item to update.", "error")
        return redirect(url_for('cart'))

    try:
        new_quantity = int(request.form.get('quantity'))
        if new_quantity < 1:
            flash("Quantity must be at least 1.", "error")
            return redirect(url_for('cart'))
    except (ValueError, TypeError):
        flash("Invalid quantity specified.", "error")
        return redirect(url_for('cart'))

    item_to_update = session['cart'][item_index]
    con = get_db_connection()
    try:
        stock_row = con.execute("SELECT quantity FROM product_sizes WHERE product_id = ? AND size = ?",
                                (item_to_update['product_id'], item_to_update['size'])).fetchone()
        available_stock = stock_row['quantity'] if stock_row else 0
        
        if new_quantity > available_stock:
            flash(f"Not enough stock for '{item_to_update['name']}'. Only {available_stock} available.", "error")
        else:
            session['cart'][item_index]['quantity'] = new_quantity
            session.modified = True
            flash(f"Quantity for '{item_to_update['name']}' updated successfully.", "success")
            
    except sqlite3.Error as e:
        app.logger.error(f"Database error during cart update: {e}")
        flash("An error occurred while updating the cart.", "error")
    finally:
        con.close()

    return redirect(url_for('cart'))

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    """MODIFIED: Checkout route handles payment redirection and card/gcash validation."""
    if 'cart' not in session or not session['cart']:
        flash("Your cart is empty. Please add items before checking out.", "error")
        return redirect(url_for('shop'))

    current_cart = session.get('cart', [])
    valid_cart_items = []
    stock_issue_found = False
    
    con = get_db_connection()
    try:
        for item in current_cart:
            cur = con.cursor()
            cur.execute(
                "SELECT quantity FROM product_sizes WHERE product_id = ? AND size = ?",
                (item['product_id'], item['size'])
            )
            stock_info = cur.fetchone()
            available_stock = stock_info['quantity'] if stock_info else 0
            
            if item['quantity'] <= available_stock:
                valid_cart_items.append(item)
            else:
                stock_issue_found = True
                flash(f"Sorry, the requested quantity for '{item['name']}' (Size: {item['size']}) is not available. Only {available_stock} left in stock.", "error")
    except sqlite3.Error as e:
        app.logger.error(f"Database error during checkout stock check: {e}")
        flash("An error occurred during stock validation. Please try again.", "error")
        return redirect(url_for('cart'))
    finally:
        con.close()
    
    session['cart'] = valid_cart_items
    session.modified = True

    if not valid_cart_items:
        return redirect(url_for('shop'))
    if stock_issue_found:
        return redirect(url_for('cart'))

    cart_items = session['cart']
    subtotal = sum(item['price'] * item['quantity'] for item in cart_items)
    shipping = 150.00
    tax = subtotal * 0.12
    total_amount = subtotal + shipping + tax

    if request.method == "POST":
        checkout_data = {
            "first_name": request.form.get("first_name", "").strip(),
            "last_name": request.form.get("last_name", "").strip(),
            "email": request.form.get("email", "").strip(),
            "phone": request.form.get("phone", "").strip(),
            "address": request.form.get("address", "").strip(),
            "city": request.form.get("city", "").strip(),
            "barangay": request.form.get("barangay", "").strip(), 
            "landmark": request.form.get("landmark", "").strip(),
            "province": request.form.get("province", "").strip(),
            "postal_code": request.form.get("postal_code", "").strip(),
            "save_address": 1 if request.form.get("save_address") else 0,
            "payment_method": request.form.get("payment_method", "").strip(),
            "notes": request.form.get("notes", "").strip(),
            "total_amount": total_amount
        }

        required_fields = ["first_name", "last_name", "email", "phone", "address", "city", "barangay", "province", "postal_code", "payment_method"]
        payment_method = checkout_data.get("payment_method")

        if payment_method == "bank":
            card_fields = ["card_name", "card_number", "card_expiry", "card_cvv"]
            required_fields.extend(card_fields)
            for field in card_fields:
                checkout_data[field] = request.form.get(field, "").strip()
        
        elif payment_method == "gcash":
            gcash_fields = ["gcash_name", "gcash_number", "gcash_reference"]
            required_fields.extend(gcash_fields)
            for field in gcash_fields:
                checkout_data[field] = request.form.get(field, "").strip()

        if not all(checkout_data.get(field) for field in required_fields):
            flash("Please fill in all required fields, including payment details for your chosen method.", "error")
            return render_template("checkout.html", cart_items=cart_items, subtotal=subtotal, shipping=shipping, tax=tax, total_amount=total_amount, location_data=LOCATION_DATA, form_data=checkout_data)
        
        try:
            user_id = session.get('user_id')
            tracking_number = save_checkout_info(checkout_data, cart_items, user_id=user_id)
            
            send_order_confirmation_email(
                recipient_email=checkout_data["email"],
                tracking_number=tracking_number,
                checkout_data=checkout_data,
                cart_items=cart_items
            )

            session.pop('cart', None)

            if payment_method == 'paypal':
                flash(f"Order placed! Redirecting to PayPal. Tracking #: {tracking_number}", "success")
                return redirect("https://www.paypal.com/signin")
            else: 
                flash(f"Your order has been placed successfully! Your tracking number is: {tracking_number}. A confirmation email has been sent.", "success")
                return redirect(url_for('track_order', tracking_number=tracking_number))
                
        except Exception as e:
            flash(f"There was an error processing your order: {e}", "error")
            app.logger.error(f"Error processing checkout: {e}")

    user_info = None
    if 'user_id' in session:
        user_id = session.get('user_id')
        user_info = get_user_by_id(user_id)
        if user_info:
            default_address_data = {
                'first_name': user_info.get('first_name'),
                'last_name': user_info.get('last_name'),
                'email': user_info.get('email'),
                'phone': user_info.get('phone'),
                'address': user_info.get('address'),
                'city': user_info.get('city'),
                'barangay': user_info.get('barangay'),
                'province': user_info.get('province'),
                'postal_code': user_info.get('postal_code'),
                'landmark': user_info.get('landmark')
            }
            if default_address_data.get('address'):
                user_info['default_address'] = default_address_data
            else:
                user_info['default_address'] = None

    return render_template("checkout.html",
                           cart_items=cart_items,
                           subtotal=subtotal,
                           shipping=shipping,
                           tax=tax,
                           total_amount=total_amount,
                           user_info=user_info,
                           location_data=LOCATION_DATA)

@app.route("/track_order", methods=["GET", "POST"])
def track_order():
    """
    Route for the 'Track Your Order' page.
    Handles form submission and displays order details based on tracking number.
    """
    order_details = None
    tracking_number_from_url = request.args.get('tracking_number') 

    if request.method == "POST":
        tracking_number_from_form = request.form.get("tracking_number", "").strip()
        if not tracking_number_from_form:
            flash("Please enter a tracking number.", "error")
        else:
            order_details = get_order_by_tracking_number(tracking_number_from_form)
            if not order_details:
                flash(f"No order found with tracking number '{tracking_number_from_form}'. Please check the number and try again.", "error")
        return render_template("track_your_order.html", order=order_details, tracking_number=tracking_number_from_form)

    if tracking_number_from_url:
        order_details = get_order_by_tracking_number(tracking_number_from_url)
        if not order_details:
             flash(f"No order found with tracking number '{tracking_number_from_url}'.", "error")

    return render_template("track_your_order.html", order=order_details, tracking_number=tracking_number_from_url)

@app.route('/receipt/<int:order_id>')
@login_required
def receipt(order_id):
    """Renders a detailed receipt for a specific order."""
    order = get_order_by_id(order_id)
    if not order:
        flash("Order not found.", "error")
        return redirect(url_for('my_account'))
    
    if order.user_id != session.get('user_id') and not session.get('is_admin'):
        flash("You are not authorized to view this receipt.", "error")
        return redirect(url_for('my_account'))
        
    return render_template('receipt.html', order=order)

@app.route("/my_account")
@login_required
def my_account():
    """Displays user's account history, information, and default address."""
    user_id = session.get('user_id')
    user_info = get_user_by_id(user_id)
    orders = get_user_orders(user_id) 

    if user_info:
        default_address_data = {
            'first_name': user_info.get('first_name'),
            'last_name': user_info.get('last_name'),
            'email': user_info.get('email'),
            'phone': user_info.get('phone'),
            'address': user_info.get('address'),
            'city': user_info.get('city'),
            'barangay': user_info.get('barangay'),
            'province': user_info.get('province'),
            'postal_code': user_info.get('postal_code'),
            'landmark': user_info.get('landmark')
        }
        if default_address_data.get('address'):
            user_info['default_address'] = default_address_data
        else:
            user_info['default_address'] = None

    return render_template("my_account.html", user_info=user_info, orders=orders, location_data_json=json.dumps(LOCATION_DATA))


@app.route("/inbox")
@login_required
def inbox():
    """Displays the user's inbox with replies to their contact messages."""
    user_id = session.get('user_id')
    user_info = get_user_by_id(user_id)
    
    messages = []
    if user_info and user_info.get('email'):
        messages = get_user_contact_messages(user_info['email'])
        
    return render_template("inbox.html", messages=messages, user_info=user_info)

@app.route('/update_account', methods=['POST'])
@login_required 
def update_account():
    """Handles updating user account information."""
    user_id = session['user_id']
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()

    if not all([first_name, last_name, email, phone]):
        flash("All account information fields are required.", "error")
    else:
        try:
            update_user_info(user_id, first_name, last_name, email, phone)
            flash('Account information updated successfully!', 'success')
        except Exception as e:
            flash(f"Error updating account information: {e}", "error")
    return redirect(url_for('my_account'))

@app.route('/update_address', methods=['POST'])
@login_required 
def update_address():
    """Handles updating user default address and contact information."""
    user_id = session['user_id']
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    address = request.form.get('address', '').strip()
    city = request.form.get('city', '').strip()
    barangay = request.form.get('barangay', '').strip()
    province = request.form.get('province', '').strip()
    postal_code = request.form.get('postal_code', '').strip()
    landmark = request.form.get('landmark', '').strip()

    try:
        update_user_address(user_id, first_name, last_name, email, phone, address, city, barangay, province, postal_code, landmark)
        flash('Default address updated successfully!', 'success')
    except Exception as e:
        flash(f"Error updating address: {e}", "error")
        app.logger.error(f"Error updating address for user {user_id}: {e}")
    return redirect(url_for('my_account'))


@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    """Handles updating the user's password from the My Account page."""
    user_id = session['user_id']
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_new_password = request.form.get('confirm_new_password')

    if not all([current_password, new_password, confirm_new_password]):
        flash("All password fields are required.", "error")
        return redirect(url_for('my_account'))

    user = get_user_with_password_by_id(user_id)

    if not user or user['password'] != current_password:
        flash("Incorrect current password.", "error")
        return redirect(url_for('my_account'))

    if new_password != confirm_new_password:
        flash("New passwords do not match.", "error")
        return redirect(url_for('my_account'))

    if len(new_password) < 4:
        flash("Password must be at least 4 characters long.", "error")
        return redirect(url_for('my_account'))

    if not re.match(r'^[A-Za-z0-9]+$', new_password):
        flash("Password can only contain letters and numbers.", "error")
        return redirect(url_for('my_account'))
        
    if new_password == current_password:
        flash("New password cannot be the same as the old password.", "warning")
        return redirect(url_for('my_account'))

    try:
        update_user_password(user_id, new_password)
        flash('Password updated successfully!', 'success')
    except Exception as e:
        flash(f"Error updating password: {e}", "error")
        app.logger.error(f"Error updating password for user {user_id}: {e}")

    return redirect(url_for('my_account'))

@app.route("/admin")
@admin_required
def admin_dashboard():
    """Admin dashboard."""
    return render_template("admin_dashboard.html")

@app.route("/admin/products", methods=["GET", "POST"])
@admin_required
def admin_products():
    """Manages products (list, add)."""
    if request.method == "POST":
        product_data = {
            "name": request.form.get("name"),
            "brand": request.form.get("brand"),
            "price": float(request.form.get("price")),
            "original_price": float(request.form.get("original_price")) if request.form.get("original_price") else None,
            "quantity": int(request.form.get("quantity", 0)),
            "category": request.form.get("category"),
            "gender": request.form.get("gender"),
            "on_sale": 'on_sale' in request.form,
            "colors": [color.strip() for color in request.form.get("colors", "").split(',') if color.strip()],
            "description": request.form.get("description", "").strip() # MODIFICATION: Get description
        }

        if not all(product_data[k] is not None for k in ["name", "brand", "category", "gender"]) or product_data["price"] is None:
            flash("Product name, brand, price, category, and gender are required fields.", "error")
            return redirect(request.url)

        if 'product_image' not in request.files or request.files['product_image'].filename == '':
            flash('Product image is required.', 'error')
            return redirect(request.url)
        
        file = request.files['product_image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            product_data["image_url"] = url_for('static', filename=f'uploads/{filename}')
        else:
            flash('Invalid file type for product image.', 'error')
            return redirect(request.url)

        try:
            add_product(product_data)
            flash("Product added successfully! You can now manage its stock by size.", "success")
        except Exception as e:
            flash(f"Error adding product: {e}", "error")
        return redirect(url_for('admin_products'))
    
    products_with_stock = get_all_products()
    return render_template("admin_products.html", products=products_with_stock,
                           brands=brand, categories=["sneakers", "clothing"])

@app.route("/admin/products/edit/<int:product_id>", methods=["GET", "POST"])
@admin_required
def admin_edit_product(product_id):
    """Edits an existing product's details (not stock)."""
    product = get_product_by_id(product_id)
    if not product:
        flash("Product not found.", "error")
        return redirect(url_for('admin_products'))

    if request.method == "POST":
        product_data = {
            "name": request.form.get("name"),
            "brand": request.form.get("brand"),
            "price": float(request.form.get("price")),
            "original_price": float(request.form.get("original_price")) if request.form.get("original_price") else None,
            "category": request.form.get("category"),
            "gender": request.form.get("gender"),
            "on_sale": 'on_sale' in request.form,
            "colors": [color.strip() for color in request.form.get("colors", "").split(',') if color.strip()],
            "image_url": product['image_url'],
            "description": request.form.get("description", "").strip() # MODIFICATION: Get description
        }

        if 'product_image' in request.files:
            file = request.files['product_image']
            if file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                product_data["image_url"] = url_for('static', filename=f'uploads/{filename}')

        try:
            update_product(product_id, product_data)
            flash("Product updated successfully!", "success")
        except Exception as e:
            flash(f"Error updating product: {e}", "error")
        return redirect(url_for('admin_products'))

    return render_template("admin_edit_product.html", product=product,
                           brands=brand, categories=["sneakers", "clothing"])

@app.route("/admin/products/delete/<int:product_id>", methods=["POST"])
@admin_required
def admin_delete_product(product_id):
    """Deletes a product."""
    try:
        delete_product(product_id)
        flash("Product deleted successfully!", "success")
    except Exception as e:
        flash(f"Error deleting product: {e}", "error")
    return redirect(url_for('admin_products'))

@app.route("/admin/orders")
@admin_required
def admin_orders():
    """Lists all customer orders."""
    orders = get_all_checkouts_with_items()
    return render_template("admin_orders.html", orders=orders)

@app.route("/admin/orders/update_status/<int:order_id>", methods=["POST"])
@admin_required
def admin_update_order_status(order_id):
    """Updates the status of a specific order."""
    new_status = request.form.get("status")
    if new_status:
        try:
            update_checkout_status(order_id, new_status)
            flash(f"Order {order_id} status updated to '{new_status}'.", "success")
        except Exception as e:
            flash(f"Error updating order status: {e}", "error")
    return redirect(url_for('admin_orders'))

@app.route("/admin/orders/delete/<int:order_id>", methods=["POST"])
@admin_required
def admin_delete_order(order_id):
    """Deletes a specific order."""
    try:
        delete_checkout(order_id)
        flash(f"Order {order_id} deleted successfully.", "success")
    except Exception as e:
            flash(f"Error deleting order: {e}", "error")
    return redirect(url_for('admin_orders'))

@app.route("/admin/users", methods=["GET", "POST"])
@admin_required
def admin_user_management():
    """Manages users (list, add, edit password, delete)."""
    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "add_user":
            username = request.form.get("username")
            password = request.form.get("password")
            email = request.form.get("email") 
            is_admin = 'is_admin' in request.form
            
            if not username or not password or not email:
                flash("Username, password, and email are required.", "error")
            elif get_user(username):
                flash("Username already exists.", "error")
            else:
                try:
                    add_user(username=username, password=password, email=email, is_admin=is_admin)
                    flash("User added successfully.", "success")
                except Exception as e:
                    flash(f"Error adding user: {e}", "error")

        elif action == "edit_password":
            user_id = request.form.get("user_id")
            new_password = request.form.get("new_password")
            if not new_password:
                flash("New password cannot be empty.", "error")
            else:
                try:
                    update_user_password(user_id, new_password)
                    flash("Password updated successfully.", "success")
                except Exception as e:
                    flash(f"Error updating password: {e}", "error")

        elif action == "delete_user":
            user_id_to_delete = request.form.get("user_id")
            if user_id_to_delete and int(user_id_to_delete) != session.get('user_id'):
                try:
                    delete_user(user_id_to_delete)
                    flash("User deleted successfully.", "success")
                except Exception as e:
                    flash(f"Error deleting user: {e}", "error")
            elif user_id_to_delete and int(user_id_to_delete) == session.get('user_id'):
                flash("You cannot delete your own account.", "error")

        return redirect(url_for('admin_user_management'))
        
    users = get_all_users()
    return render_template("admin_user_management.html", users=users)
        
    users = get_all_users()
    return render_template("admin_user_management.html", users=users)

@app.route("/admin/messages")
@admin_required
def admin_contact_messages():
    """Displays all contact messages."""
    messages = get_all_contact_messages()
    return render_template("admin_contact_messages.html", messages=messages)

@app.route("/admin/reviews")
@admin_required
def admin_reviews():
    """Displays all customer reviews for management and calculates summary statistics."""
    reviews = get_all_reviews()
    
    total_reviews = len(reviews)
    average_rating = 0
    rating_distribution = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    
    if total_reviews > 0:
        total_rating_sum = sum(r['rating'] for r in reviews)
        average_rating = total_rating_sum / total_reviews
        
        for r in reviews:
            if r['rating'] in rating_distribution:
                rating_distribution[r['rating']] += 1

    rating_percentages = {
        star: (count / total_reviews) * 100 if total_reviews > 0 else 0
        for star, count in rating_distribution.items()
    }

    return render_template(
        "admin_reviews.html", 
        reviews=reviews,
        total_reviews=total_reviews,
        average_rating=average_rating,
        rating_percentages=rating_percentages
    )

@app.route("/admin/reviews/delete/<int:review_id>", methods=["POST"])
@admin_required
def admin_delete_review(review_id):
    """Deletes a specific review from the database."""
    try:
        delete_review(review_id)
        flash("Review has been deleted successfully.", "success")
    except Exception as e:
        flash(f"An error occurred while deleting the review: {e}", "error")
        app.logger.error(f"Error deleting review {review_id}: {e}")
    return redirect(url_for('admin_reviews'))

def save_review_reply(review_id, reply_message):
    """Saves an admin's reply to a review."""
    con = get_db_connection()
    try:
        cur = con.cursor()
        cur.execute(
            """
            UPDATE reviews
            SET reply_message = ?, replied_at = ?
            WHERE id = ?
            """,
            (reply_message, datetime.now().isoformat(), review_id)
        )
        con.commit()
    except sqlite3.Error as e:
        con.rollback()
        app.logger.error(f"Database error in save_review_reply: {e}")
        raise
    finally:
        con.close()

@app.route("/admin/reviews/reply/<int:review_id>", methods=["POST"])
@admin_required
def admin_reply_review(review_id):
    """Handles the submission of an admin's reply to a review."""
    reply_message = request.form.get("reply_message", "").strip()
    if not reply_message:
        flash("Reply message cannot be empty.", "error")
        return redirect(url_for('admin_reviews'))

    try:
        save_review_reply(review_id, reply_message)
        flash("Your reply has been saved successfully.", "success")
    except Exception as e:
        flash(f"Error saving reply: {e}", "error")

    return redirect(url_for('admin_reviews'))

def save_admin_reply(message_id, reply_message):
    """Saves an admin's reply to a contact message."""
    con = get_db_connection()
    try:
        cur = con.cursor()
        cur.execute(
            """
            UPDATE contact_messages
            SET reply_message = ?, replied_at = ?
            WHERE id = ?
            """,
            (reply_message, datetime.now().isoformat(), message_id)
        )
        con.commit()
    except sqlite3.Error as e:
        con.rollback()
        app.logger.error(f"Database error in save_admin_reply: {e}")
        raise
    finally:
        con.close()

@app.route("/admin/messages/reply/<int:message_id>", methods=["POST"])
@admin_required
def admin_reply_message(message_id):
    """Handles the submission of an admin's reply to a contact message."""
    reply_message = request.form.get("reply_message", "").strip()
    if not reply_message:
        flash("Reply message cannot be empty.", "error")
        return redirect(url_for('admin_contact_messages'))

    try:
        save_admin_reply(message_id, reply_message)
        flash("Your reply has been sent successfully.", "success")
    except Exception as e:
        flash(f"Error sending reply: {e}", "error")

    return redirect(url_for('admin_contact_messages'))

@app.route("/admin/stocks")
@admin_required
def manage_stocks():
    """Renders the stock management page with filtering and statistics."""
    all_products = get_all_products()

    filtered_products = all_products
    stock_status_filter = request.args.get('stock_status')
    brand_filter = request.args.get('brand')
    category_filter = request.args.get('category')
    gender_filter = request.args.get('gender')

    if stock_status_filter:
        if stock_status_filter == 'out':
            filtered_products = [p for p in filtered_products if p['total_quantity'] == 0]
        elif stock_status_filter == 'low':
            filtered_products = [p for p in filtered_products if 0 < p['total_quantity'] <= 10]
        elif stock_status_filter == 'good':
            filtered_products = [p for p in filtered_products if p['total_quantity'] > 10]
    
    if brand_filter:
        filtered_products = [p for p in filtered_products if p['brand'] == brand_filter]
    if category_filter:
        filtered_products = [p for p in filtered_products if p['category'] == category_filter]
    if gender_filter:
        filtered_products = [p for p in filtered_products if p['gender'] == gender_filter]

    total_products = len(all_products)
    out_of_stock_count = sum(1 for p in all_products if p['total_quantity'] == 0)
    low_stock_count = sum(1 for p in all_products if 0 < p['total_quantity'] <= 10)
    total_stock_items = sum(p['total_quantity'] for p in all_products)

    con = get_db_connection()
    brands = []
    categories = []
    sold_items_count = 0
    try:
        brands = [row['brand'] for row in con.execute("SELECT DISTINCT brand FROM products ORDER BY brand").fetchall()]
        categories = [row['category'] for row in con.execute("SELECT DISTINCT category FROM products ORDER BY category").fetchall()]
        
        sold_items_result = con.execute("SELECT SUM(item_quantity) FROM order_items").fetchone()
        if sold_items_result and sold_items_result[0] is not None:
            sold_items_count = sold_items_result[0]
            
    except sqlite3.Error as e:
        app.logger.error(f"Database error fetching stats for manage_stocks: {e}")
    finally:
        con.close()

    return render_template(
        "admin_manage_stocks.html",
        products=filtered_products,
        brands=brands,
        categories=categories,
        total_products=total_products,
        out_of_stock_count=out_of_stock_count,
        low_stock_count=low_stock_count,
        total_stock_value=total_stock_items,
        sold_items_count=sold_items_count
    )

@app.route("/admin/stock/quick_update/<int:product_id>/<size>", methods=["POST"])
@admin_required
def quick_update_stock(product_id, size):
    """Updates the stock for a single product size."""
    try:
        new_quantity = int(request.form.get("new_quantity"))
        if new_quantity < 0:
            flash("Quantity cannot be negative.", "error")
        else:
            con = get_db_connection()
            try:
                con.execute(
                    "UPDATE product_sizes SET quantity = ? WHERE product_id = ? AND size = ?",
                    (new_quantity, product_id, size)
                )
                con.commit()
                flash(f"Stock for size {size} updated successfully.", "success")
            except sqlite3.Error as e:
                con.rollback()
                app.logger.error(f"Database error in quick_update_stock: {e}")
                flash(f"Error updating stock: {e}", "error")
            finally:
                con.close()
    except (ValueError, TypeError):
        flash("Invalid quantity provided.", "error")
    
    return redirect(url_for('manage_stocks', **request.args))

@app.route("/subscribe_newsletter", methods=["POST"])
def subscribe_newsletter():
    """Handles newsletter subscription form submission and sends a confirmation email."""
    
    email = request.form.get("email")

    if not email:
        flash("Please enter a valid email address.", "error")
        return redirect(url_for('home'))

    success = send_subscription_confirmation_email(email)

    if success:
        flash(f"Success! A confirmation email has been sent to {email}. Check your inbox!", "success")
    else:
        flash("Oops! There was an issue sending your confirmation. Please try again later.", "error")

    return redirect(url_for('home'))

if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(host='0.0.0.0', port=5000, debug=True)