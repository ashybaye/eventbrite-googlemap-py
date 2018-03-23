from flask import render_template, flash, redirect, url_for, request, Flask,jsonify,json
from app import app
from app.forms import PlacesForm
from .createjson import CreateJSON
from flask_googlemaps import GoogleMaps, Map

GoogleMaps(app)

@app.route('/')
@app.route('/index')
def index():
    return render_template('map.html', title='Home')
    
@app.route('/map', methods=['GET', 'POST'])
def places():
    form = PlacesForm()
    if request.method == 'POST': 
        try:
            place_start = request.form.get('place_start')
            place_end = request.form.get('place_end')
            interest = request.form.get('interest')
            dt_start = request.form.get('dt_start')
            dt_end = request.form.get('dt_end')            

            placesJSON = CreateJSON(place_start,place_end,interest,dt_start,dt_end)
            # return placesJSON
            sndmap = Map(
                identifier = "sndmap",
                style = "height:80%;width:auto;margin:0;",
                lat = placesJSON[0]['lat'],
                lng = placesJSON[0]['lng'],
                markers = placesJSON,
                fit_markers_to_bounds = True
            )
            return render_template('map.html', title='Set up the route', form=form , sndmap=sndmap) 

            
        except Exception as e:
            return error.format_exception(
                e,
                target=self.__class__.__name__.lower(),
                action='PUT')             
    return render_template('map.html', title='Set up the route', form=form) 
    