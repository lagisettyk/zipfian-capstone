from flask import Flask, render_template, redirect, url_for, jsonify
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map
import backend as service
from flask import request

app = Flask(__name__, template_folder="templates")

# you can set key as config
app.config['GOOGLEMAPS_KEY'] = "AIzaSyBTT8YSKGtJV9ZVcoVEqHUJuLCLPqXXAto"

# Initialize the extension
GoogleMaps(app)

latitude = None
longitude = None
userid = None

#### load global data....
service.load_data()

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/venues")
def venues():
    if latitude == None:
        venues = service.venue_density()
    else:
        venues = service.venue_density(latitude=latitude, longitude=longitude)
    icons = ['http://maps.google.com/mapfiles/ms/icons/red-dot.png']
    markers = []
    rec_len = len(venues) if len(venues) <= 5000 else 5000
    for index in xrange(rec_len):
        marker = {'icon': icons[0],
                'lat': venues['latitude'].values[index],
                'lng': venues['longitude'].values[index],
                'infobox': "<b>"+venues['Venue_name'].values[index]+"</b>"
                }
        markers.append(marker)
    sndmap = Map(
        identifier="sndmap",
        lat= venues['latitude'].values[0],
        lng= venues['longitude'].values[0],
        style="height:750px;width:900px;margin:0;",
        collapsible= True,
        markers = markers
    )
    return render_template('density.html', latitude=latitude, longitude=longitude, userid=userid, sndmap=sndmap)

@app.route("/usrlocationmap")
def usr_location_map():
    return render_template('d3-example.html', latitude=latitude, longitude=longitude, userid=userid)

@app.route("/locationmap", methods=['GET'])
def getLocationMap():
    locationMap = None
    if latitude == None:
        locationMap = service.getUsrLocationMap()
    else:
        locationMap = service.getUsrLocationMap(latitude, longitude, userid)
    print request
    return jsonify([locationMap])

def buildMap(suggestions):
    if len(suggestions) >= 1:
        print suggestions['Venue_name'].values[0]
        icons = ['http://maps.google.com/mapfiles/ms/icons/green-dot.png',
                   'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
                   'http://maps.google.com/mapfiles/ms/icons/red-dot.png',
                   'http://maps.google.com/mapfiles/ms/icons/yellow-dot.png',
                   'http://maps.google.com/mapfiles/ms/icons/orange-dot.png']
        markers = []
        rec_len = len(suggestions) if len(suggestions) <= 5 else 5
        for index in xrange(rec_len):
            marker = {'icon': icons[index],
                    'lat': suggestions['latitude'].values[index],
                    'lng': suggestions['longitude'].values[index],
                    'infobox': "<b>"+suggestions['Venue_name'].values[index]+"</b>"
                    }
            markers.append(marker)
        sndmap = Map(
            identifier="sndmap",
            lat= suggestions['latitude'].values[0],
            lng= suggestions['longitude'].values[0],
            style="height:750px;width:900px;margin:0;",
            collapsible= True,
            markers = markers
        )
    else:
        print "NO LOCATION HISTORY for this user....: ", len(suggestions)
        sndmap = Map(
            identifier="sndmap",
            lat= 33.842623,
            lng= -118.288384079933,
            style="height:750px;width:900px;margin:0;",
            collapsible= True,
            markers=[
              {
                 'icon': 'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
                 'lat': 33.842623,
                 'lng': -118.288384079933,
                 'infobox': "<b>"+"No location history for this user...."+"</b>"
              }
            ]
        )
    return sndmap

#@app.route("/analysis", methods=['POST','GET'])
@app.route("/", methods=['POST','GET'])
def mapview():
    global latitude, longitude, userid
    suggestions = None
    if len(request.form) != 0:
        latitude = float(request.form["latitude"])
        longitude = float(request.form["longitude"])
        userid = int(request.form["userid"])
        print latitude, longitude, userid
        suggestions = service.run(latitude, longitude, userid)
        sndmap = buildMap(suggestions)
        return render_template('recommend.html', \
            latitude=latitude, longitude=longitude, userid=userid, sndmap=sndmap)
    elif latitude != None:
        print latitude, longitude, userid
        suggestions = service.run(latitude, longitude, userid)
        sndmap = buildMap(suggestions)
        return render_template('recommend.html', \
            latitude=latitude, longitude=longitude, userid=userid, sndmap=sndmap)
    else:
        print "Default MAP Location"
        sndmap = Map(
            identifier="sndmap",
            lat= 33.842623,
            lng= -118.288384079933,
            style="height:750px;width:900px;margin:0;",
            collapsible= True,
            markers=[
              {
                 'icon': 'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
                 'lat': 33.842623,
                 'lng': -118.288384079933,
                 'infobox': "<b>"+"Hello Please Select a Place"+"</b>"
              }
            ]
        )
        return render_template('recommend.html', sndmap=sndmap)

if __name__ == "__main__":
    app.run(debug=True, threaded=True, port=12345)
