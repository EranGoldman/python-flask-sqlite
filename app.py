# Author: Clinton Daniel, University of South Florida
# Date: 4/4/2023
# Description: This is a Flask App that uses SQLite3 to
# execute (C)reate, (R)ead, (U)pdate, (D)elete operations

from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
from flask import Response
from flask import send_file
import sqlite3
import csv
import io
import barcode
from barcode.writer import ImageWriter
import os

app = Flask(__name__)

# Create a directory for barcode images if it doesn't exist
BARCODE_DIR = 'static/barcodes'
if not os.path.exists(BARCODE_DIR):
    os.makedirs(BARCODE_DIR)

# Home Page route
@app.route("/")
def home():
    return render_template("home.html")

# Route to form used to add a new student to the database
@app.route("/enternew")
def enternew():
    return render_template("item.html")

# Route to add a new record (INSERT) student data to the database
@app.route("/addrec", methods = ['POST', 'GET'])
def addrec():
    # Data will be available from POST submitted by the form
    if request.method == 'POST':
        try:
            barcode = request.form['barcode']
            product_name = request.form['product_name'] 
            barcode = request.form['barcode']
            description = request.form['description']
            quantity = request.form['quantity']
            price = request.form['price']
            category = request.form['category']
            supplier = request.form['supplier']

            # Connect to SQLite3 database and execute the INSERT
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute("INSERT INTO inventory (barcode, product_name, description, quantity, price, category, supplier) VALUES (?,?,?,?,?,?,?)",(barcode, product_name, description, quantity, price, category, supplier))

                con.commit()
                msg = "Record successfully added to database"
        except:
            con.rollback()
            msg = "Error in the INSERT"

        finally:
            con.close()
            print(generate_barcode(barcode))
            # Send the transaction message to result.html
            return render_template('item.html',msg=msg)

# Route to SELECT all data from the database and display in a table      
@app.route('/list')
def list():
    # Connect to the SQLite3 datatabase and 
    # SELECT id and all Rows from the inventory table.
    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row

    cur = con.cursor()
    cur.execute("SELECT id, * FROM inventory")

    rows = cur.fetchall()
    con.close()
    # Send the results of the SELECT to the list.html page
    return render_template("list.html",rows=rows)

# Route that will SELECT a specific row in the database then load an Edit form 
@app.route("/edit", methods=['POST','GET'])
def edit():
    if request.method == 'POST':
        try:
            # Use the hidden input value of id from the form to get the id
            id = request.form['id']
            # Connect to the database and SELECT a specific id
            con = sqlite3.connect("database.db")
            con.row_factory = sqlite3.Row

            cur = con.cursor()
            cur.execute("SELECT id, * FROM inventory WHERE id = " + id)

            rows = cur.fetchall()
        except:
            id=None
        finally:
            con.close()
            # Send the specific record of data to edit.html
            return render_template("edit.html",rows=rows)

# Route used to execute the UPDATE statement on a specific record in the database
@app.route("/editrec", methods=['POST','GET'])
def editrec():
    # Data will be available from POST submitted by the form
    if request.method == 'POST':
        try:
            # Use the hidden input value of id from the form to get the id
            id = request.form['id']
            barcode = request.form['barcode']
            product_name = request.form['product_name']
            quantity = request.form['quantity']
            description = request.form['description']
            price = request.form['price']
            category = request.form['category']
            supplier = request.form['supplier']

            # UPDATE a specific record in the database based on the id
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute("UPDATE inventory SET barcode='"+barcode+"', product_name='"+product_name+"', description='"+description+"', quantity='"+quantity+"', price='"+price+"', category='"+category+"', supplier='"+supplier+"' WHERE id="+id)

                con.commit()
                msg = "Record successfully edited in the database"
        except:
            con.rollback()
            msg = "Error in the Edit: UPDATE inventory SET barcode="+barcode+", product_name="+product_name+", description="+description+", quantity="+quantity+", price="+price+", category="+category+", supplier="+supplier+" WHERE id="+id

        finally:
            con.close()
            # Send the transaction message to result.html
            return render_template('result.html',msg=msg)

