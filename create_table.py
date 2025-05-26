# Author: Clinton Daniel, University of South Florida
# Date: 4/4/2023
# Description: This python script assumes that you already have
# a database.db file at the root of your workspace.
# This python script will CREATE a table called inventory 
# in the database.db using SQLite3 which will be used
# to store inventory management data
# Execute this python script before testing or editing this app code. 
# Open a python terminal and execute this script:
# python create_table.py

import sqlite3

conn = sqlite3.connect('database.db')
print("Connected to database successfully")

conn.execute('''CREATE TABLE inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    barcode TEXT NOT NULL UNIQUE,
    product_name TEXT NOT NULL,
    description TEXT,
    quantity INTEGER NOT NULL,
    price REAL NOT NULL,
    category TEXT,
    supplier TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')
print("Created inventory table successfully!")

conn.close()

