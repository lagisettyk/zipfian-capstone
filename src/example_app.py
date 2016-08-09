from flask import Flask, render_template
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map
import backend as service

app = Flask(__name__, template_folder="startbootstrap-simple-sidebar-gh-pages")

# you can set key as config
app.config['GOOGLEMAPS_KEY'] = "AIzaSyBTT8YSKGtJV9ZVcoVEqHUJuLCLPqXXAto"

# Initialize the extension
GoogleMaps(app)

@app.route("/")
def home():
    return render_template('index.html')


@app.route("/analysis")
def mapview():
    suggestions = service.run()
    print suggestions['Venue_name'].values[0], suggestions['Venue_name'].values[1]
    sndmap = Map(
        identifier="sndmap",
        lat= suggestions['latitude'].values[0],
        lng= suggestions['longitude'].values[0],
        markers=[
          {
             'icon': 'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
             'lat': suggestions['latitude'].values[0],
             'lng': suggestions['longitude'].values[0],
             'infobox': "<b>"+suggestions['Venue_name'].values[0]+"</b>"
          },
          {
             'icon': 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
             'lat': suggestions['latitude'].values[1],
             'lng': suggestions['longitude'].values[1],
             'infobox': "<b>"+suggestions['Venue_name'].values[1]+"</b>"
          },
         {
           'icon': 'http://maps.google.com/mapfiles/ms/icons/red-dot.png',
           'lat': suggestions['latitude'].values[2],
           'lng': suggestions['longitude'].values[2],
           'infobox': "<b>"+suggestions['Venue_name'].values[2]+"</b>"
         },
          {
            'icon': 'http://maps.google.com/mapfiles/ms/icons/yellow-dot.png',
            'lat': suggestions['latitude'].values[3],
            'lng': suggestions['longitude'].values[3],
            'infobox': "<b>"+suggestions['Venue_name'].values[3]+"</b>"
          },
           {
             'icon': 'http://maps.google.com/mapfiles/ms/icons/orange-dot.png',
             'lat':  suggestions['latitude'].values[4],
             'lng': suggestions['longitude'].values[4],
             'infobox': "<b>"+suggestions['Venue_name'].values[4]+"</b>"
           }


        ]
    )
    return render_template('example.html', sndmap=sndmap)
    # return render_template('example.html', mymap=mymap)

if __name__ == "__main__":
    app.run(debug=True)
