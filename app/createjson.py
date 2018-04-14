from flask import Flask,jsonify
import json, requests, csv, pprint
import uuid
import sys

def CreateJSON(s,e,k,dt_start,dt_end):

    """
    1. Get initial user parameters (locations, keywords, etc.)
    """

    input_origin = s
    print("Origin_Destination {}, {}: ".format (s, e) )
    input_destination = e
    keyword1 = k
    radius = 30
    start_date_time_start = dt_start
    start_date_time_start = start_date_time_start + 'T18:00:00'
    start_date_time_end = dt_end
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
            points = int(abs(delta_true_lat) // within) + 1
            if points < 2:
                points = 2
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

        else:
            list_lats_short.append(list_lats[pos+1])
            list_lngs_short.append(list_lngs[pos+1])

    # print("List after updating latitudes: ")
    # for i, k in zip(list_lats_short, list_lngs_short):
    #     print(i, k)

    # Checking longitudes
    print("Checking longitudes:")
    print("Length of list_lngs_short is:", len(list_lngs_short))

    temp_origin_lat = list_lats_short[0]
    temp_origin_lng = list_lngs_short[0]
    for pos in range(0, len(list_lngs_short) - 1):
        abs_diff = abs(list_lngs_short[pos+1] - temp_origin_lng)
        if abs_diff > (2 * within):
            delta_true_lat = list_lats_short[pos+1] - list_lats_short[pos]
            delta_true_lng = list_lngs_short[pos+1] - list_lngs_short[pos]
            points = int(abs(delta_true_lng) // within) + 1
            if points < 2:
                points = 2
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
        abs_diff_lat = abs(list_lats_short2[pos] - temp_origin_lat)
        abs_diff_lng = abs(list_lngs_short2[pos] - temp_origin_lng)
        # print("Abs dif in round 3 is: ", abs_diff)
        # print("temp_origin_lat is: ", temp_origin_lat)
        if abs_diff_lat > 1.2 * within or abs_diff_lng > 1.2 * within:
            # print("In 2within round3 loop...")
            list_lats_short3.append(round(list_lats_short2[pos], 7))
            list_lngs_short3.append(round(list_lngs_short2[pos], 7))
            temp_origin_lat = list_lats_short2[pos]
            temp_origin_lng = list_lngs_short2[pos]

    # print("The list after longitudes: ")
    # for i, k in zip(list_lats_short2, list_lngs_short2):
    #     print(i, k)

    #append the final destination
    # print(list_lats[-1])
    # print(list_lngs[-1])
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

    # print("The final coordinates list is: ")
    # for i, k in zip(list_lats_short3, list_lngs_short3):
    #     print(i, k)

    print("The length of final coordinate list is: ", len(list_lats_short3))

    if len(list_lats_short3) > 60:
        print("The final list of coordinates is too long. Please select shorter route.\
        Mapping events for the destination only.")
        list_lats_short3 = list_lats_short3[-2:-1]
        list_lngs_short3 = list_lngs_short3[-2:-1]
    """
    4. Submit the 'cleaned' locations to the Eventbright API.
    """

    # coord_list_length = len(list_lats_short3)
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
            except (RuntimeError, TypeError, NameError):
                longitude = latitude = 'Empty'
                pass

            try:
                name = data['events'][event_num]['name']['text']
                if name != None:
                    name = ' '.join(name.split())
                    name = ((name[:42] + '..') if len(name) > 44 else name)
            except (RuntimeError, TypeError, NameError):
                name = 'Empty'
                pass

            try:
                description_raw = data['events'][event_num]['description']['text']
                if description_raw != None:
                    description = ' '.join(description_raw.split())
                    description = ((description[:110] + '..') if len(description) > 110 else description)
                else:
                    description = 'No description_n'
            except (RuntimeError, TypeError, NameError):
                description = 'No description_e'
                pass

            try:
                start_datetime = data['events'][event_num]['start']['local']
                if start_datetime != None:
                    start_datetime = ' '.join(start_datetime.split('T'))
                else:
                    start_datetime = ''
            except (RuntimeError, TypeError, NameError):
                start_datetime = 'strdt_e'
                pass

            try:
                end_datetime = data['events'][event_num]['end']['local']
                if end_datetime != None:
                    end_datetime = ' '.join(end_datetime.split('T'))
                else:
                    start_datetime = ''
            except (RuntimeError, TypeError, NameError):
                end_datetime = 'enddt_e'
                pass

            try:
                event_url = data['events'][event_num]['url']
                if  event_url == None:
                    event_url = ''
            except (RuntimeError, TypeError, NameError):
                event_url = ''
                pass

            try:
                image_logo = data['events'][event_num]['logo']['url']
                if  image_logo == None:
                    image_logo = ''
            except (RuntimeError, TypeError, NameError):
                image_logo = ''
                pass

            try:
                # venue_name = ''
                venue_name = data['events'][event_num]['venue']['name']
                if venue_name == None:
                    venue_name = 'No venue name_n'
            except (RuntimeError, TypeError, NameError):
                venue_name = 'No venue name_e'
                pass

            try:
                venue_address2 = data['events'][event_num]['venue']['address']['localized_address_display']
                if venue_address2 == None:
                    venue_address2 = 'No venue address_n'
                    # print("The venue address: ", venue_address2)
            except (RuntimeError, TypeError, NameError):
                print("Error: ", sys.exc_info()[0])
                venue_address2 = 'No venue address_e.'
                pass

            #form a list with the event's info, trace how many had missing info
            if name != 'Empty':
                list_venue_details = [name, description, latitude, longitude, event_url, start_datetime,
                end_datetime, image_logo, venue_name, venue_address2]
            else:
                events_with_missing_details.append(list_venue_details)

            #append the list of event properties to the list of events if no duplicates are present
            if list_venue_details not in list_of_lists_events: list_of_lists_events.append(list_venue_details)

    # with open('evbright_results.json', 'w') as fp1: #save to JSON
    #     json.dump(data, fp1, indent = 2)

    #check how many events were parsed into the file and how many left out because of missing details
    print("The total number of events found is: ", len(list_of_lists_events) - 1)
    print("The number of events with missing info is: ", len(events_with_missing_details))

    #set limit to prevent slow response
    if len(list_of_lists_events) > 200:
        print("The number of events exceeds top limit (200). Please change your search parameters. \
        The first 200 events are mapped.")
        list_of_lists_events = list_of_lists_events[1:200]
    elif len(list_of_lists_events) == 1:
        print("No events found.")
        return None    

    """
    5. Create a JSON file for mapping by Google Maps JavaScript.
    (Use data from the Eventbright list to create a dictionary for
    saving into JSON and for mapping later.)
    """

    for event in range(1, len(list_of_lists_events)): #skips the header (1st row)
        list_coord = [list_of_lists_events[event][2], list_of_lists_events[event][3]]

        #create an event dictionary with all the info
        # add image
        infobox = '<div id="content">' + '<img src="' + list_of_lists_events[event][7] + '"/>'
        # add title
        infobox += '<h5>' + list_of_lists_events[event][0] + '</h5>'
        # add date/time
        infobox += '<div id="bodyContent">' + '<p><strong>' + 'Date: '+ list_of_lists_events[event][5] + ' - ' + list_of_lists_events[event][6] + '</strong><br/><br/>'
        # add description and URL
        infobox += list_of_lists_events[event][1] + '<a href="' + list_of_lists_events[event][4] + '">More...</a>' + '<br/><br/>'
        # add venue name
        infobox += 'Venue: ' + list_of_lists_events[event][8]  + '<br/>'
        # add address
        infobox += list_of_lists_events[event][9] + '<br/><br/>'
        # add closing tags
        infobox += '</p></div></div>'

        dict_event = {"icon": "http://maps.google.com/mapfiles/ms/icons/green-dot.png", "lat": list_of_lists_events[event][2], "lng": list_of_lists_events[event][3], "infobox": infobox}
        list_of_event_dictionaries.append(dict_event)

    data_json = list_of_event_dictionaries

    # pp.pprint(data_json)
    ##save to JSON for mapping
    # with open('trip_json_res.json', 'w') as fp:
    #     json.dump(data_json, fp, indent = 2)

    # save CSV file (for Google Fusion Tables or else)
    # with open('mytripevents.csv', 'w') as csvfile:
    #     writer = csv.writer(csvfile)
    #     writer.writerows(list_of_lists_events)
    return data_json
