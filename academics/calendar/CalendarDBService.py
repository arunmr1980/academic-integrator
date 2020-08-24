import boto3
from boto3.dynamodb.conditions import Key,Attr
import academics.calendar.Calendar as cal


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

# TODO Change the implementation
# a new index of institution_key and subscriber_type is added
# Also implement getting attitional items if in one query all items are not returned
#
def get_all_calendars(institution_key,subscriber_type):
    calendar_list =[]
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(CALENDAR_TBL)
    response = table.scan(
        FilterExpression=Attr("institution_key").eq(institution_key) & Attr('subscriber_type').eq(subscriber_type)
    )
    for item in response['Items'] :
        calendar = cal.Calendar(item)
        calendar_list.append(calendar)
    return calendar_list


def add_or_update_calendar(calendar):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(CALENDAR_TBL)
    response = table.put_item(
        Item = calendar
    )
    return response
