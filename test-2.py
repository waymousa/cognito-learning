import boto3, logging
boto3.set_stream_logger('botocore.endpoint', logging.DEBUG)
boto3.set_stream_logger('botocore.auth', logging.DEBUG)
# Retrieve the list of existing buckets
#s3 = boto3.client('s3')
#response = s3.list_buckets()

# Output the bucket names
#print('Existing buckets:')
#for bucket in response['Buckets']:
#    print(f'  {bucket["Name"]}')


ec2 = boto3.client('ec2')
response = ec2.describe_instances()
print(response)