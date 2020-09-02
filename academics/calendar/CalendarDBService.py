import boto3
from boto3.dynamodb.conditions import Key,Attr
import academics.calendar.Calendar as cal
from academics.logger import GCLogger as logger
import operator

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

def get_calendar(calendar_key) :
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(CALENDAR_TBL)
    response=table.get_item(
      Key={
        'calendar_key':calendar_key
      }
    )
    if response['Item'] is not None:
        return cal.Calendar(response['Item'])


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
    calendars.sort(key = operator.itemgetter('calendar_date'))
    return make_caendar_obj(calendars)

def add_calendars_from_response(response, calendars):
    for item in response['Items']:
        calendars.append(item)

def make_caendar_obj(calendars):
    cal_obj_list = []
    for item in calendars:
        calendar = cal.Calendar(item)
        cal_obj_list.append(calendar)
    return cal_obj_list

def add_or_update_calendar(calendar):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(CALENDAR_TBL)
    response = table.put_item(
        Item = calendar
    )
    return response
