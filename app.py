"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/

This file creates your application.
"""

import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, Response, abort, make_response, jsonify
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from splatter import SplatService

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'this_should_be_configured')
logger = app.logger

###
# Configure the database client
# MONGODB_URI should be of the format mongodb://<dbuser>:<dbpass>@<host>:<port>/<dbname>
###
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

splat_service = SplatService(database)

###
# Routing for your application.
###

def check_api_key(api_key):
    return splat_service.has_api_key(api_key)

def requires_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.authorization
        if not api_key or not check_api_key(api_key):
            return abort(401)
        return f(*args, **kwargs)
    return decorated

def requires_json_payload(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        json = request.json
        if not json:
            return abort(400)
        return f(*args, **kwargs)
    return decorated

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

@app.route('/keys', methods=['DELETE'])
@requires_api_key
@requires_json_payload
def delete_api_key(splat_service=splat_service):
    api_key = request.json
    deleted = splat_service.delete_api_key(doc_id=api_key['id'], name=api_key['name'], key=api_key['key'])
    if deleted is None:
        return abort(404)
    return make_response('OK', 200)

@app.route('/keys', methods=['POST'])
@requires_json_payload
def create_api_key(splat_service=splat_service):
    api_key = request.json
    if 'name' not in api_key:
        return bad_request('Name required for API key')
    result_id = splat_service.create_api_key(name=api_key['name'], key=api_key['key'] if 'key' in api_key else None)
    return make_response(jsonify(splat_service.find_api_key(doc_id=result_id)), 201)

@app.errorhandler(403)
def bad_request(msg):
    return make_response(jsonify({'msg': msg}), 403)

@app.errorhandler(404)
def resource_not_found():
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(401)
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

@app.errorhandler(500)
def server_blew_up_handler(error):
    logger.error(error)
    return make_response(jsonify({'error': 'Server error'}), 500)

if __name__ == '__main__':
    app.run(debug=True)
