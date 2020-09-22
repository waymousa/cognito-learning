import flask, logging, watchtower
from flask import request, jsonify, make_response
from waitress import serve

app = flask.Flask(__name__)
app.config["DEBUG"] = True
logging.basicConfig(level=logging.INFO)
handler = watchtower.CloudWatchLogHandler(log_group='cognito-learning', stream_name='api', create_log_group=False, use_queues=False)
app.logger.addHandler(handler)
app.logger.setLevel(logging.DEBUG)
logging.getLogger("watiress").setLevel(logging.WARNING)
logging.getLogger("watiress").addHandler(handler)

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

homepage = '''
    <html>
        <h1>Hello world</h1>
        <p>This site is a prototype API which does little.</p>
        <p>Here is some public stuff...</p>
        <a href="/v1/public">Public Stuff</a>
        <p>Here is some secret stuff...</p>
        <a href="/v1/secrets">Secret Stuff</a>
        <p>Here is a logout link...</p>
        <a href="https://sams-test-site.auth.us-east-1.amazoncognito.com/logout?client_id=6uri15vh9sig0e0j3fimc656m6&logout_uri=https://sams-test-site.com/logout">Logout</a>
    </html>
'''

logoutpage = '''
    <html>
        <!--
        <script>
            function logout (){
                window.location.href = "https://sams-test-site.com"
            }
        </script>
        <body onload="logout();"> 
        -->
        <p>You are logged out.</P>
        <a href="https://sams-test-site/">Home</a>
    </html>
'''

@app.before_request
def log_request_info():
    app.logger.debug('>>> Start Request.')
    app.logger.debug('URL: %s', request.url)
    app.logger.debug('Headers: %s', request.headers)
    app.logger.debug('Cookies: %s', request.cookies)
    app.logger.debug('Body: %s', request.get_data())
    app.logger.debug('<<< Finish Request.')

@app.after_request
def after_request_func(response):
    app.logger.debug('>>> Start Response.')
    app.logger.debug('Headers: %s', response.headers)
    app.logger.debug('Body: %s', response.get_data())
    app.logger.debug('<<< Finish Response.')
    return response

# A default route
@app.route('/', methods=['GET'])
def home():
    return homepage

# A logout route
@app.route('/logout', methods=['GET'])
def logout():
    res = make_response(logoutpage)
    res.set_cookie('AWSELBAuthSessionCookie-0', max_age=0)
    res.set_cookie('AWSELBAuthSessionCookie-1', max_age=0)
    return res

# A route to return all of the available entries in our catalog.
@app.route('/v1/secrets', methods=['GET'])
def api_secrets():
    return jsonify(secrets)

# A route to return all of the available entries in our catalog.
@app.route('/v1/public', methods=['GET'])
def api_public():
    return jsonify(public)

if __name__ == "__main__":
   #app.run() ##Replaced with below code to run it using waitress 
   serve(app, host='0.0.0.0', port=5000)

