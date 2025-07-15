"""
app.py
The main flask application file that initializes and configures the web app,
sets up routes, handles user requests, and manages form submissions related to wildlife sightings.
This file integrates the Flask app with the database, form validations, and templates
to create a full-featured wildlife sighting tracking application.
"""


from flask import Flask, render_template, request, redirect, url_for
from models import db, Sighting
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from forms import SightingForm
from forms import HarvestForm
from models import Harvest
from flask import flash
from flask import jsonify

# ------------------------------
# Flask App Setup
# ------------------------------
app = Flask(__name__)

# Set up SQLite database using SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sightings.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Enable CSRF protection for Flask-WTF form
# Can use a string for key for now, in production should be secure random value from secrets manager or environment variable
app.config['SECRET_KEY'] = 'replace-this-with-a-strong-random-secret'

# Set upload folder for storing user-uploaded images
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Converts a Harvest model object to a dictionary that can be used in JSON
def harvest_to_dict(h):
    return {
        'id': h.id,
        'animal': h.animal,
        'date_time': h.date_time.isoformat() if h.date_time else None,
        'weapon_type': h.weapon_type,
        'caliber': h.caliber,
        'broadhead': h.broadhead,
        'shot_lat': h.shot_lat,
        'shot_lng': h.shot_lng,
        'recovery_lat': h.recovery_lat,
        'recovery_lng': h.recovery_lng,
        'distance_traveled': h.distance_traveled,
        'notes': h.notes,
        'marker_color': h.marker_color,
        'photo_filename': h.photo_filename
    }

# Initialize SQLAlchemy with Flask app
db.init_app(app)


# ROUTE FOR HOME PAGE --------------------------------------
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/sightings')
def sightings_page():
    animal_filter = request.args.get('animal')
    sort_order = request.args.get('sort', 'desc')

    query = Sighting.query
    if animal_filter:
        query = query.filter_by(animal=animal_filter)
    if sort_order.lower() == 'asc':
        query = query.order_by(Sighting.date_time.asc())
    else:
        query = query.order_by(Sighting.date_time.desc())

    sightings = query.all()
    sightings_data = [s.to_dict() for s in sightings]

    unique_animals = db.session.query(Sighting.animal).distinct().order_by(Sighting.animal).all()
    unique_animals = [a[0] for a in unique_animals]

    return render_template(
        'index.html',
        sightings=sightings_data,
        animal_filter=animal_filter or '',
        sort_order=sort_order,
        unique_animals=unique_animals
    )

# ------------------------------
# Home Route (INDEX PAGE) ------------------------------------
# Shows all sightings and filtering options
# ------------------------------


@app.route('/')
def index():
    animal_filter = request.args.get('animal')         # Filter by animal(optional)
    sort_order = request.args.get('sort', 'desc')       # Sort by date - newest first

    # BUILD QUERY DYNAMICALLY BASED ON FILTER/SORT
    query = Sighting.query
    if animal_filter:
        query = query.filter_by(animal=animal_filter)
    if sort_order.lower() == 'asc':
        query = query.order_by(Sighting.date_time.asc())
    else:
        query = query.order_by(Sighting.date_time.desc())

    sightings = query.all()

    # Use model helper to convert to dict
    sightings_data = [s.to_dict() for s in sightings]

    # GET DISTINCT LIST OF ANIMAL NAMES FOR DROPDOWN
    unique_animals = db.session.query(Sighting.animal).distinct().order_by(Sighting.animal).all()
    unique_animals = [a[0] for a in unique_animals]

    return render_template(
        'index.html',
        sightings=sightings_data,  # Send the serialized data to template
        animal_filter=animal_filter or '',
        sort_order=sort_order,
        unique_animals=unique_animals
    )


# ------------------------------
# ADD NEW SIGHTING ROUTE ------------------------------------
# Handles form submission for new sightings
# ------------------------------


@app.route('/add', methods=['GET', 'POST'])
def add():
    form = SightingForm()
    if form.validate_on_submit():
        photo_file = form.photo.data
        photo_filename = None

        if photo_file:
            filename = secure_filename(photo_file.filename)
            photo_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            photo_filename = filename

        # def try to handle empty inputs when submitting sightings
        # Helper function to safely convert to float or return None
        def safe_float(val):
            try:
                return float(val)
            except (ValueError, TypeError):
                return None

        new_sighting = Sighting(
            animal=form.animal.data,
            date_time=form.date_time.data or None,
            weather=form.weather.data or None,
            wind=form.wind.data or None,
            wind_speed=safe_float(form.wind_speed.data),
            wind_direction=form.wind_direction.data or None,
            humidity=form.humidity.data or None,
            temperature=form.temperature.data or None,
            location=form.location.data or None,
            notes=form.notes.data or None,
            marker_color=form.marker_color.data or None,
            lat=safe_float(form.lat.data),
            lng=safe_float(form.lng.data),
            photo_filename=photo_filename
        )
        db.session.add(new_sighting)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add.html', form=form)

# ------------------------------
# DELETE ROUTE ------------------------------------------------
# Handles batch deletion of selected sightings
# ------------------------------


