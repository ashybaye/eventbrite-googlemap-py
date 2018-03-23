from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class PlacesForm(FlaskForm):
    place_start = StringField('Start', validators=[DataRequired()])
    place_end = StringField('End', validators=[DataRequired()])
    interest = StringField('Keyword', validators=[DataRequired()])
    dt_start = StringField('Start Date', validators=[DataRequired()])
    dt_end = StringField('End Date', validators=[DataRequired()])    
    submit = SubmitField('Get events')    