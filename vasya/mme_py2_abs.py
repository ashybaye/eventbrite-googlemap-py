import json, requests, csv, pprint
import uuid
from itertools import izip
from io import open
# from __future__ import with_statement
# from __future__ import division
# from __future__ import absolute_import

u"""
1. Get initial user parameters (locations, keywords, etc.)
"""



input_origin = u'Raleigh,NC'
input_destination = u'Nashville,TN'
keyword1 = u'music'
radius = 30
start_date_time_start = u'2018-03-11'
start_date_time_start = start_date_time_start + u'T18:00:00'
start_date_time_end = u'2018-03-16'
start_date_time_end = start_date_time_end + u'T23:00:00'

via1 = u'|via:Carolina+Beach,NC'
# via1
# via2 = 'Charlotte,NC'
# via3 = 'Asheville,NC'

# print("Enter the 'Start' location (city,state/address) with no spaces:")
# input_origin = input("Start: ")
# print("Enter your 'Destination' location (city,state/address) with no spaces:")
# input_destination = input("Destination: ")
# print("Enter the event topic you are searching for (music, dance, etc.): ")
# keyword1 = input("Keyword 1: ")

# # print("Enter the 2nd event topic you are searching for (music, dance, etc.): ")
# # keyword2 = input("Keyword 2: ")
# # print("Enter the 3rd event topic you are searching for (music, dance, etc.): ")
# # keyword3 = input("Keyword 3: ")
# print("Enter the distance from your route to search (kilometers): ")
# radius = input("Radius (km): ")

# print("Enter the Start date of your trip 'YYYY-MM-DD' (2018-01-31): ")
# start_date_time = input("Start date: ")

# print("Enter the End date of your trip 'YYYY-MM-DD' (2018-01-31): ")
# end_date_time = input("End date: ")
# Iowa+City,IA
# Dayton,OH

# Raleigh,NC

# Nashville,TN

# Iowa+City,IA
u"""
2. Get directions via Google Directions API
"""
origin = u'origin=' + input_origin
destination = u'&destination=' + input_destination

GEOCODE_BASE_URL = u'https://maps.googleapis.com/maps/api/directions/json'
goog_map_directions_api_key = u'AIzaSyDhlt9FO1gnICtCt-rCKuph8ux4WWFzTE0'
#form url for submission through Google Directions API, get results as JSON
link = GEOCODE_BASE_URL + u'?' + origin + destination + u'&key=' + goog_map_directions_api_key
# link = 'https://maps.googleapis.com/maps/api/directions/json?origin=Chicago,IL&destination=Cleveland,OH&key=AIzaSyDhlt9FO1gnICtCt-rCKuph8ux4WWFzTE0'
# print('link')
#For directions with via points
#https://maps.googleapis.com/maps/api/directions/json?origin=Boston,MA&destination=Concord,MA&waypoints=Charlestown,MA|via:Lexington,MA&key=YOUR_API_KEY


resp = requests.get(link)
data = resp.json()

#initialize lats and lngs lists and append with start location
list_lats = []
list_lngs = []
start_location_lat = data[u'routes'][0][u'legs'][0][u'start_location'][u'lat']
start_location_lng = data[u'routes'][0][u'legs'][0][u'start_location'][u'lng']
list_lats.append(start_location_lat)
list_lngs.append(start_location_lng)

length = int(len(data[u'routes'][0][u'legs'][0][u'steps']))
print u"The length of steps in JSON is:", length
#generate a list of directions as lats and lngs
for i in range(0, length):
    # print('Looping through the GMDirections JSON...')
    try:
        step_lat = data[u'routes'][0][u'legs'][0][u'steps'][i][u'end_location'][u'lat']
        step_lng = data[u'routes'][0][u'legs'][0][u'steps'][i][u'end_location'][u'lng']
        list_lats.append(step_lat)
        list_lngs.append(step_lng)

    except (RuntimeError, KeyError, TypeError):
        print u"Error."
        pass

