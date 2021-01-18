import boto3
from boto3.dynamodb.conditions import Key

from academics.leave.Leave import Leave


LEAVE_TBL='Leave'




def add_or_update_leave(leave):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(LEAVE_TBL)
    response = table.put_item(
        Item = leave
    )
    return response


def delete_leave(leave_key):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(LEAVE_TBL)
    response = table.delete_item(
        Key = {
            'leave_key': leave_key
        }
    )
    return response


def get_leave(leave_key) :
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(LEAVE_TBL)
    response=table.get_item(
      Key={
        'leave_key':leave_key
      }
    )
    if response['Item'] is not None:
        return Leave(response['Item'])

# return list of leaves as dict
def get_leaves_by_subscriber_key(subscriber_key, from_date, to_date) :
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(LEAVE_TBL)
    response = table.query(
        IndexName='subscriber_key-from_date-index',
        KeyConditionExpression=Key('subscriber_key').eq(subscriber_key) & Key('from_date').between(from_date, to_date)
    )
    return response['Items']

# return list of leaves as dict
def get_leaves_by_institution_key(institution_key, from_date, to_date) :
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(LEAVE_TBL)
    response = table.query(
        IndexName='institution_key-from_date-index',
        KeyConditionExpression=Key('institution_key').eq(institution_key) & Key('from_date').between(from_date, to_date)
    )
    return response['Items']
