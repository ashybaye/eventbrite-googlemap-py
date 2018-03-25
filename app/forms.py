from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class PlacesForm(FlaskForm):
    place_start = StringField('Start (ex: Chicago)', validators=[DataRequired()])
    place_end = StringField('End (ex: Grand Rapids)', validators=[DataRequired()])
    interest = StringField('Keyword (ex: music)', validators=[DataRequired()])
    dt_start = StringField('Start Date (yyyy-mm-dd)', validators=[DataRequired()])
    dt_end = StringField('End Date (yyyy-mm-dd)', validators=[DataRequired()])    
    submit = SubmitField('Get events')    