import boto3
from boto3.dynamodb.conditions import Key
from academics.logger import GCLogger as logger
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

def get_leave_by_subscriber_key_and_from_date(subscriber_key, from_date) :
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(LEAVE_TBL)
    response = table.query(
        IndexName='subscriber_key-from_date-index',
        KeyConditionExpression=Key('subscriber_key').eq(subscriber_key) & Key('from_date').eq(from_date)
    )
    return response['Items']

def get_uncancelled_leaves(leaves) :
    uncancelled_leaves = []
    for leave in leaves :
        if leave.__contains__('status') :
            if leave['status'] != 'CANCELLED' :
                uncancelled_leaves.append(leave)
        else :
            uncancelled_leaves.append(leave)
    return uncancelled_leaves

def get_leaves_with_same_end_date(to_date,leaves) :
    leaves_list = []
    for leave in leaves :
        if leave['to_date'] == to_date :
            leaves_list.append(leave)
            logger.info(" ----- THIS LEAVE HAVE SAME FROM DATE AND TO DATE WITH ANOTHER  LEAVE. " + leave['leave_key'] +' ----- ')
    return leaves_list

def get_leaves_by_subscriber_key_and_to_date_inbetween(subscriber_key, from_date, to_date) :
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(LEAVE_TBL)
    response = table.query(
        IndexName='subscriber_key-to_date-index',
        KeyConditionExpression=Key('subscriber_key').eq(subscriber_key) & Key('to_date').between(from_date, to_date)
    )
    return response['Items']

def get_leaves_having_to_date_grater_than_adding_leave_to_date_and_from_date_less_than_adding_leave_to_date(subscriber_key, to_date) :
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(LEAVE_TBL)
    response = table.query(
        IndexName='subscriber_key-to_date-index',
        KeyConditionExpression=Key('subscriber_key').eq(subscriber_key) & Key('to_date').gt(to_date)
    )
    leaves = []
    for leave in response['Items']:
        existing_leave_from_date = datetime.datetime.strptime(leave['from_date'],'%Y-%m-%d')
        adding_leave_to_date = datetime.datetime.strptime(to_date,'%Y-%m-%d')
        if existing_leave_from_date < adding_leave_to_date :
            leaves.append(leave)
    return leaves

# return list of leaves as dict
def get_leaves_by_subscriber_key_and_from_date_inbetween(subscriber_key, from_date, to_date) :
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(LEAVE_TBL)
    response = table.query(
        IndexName='subscriber_key-from_date-index',
        KeyConditionExpression=Key('subscriber_key').eq(subscriber_key) & Key('from_date').between(from_date, to_date)
    )
    return response['Items']

def get_employee_leaves(subscriber_key,from_date,to_date) :
    conflict_value = False
    leaves_list = []
    #getting leaves having exact from date and to date
    leaves = get_leave_by_subscriber_key_and_from_date(subscriber_key,from_date)
    leaves = get_uncancelled_leaves(leaves)
    if len(leaves) > 0 :
        leaves = get_leaves_with_same_end_date(to_date,leaves)
        leaves_list.extend(leaves)

    #getting leaves having from date in between academic from date and to date
    if len(get_leaves_by_subscriber_key_and_from_date_inbetween(subscriber_key, from_date, to_date)) > 0 :
        leaves = get_leaves_by_subscriber_key_and_from_date_inbetween(subscriber_key, from_date, to_date)
        leaves = get_uncancelled_leaves(leaves)
        if len(leaves) > 0 :
            logger.info(' ------------ Existing Leave [ From Time ] is in between of academic year duration ------------')
        leaves_list.extend(leaves)

    #getting leaves having to date in between academic from date and to date
    if len(get_leaves_by_subscriber_key_and_to_date_inbetween(subscriber_key, from_date, to_date)) > 0 :
        leaves = get_leaves_by_subscriber_key_and_to_date_inbetween(subscriber_key, from_date, to_date)
        leaves = get_uncancelled_leaves(leaves)
        if len(leaves) > 0 :
            logger.info(' ----------- Existing Leave [ To Time ] is in between of academic year duration ------------')
        leaves_list.extend(leaves)

    #getting leaves having to date is greater than  academic to date and from date less than academic to date
    if len(get_leaves_having_to_date_grater_than_adding_leave_to_date_and_from_date_less_than_adding_leave_to_date(subscriber_key, to_date)) > 0 :
        leaves = get_leaves_having_to_date_grater_than_adding_leave_to_date_and_from_date_less_than_adding_leave_to_date(subscriber_key,to_date)
        leaves = get_uncancelled_leaves(leaves)
        if len(leaves) > 0 :
            logger.info(' ----------- Existing Leave [ To Time ] is grater than academic year duration ------------')
        leaves_list.extend(leaves)

    logger.info(str(len(leaves))+ '   ----------- Count of leaves list --------   ')
    leaves_list = remove_duplicates(leaves_list)

    return leaves_list
   
def remove_duplicates(leaves_list) :
    final_leave_list = []
    for leave in leaves_list :
        if check_leave_already_exist(final_leave_list,leave) == False :
            final_leave_list.append(leave)
    return final_leave_list

def check_leave_already_exist(final_leave_list,leave) :
    is_exist = False
    for final_leave in final_leave_list :
        if final_leave['leave_key'] == leave['leave_key'] :
            is_exist = True
    return is_exist




    