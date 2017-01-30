"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/

This file creates your application.
"""

import os
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from splatter import SplatterService

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'this_should_be_configured')

###
# Configure the database client
# MONGODB_URI should be of the format mongodb://<dbuser>:<dbpass>@<host>:<port>/<dbname>
###
logger = app.logger
mongodb_uri = os.environ['MONGODB_URI'] if 'MONGODB_URI' in os.environ else 'mongodb://localhost:27017/splatpal'
logger.info("Attempting initial connection to Mongo at URI: %s", mongodb_uri)
database = MongoClient(mongodb_uri)
try:
    # The official recommended hack to determine if the client connected successfully,
    # since the constructor is non-blocking and will not raise an exception otherwise
    database.admin.command('ismaster')
except ConnectionFailure:
    logger.critical("Unable to connect to Mongo client at URI: %s", mongodb_uri)
    quit()
logger.info("Successfully connected to Mongo")

splatter_service = SplatterService(database)

###
# Routing for your application.
###

@app.route('/')
def index():
    """GET to generate a list of endpoints and their docstrings"""
    urls = dict([(r.rule, app.view_functions.get(r.endpoint).func_doc)
                 for r in app.url_map.iter_rules()
                 if not r.rule.startswith('/static')])
    return render_template('index.html', urls=urls)


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html')

@app.route('/get/<thing>', methods=['GET'])
def select(thing):
    """Retrieve a thing.

    GET: Returns thing previously 'put' at given location.
         Returns HTTP 200 on success; body is payload as-is.
         Returns HTTP 404 when data does not exist.
    """
    # result = db.get(thing)
    return 1


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=600'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
