from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import CSRFProtect

from models import db, Sighting, Harvest, Animal
from forms import SightingForm, HarvestForm, ANIMAL_CHOICES
from werkzeug.utils import secure_filename
from datetime import datetime
import os

app = Flask(__name__)

# -------------------
# CORE CONFIG
# -------------------

# Secret key for session management (env override -> fallback)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-fallback-key'

# Upload folder and size cap
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB

# ---------------------------------------
# Database config (env or local sqlite)
# ---------------------------------------
database_url = os.getenv('DATABASE_URL')
if not database_url:
    # Build an absolute sqlite path and normalize slashes for SQLAlchemy
    db_path = os.path.join(app.root_path, "wildlife.db")
    db_path = db_path.replace('\\', '/')  # important on Windows
    database_url = f"sqlite:///{db_path}"

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

print("Using DB:", app.config['SQLALCHEMY_DATABASE_URI'])

# Initialize extensions AFTER all config is set
db.init_app(app)
csrf = CSRFProtect(app)

# =========================================
# HELPER FUNCTIONS
# =========================================


def handle_file_upload(file_field):
    """Safe file upload handler with error checking"""
    if file_field and file_field.filename:
        filename = secure_filename(file_field.filename)
        try:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file_field.save(filepath)
            return filename
        except Exception as e:
            flash('File upload failed: ' + str(e), 'error')
            return None
    return None

# --------
# Utilities
# --------


def safe_float(val):
    """
    Safely convert "val" to "float".
    Returns 'None' when 'val' is 'None' or an empty string mirroring
    typical form behavior where missing fields come through as empty values.
    Any value that cannot be converted to 'float' will also result in 'None'
    """
    if val in (None, ""):
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


# -----------------------
# HOME / LANDING PAGE
# -----------------------
@app.route('/')
def home():
    return render_template('home.html')


# @app.route('/')
# def index():
#     return render_template('index.html')


# -----------------------
# SIGHTING ROUTES
# -----------------------

# VIEW ALL SIGHTINGS ======================================
@app.route('/sightings')
def view_sightings():
    # Get filter/sort query params
    animal_filter = request.args.get('animal')
    sort_order = request.args.get('sort', 'desc')

    # base query
    sightings_query = Sighting.query

    # Apply filter
    if animal_filter:
        sightings_query = sightings_query.join(Animal).filter(Animal.name == animal_filter)

    # Apply sort
    if sort_order == 'asc':
        sightings_query = sightings_query.order_by(Sighting.date_time.asc())  # <<< CHANGED
    else:
        sightings_query = sightings_query.order_by(Sighting.date_time.desc())  # <<< CHANGED (ensure order_by)

    sightings = sightings_query.all()

    # Build JSON for map
    sightings_json = [
        {
            'id': s.id,
            'marker_color': s.marker_color,
            'sighting_name': s.sighting_name,
            'animal': s.animal.name if s.animal else None,
            'location': s.location,
            'date_time': s.date_time.strftime('%Y-%m-%d %H:%M') if s.date_time else '',  # <<< CHANGED: guard None
            'lat': s.lat,
            'lng': s.lng,
            'notes': s.notes,
            'photo_filename': s.photo_filename
        } for s in sightings
    ]

    # Build animal filter list
    unique_animals = [a.name for a in Animal.query.order_by(Animal.name).all()]

    return render_template(
        'index.html',
        sightings=sightings,
        sightings_json=sightings_json,
        animal_filter=animal_filter,
        sort_order=sort_order,
        unique_animals=unique_animals
    )


# ADD NEW SIGHTINGS ========================================


@app.route('/sightings/add', methods=['GET', 'POST'])
def add_sighting():
    form = SightingForm()

    # Dynamically update animal choices based on selected category
    selected_category = request.form.get('animal_category') or form.animal_category.data
    if selected_category in ANIMAL_CHOICES:
        form.animal.choices = [(a, a) for a in ANIMAL_CHOICES[selected_category]]
    else:
        form.animal.choices = []

    if form.validate_on_submit():
        image_file = request.files.get('photo')  # .get avoids KeyError
        filename = handle_file_upload(image_file)  # <<< CHANGED: use helper

        # find Animal by name
        animal_obj = Animal.query.filter_by(name=form.animal.data).first()
        if not animal_obj:
            flash("Animal not found in database.", "error")
            return render_template('add.html', form=form, animal_choices=ANIMAL_CHOICES)

        # Create new sighting using all form fields
        new_sighting = Sighting(
            animal=animal_obj,  # relationship sets animal_id
            sighting_name=form.sighting_name.data,
            location=form.location.data,
            date_time=form.date_time.data,
            notes=form.notes.data,
            photo_filename=filename,
            weather=form.weather.data,
            wind=form.wind.data,
            wind_speed=form.wind_speed.data,
            wind_direction=form.wind_direction.data,
            humidity=form.humidity.data,
            temperature=form.temperature.data,
            marker_color=form.marker_color.data,
            lat=safe_float(form.lat.data),
            lng=safe_float(form.lng.data)
        )

        db.session.add(new_sighting)
        db.session.commit()
        flash('Sighting added!')
        return redirect(url_for('view_sightings'))

    return render_template('add.html', form=form, animal_choices=ANIMAL_CHOICES)

