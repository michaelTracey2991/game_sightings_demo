"""
models.py
- Defines the database schema for the application using SQLAlchemy ORM.
- This file contains the Sighting model for recording wildlife sightings and
  the Harvest model for logging successful harvests.
- Each model maps attributes to columns for persistent storage.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# ----------------------------
# Wildlife Sighting Model
# ----------------------------
class Sighting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    animal = db.Column(db.String(100), nullable=False)
    date_time = db.Column(db.DateTime, nullable=True)
    weather = db.Column(db.String(100), nullable=True)
    wind = db.Column(db.String(100), nullable=True)
    wind_speed = db.Column(db.String(100), nullable=True)
    wind_direction = db.Column(db.String(50), nullable=True)
    humidity = db.Column(db.String(20), nullable=True)
    temperature = db.Column(db.String(20), nullable=True)
    location = db.Column(db.String(200), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    marker_color = db.Column(db.String(20), nullable=True)
    lat = db.Column(db.Float, nullable=True)
    lng = db.Column(db.Float, nullable=True)
    photo_filename = db.Column(db.String(120), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "animal": self.animal,
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

# ----------------------------
# Harvest Log Model
# ----------------------------
class Harvest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    animal = db.Column(db.String(100), nullable=False)
    date_time = db.Column(db.DateTime, nullable=True)
    weapon_type = db.Column(db.String(50), nullable=True)
    caliber = db.Column(db.String(50), nullable=True)
    broadhead = db.Column(db.String(100), nullable=True)
    shot_lat = db.Column(db.Float, nullable=True)
    shot_lng = db.Column(db.Float, nullable=True)
    recovery_lat = db.Column(db.Float, nullable=True)
    recovery_lng = db.Column(db.Float, nullable=True)
    distance_traveled = db.Column(db.Float, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    photo_filename = db.Column(db.String(120), nullable=True)
    marker_color = db.Column(db.String(20), nullable=True, default="#3388ff") # default marker color

    def to_dict(self):
        return {
            "id": self.id,
            "animal": self.animal,
            "date_time": self.date_time,
            "weapon_type": self.weapon_type,
            "caliber": self.caliber,
            "broadhead": self.broadhead,
            "shot_lat": self.shot_lat,
            "shot_lng": self.shot_lng,
            "recovery_lat": self.recovery_lat,
            "recovery_lng": self.recovery_lng,
            "distance_traveled": self.distance_traveled,
            "notes": self.notes,
            "photo_filename": self.photo_filename,
            "marker_color": self.marker_color
        }
