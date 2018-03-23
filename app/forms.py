from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class PlacesForm(FlaskForm):
    place_start = StringField('Start', validators=[DataRequired()])
    place_end = StringField('End', validators=[DataRequired()])
    interest = StringField('Keyword', validators=[DataRequired()])
    submit = SubmitField('Get events')    