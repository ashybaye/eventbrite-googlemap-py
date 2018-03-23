from flask import render_template, flash, redirect, url_for, request, Flask,jsonify,json
from app import app
from app.forms import LoginForm, PlacesForm
from .createjson import CreateJSON
from flask_googlemaps import GoogleMaps, Map

GoogleMaps(app)

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Amy'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home', user=user, posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form) 

@app.route('/result')
def result():
   return render_template('result.html', title='Submitted route')
    
@app.route('/places', methods=['GET', 'POST'])
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
                style = "height:800px;width:800px;margin:0;",
                lat = placesJSON[0]['lat'],
                lng = placesJSON[0]['lng'],
                markers = placesJSON,
                fit_markers_to_bounds = True
            )
            return render_template('map.html', sndmap=sndmap) 

            
        except Exception as e:
            return error.format_exception(
                e,
                target=self.__class__.__name__.lower(),
                action='PUT')             
        # try:

        #     # Initialize a employee list
        #     employeeList = []

        #     # create a instances for filling up employee list
        #     for i in range(0,2):
        #         empDict = {
        #         'firstName': 'Roy',
        #         'lastName': 'Augustine'}
        #         employeeList.append(empDict)
        
        #     # convert to json data
        #     jsonStr = json.dumps(employeeList)

        # except Exception as e:
        #     return error.format_exception(
        #         e,
        #         target=self.__class__.__name__.lower(),
        #         action='PUT') 

        # return jsonify(Employees=jsonStr) 
        # place_start = request.form.get('place_start')
        # place_end = request.form.get('place_end')
        # interest = request.form.get('interest')

        # return '''<p>The starting point is: {}</p>
        #             <p>The end point is: {}</p>
        #             <p>The keyword is: {}</p>'''.format(place_start, place_end, interest)
    # if form.validate_on_submit():
    #     flash('Start: {}, end: {}, keyword: {}'.format(
    #         form.place_start.data, form.place_end.data, form.interest.data))
    #     return redirect(url_for('result'))
    return render_template('places.html', title='Set up the route', form=form)

@app.route("/map")
def mapview():
    # creating a map in the view
    mymap = Map(
        identifier="view-side",
        lat=37.4419,
        lng=-122.1419,
        markers=[(37.4419, -122.1419)]
    )
    sndmap = Map(
        identifier="sndmap",
        lat=37.4419,
        lng=-122.1419,
        markers=[
          {
             'icon': 'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
             'lat': 37.4419,
             'lng': -122.1419,
             'infobox': "<b>Hello World</b>"
          },
          {
             'icon': 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
             'lat': 37.4300,
             'lng': -122.1400,
             'infobox': "<b>Hello World from other place</b>"
          }
        ]
    )
    return render_template('map.html', sndmap=sndmap)    
    