import flask
from flask import request, jsonify

app = flask.Flask(__name__)
app.config["DEBUG"] = True

secrets = [
    {
        'name': 'Boris Johnson',
        'number': '1-333-444-5555'
    },
    {
        'name': 'Kier Starmer',
        'number': '1-444-555-6666'
    },
    {
        'name': 'Ian Blackford',
        'number': '1-555-666-7777'
    },
    {
        'name': 'Ed Davey',
        'number': '1-666-777-8888'
    },
    {
        'name': 'Jeffrey Donaldson',
        'number': '1-777-888-9999'
    },
    {
        'name': 'Liz Saville Roberts',
        'number': '1-888-999-0000'
    },
        {
        'name': 'Caroline Lucas',
        'number': '1-999-000-1111'
    }
    
]

public = [
    {
        'name': 'Boris Johnson',
        'party': 'Conservative Party'
    },
    {
        'name': 'Kier Starmer',
        'party': 'Labour Party'
    },
    {
        'name': 'Ian Blackford',
        'party': 'Scottish National Party'
    },
    {
        'name': 'Ed Davey',
        'party': 'Liberal Democrats'
    },
    {
        'name': 'Jeffrey Donaldson',
        'party': 'Democratic Unionist Party'
    },
    {
        'name': 'Liz Saville Roberts',
        'party': 'Plaid Cymru'
    },
        {
        'name': 'Caroline Lucas',
        'party': 'Green Party of England and Wales'
    }
    
]

@app.before_request
def log_request_info():
    app.logger.info('Headers: %s', request.headers)
    app.logger.info('Cookies: %s', request.cookies)
    app.logger.info('Body: %s', request.get_data())

# A default route
@app.route('/', methods=['GET'])
def home():
    return "<h1>Hello world</h1><p>This site is a prototype API which does little.</p>"

# A route to return all of the available entries in our catalog.
@app.route('/v1/secrets', methods=['GET'])
def api_secrets():
    return jsonify(secrets)

# A route to return all of the available entries in our catalog.
@app.route('/v1/public', methods=['GET'])
def api_public():
    return jsonify(public)

app.run()