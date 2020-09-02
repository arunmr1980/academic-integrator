import json
import boto3

from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    data = {
       "message": "Hello World"
    }
    return {
        'statusCode': 200,
        'body': json.dumps([data])
    }