@app.route('/delete', methods=['POST'])
def delete():
    ids_to_delete = request.form.getlist('delete_ids')
    if ids_to_delete:
        for sighting_id in ids_to_delete:
            sighting = Sighting.query.get(sighting_id)
            if sighting:
                db.session.delete(sighting)
        db.session.commit()
    return redirect(url_for('index'))


# ------------------------------------
# ROUTE TO ADD NEW HARVEST -------------------------------------
# ------------------------------


@app.route('/add-harvest', methods=['GET', 'POST'])
def add_harvest():
    form = HarvestForm()
    photo_filename = None

    if form.validate_on_submit():
        # ---- Handle uploaded photo ----
        photo = form.photo.data
        if photo:
            photo_filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))

        # Convert string inputs safely
        def safe_float(val):
            try:
                return float(val)
            except (ValueError, TypeError):
                return None

        new_harvest = Harvest(
            animal=form.animal.data,
            date_time=form.date_time.data or None,
            weapon_type=form.weapon_type.data or None,
            caliber=form.caliber.data or None,
            broadhead=form.broadhead.data or None,
            shot_lat=safe_float(form.shot_lat.data),
            shot_lng=safe_float(form.shot_lng.data),
            recovery_lat=safe_float(form.recovery_lat.data),
            recovery_lng=safe_float(form.recovery_lng.data),
            distance_traveled=safe_float(form.distance_traveled.data),
            notes=form.notes.data or None,
            marker_color=form.marker_color.data or "#2e7d32",
            photo_filename=photo_filename
        )
        db.session.add(new_harvest)
        db.session.commit()
        # flash message
        flash("Harvest successfully logged!", "success")
        return redirect(url_for('view_harvests')) # redirect to your home or harvest view page

    # This part makes red flash message show up
    if form.errors:
        flash("Please correct the errors below and resubmit.", "danger")

    return render_template('add_harvest.html', form=form)


@app.route('/harvests')
def view_harvests():
    # Order harvests by date_time descending (newest first)
    harvests = Harvest.query.order_by(Harvest.date_time.desc()).all()

    # gt the latest harvest ID to highlight in the table
    latest_id = harvests[0].id if harvests else None

    harvests_json = [harvest_to_dict(h) for h in harvests]
    return render_template('view_Harvests.html', harvests=harvests, harvests_json=harvests_json, latest_id=latest_id)

# ----------------------------------------
# EDIT ROUTES - EDIT SIGHTING AND EDIT HARVEST
# ----------------------------------------
# EDIT HARVEST ROUTE


@app.route("/edit-harvest/<int:harvest_id>", methods=['GET', 'POST'])
def edit_harvest(harvest_id):
    harvest = Harvest.query.get_or_404(harvest_id)
    form = HarvestForm(obj=harvest)

    if form.validate_on_submit():
        form.populate_obj(harvest)
        db.session.commit()
        flash("Harvest udated!", "success")
        return redirect(url_for("view_harvest", harvest_id=harvest.id))

    return render_template("edit_harvest.html", form=form, harvest=harvest)


# -------------------------------------
# EDIT SIGHTINGS ROUTE ----
# -------------------------------------


@app.route("/edit-sighting/<int:sighting_id>", methods=['GET', 'POST'])
def edit_sighting(sighting_id):
    sighting = Sighting.query.get_or_404(sighting_id)
    form = SightingForm(obj=sighting)

    if form.validate_on_submit():
        form.populate_obj(sighting)
        db.session.commit()
        flash("Sighting updated!", "success")
        return redirect(url_for("view_Sighting", sighting_id=sighting.id))

    return render_template('edit_sighting.html', form=form, sighting=sighting)


# ------------------------------
# View Single Harvest - let you redirect to a detailed view after editing or adding
# -----------------------------


@app.route('/harvest/<int:harvest_id>')
def view_harvest(harvest_id):
    harvest = Harvest.query.get_or_404(harvest_id)
    return render_template('view_Harvest.html', harvest=harvest)


# -----------------------
# View Single Sighting - redirect to a detailed view after editing or adding
# -----------------------
@app.route('/sighting/<int:sighting_id>')
def view_sighting(sighting_id):
    sighting = Sighting.query.get_or_404(sighting_id)
    return render_template('view_sighting.html', sighting=sighting)


#------------------------------
# DELETE SINGLE SIGHTING
# -----------------------------


@app.route("/delete-sighing/<int:sighting_id>", methods=["POST"])
def delete_sighting(sighting_id):
    sighting = Sighting.query.get_or_404(sighting_id)
    db.session.delete(sighting)
    db.session.commit()
    flash("Sighting deleted!", "info")
    return redirect(url_for("index"))


# -----------------------------
# DELETE SINGLE HARVEST
# -----------------------------


@app.route("/delete-harvest/<int:harvest_id>", methods=["POST"])
def delete_harvest(harvest_id):
    harvest = Harvest.query.get_or_404(harvest_id)
    db.session.delete(harvest)
    db.session.commit()
    flash("Harvest deleted!", "info")
    return redirect(url_for("view_harvests"))

# ------------------------------
# RUN FLASK APP
# ------------------------------


if __name__ == '__main__':
    # Only run once to create database tables:
    with app.app_context():
        db.create_all()
    app.run(debug=True)
