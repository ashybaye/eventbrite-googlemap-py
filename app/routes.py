from flask import render_template, flash, redirect, url_for, request, Flask,jsonify,json
from app import app
from app.forms import PlacesForm
from .createjson import CreateJSON
from flask_googlemaps import GoogleMaps, Map

GoogleMaps(app)

@app.route('/')
@app.route('/index')
def index():
    return redirect(url_for('places'))

@app.route('/map', methods=['GET', 'POST'])
def places():
    form = PlacesForm()
    if request.method == 'POST' and form.validate_on_submit():
        try:
            place_start = request.form.get('place_start')
            place_end = request.form.get('place_end')
            interest = request.form.get('interest')
            dt_start = request.form.get('dt_start')
            dt_end = request.form.get('dt_end')

            placesJSON = CreateJSON(place_start,place_end,interest,dt_start,dt_end)
            # return placesJSON

            if placesJSON == None: 
                defaultmap = Map(
                    identifier="view-side",
                    style = "height:100%;width:100%;margin:0;",
                    lat = 40.0,
                    lng = -95.0,
                    zoom = 4
                )
                message = "No events. Please change the search parameters."
                return render_template('map.html', title='Set up the route', form=form, defaultmap=defaultmap, message = message) 
            else:
                sndmap = Map(
                    identifier = "sndmap",
                    style = "height:100%;width:100%;margin:0;",
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
    else:
        defaultmap = Map(
            identifier="view-side",
            style = "height:90%;width:auto;margin:0;",
            lat = 40.0,
            lng = -95.0,
            zoom = 4
        )
        return render_template('map.html', title='Set up the route', form=form, defaultmap=defaultmap)                   
    return render_template('map.html', title='Set up the route', form=form)