# print(list_lats)
# print(list_lngs)
# print("The lats/lngs of GM Dir are: ")
# for i, k in zip(list_lats, list_lngs):
#     print(i, k)
# return list_lats, list_lngs

u"""
3. Go through latitudes.
Create new list of route's lats and lngs spaced at ~55km (0.5deg latitude)
it is different for longitude, for now we'll forget it
"""

u"""
# 4. Go through longitudes.
"""

temp_origin_lat = list_lats[0]
temp_origin_lng = list_lngs[0]

list_lats_short = [list_lats[0]]
list_lngs_short = [list_lngs[0]]

list_lats_short2 = [list_lats_short[0]]
list_lngs_short2 = [list_lngs_short[0]]

#Checking for large changes in longitude

within = 0.5

print u"Checking latitudes:"
for pos in range(0, len(list_lats)-1):
    abs_diff = abs(list_lats[pos+1] - temp_origin_lat)
    # print("Going through pos: ", pos)
    # print("Current list_lats value is: ", list_lats[pos])
    # print("Current list_lats[pos+1] value is: ", list_lats[pos + 1])
    # print("Abs diff is: ", abs_diff)
    if abs_diff > (2 * within):
        # print("In lat loop.")
        delta_true_lat = list_lats[pos+1] - list_lats[pos]
        # print("Delta true lat is: ", delta_true_lat)
        delta_true_lng = list_lngs[pos+1] - list_lngs[pos]
        # print("Delta true lng is: ", delta_true_lng)
        points = int(abs(delta_true_lat) // within)
        # print("Points is:", points)
        adjustment_lat = delta_true_lat/points
        # print("Adjustment lat is: ", adjustment_lat)
        adjustment_lng = delta_true_lng/points
        # print("Adjustment lng is: ", adjustment_lat)
        for i in range(0, points):
            new_lati = list_lats[pos] + adjustment_lat
            new_lngi = list_lngs[pos] + adjustment_lng
            list_lats_short.append(new_lati)
            list_lngs_short.append(new_lngs)
            adjustment_lat += adjustment_lat
            adjustment_lng += adjustment_lng
    elif abs_diff > within:
        # print("elif lat loop.")
        list_lats_short.append(list_lats[pos+1])
        list_lngs_short.append(list_lngs[pos+1])
    else:
        # print("Else lat loop.")
        list_lats_short.append(list_lats[pos+1])
        list_lngs_short.append(list_lngs[pos+1])
        # print("Appending list_lats[pos+1] equal to:", list_lats[pos+1])
        # print("Appending list_lngs[pos+1] equal to:", list_lngs[pos+1])

print u"List after updating latitudes: "
for i, k in izip(list_lats_short, list_lngs_short):
    print i, k
#Checking for large changes in longitude

print u"Checking longitudes:"
print u"Length of list_lngs_short is:", len(list_lngs_short)

# print("Temp_origin_lng before longitude loop is:", temp_origin_lng)
temp_origin_lat = list_lats_short[0]
temp_origin_lng = list_lngs_short[0]
# print("Temp_origin_lng after re-initiating with list_lngs_short[0]:", temp_origin_lng)
for pos in range(0, len(list_lngs_short) - 1):
    # print("Temp_origin_lng is:", temp_origin_lng)
    abs_diff = abs(list_lngs_short[pos+1] - temp_origin_lng)
    # print("Going through pos: ", pos)
    # print("Current list_lngs value is: ", list_lngs_short[pos])
    # print("Current list_lngs[pos+1] value is: ", list_lngs_short[pos + 1])
    # print("Temp_origin_lng is:", temp_origin_lng)
    # print("Abs diff is: ", abs_diff)
    if abs_diff > (2 * within):
        # print("In lng loop.")
        delta_true_lat = list_lats_short[pos+1] - list_lats_short[pos]
        # print("Delta true lat is: ", delta_true_lat)
        delta_true_lng = list_lngs_short[pos+1] - list_lngs_short[pos]
        # print("Delta true lng is: ", delta_true_lng)
        points = int(abs(delta_true_lng) // within)
        if points < 2:
            points = 2
        else: points = points
        # print("Points is:", points)
        adjustment_lat = delta_true_lat/points
        # print("Adjustment lat is: ", adjustment_lat)
        adjustment_lng = delta_true_lng/points
        # print("Adjustment lng is: ", adjustment_lng)
        for i in range(0, points):
            new_lati = list_lats_short[pos] + adjustment_lat
            new_lngi = list_lngs_short[pos] + adjustment_lng
            list_lats_short2.append(new_lati)
            list_lngs_short2.append(new_lngi)
            list_lats_short[pos] = new_lati
            list_lngs_short[pos] = new_lngi
        temp_origin_lat = list_lats_short[pos+1]
        temp_origin_lng = list_lngs_short[pos+1]

    elif abs_diff > within and abs_diff < within * 2:
        # print("elif lng loop.")
        list_lats_short2.append(list_lats_short[pos+1])
        # print("Appended list_lats_short[pos+1] is: ", list_lats_short[pos+1])
        list_lngs_short2.append(list_lngs_short[pos+1])
        # print("Appended list_lngs_short[pos+1] is: ", list_lngs_short[pos+1])
    else:
        # print("Else lng loop.")
        pass

#list of coord for Eventbright submission, append end_distination
list_lats_short2.append(list_lats_short[len(list_lats_short) - 1])
list_lngs_short2.append(list_lngs_short[len(list_lngs_short) - 1])

print u"The lats/lngs in cleaned coordinates are: "
for i, k in izip(list_lats_short2, list_lngs_short2):
    print i, k

u"""
5.Submit updated lats/lngs to Eventbright API. Write CSV with events.
"""
coord_list_length = len(list_lats_short2)

#open CSV file for writing
# unique_filename = str(uuid.uuid4())

#works (remove key for batch request)
# https://www.eventbriteapi.com/v3/events/search/?token=TZCRCUITRNKQZFMSWHZ4&expand=venue&q=music&location.latitude=35.78&location.longitude=-78.64&location.within=30km&start_date.range_start=2018-03-10T00:00:00&start_date.range_end=2018-03-12T00:00:00


# n = 0
# with open('api_reqs_sent_to_EvBr2.csv', 'a', newline='') as evbr_links:
#     writer = csv.writer(evbr_links)
#     writer.writerows(link)
#     n += 1
#     print("Writing api reqs to a file", n)




u"""
Getting data from Eventbright and saving JSON and CSV
"""


list_of_evbr_api_reqs = []
for lati, longi in izip(list_lats_short2, list_lngs_short2):
    location = \
    u'&location.latitude=' + unicode(lati) + \
    u'&location.longitude=' + unicode(longi) + \
    u'&location.within=' + unicode(radius) + u'km'
    dates = \
    u'&start_date.range_start=' + unicode(start_date_time_start) +\
    u'&start_date.range_end=' + unicode(start_date_time_end)

    link = u"https://www.eventbriteapi.com/v3/events/search/?expand=venue&q=" + \
    keyword1 + location + dates
    list_of_evbr_api_reqs.append(unicode(link))

print u"Length of EvBr links list (locations) is: ", len(list_of_evbr_api_reqs)

list_venue_details = [u"event", u"description", u"latitude", u"longitude", u"event_url", u"start_date_time", u"end_date_time", u"image_logo", u"venue", u"address"]
list_coord = []
list_of_events = []
list_of_lists_events = [list_venue_details]

for req in  list_of_evbr_api_reqs:
    print u"Printing EvBr links from list: ", req

    response = requests.get(
        # "https://www.eventbriteapi.com/v3/users/me/owned_events/", #original call
        req,
        headers = {
            u"Authorization": u"Bearer TZCRCUITRNKQZFMSWHZ4", #my Eventbright key
        },
        verify = True,  # Verify SSL certificate
    )
    data = response.json()

    #Event details in JSON/Python JSON object
    length = int(len(data[u'events']))
    print u"The number of events for current location: ", length

    for event_num in range(0, length):
        print u"The current event_num is: ", event_num
        try:
            #generate list of lat and long
            longitude = data[u'events'][event_num][u'venue'][u'address'][u'longitude']
            latitude = data[u'events'][event_num][u'venue'][u'address'][u'latitude']
            name = data[u'events'][event_num][u'name'][u'text']
        #
        # except (RuntimeError, TypeError, NameError):
        #     print("Lat/lng info is incomplete in event_num ", event_num)
        #     pass

        # try:
            description_raw = unicode(data[u'events'][event_num][u'description'][u'text'])
            if description_raw != u'':
                description = u' '.join(description_raw.split())
                description = (description[:100] + u'..') if len(description) > 100 else description
            else: description = u'No description.'

            start_datetime = data[u'events'][event_num][u'start'][u'local']
            if start_datetime == u'':
                start_datetime = u"No start time info."
            end_datetime = data[u'events'][event_num][u'end'][u'local']
            if end_datetime == u'':
                end_datetime = u"No end time info."
            event_url = data[u'events'][event_num][u'url']
            if event_url == u'':
                event_url = u"No url."
            image_logo = data[u'events'][event_num][u'logo'][u'url']
            if image_logo == u'':
                image_logo == u'No image.'
            venue_name = data[u'events'][event_num][u'venue'][u'name']
            if venue_name == u'':
                venue_name == u'No venue name.'
            venue_address = data[u'events'][event_num][u'venue'][u'address'][u'localized_address_display']
            if venue_address ==u'':
                venue_address = u'No address.'
        except (RuntimeError, TypeError, NameError):
            print u"Error.", event_num
            pass

        list_venue_details = [name, description, latitude, longitude, event_url, start_datetime, \
        end_datetime, image_logo, venue_name, venue_address]
        print u"Venue details: ", list_venue_details
        if list_venue_details not in list_of_lists_events: list_of_lists_events.append(list_venue_details)
            # print("The event descripton is: ", description)
            # print("The length of list_venue_details is: ", len(list_venue_details))

        u"""
        Make a JSON for mapping
        """
        list_coord = [longitude, latitude]
# list_venue_details = ["event", "description", "latitude", "longitude", "event_url", "start_date_time", "end_date_time", "image_logo", "venue", "address"]
        #create a dictionaries with event data
        dict_coord = {u"type": u"Point", u"coordinates" : list_coord}

        dict_properties ={u"event" : name, u"description" : description,  \
        u"start_datetime" : start_datetime, u"end_datetime" : end_datetime, \
        u"image" : image_logo, u"url" : event_url, u"venue" : venue_name, u"address" : venue_address}

        #create an event dictionary with all the info
        dict_event = {u"geometry" : dict_coord, u"properties" : dict_properties}
        list_of_events.append(dict_event)
    #Create final dictionary for saving to JSON
data_json = {u"type" : u"FeatureCollection", u"features" : list_of_events}
print u"Printing resulting JSON structure"
print data_json
with open(u'trip_json_res.json', u'w', encoding = 'utf-8') as fp:
    # json.dumps(data_json, fp, indent = 2)
    my_json_str = json.dumps(data_json, ensure_ascii = False, indent = 2)
    if isinstance(my_json_str, str):
        my_json_str = my_json_str.decode('utf-8')
    fp.write(my_json_str)
#
# print u"The length of list_of_lists_events is: ", len(list_of_lists_events)
# with open(u'mytripevents.csv', u'w', newline=u'') as csvfile:
#     writer = csv.writer(csvfile)
#     writer.writerows(list_of_lists_events)

# mode = 'w'
# if sys.version_info.major < 3:
#     mode += 'b'
# csvfile_ = open(input_origin + input_destination + "_events.csv", mode, newline='')