# VIEW SINGLE SIGHTING ===================================


@app.route('/sightings/<int:id>')
def view_sighting(id):
    sighting = Sighting.query.get_or_404(id)
    return render_template('view_sighting.html', sighting=sighting)


# EDIT SIGHTING ==============================================
@app.route('/sightings/<int:id>/edit', methods=['GET', 'POST'])
def edit_sighting(id):
    sighting = Sighting.query.get_or_404(id)
    form = SightingForm(obj=sighting)

    # Ensure choices include the current animal on GET
    if request.method == 'GET' and sighting.animal:
        current_cat = sighting.animal.animal_class
        form.animal_category.data = current_cat
        if current_cat in ANIMAL_CHOICES:
            form.animal.choices = [(a, a) for a in ANIMAL_CHOICES[current_cat]]
            form.animal.data = sighting.animal.name
        else:
            form.animal.choices = [("", "Select an animal first")]  # fallback
    else:
        # Keep animal choices coherent on GET/POST
        selected_category = request.form.get('animal_category') or form.animal_category.data
        if selected_category in ANIMAL_CHOICES:
            form.animal.choices = [(a, a) for a in ANIMAL_CHOICES[selected_category]]
        else:
            form.animal.choices = [("", "Select an animal first")]  # fallback

    if form.validate_on_submit():
        animal_obj = Animal.query.filter_by(name=form.animal.data).first()
        if not animal_obj:
            flash("Animal not found in database.", "error")
            return render_template('edit_sighting.html', form=form, sighting=sighting, animal_choices=ANIMAL_CHOICES)

        # Fields available for editing when editing a sighting
        sighting.animal = animal_obj
        sighting.sighting_name = form.sighting_name.data
        sighting.location = form.location.data
        sighting.date_time = form.date_time.data
        sighting.notes = form.notes.data
        sighting.weather = form.weather.data
        sighting.wind = form.wind.data
        sighting.wind_speed = form.wind_speed.data
        sighting.wind_direction = form.wind_direction.data
        sighting.humidity = form.humidity.data
        sighting.temperature = form.temperature.data
        sighting.marker_color = form.marker_color.data
        sighting.lat = safe_float(form.lat.data)
        sighting.lng = safe_float(form.lng.data)

        image_file = request.files.get('photo')
        filename = handle_file_upload(image_file)
        if filename:
            sighting.photo_filename = filename

        db.session.commit()
        flash('Sighting updated!')
        return redirect(url_for('view_sighting', id=id))

    return render_template('edit_sighting.html', form=form, sighting=sighting, animal_choices=ANIMAL_CHOICES)


# DELETE SIGHTING ===============================================


@app.route('/sightings/<int:id>/delete', methods=['POST'])
def delete_sighting(id):
    sighting = Sighting.query.get_or_404(id)
    db.session.delete(sighting)
    db.session.commit()
    flash('Sighting deleted!')
    return redirect(url_for('view_sightings'))


# ---------------------------------------------------------
# HARVEST ROUTES
# ---------------------------------------------------------

# VIEW ALL HARVESTS ========================================
@app.route('/view-harvests')
def view_all_harvests():
    harvests = Harvest.query.all()
    harvests_json = [
        {
            'id': h.id,
            'animal': h.animal.name if h.animal else None,
            'harvest_name': h.harvest_name,
            'date_time': h.date_time.strftime('%Y-%m-%d %H:%M') if h.date_time else '',
            'weather': h.weather,
            'wind_speed': h.wind_speed,
            'wind_direction': h.wind_direction,
            'humidity': h.humidity,
            'weapon_type': h.weapon_type,
            'caliber': h.caliber,
            'broadhead': h.broadhead,
            'location': h.location,
            'distance_traveled': h.distance_traveled,
            'notes': h.notes,
            'photo_filename': h.photo_filename,
            'marker_color': h.marker_color,
            'shot_lat': h.shot_lat,
            'shot_lng': h.shot_lng,
            'recovery_lat': h.recovery_lat,
            'recovery_lng': h.recovery_lng,
        } for h in harvests
    ]
    return render_template('view_harvests.html', harvests=harvests, harvests_json=harvests_json)


