from flask import Flask, request, render_template, redirect, url_for, flash
import mysql.connector
import string
import random
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# MySQL DB setup
def get_db_connection():
    conn = mysql.connector.connect(
        host=os.getenv('MYSQL_HOST'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DATABASE')
    )
    return conn

# Function to generate a new random link (you can modify this logic)
def generate_new_link():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(8))

# Home route
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original_link = request.form['original_link']
        
        if not original_link:
            flash("Please enter a valid link", 'error')
            return redirect(url_for('index'))
        
        # Generate new link
        new_link = generate_new_link()

        # Store in database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO links (original_link, new_link) VALUES (%s, %s)', 
                       (original_link, new_link))
        conn.commit()
        cursor.close()
        conn.close()

        # Flash the message to display the new link
        flash(f"New link created: {request.host_url}{new_link}", 'success')

        # Redirect to GET method after processing the form (PRG pattern)
        return redirect(url_for('index'))

    return render_template('index.html')

# Redirect route for the new link
@app.route('/<new_link>')
def redirect_link(new_link):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT original_link FROM links WHERE new_link = %s', (new_link,))
    link_data = cursor.fetchone()
    cursor.close()
    conn.close()

    if link_data:
        # Redirect to original link
        return redirect(link_data['original_link'])
    else:
        flash('Link not found!', 'error')
        return redirect(url_for('index'))

# Initialize the database with a table (Run this once to set up the table)
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS links (
            id INT AUTO_INCREMENT PRIMARY KEY,
            original_link TEXT NOT NULL,
            new_link VARCHAR(255) NOT NULL UNIQUE
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(debug=True)