from flask import Flask
from config import Config
from flask_cache import Cache 

app = Flask(__name__)
app.config.from_object(Config)
cache = Cache(app,config={'CACHE_TYPE': 'null'})
cache.init_app(app)

app.config["CACHE_TYPE"] = "null"
app.config['GOOGLEMAPS_KEY'] = "AIzaSyAnugTZi7ReyWzCtaTWyLyhSs9M7VTO4xw"

from app import routes