# ADD HARVEST ====================================================
@app.route('/harvests/add', methods=['GET', 'POST'])
def add_harvest():
    form = HarvestForm()
    if form.validate_on_submit():
        photo_file = request.files.get('photo')
        filename = handle_file_upload(photo_file)

        animal_obj = Animal.query.filter_by(name=form.animal.data).first()
        if not animal_obj:
            flash("Animal not found in database.", "error")
            return render_template('add_harvest.html', form=form)

        new_harvest = Harvest(
            animal=animal_obj,
            harvest_name=form.harvest_name.data,
            date_time=form.date_time.data,
            weather=form.weather.data,
            wind_speed=form.wind_speed.data,
            wind_direction=form.wind_direction.data,
            humidity=form.humidity.data,
            weapon_type=form.weapon_type.data,
            other_weapon_type=form.other_weapon_type.data,
            caliber=form.caliber.data,
            other_caliber=form.other_caliber.data,
            broadhead=form.broadhead.data,
            other_broadhead=form.other_broadhead.data,
            location=form.location.data,
            shot_lat=safe_float(form.shot_lat.data),
            shot_lng=safe_float(form.shot_lng.data),
            recovery_lat=safe_float(form.recovery_lat.data),
            recovery_lng=safe_float(form.recovery_lng.data),
            distance_traveled=safe_float(form.distance_traveled.data),
            notes=form.notes.data,
            photo_filename=filename,
            marker_color=form.marker_color.data
        )
        db.session.add(new_harvest)
        db.session.commit()
        flash('Harvest successfully added!', 'success')
        return redirect(url_for('view_all_harvests'))

    return render_template('add_harvest.html', form=form)

# VIEW SINGLE HARVEST =============================================


@app.route('/harvests/<int:id>')
def view_harvest(id):
    harvest = Harvest.query.get_or_404(id)
    return render_template('view_harvest.html', harvest=harvest)

# EDIT HARVEST ================================================


@app.route('/harvests/<int:id>/edit', methods=['GET', 'POST'])
def edit_harvest(id):
    harvest = Harvest.query.get_or_404(id)
    form = HarvestForm(obj=harvest)

    if form.validate_on_submit():
        animal_obj = Animal.query.filter_by(name=form.animal.data).first()
        if not animal_obj:
            flash("Animal not found in database.", "error")
            return render_template('edit_harvest.html', form=form, harvest=harvest)
        harvest.animal = animal_obj

        harvest.harvest_name = form.harvest_name.data
        harvest.date_time = form.date_time.data
        harvest.weather = form.weather.data
        harvest.wind_speed = form.wind_speed.data
        harvest.wind_direction = form.wind_direction.data
        harvest.humidity = form.humidity.data
        harvest.weapon_type = form.weapon_type.data
        harvest.other_weapon_type = form.other_weapon_type.data
        harvest.caliber = form.caliber.data
        harvest.other_caliber = form.other_caliber.data
        harvest.broadhead = form.broadhead.data
        harvest.other_broadhead = form.other_broadhead.data
        harvest.location = form.location.data
        harvest.shot_lat = safe_float(form.shot_lat.data)
        harvest.shot_lng = safe_float(form.shot_lng.data)
        harvest.recovery_lat = safe_float(form.recovery_lat.data)
        harvest.recovery_lng = safe_float(form.recovery_lng.data)
        harvest.distance_traveled = safe_float(form.distance_traveled.data)
        harvest.notes = form.notes.data
        harvest.marker_color = form.marker_color.data

        photo_file = request.files.get('photo')
        filename = handle_file_upload(photo_file)
        if filename:
            harvest.photo_filename = filename

        db.session.commit()
        flash('Harvest updated!')
        return redirect(url_for('view_harvest', id=id))

    return render_template('edit_harvest.html', form=form, harvest=harvest)


# ---------------------------------------------
# DELETE HARVEST ROUTE
# ---------------------------------------------


@app.route('/harvests/<int:id>/delete', methods=['POST'])
def delete_harvest(id):
    harvest = Harvest.query.get_or_404(id)
    db.session.delete(harvest)
    db.session.commit()
    flash('Harvest deleted!')
    return redirect(url_for('view_all_harvests'))


# -----------------------
# Run the App
# -----------------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # Optional DEV SEED:
        # Insert animals if the table is empty (or insert any missing ones).
        # Remove this block in production or guard with an env flag.
        existing = {a.name for a in Animal.query.with_entities(Animal.name).all()}
        to_insert = []
        for category, names in ANIMAL_CHOICES.items():
            for name in names:
                if name not in existing:
                    to_insert.append(Animal(name=name, animal_class=category))
        if to_insert:
            db.session.add_all(to_insert)
            db.session.commit()
            print(f"Seeded {len(to_insert)} animals.")

    app.run(debug=True)
