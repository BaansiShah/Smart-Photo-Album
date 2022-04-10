import json
import os
import time
import logging
import boto3
import requests
from datetime import datetime
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from requests.auth import HTTPBasicAuth

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

region = 'us-east-1'
service = 'es'
credentials = boto3.Session().get_credentials()

awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

rekognition = boto3.client('rekognition')

es = Elasticsearch(
    http_auth = awsauth,
    use_ssl = True,
    verify_certs = True,
    connection_class = RequestsHttpConnection
)
print("ES:", es)

def handler(event, context):

    os.environ['TZ'] = 'America/New_York'
    time.tzset()

    logger.debug(credentials)
    records = event['Records']
    print("RECORDS",records)

    for record in records:

        s3object = record['s3']
        bucket = s3object['bucket']['name']
        objectKey = s3object['object']['key']

        image = {
            'S3Object' : {
                'Bucket' : bucket,
                'Name' : objectKey
            }
        }
        print("IMAGE",image)
        response = rekognition.detect_labels(Image = image, MaxLabels = 10)
        print("RESPONSE FROM REKOGNITION",response)
        labels = list(map(lambda x : x['Name'], response['Labels']))
        timestamp = datetime.now().strftime('%Y-%d-%mT%H:%M:%S')
        print("LABELS",labels)
        esObject = json.dumps({
            'objectKey' : objectKey,
            'bucket' : bucket,
            'createdTimesatamp' : timestamp,
            'labels' : labels
        })

        print("ES OBJ:", esObject)
        url = "<ES LINK>"
        headers = { "Content-Type": "application/json" }
        print("JSON DUMPS: ", json.dumps(esObject))
        
        r = requests.post(url,auth=HTTPBasicAuth('<MASTER USER NAME', 'MASTER USER PASSWORD'), data=esObject, headers=headers)
        print(r.text)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }