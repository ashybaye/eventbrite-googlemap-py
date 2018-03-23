from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

app.config['GOOGLEMAPS_KEY'] = "AIzaSyAnugTZi7ReyWzCtaTWyLyhSs9M7VTO4xw"

from app import routes