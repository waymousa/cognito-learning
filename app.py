import flask, logging, watchtower, aws_encryption_sdk, botocore.session, boto3, json, base64, datetime, hashlib, hmac, requests, jwt
from flask import request, jsonify, make_response, Response
from waitress import serve
from boto3.dynamodb.types import Binary
from aws_encryption_sdk.identifiers import CommitmentPolicy

app = flask.Flask(__name__)
app.config["DEBUG"] = True
logging.basicConfig(level=logging.INFO)
handler = watchtower.CloudWatchLogHandler(log_group='cognito-learning', stream_name='api', create_log_group=False, use_queues=False)
app.logger.addHandler(handler)
app.logger.setLevel(logging.DEBUG)
logging.getLogger("waitress").setLevel(logging.WARNING)
logging.getLogger("waitress").addHandler(handler)
logging.getLogger("aws_encryption_sdk").setLevel(logging.WARNING)
logging.getLogger("aws_encryption_sdk").addHandler(handler)
logging.getLogger("botocore").setLevel(logging.WARNING)
logging.getLogger("botocore").addHandler(handler)

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


data = [
    {
        'name': 'Boris Johnson',
        'party': 'Conservative Party',
        'number': '1-333-444-5555'
    },
    {
        'name': 'Kier Starmer',
        'party': 'Labour Party',
        'number': '1-444-555-6666'
    },
    {
        'name': 'Ian Blackford',
        'party': 'Scottish National Party',
        'number': '1-555-666-7777'
    },
    {
        'name': 'Ed Davey',
        'party': 'Liberal Democrats',
        'number': '1-666-777-8888'
    },
    {
        'name': 'Jeffrey Donaldson',
        'party': 'Democratic Unionist Party',
        'number': '1-777-888-9999'
    },
    {
        'name': 'Liz Saville Roberts',
        'party': 'Plaid Cymru',
        'number': '1-888-999-0000'
    },
        {
        'name': 'Caroline Lucas',    
        'party': 'Green Party of England and Wales',
        'number': '1-999-000-1111'
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
        <p>Here is an api call to encrypt and load some data...</p>
        <a href="/v1/loaddata">Load some data</a>
        <p>Here is a call to decrypt some stuff</p>
        <a href="/v1/decrypt">Decrypt Stuff</a>
        <p>Here is a api call to get the credentials</p>
        <a href="/v1/sigv4gen">Get Credentials</a>
        <p>Here is a logout link...</p>
        <a href="https://sams-test-site.auth.us-east-1.amazoncognito.com/logout?client_id=6uri15vh9sig0e0j3fimc656m6&logout_uri=https://sams-test-site.com/logout">Logout</a>
        <p>Here is the current header information...</p>
        
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
        <a href="https://sams-test-site.com/">Home</a>
    </html>
'''

errorpage = '''
    <html>
        <p>Something went wrong, check the logs.</P>
        <a href="https://sams-test-site.com/">Home</a>
    </html>
'''

sucesspage = '''
    <html>
        <p>That probably worked, check the logs.</P>
        <a href="https://sams-test-site.com/">Home</a>
    </html>
'''

@app.before_request
def log_request_info():
    app.logger.debug('>>> Start Request.')
    app.logger.debug('URL: %s', request.url)
    app.logger.debug('Headers: %s', request.headers)
    app.logger.debug('Cookies: %s', request.cookies)
    app.logger.debug('x-amzn-oidc-accesstoken: %s', request.headers.get('x-amzn-oidc-accesstoken'))
    app.logger.debug('x-amzn-oidc-identity: %s', request.headers.get('x-amzn-oidc-identity'))
    app.logger.debug('x-amzn-oidc-data: %s', request.headers.get('x-amzn-oidc-data'))
    if request.headers.get('x-amzn-oidc-data') is not None:
        app.logger.debug('Found an odic data header to process')
        encoded_jwt = request.headers.get('x-amzn-oidc-data')
        jwt_headers = encoded_jwt.split('.')[0]
        app.logger.debug('jwt_headers: %s', jwt_headers)
        decoded_jwt_headers = base64.b64decode(jwt_headers)
        app.logger.debug('decoded_jwt_headers: %s', decoded_jwt_headers)
        decoded_jwt_headers = decoded_jwt_headers.decode("utf-8")
        app.logger.debug('decoded_jwt_headers: %s', decoded_jwt_headers)
        decoded_json = json.loads(decoded_jwt_headers)
        app.logger.debug('decoded_json: %s', decoded_json)
        kid = decoded_json['kid']
        app.logger.debug('kid: %s', kid)
        url = 'https://public-keys.auth.elb.us-east-1.amazonaws.com/' + kid
        app.logger.debug('url: %s', url)
        req = requests.get(url)
        app.logger.debug('req: %s', req)
        pub_key = req.text
        app.logger.debug('pub_key: %s', pub_key)
        payload = jwt.decode(encoded_jwt, pub_key, algorithms=['ES256'])
        app.logger.debug('payload: %s', payload)
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
    app.logger.debug('>>> api_secrets.')
    sub = getUserName()
    app.logger.debug('sub: %s', sub)
    #if checkAuthorised(sub):
    #    app.logger.debug('authorised')
    if checkEnabled(sub):
        app.logger.debug('enabled')
    existing_botocore_session = botocore.session.Session()
    client = aws_encryption_sdk.EncryptionSDKClient(commitment_policy=CommitmentPolicy.REQUIRE_ENCRYPT_ALLOW_DECRYPT)
    kms_key_provider = aws_encryption_sdk.StrictAwsKmsMasterKeyProvider(botocore_session=existing_botocore_session, key_ids=['arn:aws:kms:us-east-1:038180129555:key/45d982fa-69c0-4e10-88a3-f7cd8e48bb9c'])
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Politians')
    response = table.scan()
    app.logger.debug(response)
    items = response.get('Items', [])
    app.logger.debug(items)
    converted_items = []    
    for item in items:
        app.logger.debug(item)
        name = item['name']
        app.logger.debug(name)
        party = item['party']
        app.logger.debug(party)
        number_c = item['number'].value
        app.logger.debug(number_c)
        number_d, number_dh = client.decrypt(source=number_c, key_provider=kms_key_provider)
        converted_item = {'name':name, 'party':party, 'number':number_d.decode('utf-8')}
        converted_items.append(converted_item)
    app.logger.debug(converted_items)    
    app.logger.debug('<<< api_secrets.')
    return jsonify(converted_items)

# A route to return all of the available entries in our catalog.
@app.route('/v1/public', methods=['GET'])
def api_public():
    app.logger.debug('>>> api_public.')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Politians')
    response = table.scan()
    app.logger.debug(response)
    items = response.get('Items', [])
    app.logger.debug(items)
    converted_items = []    
    for item in items:
        app.logger.debug(item)
        name = item['name']
        app.logger.debug(name)
        party = item['party']
        app.logger.debug(party)
        number = item['number'].value
        app.logger.debug(number)
        number_b64 = base64.b64encode(number, altchars=None)
        app.logger.debug(number_b64)
        number_utf8 = number_b64.decode('utf-8')
        app.logger.debug(number_utf8)
        converted_item = {'name':name, 'party':party, 'number':number_utf8}
        converted_items.append(converted_item)
    app.logger.debug(converted_items)

    app.logger.debug('<<< api_public.')
    return jsonify(converted_items)

# A route to encrypt a string using a data key from KMS. Demo of Encryption SDK.
@app.route('/v1/loaddata', methods=['GET'])
def api_loaddata():
    app.logger.debug('>>> api_loaddata.')
    existing_botocore_session = botocore.session.Session()
    kms_key_provider = aws_encryption_sdk.KMSMasterKeyProvider(botocore_session=existing_botocore_session, key_ids=['arn:aws:kms:us-east-1:038180129555:key/45d982fa-69c0-4e10-88a3-f7cd8e48bb9c'])
    #username = 'Samuel Waymouth'
    #address = '39 Belmont Lane, Stanmore, London, HA7 2PU, United Kingdom.'
    #app.logger.debug(username)
    #username_c, username_eh = aws_encryption_sdk.encrypt(source=username, key_provider=kms_key_provider)
    #username_d, username_dh = aws_encryption_sdk.decrypt(source=username_c, key_provider=kms_key_provider)
    #assert username == username_d.decode('utf-8')
    #assert username_eh.encryption_context == username_dh.encryption_context
    #app.logger.debug('username_c = %s' % username_c)
    #app.logger.debug(address)
    #address_c, address_eh = aws_encryption_sdk.encrypt(source=address, key_provider=kms_key_provider)
    #address_d, address_dh = aws_encryption_sdk.decrypt(source=address_c, key_provider=kms_key_provider)
    #assert address == address_d.decode('utf-8')
    #assert address_eh.encryption_context == address_dh.encryption_context
    #app.logger.debug('address_c = %s' % address_c)
    #item = [{'userid': 'swaym', 'username': username_c, 'address': address_c}]
    #app.logger.debug('item = %s' % item)
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.create_table(
        TableName='Politians',
        KeySchema=[
            {
                'AttributeName': 'name',
                'KeyType': 'HASH'
            },
                        {
                'AttributeName': 'party',
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'name',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'party',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    # Wait until the table exists.
    table.meta.client.get_waiter('table_exists').wait(TableName='Politians')
    for item in data:
        name = item['name']
        party = item['party']
        number = item['number']
        number_c, number_eh = aws_encryption_sdk.encrypt(source=number, key_provider=kms_key_provider)
        number_d, number_dh = aws_encryption_sdk.decrypt(source=number_c, key_provider=kms_key_provider)
        assert number == number_d.decode('utf-8')
        assert number_eh.encryption_context == number_dh.encryption_context
        table.put_item(Item={'name': name, 'party': party, 'number': number_c})
    res = make_response(sucesspage)
    app.logger.debug('<<< api_loaddata.')
    return res

# A route to decrypt a string using a data key from KMS. Demo of Encryption SDK.
@app.route('/v1/decrypt', methods=['GET'])
def api_decrypt():
    app.logger.debug('>>> api_decrypt.')
    existing_botocore_session = botocore.session.Session()
    client = aws_encryption_sdk.EncryptionSDKClient(commitment_policy=CommitmentPolicy.REQUIRE_ENCRYPT_ALLOW_DECRYPT)
    kms_key_provider = aws_encryption_sdk.StrictAwsKmsMasterKeyProvider(botocore_session=existing_botocore_session, key_ids=['arn:aws:kms:us-east-1:038180129555:key/45d982fa-69c0-4e10-88a3-f7cd8e48bb9c'])
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('cognito-learning-encrypted-stuff')
    userrecord = table.get_item(Key={'userid': 'swaym'})
    app.logger.debug('userrecord = %s' % userrecord)
    userjson = userrecord['Item']
    app.logger.debug('userjson = %s' % userjson)
    username_c = userjson['username'].value
    app.logger.debug('username_c = %s' % username_c)
    address_c = userjson['address'].value
    app.logger.debug('address_c = %s' % address_c)
    username_d, username_dh = client.decrypt(source=username_c, key_provider=kms_key_provider)
    #username_d, username_dh = aws_encryption_sdk.decrypt(source=username_c, key_provider=kms_key_provider)
    address_d, address_dh = client.decrypt(source=address_c, key_provider=kms_key_provider)
    #address_d, address_dh = aws_encryption_sdk.decrypt(source=address_c, key_provider=kms_key_provider)
    item = [{'userid': 'swaym', 'username': username_d.decode('utf-8'), 'address': address_d.decode('utf-8')}]
    app.logger.debug('item = %s' % item)
    app.logger.debug('<<< api_decrypt.')
    return jsonify(item)

# A route to generate a SigV4 request manually that gest the S3 list buckets for the current role.
@app.route('/v1/sigv4gen', methods=['GET'])
def api_sigv4gen():
    app.logger.debug('>>> api_sigv4gen.')
    method = 'GET'
    service = 'ec2'
    host = 'ec2.amazonaws.com'
    region = 'us-east-1'
    endpoint = 'https://ec2.amazonaws.com'
    request_parameters = 'Action=DescribeRegions&Version=2013-10-15'
    existing_botocore_session = botocore.session.Session()
    credentials = existing_botocore_session.get_credentials()
    app.logger.debug('credentials = %s' % credentials)
    app.logger.debug('access_key = %s' % credentials.access_key)
    app.logger.debug('secret_key = %s' % credentials.secret_key)
    app.logger.debug('token = %s' % credentials.token)
    access_key = credentials.access_key
    secret_key = credentials.secret_key
    session_token = credentials.token
    t = datetime.datetime.utcnow()
    app.logger.debug('t = %s' % t)
    amzdate = t.strftime('%Y%m%dT%H%M%SZ')
    app.logger.debug('amzdate = %s' % amzdate)
    datestamp = t.strftime('%Y%m%d')
    app.logger.debug('datestamp = %s' % datestamp)
    canonical_uri = '/'
    app.logger.debug('canonical_uri = %s' % canonical_uri)
    canonical_querystring = request_parameters
    app.logger.debug('canonical_querystring = %s' % canonical_querystring)
    canonical_headers = 'host:' + host + '\n' + 'x-amz-date:' + amzdate + '\n' + 'x-amz-security-token:' + session_token + '\n' 
    app.logger.debug('canonical_headers = %s' % canonical_headers)
    signed_headers = 'host;x-amz-date;x-amz-security-token'
    app.logger.debug('signed_headers = %s' % signed_headers)
    payload_hash = hashlib.sha256(('').encode('utf-8')).hexdigest()
    app.logger.debug('payload_hash = %s' % payload_hash)
    canonical_request = method + '\n' + canonical_uri + '\n' + canonical_querystring + '\n' + canonical_headers + '\n' + signed_headers + '\n' + payload_hash
    app.logger.debug('canonical_request = %s' % canonical_request)
    algorithm = 'AWS4-HMAC-SHA256'
    app.logger.debug('algorithm = %s' % algorithm)
    credential_scope = datestamp + '/' + region + '/' + service + '/' + 'aws4_request'
    app.logger.debug('credential_scope = %s' % credential_scope)
    string_to_sign = algorithm + '\n' +  amzdate + '\n' +  credential_scope + '\n' +  hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
    app.logger.debug('string_to_sign = %s' % string_to_sign)
    signing_key = getSignatureKey(secret_key, datestamp, region, service)
    app.logger.debug('signing_key = %s' % signing_key)
    signature = hmac.new(signing_key, (string_to_sign).encode('utf-8'), hashlib.sha256).hexdigest()
    app.logger.debug('signature = %s' % signature)
    authorization_header = algorithm + ' ' + 'Credential=' + access_key + '/' + credential_scope + ', ' +  'SignedHeaders=' + signed_headers + ', ' + 'Signature=' + signature
    app.logger.debug('authorization_header = %s' % authorization_header)
    headers = {'x-amz-date':amzdate, 'Authorization':authorization_header, 'X-Amz-Security-Token':session_token}
    app.logger.debug('headers: %s' % headers)
    request_url = endpoint + '?' + canonical_querystring
    app.logger.debug('request_url: %s' % request_url)    
    r = requests.get(request_url, headers=headers)
    app.logger.debug('response: %s' % r)
    app.logger.debug('headers: %s' % r.headers)
    app.logger.debug('cookies: %s' % r.cookies)
    app.logger.debug('text: %s' % r.text)
    xml = r.text
    app.logger.debug('<<< api_sigv4gen.')
    return Response(xml, mimetype='text/xml')

    # https://docs.aws.amazon.com/general/latest/gr/sigv4_signing.html
    # https://docs.aws.amazon.com/code-samples/latest/catalog/python-signv4-v4-signing-get-authheader.py.html
    # https://docs.aws.amazon.com/general/latest/gr/signature-v4-examples.html#signature-v4-examples-python 

def sign(key, msg):
    hmac_new = hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()
    app.logger.debug('hmac_new: %s' % hmac_new)
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

def getSignatureKey(key, dateStamp, regionName, serviceName):
    kDate = sign(('AWS4' + key).encode('utf-8'), dateStamp)
    app.logger.debug('kDate: %s' % kDate)
    kRegion = sign(kDate, regionName)
    app.logger.debug('kRegion: %s' % kRegion)
    kService = sign(kRegion, serviceName)
    app.logger.debug('kService: %s' % kService)
    kSigning = sign(kService, 'aws4_request')
    app.logger.debug('kSigning: %s' % kSigning)
    return kSigning

def checkEnabled(sub):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('cognito-learning-users')
    response = table.get_item(Key={'sub' : sub})
    app.logger.debug('response: %s', response)
    item = response['Item']
    app.logger.debug('item: %s', item)
    status = item['Enabled']
    app.logger.debug('status: %s', status)
    return True

def checkAuthorised():
    return True

def getUserName():
    encoded_jwt = request.headers.get('x-amzn-oidc-data')
    jwt_headers = encoded_jwt.split('.')[0]
    app.logger.debug('jwt_headers: %s', jwt_headers)
    decoded_jwt_headers = base64.b64decode(jwt_headers)
    app.logger.debug('decoded_jwt_headers: %s', decoded_jwt_headers)
    decoded_jwt_headers = decoded_jwt_headers.decode("utf-8")
    app.logger.debug('decoded_jwt_headers: %s', decoded_jwt_headers)
    decoded_json = json.loads(decoded_jwt_headers)
    app.logger.debug('decoded_json: %s', decoded_json)
    kid = decoded_json['kid']
    app.logger.debug('kid: %s', kid)
    url = 'https://public-keys.auth.elb.us-east-1.amazonaws.com/' + kid
    app.logger.debug('url: %s', url)
    req = requests.get(url)
    app.logger.debug('req: %s', req)
    pub_key = req.text
    app.logger.debug('pub_key: %s', pub_key)
    payload = jwt.decode(encoded_jwt, pub_key, algorithms=['ES256'])
    app.logger.debug('payload: %s', payload)
    sub = payload['sub']
    app.logger.debug('sub: %s', sub)
    return sub

if __name__ == "__main__":
   #app.run() ##Replaced with below code to run it using waitress 
   serve(app, host='0.0.0.0', port=5000)

