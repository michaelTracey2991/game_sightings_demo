"""
forms.py
- Defines the Flask-WTF form classes used in the application.
- Contains SightingForm and HarvestForm for capturing wildlife sightings and harvest records.
- Each form includes fields, widgets, and validation rules for clean user input.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, DateTimeLocalField, FileField, HiddenField, DateTimeField
from wtforms.validators import DataRequired, Optional
from wtforms.widgets import ColorInput
from flask_wtf.file import FileAllowed

# ----------------------------
# Wildlife Sighting Form
# ----------------------------


class SightingForm(FlaskForm):
    animal = SelectField('Animal', choices=[
        ("", "Select animal"),
        ("American Bison", "American Bison"),
        ("Black Bear", "Black Bear"),
        ("Brown Bear", "Brown Bear"),
        ("Caribou", "Caribou"),
        ("Cougar", "Cougar"),
        ("Elk", "Elk"),
        ("Moose", "Moose"),
        ("Mule Deer", "Mule Deer"),
        ("Pronghorn", "Pronghorn"),
        ("Whitetail Deer(Buck)", "Whitetail Deer(Buck)"),
        ("Whitetail Deer(Doe)", "Whitetail Deer(Doe)"),
        ("Whitetail Deer(Button Buck)", "Whitetail Deer(Button Buck)"),
        ("Wild Boar", "Wild Boar"),
        ("Beaver", "Beaver"),
        ("Cottontail", "Cottontail"),
        ("Crow", "Crow"),
        ("Groundhog", "Groundhog"),
        ("Opossum", "Opossum"),
        ("Porcupine", "Porcupine"),
        ("Rabbit", "Rabbit"),
        ("Raccoon", "Raccoon"),
        ("Squirrel", "Squirrel"),
        ("Bobwhite Quail", "Bobwhite Quail"),
        ("Chukar Partridge", "Chukar Partridge"),
        ("Grouse", "Grouse (Ruffed, Sage, Spruce, Sharp-Tailed)"),
        ("Hungarian Partridge", "Hungarian Partridge"),
        ("Pheasant", "Pheasant"),
        ("Ptarmigan", "Ptarmigan"),
        ("Turkey", "Turkey"),
        ("Woodcock", "Woodcock"),
        ("Duck", "Duck"),
        ("Goose", "Goose"),
        ("Brant", "Brant"),
        ("Mergansers", "Mergansers"),
        ("Coyote", "Coyote"),
        ("Fox", "Fox"),
        ("Bobcat", "Bobcat"),
        ("Nutria", "Nutria")
    ], validators=[DataRequired()])

    date_time = DateTimeLocalField('Date/Time', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    weather = StringField('Weather', validators=[Optional()])
    wind = StringField('Wind', validators=[Optional()])
    wind_direction = StringField('Wind Direction', validators=[Optional()])
    temperature = StringField('Temperature', validators=[Optional()])

    wind_speed = SelectField('Wind Speed (mph)', choices=[
        ("", "Select a wind speed"),
        *[(f"{i} mph", f"{i} mph") for i in range(0, 55, 5)],
        ("55+ mph", "55+ mph")
    ], validators=[Optional()])

    humidity = SelectField('Humidity (%)', choices=[
        ("", "Select humidity"),
        *[(f"{i}%", f"{i}%") for i in range(0, 105, 5)]
    ], validators=[Optional()])

    location = StringField('Location', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
    marker_color = StringField('Marker Color', widget=ColorInput(), validators=[Optional()])
    lat = HiddenField('Latitude')
    lng = HiddenField('Longitude')
    photo = FileField('Photo (optional)', validators=[Optional()])

# ----------------------------
# Harvest Logging Form
# ----------------------------


class HarvestForm(FlaskForm):
    animal = SelectField('Animal', choices=[
        ("", "Select animal"),
        ("American Bison", "American Bison"),
        ("Black Bear", "Black Bear"),
        ("Brown Bear", "Brown Bear"),
        ("Caribou", "Caribou"),
        ("Cougar", "Cougar"),
        ("Elk", "Elk"),
        ("Moose", "Moose"),
        ("Mule Deer", "Mule Deer"),
        ("Pronghorn", "Pronghorn"),
        ("Whitetail Deer(Buck)", "Whitetail Deer(Buck)"),
        ("Whitetail Deer(Doe)", "Whitetail Deer(Doe)"),
        ("Whitetail Deer(Button Buck)", "Whitetail Deer(Button Buck)"),
        ("Wild Boar", "Wild Boar"),
        ("Beaver", "Beaver"),
        ("Cottontail", "Cottontail"),
        ("Crow", "Crow"),
        ("Groundhog", "Groundhog"),
        ("Opossum", "Opossum"),
        ("Porcupine", "Porcupine"),
        ("Rabbit", "Rabbit"),
        ("Raccoon", "Raccoon"),
        ("Squirrel", "Squirrel"),
        ("Bobwhite Quail", "Bobwhite Quail"),
        ("Chukar Partridge", "Chukar Partridge"),
        ("Grouse", "Grouse (Ruffed, Sage, Spruce, Sharp-Tailed)"),
        ("Hungarian Partridge", "Hungarian Partridge"),
        ("Pheasant", "Pheasant"),
        ("Ptarmigan", "Ptarmigan"),
        ("Turkey", "Turkey"),
        ("Woodcock", "Woodcock"),
        ("Duck", "Duck"),
        ("Goose", "Goose"),
        ("Brant", "Brant"),
        ("Mergansers", "Mergansers"),
        ("Coyote", "Coyote"),
        ("Fox", "Fox"),
        ("Bobcat", "Bobcat"),
        ("Nutria", "Nutria"),
        ("Other", "Other")
    ], validators=[DataRequired()])

    date_time = DateTimeLocalField('Date/Time', format='%Y-%m-%dT%H:%M', validators=[Optional()])

    weapon_type = SelectField('Weapon Type', choices=[
        ('', 'Select weapon type'),
        ('Recurve Bow', 'Recurve Bow'),
        ('Longbow', 'Longbow'),
        ('Compound Bow', 'Compound Bow'),
        ('Crossbow', 'Crossbow'),
        ('Shotgun', 'Shotgun'),
        ('Rifle', 'Rifle'),
        ('Muzzleloader', 'Muzzleloader'),
        ('Other', 'Other')
    ], validators=[Optional()])

    other_weapon_type = StringField(
        'If "Other", specify weapon type',
        validators=[Optional()],
        render_kw={"placeholder": "e.g. Slingbow"}
    )

    caliber = SelectField('Caliber / Gauge', choices=[
        ("", "Select caliber or Gauge"),
        ("12ga", "12 Gauge"),
        ("20ga", "20 Gauge"),
        ("28ga", "28 Gauge"),
        (".223", ".223 Remington"),
        (".243", ".243 Winchester"),
        (".270", ".270 Winchester"),
        (".30-06", ".30-06 Springfield"),
        (".308", ".308 Winchester"),
        ("Other", "Other")
    ], validators=[Optional()])

    other_caliber = StringField(
        'If "Other", specifically caliber',
        validators=[Optional()],
        render_kw={"placeholder": "e.g. .450 Bushmaster"}
    )

    broadhead = SelectField('Broadhead Type', choices=[
        ('', 'Select broadhead type'),
        ('Fixed Blade', 'Fixed Blade'),
        ('Mechanical', 'Mechanical'),
        ('Hybrid', 'Hybrid'),
        ('Other', 'Other')
        ], validators=[Optional()])

    other_broadhead = StringField(
        'If "Other", specify broadhead',
        validators=[Optional()],
        render_kw={"placeholder": "e.g. Rage Hypodermic"}
    )

    shot_lat = HiddenField('Shot Latitude')         # changed to HiddenField for map integration
    shot_lng = HiddenField('Shot Longitude')
    recovery_lat = HiddenField('Recovery Latitude')
    recovery_lng = HiddenField('Recovery Longitude')
    distance_traveled = StringField('Distance Traveled (yards)', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
    photo = FileField('Upload Photo', validators=[Optional()])
    marker_color = StringField('Marker Color', widget=ColorInput(), validators=[Optional()])


