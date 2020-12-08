import json, logging, os, boto3
logger = logging.getLogger()
# You will need an environment variable call log in the lambda function to set your logging level.
logger.setLevel(os.environ['log'])

def lambda_handler(event, context):
    logging.info('LogCognitoEvent')
    # Check the event is good
    logging.debug('event: %s' % json.dumps(event))
    #Create a response object from the event because we won't be changing it
    response_obj = event
    # Convert to dict
    event = json.loads(json.dumps(event))
    logging.debug('event_json: %s' % json.dumps(event))
    logging.debug('triggerSource: %s' % event['triggerSource'])
    userName = event['userName']
    logging.info('userName: %s' % userName)
    userPoolId = event['userPoolId']
    logging.info('userPoolId: %s' % userPoolId)
    request = event["request"]
    logging.debug('request: %s' % request)
    userAttributes = request['userAttributes']
    logging.debug('userAttributes: %s' % userAttributes)
    sub = userAttributes['sub']
    logging.info('sub: %s' % sub)
    userstatus = userAttributes['cognito:user_status']
    logging.info('cognito:user_status: %s' % userstatus)
    # Update the DynamoDb for users
    dynamodb = boto3.resource('dynamodb')
    # You will need an environment variable call log in the lambda function to set your logging level.
    table = dynamodb.Table(os.environ['usertable'])
    Item = {'sub' : sub, 'Username' : userName, 'Enabled' : True, 'UserStatus' : userstatus}
    logging.debug('Item: %s' % Item)
    table.put_item(Item={'sub' : sub, 'Username' : userName, 'Enabled' : True, 'UserStatus' : userstatus})
    # check the item was added
    response = table.get_item(Key={'sub' : sub})
    item = response['Item']
    logging.debug('item: %s' % item)
    return response_obj