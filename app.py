from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import CSRFProtect

from models import db, Sighting, Harvest, Animal
from forms import SightingForm, HarvestForm, ANIMAL_CHOICES
from werkzeug.utils import secure_filename
from datetime import datetime
import os

app = Flask(__name__)

# Secret key for session management - ENVIRONMENT VARIABLES
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-fallback-key'

# Upload folder for user-uploaded images
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database config - ENVIRONMENT VARIABLES
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///wildlife.db')
# Initialize extension
db.init_app(app)
csrf = CSRFProtect(app) # CSRF protection

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
        sightings_query = sightings_query.order(Sighting.date_time.asc())
    else:
        sightings_query = sightings_query.order_by(Sighting.date_time.desc())

    sightings = sightings_query.all()

    # Build JSON for map
    sightings_json = [
        {
            'id': s.id,
            "marker_color": s.marker_color,
            'animal': s.animal.name if s.animal else None,
            'location': s.location,
            'date_time': s.date_time.strftime('%Y-%m-%d %H:%M'),
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
    # if request.method == 'POST':
    # Always set animal choices if category is selected (GET or POST)
    selected_category = request.form.get('animal_category') or form.animal_category.data
    if selected_category in ANIMAL_CHOICES:
        form.animal.choices = [(a, a) for a in ANIMAL_CHOICES[selected_category]]
    else:
        form.animal.choices = []

    if form.validate_on_submit():
        image_file = request.files.get('photo') # .get('photo') avoids key error if no photo/image uploaded
        filename = None
        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(filepath)

        from models import Animal
        animal_obj = Animal.query.filter_by(name=form.animal.data).first()
        if not animal_obj:
            flash("Animal not found in database.", "error")
            return render_template('add.html', form=form, animal_choices=ANIMAL_CHOICES)

        # Create new sighting using all form fields
        new_sighting = Sighting(
            animal=animal_obj,
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
            lat=form.lat.data,
            lng=form.lng.data
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

    if form.validate_on_submit():
        # sighting.animal = form.animal.data
        animal_obj = Animal.query.filter_by(name=form.animal.data).first()
        sighting.animal = animal_obj
        sighting.location = form.location.data
        sighting.date_time = form.date_time.data
        sighting.notes = form.notes.data

        image_file = request.files.get('photo')
        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(filepath)
            sighting.image = filename

        db.session.commit()
        flash('Sighting updated!')
        return redirect(url_for('view_sighting', id=id))

    return render_template('edit_sighting.html', form=form, sighting=sighting)


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

    # Convert to JSON-serializable list
    harvests_json = [
        {
            'id': h.id,
            'animal': h.animal,
            'date_time': h.date_time.strftime('%Y-%m-%d') if h.date else '',
            'location': h.location,
            'weight': h.weight,
            'notes': h.notes,
        } for h in harvests
    ]

    return render_template('view_harvests.html', harvests=harvests, harvests_json=harvests_json)


# ADD HARVEST ====================================================
@app.route('/harvests/add', methods=['GET', 'POST'])
def add_harvest():
    form = HarvestForm()

    if form.validate_on_submit():
        photo_file = request.files['photo']
        filename = secure_filename(photo_file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        photo_file.save(filepath)

        new_harvest = Harvest(
            harvest_name=form.harvest_name.data,
            animal=form.animal.data,
            date_time=form.date_time.data,
            weapon_type=form.weapon_type.data,
            other_weapon_type=form.other_weapon_type.data,
            caliber=form.caliber.data,
            other_caliber=form.other_caliber.data,
            broadhead=form.broadhead.data,
            other_broadhead=form.other_broadhead.data,
            weather=form.weather.data,
            wind_speed=form.wind_speed.data,
            wind_direction=form.wind_direction.data,
            humidity=form.humidity.data,
            notes=form.notes.data,
            photo=filename,
            marker_color=form.marker_color.data,
            distance_traveled=form.distance_traveled.data,
            shot_lat=form.shot_lat.data,
            shot_lng=form.shot_lng.data,
            recovery_lat=form.recovery_lat.data,
            recovery_lng=form.recovery_lng.data
        )
        db.session.add(new_harvest)
        db.session.commit()
        flash('Harvest successfully added!', 'success')
        return redirect(url_for('view_harvests'))

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
        harvest.animal = form.animal.data
        harvest.location = form.location.data
        harvest.date_time = form.date_time.data
        harvest.method = form.method.data
        harvest.notes = form.notes.data

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
    app.run(debug=True)
