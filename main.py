import streamlit as st
import sqlitecloud
import threading
import time
from datetime import datetime

# Database connection and table creation functions
def create_users_table():
    conn = sqlitecloud.connect("sqlitecloud://ce3yvllesk.sqlite.cloud:8860/gas?apikey=kOt8yvfwRbBFka2FXT1Q1ybJKaDEtzTya3SWEGzFbvE")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def create_password_options_table():
    conn = sqlitecloud.connect("sqlitecloud://ce3yvllesk.sqlite.cloud:8860/gas?apikey=kOt8yvfwRbBFka2FXT1Q1ybJKaDEtzTya3SWEGzFbvE")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS password_options (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            option TEXT NOT NULL UNIQUE
        )
    ''')
    cursor.execute('''
        INSERT OR IGNORE INTO password_options (option) VALUES
        ('compound 1'),
        ('compound 2'),
        ('compound 3')
    ''')
    conn.commit()
    conn.close()

def create_bookings_table():
    conn = sqlitecloud.connect("sqlitecloud://ce3yvllesk.sqlite.cloud:8860/gas?apikey=kOt8yvfwRbBFka2FXT1Q1ybJKaDEtzTya3SWEGzFbvE")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'Processing',
            booking_date TEXT NOT NULL,
            password TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')
    conn.commit()
    conn.close()

def fetch_password_options():
    conn = sqlitecloud.connect("sqlitecloud://ce3yvllesk.sqlite.cloud:8860/gas?apikey=kOt8yvfwRbBFka2FXT1Q1ybJKaDEtzTya3SWEGzFbvE")
    cursor = conn.cursor()
    cursor.execute('SELECT option FROM password_options')
    options = cursor.fetchall()
    conn.close()
    return [option[0] for option in options]

def fetch_products():
    conn = sqlitecloud.connect("sqlitecloud://ce3yvllesk.sqlite.cloud:8860/gas?apikey=kOt8yvfwRbBFka2FXT1Q1ybJKaDEtzTya3SWEGzFbvE")
    cursor = conn.cursor()
    cursor.execute('SELECT id, image, name, price FROM products')
    products = cursor.fetchall()
    conn.close()
    return products

def signup(username, password):
    conn = sqlitecloud.connect("sqlitecloud://ce3yvllesk.sqlite.cloud:8860/gas?apikey=kOt8yvfwRbBFka2FXT1Q1ybJKaDEtzTya3SWEGzFbvE")
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
    conn.commit()
    conn.close()

def signin(username, password):
    conn = sqlitecloud.connect("sqlitecloud://ce3yvllesk.sqlite.cloud:8860/gas?apikey=kOt8yvfwRbBFka2FXT1Q1ybJKaDEtzTya3SWEGzFbvE")
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

def book_product(user, product_id):
    booking_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlitecloud.connect("sqlitecloud://ce3yvllesk.sqlite.cloud:8860/gas?apikey=kOt8yvfwRbBFka2FXT1Q1ybJKaDEtzTya3SWEGzFbvE")
    cursor = conn.cursor()
    
    # Check if the booking already exists
    cursor.execute('SELECT * FROM bookings WHERE user_id = ? AND product_id = ?', (user[0], product_id))
    existing_booking = cursor.fetchone()
    
    if not existing_booking:
        cursor.execute('INSERT INTO bookings (user_id, product_id, status, booking_date, password) VALUES (?, ?, ?, ?, ?)', 
                       (user[0], product_id, 'Processing', booking_date, user[2]))
        conn.commit()
    
    conn.close()

def fetch_bookings(user_id):
    conn = sqlitecloud.connect("sqlitecloud://ce3yvllesk.sqlite.cloud:8860/gas?apikey=kOt8yvfwRbBFka2FXT1Q1ybJKaDEtzTya3SWEGzFbvE")
    cursor = conn.cursor()
    cursor.execute('SELECT product_id, status FROM bookings WHERE user_id = ?', (user_id,))
    bookings = cursor.fetchall()
    conn.close()
    return bookings

# Streamlit app
def main():
    st.title("GAS BOOKING")

    # Create tables
    create_users_table()
    create_password_options_table()
    create_bookings_table()

    # Navigation
    if "page" not in st.session_state:
        st.session_state.page = "Sign In"

    if st.session_state.page == "Sign In":
        signin_page()
    elif st.session_state.page == "Sign Up":
        signup_page()
    elif st.session_state.page == "Products":
        if "user" in st.session_state:
            products_page()
        else:
            st.warning("Please sign in first.")
            st.session_state.page = "Sign In"

def signin_page():
    st.header("Sign In")
    username = st.text_input("Username")
    password_options = fetch_password_options()
    password = st.selectbox("Password", password_options)

    if st.button("Sign In"):
        user = signin(username, password)
        if user:
            st.session_state.user = user
            st.session_state.page = "Products"
            st.experimental_set_query_params(page="Products")
        else:
            st.error("Invalid username or password")

def signup_page():
    st.header("Sign Up")
    username = st.text_input("Username")
    password_options = fetch_password_options()
    password = st.selectbox("Password", password_options)

    if st.button("Sign Up"):
        signup(username, password)
        st.success("Signup successful! Please sign in.")
        st.session_state.page = "Sign In"
        st.experimental_set_query_params(page="Sign In")

def products_page():
    st.header("Products")
    user = st.session_state.user
    products = fetch_products()
    bookings = fetch_bookings(user[0])
    booking_dict = {booking[0]: booking[1] for booking in bookings}

    for product in products:
        product_id, product_image_url, product_name, product_price = product
        status = booking_dict.get(product_id)

        st.image(product_image_url, width=300)
        st.write(f"**{product_name}**")
        st.write(f"Price: ₹{product_price}")
        if status:
            st.write(f"Status: {status}")
        if st.button(f"Book {product_name}", key=product_id):
            book_product(user, product_id)
            st.success(f"Product {product_name} booked successfully!")

if __name__ == "__main__":
    main()
