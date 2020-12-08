import json, logging, os, boto3
logger = logging.getLogger()
logger.setLevel(os.environ['log'])

def lambda_handler(event, context):
    logging.info('LogCognitoEvent')
    # Check the event is good
    logging.debug('event: %s' % json.dumps(event))
    # Convert to dict
    event = json.loads(json.dumps(event))
    logging.debug('detail: %s' % event['detail'])
    # extract the Cognito Event details
    cognitoEvent = event['detail']
    logging.debug('cognitoEvent: %s' % cognitoEvent)
    eventTime = cognitoEvent['eventTime']
    logging.info('eventTime: %s' % eventTime)
    eventSource = cognitoEvent['eventSource']
    logging.info('eventSource: %s' % eventSource)
    eventCategory = cognitoEvent['eventCategory']
    logging.info('eventCategory: %s' % eventCategory)
    eventName = cognitoEvent['eventName']
    logging.info('eventName: %s' % eventName)
    requestParameters = cognitoEvent['requestParameters']
    logging.debug('requestParameters: %s' % requestParameters)
    userPoolId = requestParameters['userPoolId']
    logging.info('userPoolId: %s' % userPoolId)

    # Check for the eventName cases
    if eventName == 'ConfirmSignUp':
        # Update the DynamoDb for users
        logging.info('ConfirmSignUp')
        additionalEventData = cognitoEvent['additionalEventData']
        sub = additionalEventData['sub']
        logging.info('sub: %s' % sub)
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ['usertable'])
        Item = {'sub' : sub, 'Username' : username, 'Enabled' : userenabled, 'UserStatus' : userstatus}
        logging.debug('Item: %s' % Item)
        table.put_item(Item={'sub' : sub, 'Username' : username, 'Enabled' : userenabled, 'UserStatus' : userstatus})
        # check the item was added
        response = table.get_item(Key={'sub' : sub})
        item = response['Item']
        logging.debug('item: %s' % item)
    elif eventName == 'AdminDeleteUser':
        # Update the DynamoDb for users
        logging.info('AdminDeleteUser')
        username = requestParameters['username']
        logging.info('username: %s' % username)
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ['usertable'])
        response = table.delete_item(Key={'Username' : username})
    else:
        logging.info('eventName: %s is not processed by this function.' % eventName)
    return response