# Route used to execute the UPDATE statement on a specific record in the database
@app.route("/updateItemQuantity", methods=['POST','GET'])
def updateItemQuantity():
    # Data will be available from POST submitted by the form
    if request.method == 'POST':
        try:
            barcode = request.form['barcode']
            quantity_to_subtract = int(request.form['quantity'])

            # First get the current quantity
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                cur.execute("SELECT quantity FROM inventory WHERE barcode = ?", (barcode,))
                current_quantity = cur.fetchone()
                
                if current_quantity is None:
                    msg = "Error: Barcode not found"
                else:
                    current_quantity = current_quantity[0]
                    new_quantity = current_quantity - quantity_to_subtract
                    
                    if new_quantity < 0:
                        msg = "Error: Cannot have negative quantity"
                    else:
                        # UPDATE the quantity in the database
                        cur.execute("UPDATE inventory SET quantity = ? WHERE barcode = ?", (new_quantity, barcode))
                        con.commit()
                        msg = f"Successfully updated quantity. New quantity: {new_quantity}"
        except ValueError:
            msg = "Error: Please enter a valid number for quantity"
        except Exception as e:
            con.rollback()
            msg = f"Error in the Update: {str(e)}"
        finally:
            con.close()
            return render_template('home.html', msg=msg)

# Route used to DELETE a specific record in the database    
@app.route("/delete", methods=['POST','GET'])
def delete():
    if request.method == 'POST':
        try:
             # Use the hidden input value of id from the form to get the id
            id = request.form['id']
            # Connect to the database and DELETE a specific record based on id
            with sqlite3.connect('database.db') as con:
                    cur = con.cursor()
                    cur.execute("DELETE FROM inventory WHERE id="+id)

                    con.commit()
                    msg = "Record successfully deleted from the database"
        except:
            con.rollback()
            msg = "Error in the DELETE"

        finally:
            con.close()
            # Send the transaction message to result.html
            return render_template('result.html',msg=msg)

# Route to get quantity by barcode
@app.route("/get_quantity/<barcode>")
def get_quantity(barcode):
    try:
        con = sqlite3.connect("database.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT quantity FROM inventory WHERE barcode = ?", (barcode,))
        row = cur.fetchone()
        con.close()
        
        if row:
            return jsonify({"quantity": row["quantity"]})
        else:
            return jsonify({"quantity": None})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to download inventory as CSV
@app.route("/download_csv")
def download_csv():
    try:
        # Connect to the database and get all inventory data
        con = sqlite3.connect("database.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM inventory")
        rows = cur.fetchall()
        con.close()

        # Create a StringIO object to write CSV data
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(['ID', 'Barcode', 'Product Name', 'Description', 'Quantity', 
                        'Price', 'Category', 'Supplier', 'Last Updated'])

        # Write data rows
        for row in rows:
            writer.writerow([
                row['id'],
                row['barcode'],
                row['product_name'],
                row['description'],
                row['quantity'],
                row['price'],
                row['category'],
                row['supplier'],
                row['last_updated']
            ])

        # Create the response
        output.seek(0)
        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=inventory.csv"}
        )
    except Exception as e:
        return str(e), 500

# Route to generate and serve barcode image
@app.route('/barcode/<barcode_text>')
def generate_barcode(barcode_text):
    try:
        # Check if the file already exists
        filename = f"{barcode_text}"+".png"
        filepath = os.path.join(BARCODE_DIR, filename)
        
        if os.path.exists(filepath):
            # If file exists, serve it directly
            return send_file(filepath, mimetype='image/png')
        
        # If file doesn't exist, generate the barcode
        code128 = barcode.get('code128', barcode_text, writer=ImageWriter())
        code128.save(filepath[:-4])
        
        # Serve the newly created file
        return send_file(filepath, mimetype='image/png')
    except Exception as e:
        return str(e), 500