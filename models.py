from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# to search for places
from geopy.geocoders import Nominatim
import urllib.request
import urllib.error
import urllib.parse
import json


# to define tables models
db = SQLAlchemy()


class User(db.Model):
    """Model for the users table"""
    __tablename__ = 'users'

    uid = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    pwdhash = db.Column(db.String(54))

    def __init__(self, firstname, lastname, email, password):
        self.firstname = firstname.title()
        self.lastname = lastname.title()
        self.email = email.lower()
        self.set_password(password)

    def set_password(self, password):
        self.pwdhash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pwdhash, password)


# Wikipedia's geodata API to find places around a point
class Place(object):
    def meters_to_walking_time(self, meters):
        # 80 meters is one minute walking time
        return int(meters / 80)

    def wiki_path(self, slug):
        return urllib.parse.urljoin("http://en.wikipedia.org/wiki/", slug.replace(" ", "_"))

    def address_to_latlng(self, address):
        """converts an address into a latitude and longitude coordinate. """
        geolocator = Nominatim(user_agent="mapio")
        location = geolocator.geocode(address)

        return location.latitude, location.longitude

    def query(self, address):
        """searches the geodata API"""
        lat, lng = self.address_to_latlng(address)

        # constructs the geodata API URL and then visits it, so there's the URL.
        query_url = "https://en.wikipedia.org/w/api.php?action=query&list=geosearch&gsradius=5000&gscoord={0}%7C{1}&gslimit=20&format=json".format(lat, lng)

        info_request = urllib.request.urlopen(query_url)

        results = info_request.read()
        info_request.close()

        # convert results (bytes type) to string type
        output = results.decode()

        # to convert the string into a python dictionary.
        data = json.loads(output)

        # iterate through the dict and pick up needed fields
        places = []
        for place in data["query"]["geosearch"]:
            name = place["title"]
            meters = place["dist"]
            lat = place["lat"]
            lng = place["lon"]

            wiki_url = self.wiki_path(name)
            walking_time = self.meters_to_walking_time(meters)

            new_dict = {
                "name": name,
                "url": wiki_url,
                "time": walking_time,
                "lat": lat,
                "lng": lng
            }

            places.append(new_dict)

        return places
