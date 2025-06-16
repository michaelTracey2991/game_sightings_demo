from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

# ------------------------------
# Initialize the database with the sightings table
# ------------------------------
def init_db():
    conn = sqlite3.connect('sightings.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS sightings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            animal TEXT,
            date_time TEXT,
            weather TEXT,
            wind TEXT,
            wind_speed TEXT,
            wind_direction TEXT,
            humidity TEXT,
            temperature TEXT,
            location TEXT,
            notes TEXT,
            marker_color TEXT,
            lat TEXT,
            lng TEXT
        )
    ''')
    conn.commit()
    conn.close()

# ----------------------------------
# Home page route: shows the sightings table and map
# Handles optional filtering by animal and sorting by date
#-----------------------------------
@app.route('/')
def index():
    animal_filter = request.args.get('animal')
    sort_order = request.args.get('sort', 'desc')

    conn = sqlite3.connect('sightings.db')
    c = conn.cursor()

    # Get filtered or all sightings based on animal and sort order
    if animal_filter:
        query = f'''
                SELECT * FROM sightings 
                WHERE animal = ? 
                ORDER BY date_time {sort_order.upper()}
            '''
        c.execute(query, (animal_filter,))
    else:
        query = f'''
                SELECT * FROM sightings 
                ORDER BY date_time {sort_order.upper()}
            '''
        c.execute(query)

    data = c.fetchall()

    # Get a list of unique animal names for dropdown
    c.execute('SELECT DISTINCT animal FROM sightings WHERE animal IS NOT NULL ORDER BY animal ASC')
    unique_animals = [row[0] for row in c.fetchall()]

    conn.close()

    # Pass sightings, filter info, and unique animals to the template
    return render_template(
        'index.html',
        sightings=data,
        animal_filter=animal_filter or '',
        sort_order=sort_order,
        unique_animals=unique_animals
    )

# ----------------------------------------
# Route to handle adding a new sighting
# Supports weather/wind dropdowns with "Other" text option
# ----------------------------------------
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        animal = request.form['animal']
        date_time = request.form['date_time']
        # Weather Dropdown + Optional Text
        weather = request.form.get('weather')
        if weather == 'Other':
            weather = request.form.get('weather_other')

        # Wind Dropdown + Optional Text
        wind = request.form.get('wind')
        if wind == 'Other':
            wind = request.form.get('wind_other')

        wind_speed = request.form.get('wind_speed')
        wind_direction = request.form.get('wind_direction')
        humidity = request.form.get('humidity')
        temperature = request.form.get('temperature')
        location = request.form['location']
        notes = request.form['notes']
        lat = request.form.get('lat')
        lng = request.form.get('lng')

        # Marker color in add route
        marker_color = request.form.get('marker_color')

        conn = sqlite3.connect('sightings.db')
        c = conn.cursor()
        c.execute('''INSERT INTO sightings (
            animal, date_time, weather, wind, wind_speed, wind_direction,
            humidity, temperature, location, notes, marker_color, lat, lng
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
            animal, date_time, weather, wind, wind_speed, wind_direction,
            humidity, temperature, location, notes, marker_color
        ))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template('add.html')

# -------------------------------------
# Route to delete selected sightings
# Gets list of IDs from checkboxes and deletes them
# -------------------------------------
@app.route('/delete', methods=['POST'])
def delete():
    ids_to_delete = request.form.getlist('delete_ids')
    if ids_to_delete:
        conn = sqlite3.connect('sightings.db')
        c = conn.cursor()
        c.execute(f'DELETE FROM sightings WHERE id IN ({",".join("?" * len(ids_to_delete))})', ids_to_delete)
        conn.commit()
        conn.close()
    return redirect(url_for('index'))

# Initialize DB and run the Flask app
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
