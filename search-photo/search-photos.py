import json
import boto3
import time
from botocore.vendored import requests

def lambda_handler(event, context):
    print("Event:::",event)
    inputText = event['queryStringParameters']['search_query']
    print("InputText::",inputText)
    keywords = get_keywords(inputText)
    image_array = get_image_locations(keywords)
    return {
        'statusCode': 200,
        'headers':{
            'Access-Control-Allow-Origin':'*',
            'Access-Control-Allow-Credentials':True
        },
        'body': json.dumps({"results":image_array})
    }

def get_keywords(Text):
    lex = boto3.client('lex-runtime')
    response = lex.post_text(
        botName = 'PhotoSearch',
        botAlias = 'lexbot',
        userId = 'searchPhotosLambda',
        inputText = Text
    )
    print(response)
    keywords = []
    slots = response['slots']
    keywords = [v for _, v in slots.items() if v]
    print(keywords)
    return keywords
    
def get_image_locations(keywords):
    endpoint = 'https://search-photos-ghtojgkiz77c253rfdj2gd7fdi.us-east-1.es.amazonaws.com/esphotos/_search'
    headers = {'Content-Type': 'application/json'}
    auth1=('user','Ansh@123')
    prepared_q = []
    for k in keywords:
        prepared_q.append({"match": {"labels": k}})
    q = {"query": {"bool": {"should": prepared_q}}}
    r = requests.post(endpoint,auth=auth1, headers=headers, data=json.dumps(q))
    print(r)

    image_array = []
    for each in r.json()['hits']['hits']:
        objectKey = each['_source']['objectKey']
        bucket = each['_source']['bucket']
        image_url = "https://" + bucket + ".s3.amazonaws.com/" + objectKey
        image_array.append(image_url)
        print(each['_source']['labels'])
    print(image_array)
    return image_array
    
