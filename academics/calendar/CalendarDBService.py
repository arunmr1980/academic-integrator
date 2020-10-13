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

def get_calendar_by_date_and_key(calendar_date, subscriber_key):
    dynamo_db = boto3.resource('dynamodb')
    table = dynamo_db.Table(CALENDAR_TBL)
    response = table.query(
        KeyConditionExpression=Key('subscriber_key').eq(subscriber_key) & Key('calendar_date').eq(calendar_date),
        IndexName='subscriber_key-calendar_date-index'
    )
    if len(response['Items']) > 0 :
        return cal.Calendar(response['Items'][0])

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


def get_all_calendars_by_school_key_and_type(institution_key, subscriber_type):
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
    return make_calendar_obj(calendars)

def get_all_calendars_by_school_key_and_date(institution_key, calendar_date):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(CALENDAR_TBL)
    calendars = []
    response = table.query(
        IndexName='institution_key-calendar_date-index',
        KeyConditionExpression=Key('institution_key').eq(institution_key) & Key('calendar_date').eq(calendar_date)
    )
    add_calendars_from_response(response, calendars)
    logger.debug('Intermediary calendars count - ' + str(len(calendars)))
    while 'LastEvaluatedKey' in response:
        response = table.query(
            IndexName='institution_key-calendar_date-index',
           KeyConditionExpression=Key('institution_key').eq(institution_key) & Key('calendar_date').eq(calendar_date)
        )
        add_calendars_from_response(response, calendars)
        logger.debug('Intermediary calendars count - ' + str(len(calendars)))
    calendars.sort(key = operator.itemgetter('calendar_date'))
    return make_calendar_obj(calendars)


def get_all_calendars_by_key_and_type(subscriber_key, calendar_date):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(CALENDAR_TBL)
    calendars = []
    response = table.query(
        IndexName='subscriber_key-subscriber_type-index',
        KeyConditionExpression=Key('subscriber_key').eq(subscriber_key) & Key('subscriber_type').eq(subscriber_type)
    )
    add_calendars_from_response(response, calendars)
    logger.debug('Intermediary calendars count - ' + str(len(calendars)))
    while 'LastEvaluatedKey' in response:
        response = table.query(
            IndexName='subscriber_key-subscriber_type-index',
           KeyConditionExpression=Key('subscriber_key').eq(subscriber_key) & Key('subscriber_type').eq(subscriber_type)
        )
        add_calendars_from_response(response, calendars)
        logger.debug('Intermediary calendars count - ' + str(len(calendars)))
    calendars.sort(key = operator.itemgetter('calendar_date'))
    return make_calendar_obj(calendars)



def add_calendars_from_response(response, calendars):
    for item in response['Items']:
        calendars.append(item)

def make_calendar_obj(calendars):
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
