import json
import boto3

from academics.TimetableIntegrator import generate_and_save_calenders

from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):

    timetable_key = "gdgsgdhssd"
    academic_year = '2020-2021'
    generate_and_save_calenders(timetable_key, academic_year)
    data = {
       "message": "Hello World"
    }
    return {
        'statusCode': 200,
        'body': json.dumps([data])
    }
