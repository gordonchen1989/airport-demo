from flask import Flask
from flask import abort
from flask import g
from flask import render_template

import os
import db
import time
from geopy.distance import vincenty
import memcache

cache = memcache.Client( [ os.environ['CACHE_HOST'] ] )
cache.flush_all()
database = db.DB()
application = Flask(__name__)
query_count = 0

@application.before_request
def before_request():
  g.start = time.time()

@application.after_request
def after_request(response):
    global query_count
    diff_seconds = time.time() - g.start
    diff_miliseconds = diff_seconds * 1000
    if (response.response.__class__ is list):
        diag = "Execution time: %.2fms | Database queries: %s" % (diff_miliseconds, query_count)
        new_response = bytes.decode(response.response[0]).replace('__DIAGNOSTICS__', diag)
        response.set_data(new_response)
    return response

@application.route("/")
def home():
    #v1.1 use cache
    # cities = cache_query("airport_cities", "SELECT id, name, icon, latitude, longitude from city;")
    #v1.0
    cities = database.query("SELECT id, name, icon, latitude, longitude from city;")
    query_increment()
    return render_template('main.html', cities=cities)


@application.route("/<city_id>")
def city(city_id):
    #v1.1 use cache
    # cities = cache_query("airport_cities", "SELECT id, name, icon, latitude, longitude from city;")
    #v1.0
    cities = database.query("SELECT id, name, icon, latitude, longitude from city;")
    query_increment()
    city = list(filter(lambda c: c['id'] == city_id, cities))

    if len(city) < 1:
        abort(404) 
    latlng = (city[0]['latitude'], city[0]['longitude'])

    #v1.1 use cache
    # airports = cache_query("airport_airports", "SELECT name, latitude, longitude from airport;")
    #v1.0
    query_increment()
    airports = database.query("SELECT name, latitude, longitude from airport;")

    for airport in airports:
        airport['distance'] = vincenty((airport['latitude'], airport['longitude']), latlng).miles
    closest = sorted(airports, key=lambda x: x['distance'])[:5]
    return render_template('main.html', cities=cities, airports=closest)

def query_increment():
    global query_count
    query_count = query_count + 1

def cache_query(key, query):
    cached = cache.get(key)
    if not cached:
        query_increment()
        cached = database.query(query)
        cache.set(key, cached)
    return cached

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()