"""
models.py
- Defines the database schema using SQLAlchemy ORM.
- Three models:
    1) Animal: normalized list of species + category (animal_class)
    2) Sighting: individual wildlife sightings tied to Animal
    3) Harvest: logged harvests tied to Animal

NOTE: If you add/remove columns, either run a migration (Flask-Migrate) or
      delete your dev SQLite file (wildlife.db) once and let db.create_all() recreate it.
"""

from flask_sqlalchemy import SQLAlchemy

# SQLAlchemy extension instance. The Flask app calls db.init_app(app).
db = SQLAlchemy()


# =========================================================
# Animal Model
# - Normalized animal names + their category (animal_class).
# - Used by Sighting and Harvest via foreign keys.
# =========================================================
class Animal(db.Model):
    __tablename__ = 'animal'  # explicit table name for clarity

    id = db.Column(db.Integer, primary_key=True)

    # "name" must match the values you seed and use in your forms (unique across the table)
    name = db.Column(db.String(100), nullable=False, unique=True)

    # e.g., "Big Game", "Small Game", "Waterfowl", etc.
    animal_class = db.Column(db.String(50), nullable=False)

    # ORM relationships back from Sighting and Harvest
    sightings = db.relationship('Sighting', backref='animal', lazy=True)
    harvests = db.relationship('Harvest', backref='animal', lazy=True)

    def __repr__(self):
        return f"<Animal id={self.id} name='{self.name}' class='{self.animal_class}'>"


# =========================================================
# Sighting Model
# - Stores all details for a single sighting, including map coords.
# - Indexed columns (animal_id, date_time) help sorting/filtering as data grows.
# =========================================================
class Sighting(db.Model):
    __tablename__ = 'sighting'

    id = db.Column(db.Integer, primary_key=True)

    # FK -> Animal; indexed to speed up joins/filters in lists
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'), nullable=False, index=True)  # <<< indexed

    # Sighting name/title stored in database
    sighting_name = db.Column(db.String(120), nullable=True, index=True)

    # When the sighting occurred; also indexed for fast sort/filter by date
    date_time = db.Column(db.DateTime, nullable=True, index=True)  # <<< indexed

    # Weather + context
    weather = db.Column(db.String(100), nullable=True)
    wind = db.Column(db.String(100), nullable=True)
    wind_speed = db.Column(db.String(100), nullable=True)
    wind_direction = db.Column(db.String(50), nullable=True)
    humidity = db.Column(db.String(20), nullable=True)
    temperature = db.Column(db.String(20), nullable=True)

    # Free-text location label + notes
    location = db.Column(db.String(200), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    # Map marker and coordinates (optional)
    marker_color = db.Column(db.String(20), nullable=True)
    lat = db.Column(db.Float, nullable=True)
    lng = db.Column(db.Float, nullable=True)

    # Optional photo filename (relative path in /static/uploads)
    photo_filename = db.Column(db.String(120), nullable=True)

    def to_dict(self):
        """Convenience method for JSON responses / map rendering."""
        return {
            "id": self.id,
            "animal": self.animal.name if self.animal else None,
            "sighting_name": self.sighting_name,
            "date_time": self.date_time,
            "weather": self.weather,
            "wind": self.wind,
            "wind_speed": self.wind_speed,
            "wind_direction": self.wind_direction,
            "humidity": self.humidity,
            "temperature": self.temperature,
            "location": self.location,
            "notes": self.notes,
            "marker_color": self.marker_color,
            "lat": self.lat,
            "lng": self.lng,
            "photo_filename": self.photo_filename
        }

    def __repr__(self):
        animal_name = self.animal.name if self.animal else "?"
        return f"<Sighting id={self.id} animal='{animal_name}' date_time={self.date_time}>"


# =========================================================
# Harvest Model
# - Stores complete harvest details (weather, weapon, coords, etc.).
# - Mirrored with your HarvestForm and routes in app.py.
# - Indexed columns (animal_id, date_time) help list pages as data grows.
# =========================================================
class Harvest(db.Model):
    __tablename__ = 'harvest'

    id = db.Column(db.Integer, primary_key=True)

    # FK -> Animal; indexed for filters/sorts
    animal_id = db.Column(db.Integer, db.ForeignKey('animal.id'), nullable=False, index=True)  # <<< indexed

    # A human-friendly name you assign to the harvest (required in form)
    harvest_name = db.Column(db.String(100), nullable=False)

    # When the harvest happened; indexed for sort/filter by date
    date_time = db.Column(db.DateTime, nullable=True, index=True)  # <<< indexed

    # Weather bits
    weather = db.Column(db.String(100), nullable=True)
    wind_speed = db.Column(db.String(50), nullable=True)
    wind_direction = db.Column(db.String(50), nullable=True)
    humidity = db.Column(db.String(20), nullable=True)

    # Weapon / caliber / broadhead (+ "other" text fields)
    weapon_type = db.Column(db.String(50), nullable=True)
    other_weapon_type = db.Column(db.String(80), nullable=True)
    caliber = db.Column(db.String(50), nullable=True)
    other_caliber = db.Column(db.String(80), nullable=True)
    broadhead = db.Column(db.String(100), nullable=True)
    other_broadhead = db.Column(db.String(80), nullable=True)

    # Optional free-text location
    location = db.Column(db.String(200), nullable=True)

    # Map points & distance
    shot_lat = db.Column(db.Float, nullable=True)
    shot_lng = db.Column(db.Float, nullable=True)
    recovery_lat = db.Column(db.Float, nullable=True)
    recovery_lng = db.Column(db.Float, nullable=True)
    distance_traveled = db.Column(db.Float, nullable=True)

    # Misc
    notes = db.Column(db.Text, nullable=True)
    photo_filename = db.Column(db.String(120), nullable=True)
    marker_color = db.Column(db.String(20), nullable=True, default="#3388ff")

    def to_dict(self):
        """Convenience method for JSON responses / map rendering."""
        return {
            "id": self.id,
            "animal": self.animal.name if self.animal else None,
            "harvest_name": self.harvest_name,
            "date_time": self.date_time,
            "weather": self.weather,
            "wind_speed": self.wind_speed,
            "wind_direction": self.wind_direction,
            "humidity": self.humidity,
            "weapon_type": self.weapon_type,
            "other_weapon_type": self.other_weapon_type,
            "caliber": self.caliber,
            "other_caliber": self.other_caliber,
            "broadhead": self.broadhead,
            "other_broadhead": self.other_broadhead,
            "location": self.location,
            "shot_lat": self.shot_lat,
            "shot_lng": self.shot_lng,
            "recovery_lat": self.recovery_lat,
            "recovery_lng": self.recovery_lng,
            "distance_traveled": self.distance_traveled,
            "notes": self.notes,
            "photo_filename": self.photo_filename,
            "marker_color": self.marker_color
        }

    def __repr__(self):
        animal_name = self.animal.name if self.animal else "?"
        return f"<Harvest id={self.id} name='{self.harvest_name}' animal='{animal_name}' date_time={self.date_time}>"