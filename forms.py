"""
forms.py
- Defines the Flask-WTF form classes used in the application.
- Contains SightingForm and HarvestForm for capturing wildlife sightings and harvest records.
- Each form includes fields, widgets, and validation rules for clean user input.
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SelectField,
    SubmitField,
    FloatField,
    TextAreaField,
    DateTimeLocalField,
    FileField,
    HiddenField,
    DateTimeField
)
from wtforms.validators import DataRequired, Optional, Length
from wtforms.widgets import ColorInput
from flask_wtf.file import FileAllowed

# ----------------------------
# Wildlife Sighting Form
# ----------------------------


ANIMAL_CHOICES = {
    "Big Game": [
        "American Bison", "Black Bear", "Brown Bear", "Caribou", "Cougar",
        "Elk", "Moose", "Mule Deer", "Pronghorn", "Whitetail Deer(Buck)",
        "Whitetail Deer(Doe)", "Wild Boar"
    ],
    "Small Game": [
        "Beaver",
        "Cottontail",
        "Crow",
        "Groundhog",
        "Opossum",
        "Porcupine",
        "Rabbit",
        "Raccoon",
        "Squirrel"
    ],
    "Upland Birds": [
        "Bobwhite Quail",
        "Chukar Partridge",
        "Grouse (Ruffed, Sage, Spruce, Sharp-Tailed)",
        "Hungarian Partridge",
        "Pheasant",
        "Ptarmigan",
        "Turkey",
        "Woodcock"
    ],
    "Waterfowl": [
        "Duck",
        "Mallard",
        "Teal",
        "Wood Duck",
        "Canada Goose",
        "Goose",
        "Brant",
        "Mergansers"
    ],
    "Predators & Other": [
        "Coyote",
        "Fox",
        "Bobcat",
        "Nutria",
        "Other"
    ]
}


# Flattened the dictionary into list of tuples for SelectField
# Converts it to format: [('Deer', 'Deer'), so on


# Complete form with SelectField using flat list
# ------------------------------------------------------------------------
# SIGHTING LOGGING FORM FLASK CLASS ---
# ------------------------------------------------------------------------


class SightingForm(FlaskForm):
    # Add a category field
    animal_category = SelectField(
        'Animal Category',
        choices=[("", "Select category")] + [(k, k) for k in ANIMAL_CHOICES.keys()],
        validators=[DataRequired()]
    )

    # Animal field (will be populated via JavaScript)
    animal = SelectField(
        'Animal',
        choices=[("", "Select an animal first")],
        validators=[DataRequired()]
    )

    # Sightings form class Date/Time info and validation
    date_time = DateTimeLocalField(
        'Date/Time',
        format='%Y-%m-%dT%H:%M',
        validators=[Optional()])

    # Sightings form class weather info and validation
    weather = StringField('Weather', validators=[Optional()])
    wind = StringField('Wind', validators=[Optional()])
    wind_direction = StringField('Wind Direction', validators=[Optional()])
    temperature = StringField('Temperature', validators=[Optional()])

    # Sightings form class wind speed and validation
    wind_speed = SelectField('Wind Speed (mph)', choices=[
        ("", "Select a wind speed"),
        *[(f"{i} mph", f"{i} mph") for i in range(0, 55, 5)],
        ("55+ mph", "55+ mph")
    ], validators=[Optional()])

    # Sightings form class humidity section and validators
    humidity = SelectField('Humidity (%)', choices=[
        ("", "Select humidity"),
        *[(f"{i}%", f"{i}%") for i in range(0, 105, 5)]
    ], validators=[Optional()])

    # Sightings class form validators
    location = StringField('Location', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
    marker_color = StringField('Marker Color', widget=ColorInput(), validators=[Optional()])
    lat = HiddenField('Latitude')
    lng = HiddenField('Longitude')
    photo = FileField(
        'Photo (optional)',
        validators=[
            Optional(),
            FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
        ]
    )
    submit = SubmitField('Submit')


# -----------------------------------------------------------------------
# HARVEST LOGGING FORM FLASK ROUTE
# -----------------------------------------------------------------------


class HarvestForm(FlaskForm):

    # Input for Animal name (required field)
    harvest_name = StringField('Harvest Name', validators=[DataRequired(), Length(max=100)])

    # Animal Input
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

    date_time = DateTimeLocalField(
        'Date/Time',
        format='%Y-%m-%dT%H:%M',
        validators=[Optional()],
        description='Local time when sighting occurred'
    )

    weather = StringField('Weather', validators=[Optional()])

    wind_speed = SelectField('Wind Speed (mph)', choices=[
        ("", "Select a wind speed"),
        *[(f"{i} mph", f"{i} mph") for i in range(0, 55, 5)],
        ("55+ mph", "55+ mph")
    ], validators=[Optional()])

    wind_direction = StringField('Wind Direction', validators=[Optional()])

    humidity = SelectField('Humidity (%)', choices=[
        ("", "Select humidity"),
        *[(f"{i}%", f"{i}%") for i in range(0, 105, 5)]
    ], validators=[Optional()])

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
        render_kw={'placeholder': 'e.g. Rage Hypodermic'}
    )

    shot_lat = HiddenField('Shot Latitude')         # changed to HiddenField for map integration
    shot_lng = HiddenField('Shot Longitude')
    recovery_lat = HiddenField('Recovery Latitude')
    recovery_lng = HiddenField('Recovery Longitude')
    distance_traveled = StringField('Distance Traveled (yards)', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
    photo = FileField('Upload Photo', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'],
    'Images only!')])
    marker_color = StringField('Marker Color', widget=ColorInput(), validators=[Optional()])


