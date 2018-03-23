from flask import Flask,jsonify
import json, requests, csv, pprint
import uuid

def CreateJSON(s,e,k):

    """
    1. Get initial user parameters (locations, keywords, etc.)
    """

    input_origin = s
    input_destination = e
    keyword1 = k
    radius = 30
    start_date_time_start = '2018-04-11'
    start_date_time_start = start_date_time_start + 'T18:00:00'
    start_date_time_end = '2018-04-16'
    start_date_time_end = start_date_time_end + 'T23:00:00'

    #APIkeys:
    goog_map_directions_api_key = 'AIzaSyDhlt9FO1gnICtCt-rCKuph8ux4WWFzTE0'
    eventbright_api_key = 'TZCRCUITRNKQZFMSWHZ4'

    """
    2. Get directions via Google Directions API (as JSON)
    """
    origin = 'origin=' + input_origin #forms final string
    destination = '&destination=' + input_destination #forms final string
    GEOCODE_BASE_URL = 'https://maps.googleapis.com/maps/api/directions/json'

    link = GEOCODE_BASE_URL + '?' + origin + destination + '&key=' + goog_map_directions_api_key
    resp = requests.get(link)
    data = resp.json()

    #initialize lats and lngs lists and append with the start location
    list_lats = []
    list_lngs = []
    start_location_lat = data['routes'][0]['legs'][0]['start_location']['lat']
    start_location_lng = data['routes'][0]['legs'][0]['start_location']['lng']
    list_lats.append(start_location_lat)
    list_lngs.append(start_location_lng)

    #get the number of steps in the directions
    dir_steps = int(len(data['routes'][0]['legs'][0]['steps']))
    print("The length of directions steps:", dir_steps)

    #from the JSON parse the coordinates into two lists
    for i in range(0, dir_steps):
        # print('Looping through the GMDirections JSON...')
        try:
            step_lat = data['routes'][0]['legs'][0]['steps'][i]['end_location']['lat']
            step_lng = data['routes'][0]['legs'][0]['steps'][i]['end_location']['lng']
            list_lats.append(step_lat)
            list_lngs.append(step_lng)

        except (RuntimeError, KeyError, TypeError):
            # print("Error. Skipping coordinates: ", i)
            pass

    """
    3. Check latitudes and longitudes for very short and extended driving stretches.
    (To collect events along the route and to reduce the number of API calls.)
    Create a new list of route's lats and lngs spaced at ~<50km (<0.5deg latitude)
    """
    #lists for checking
    #list_lats = [-42.0, -40.4, -38.0, -37.6]
    # list_lngs = [-31.0, -30.4, -28.0, -27.6]

    temp_origin_lat = list_lats[0]
    temp_origin_lng = list_lngs[0]

    list_lats_short = [list_lats[0]]
    list_lngs_short = [list_lngs[0]]

    list_lats_short2 = [list_lats_short[0]]
    list_lngs_short2 = [list_lngs_short[0]]

    within = 0.5

    #Checking for large changes in latitude.
    # print("Checking latitudes:")
    for pos in range(0, len(list_lats)-1):
        abs_diff = abs(list_lats[pos+1] - temp_origin_lat)
        if abs_diff > (2 * within):
            delta_true_lat = list_lats[pos+1] - list_lats[pos]
            delta_true_lng = list_lngs[pos+1] - list_lngs[pos]
            points = int(abs(delta_true_lat) // within)
            if points < 2:
                points = 2
            else: points = points
            adjustment_lat = delta_true_lat/points
            adjustment_lng = delta_true_lng/points
            for i in range(0, points):
                new_lati = list_lats[pos] + adjustment_lat
                new_lngi = list_lngs[pos] + adjustment_lng
                list_lats_short.append(new_lati)
                list_lngs_short.append(new_lngi)
                list_lats[pos] = new_lati
                list_lngs[pos] = new_lngi
            temp_origin_lat = list_lats[pos+1]
            temp_origin_lng = list_lngs[pos+1]
        elif abs_diff > within:
            list_lats_short.append(list_lats[pos+1])
            list_lngs_short.append(list_lngs[pos+1])
        else:
            list_lats_short.append(list_lats[pos+1])
            list_lngs_short.append(list_lngs[pos+1])

    # print("List after updating latitudes: ")
    # for i, k in zip(list_lats_short, list_lngs_short):
    #     print(i, k)

    #Checking longitudes
    # print("Checking longitudes:")
    # print("Length of list_lngs_short is:", len(list_lngs_short))

    temp_origin_lat = list_lats_short[0]
    temp_origin_lng = list_lngs_short[0]
    for pos in range(0, len(list_lngs_short) - 1):
        abs_diff = abs(list_lngs_short[pos+1] - temp_origin_lng)
        if abs_diff > (2 * within):
            delta_true_lat = list_lats_short[pos+1] - list_lats_short[pos]
            delta_true_lng = list_lngs_short[pos+1] - list_lngs_short[pos]
            points = int(abs(delta_true_lng) // within)
            if points < 2:
                points = 2
            else: points = points
            adjustment_lat = delta_true_lat/points
            adjustment_lng = delta_true_lng/points
            for i in range(0, points):
                new_lati = list_lats_short[pos] + adjustment_lat
                new_lngi = list_lngs_short[pos] + adjustment_lng
                list_lats_short2.append(new_lati)
                list_lngs_short2.append(new_lngi)
                list_lats_short[pos] = new_lati
                list_lngs_short[pos] = new_lngi
            temp_origin_lat = list_lats_short[pos+1]
            temp_origin_lng = list_lngs_short[pos+1]

        elif abs_diff > within:
            list_lats_short2.append(list_lats_short[pos+1])
            list_lngs_short2.append(list_lngs_short[pos+1])
        else:
            list_lats_short2.append(list_lats_short[pos+1])
            list_lngs_short2.append(list_lngs_short[pos+1])

    #final cleaning parsing (removal of close coordinates)
    #initialize lists with origin coordinates
    list_lats_short3 = [list_lats_short2[0]]
    list_lngs_short3 = [list_lngs_short2[0]]

    temp_origin_lat = list_lats_short2[0]
    temp_origin_lng = list_lngs_short2[0]

    #making final list cleaning
    for pos in range(1, len(list_lats_short2)):
        abs_diff = abs(list_lats_short2[pos] - temp_origin_lat)
        if abs_diff > (2.0 * within):
            list_lats_short3.append(list_lats_short2[pos])
            list_lngs_short3.append(list_lngs_short2[pos])
            temp_origin_lat = list_lats_short2[pos]
            temp_origin_lng = list_lngs_short2[pos]
        else:
            pass

    #append the final destination
    print(list_lats[-1])
    print(list_lngs[-1])
    list_lats_short3.append(list_lats[-1])
    list_lngs_short3.append(list_lngs[-1])

    #Remove final destination if it is the same as origin
    if (list_lats_short3[0] == list_lats_short3[-1] and
    list_lngs_short3[0] == list_lngs_short3[-1]):
        del list_lats_short3[-1]
        del list_lngs_short3[-1]

    #some checks...
    # print("The initial coord list is: ")
    # for i, k in zip(list_lats, list_lngs):
    #     print(i, k)
    #
    # print("The final coordinates list is: ")
    # for i, k in zip(list_lats_short3, list_lngs_short3):
    #     print(i, k)

    """
    4. Submit the 'cleaned' locations to the Eventbright API.
    """

    coord_list_length = len(list_lats_short3)
    list_of_evbr_api_reqs = []

    #Form a url string with locations, keyword and dates, form a list.
    for lati, longi in zip(list_lats_short3, list_lngs_short3):
        location = \
        '&location.latitude=' + str(lati) + \
        '&location.longitude=' + str(longi) + \
        '&location.within=' + str(radius) + 'km'
        dates = \
        '&start_date.range_start=' + str(start_date_time_start) +\
        '&start_date.range_end=' + str(start_date_time_end)

        link = "https://www.eventbriteapi.com/v3/events/search/?expand=venue&q=" + \
        keyword1 + location + dates
        list_of_evbr_api_reqs.append(str(link))

    print("The number of locations to search for events is: ",
    len(list_of_evbr_api_reqs))

    #initialize lists for filling later
    #insert header for a list and future CSV
    list_venue_details = ["event", "description", "latitude", "longitude", "event_url",
    "start_date_time", "end_date_time", "image_logo", "venue", "address"]
    list_coord = []
    events_with_missing_details = []
    list_of_event_dictionaries = []
    list_of_lists_events = [list_venue_details]

    pp = pprint.PrettyPrinter(indent=2) #sets format for nice printing
    #send an API request to Eventbright for each line in the list of locations.
    for req in list_of_evbr_api_reqs:
        print("The current API request is: \n", req)
        response = requests.get(
            req, #url for Eventbright
            headers = {
                "Authorization": "Bearer " + eventbright_api_key,
            },
            verify = True,  # Verify SSL certificate
        )
        data = response.json() #Eventbright response

        # pp.pprint(data)
        length_events = int(len(data['events']))

        #extract only the info of interest from the Eventbright results
        for event_num in range(0, length_events):
            # print("Going through event: ", event_num + 1)

            try:
                #generate list of lat and long
                longitude = round(float(data['events'][event_num]['venue']['address']['longitude']), 7)
                latitude = round(float(data['events'][event_num]['venue']['address']['latitude']), 7)
                name = data['events'][event_num]['name']['text']
                description_raw = data['events'][event_num]['description']['text']
                if description_raw != '':
                    description = ' '.join(description_raw.split())
                    description = (description[:110] + '..') if len(description) > 110 else description
                else: description = 'No description.'

            except (RuntimeError, TypeError, NameError):
                longitude = latitude = name = description = 'Empty'
                pass
            try:
                start_datetime = data['events'][event_num]['start']['local']
                if start_datetime == '':start_datetime = "No start time info."
            except (RuntimeError, TypeError, NameError):
                start_datetime = 'No info'
                pass

            try:
                end_datetime = data['events'][event_num]['end']['local']
                if end_datetime == '':end_datetime = "No end time info."
            except (RuntimeError, TypeError, NameError):
                start_datetime = 'No info'
                pass

            try:
                end_datetime = data['events'][event_num]['end']['local']
                if end_datetime == '':end_datetime = "No end time info."
            except (RuntimeError, TypeError, NameError):
                end_datetime = 'No info'
                pass

            try:
                event_url = data['events'][event_num]['url']
                if event_url == '': event_url = "No url."
            except (RuntimeError, TypeError, NameError):
                event_url = 'No info'
                pass

            try:
                image_logo = data['events'][event_num]['logo']['url']
                if image_logo == '' : image_logo == 'No image.'
            except (RuntimeError, TypeError, NameError):
                image_logo = 'No logo'
                pass

            try:
                venue_name = data['events'][event_num]['venue']['name']
                if venue_name == '': venue_name == 'No venue name.'
            except (RuntimeError, TypeError, NameError):
                image_logo = 'No logo'
                pass

            try:
                venue_address = data['events'][event_num]['venue']['address']['localized_address_display']
                if venue_address == '': venue_address = 'No venue address.'
            except (RuntimeError, TypeError, NameError):
                venue_address = 'No venue address'
                pass

            #form a list with the event's info, trace how many had missing info
            if longitude != 'Empty':
                list_venue_details = [name, description, latitude, longitude, event_url, start_datetime,
                end_datetime, image_logo, venue_name, venue_address]
            else:
                events_with_missing_details.append(list_venue_details)

            #append the list of event properties to the list of events if no duplicates are present
            if list_venue_details not in list_of_lists_events: list_of_lists_events.append(list_venue_details)

    #check how many events were parsed into the file and how many left out because of missing details
    print("The total number of events found is: ", len(list_of_lists_events) - 1)
    print("The number of events with missing info is: ", len(events_with_missing_details))

    """
    5. Create a JSON file for mapping by Google Maps JavaScript.
    (Use data from the Eventbright list to create a dictionary for
    saving into JSON and for mapping later.)
    """

    for event in range(1, len(list_of_lists_events)): #skips the header (1st row)
        list_coord = [list_of_lists_events[event][2], list_of_lists_events[event][3]]
        #create a subdictionary with the list of coordinates
        # dict_coord = {"type": "Point", "coordinates" : list_coord}

        #create a subdictionary with the event's properties
        # dict_properties = {"name" : list_of_lists_events[event][0], "description" : list_of_lists_events[event][1],  \
        # "start_datetime" : list_of_lists_events[event][5], "end_datetime" : list_of_lists_events[event][6], \
        # "image" : list_of_lists_events[event][7], "url" : list_of_lists_events[event][4], "venue" : list_of_lists_events[event][8], "address" : list_of_lists_events[event][9]}

        #create an event dictionary with all the info
        dict_event = {"icon": "assets/images/geopoint.png", "lat": list_of_lists_events[event][2], "lng": list_of_lists_events[event][3], "infobox": name}
        list_of_events.append(dict_event)

        #create the main dictionary with the info for each event
        # dict_event = {"geometry" : dict_coord, "type": "Feature", "properties" : dict_properties}
        # print('The appended event dictionary is:', dict_event)
        # list_of_event_dictionaries.append(dict_event)

        #Create final dictionary for saving to JSON
        data_json = list_of_events
        return data_json

    #Create the final dictionary with all the events for saving to JSON
    # data_json = {"type" : "FeatureCollection", "features" : list_of_event_dictionaries}

    # pp.pprint(data_json)
    # with open('trip_json_res.json', 'w') as fp: #save to JSON
        # json.dump(data_json, fp, indent = 2)

    # save CSV file (for Google Fusion Tables or else)
    # with open('mytripevents.csv', 'w') as csvfile:
    #     writer = csv.writer(csvfile)
    #     writer.writerows(list_of_lists_events)
