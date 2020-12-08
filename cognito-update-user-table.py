import json, logging, os, boto3
from boto3.dynamodb.conditions import Key
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

    if eventName == 'AdminDeleteUser':
        # Update the DynamoDb for users
        logging.info('AdminDeleteUser')
        additionalEventData = cognitoEvent['additionalEventData']
        sub = additionalEventData['sub']
        logging.info('sub: %s' % sub)
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ['usertable'])
        response = table.delete_item(Key={'sub' : sub})
    else:
        logging.info('eventName: %s is not processed by this function.' % eventName)
    return response