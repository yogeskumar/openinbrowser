from flask import Flask, request, render_template, redirect, url_for, flash
import sqlite3
import string
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# SQLite DB setup
DATABASE = 'database.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
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
        conn.execute('INSERT INTO links (original_link, new_link) VALUES (?, ?)',
                     (original_link, new_link))
        conn.commit()
        conn.close()

        # Send the new link to frontend
        flash(f"New link created: {request.host_url}{new_link}", 'success')

    return render_template('index.html')

# Redirect route for the new link
@app.route('/<new_link>')
def redirect_link(new_link):
    conn = get_db_connection()
    link_data = conn.execute('SELECT original_link FROM links WHERE new_link = ?', (new_link,)).fetchone()
    conn.close()

    if link_data:
        # Redirect to original link
        return redirect(link_data['original_link'])
    else:
        flash('Link not found!', 'error')
        return redirect(url_for('index'))

# Initialize the database with a table
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_link TEXT NOT NULL,
            new_link TEXT NOT NULL UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(debug=True)
