import academics.calendar.CalendarDBService as calendar_service
import boto3
from boto3.dynamodb.conditions import Key,Attr
CALENDAR_TBL = 'Calendar'

import pprint
pp = pprint.PrettyPrinter(indent=4)

def get_all_calendars_by_school_key_and_type(institution_key, subscriber_type):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(CALENDAR_TBL)
    response = table.query(
        IndexName='institution_key-subscriber_type-index',
        KeyConditionExpression=Key('institution_key').eq(institution_key) & Key('subscriber_type').eq(subscriber_type)
    )
    return response['Items']


def clean_up_class_calendars():
    calendar_list = get_all_calendars_by_school_key_and_type("1e4d12bc2b58050ff084f8da","CLASS-DIV")
    print(len(calendar_list))
    for calendar in calendar_list:
        calendar_service.delete_calendar(calendar['calendar_key'])
        print("-----class calendar deleted-----" + calendar['calendar_key'])

def clean_up_employee_calendars():
    calendar_list = get_all_calendars_by_school_key_and_type("1e4d12bc2b58050ff084f8da","EMPLOYEE")
    print(len(calendar_list))
    for calendar in calendar_list:
        calendar_service.delete_calendar(calendar['calendar_key'])
        print("-----employee calendar deleted-----" + calendar['calendar_key'])

count = 500
while count > 1:
    count = count - 1
    print("---inside loop --")
    clean_up_class_calendars()
    clean_up_employee_calendars()
