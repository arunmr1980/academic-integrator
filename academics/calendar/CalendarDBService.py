import boto3
from boto3.dynamodb.conditions import Key,Attr
import academics.calendar.Calendar as cal
from academics.logger import GCLogger as logger


CALENDAR_TBL = 'Calendar'


def delete_calendar(calendar_key) :
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(CALENDAR_TBL)
    response=table.delete_item(
      Key={
        'calendar_key':calendar_key
      }
    )
    return response


def get_all_calendars(institution_key, subscriber_type):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(CALENDAR_TBL)
    calendars = []
    response = table.query(
        IndexName='institution_key-subscriber_type-index',
        KeyConditionExpression=Key('institution_key').eq(institution_key) & Key('subscriber_type').eq(subscriber_type)
    )
    add_calendars_from_response(response, calendars)
    logger.debug('Intermediary calendars count - ' + str(len(calendars)))
    while 'LastEvaluatedKey' in response:
        response = table.query(
            IndexName='institution_key-subscriber_type-index',
           KeyConditionExpression=Key('institution_key').eq(institution_key) & Key('subscriber_type').eq(subscriber_type)
        )
        add_calendars_from_response(response, calendars)
        logger.debug('Intermediary calendars count - ' + str(len(calendars)))
    return calendars


def add_calendars_from_response(response, calendars):
    for item in response['Items']:
        calendar = cal.Calendar(item)
        calendars.append(calendar)



def add_or_update_calendar(calendar):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(CALENDAR_TBL)
    response = table.put_item(
        Item = calendar
    )
    return response
