import boto3

from boto3.dynamodb.conditions import Key
from academics.timetable.TimeTable import TimeTable
from academics.logger import GCLogger as logger

TIME_TABLE_TBL = 'TimeTable'



def get_time_table(time_table_key):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TIME_TABLE_TBL)
    response = table.get_item(
                Key={
                    'time_table_key':time_table_key
                }
            )
    return TimeTable(response['Item'])
 

def create_timetable(timetable):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TIME_TABLE_TBL)
    response = table.put_item(
        Item = timetable
    )
    return response

def get_school_timetables(school_key, academic_year):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TIMETABLE_TABLE)
    timetables = []
    response = table.query(
        IndexName='school_key-academic_year-index',
        KeyConditionExpression=Key('school_key').eq(school_key) & Key('academic_year').eq(academic_year)
    )
    add_timetables_from_response(response, timetables)
    logger.debug('Intermediary timetables count - ' + str(len(timetables)))
    while 'LastEvaluatedKey' in response:
        response = table.query(
            IndexName='school_key-academic_year-index',
            KeyConditionExpression=Key('school_key').eq(school_key) & Key('academic_year').eq(academic_year)
        )
        add_timetables_from_response(response, timetables)
        logger.debug('Intermediary fee_bills count - ' + str(len(timetables)))

    return timetables


def add_timetables_from_response(response, timetables):
    for item in response['Items']:
        timetable = TimeTable(item)
        timetables.append(timetable)


def delete_timetables(timetables):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TIMETABLE_TABLE)

    for timetable in timetables:
        logger.debug('deleting timetable' + timetable.time_table_key)
        try:
            table.delete_item(
                Key={
                    'time_table_key': timetable.time_table_key
                }
            )
        except ConnectionError as coe:
            logger.error('Could not delete ' + timetable.time_table_key + ' - ' + format(str(coe)))


def update_timetable(timetable):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TIMETABLE_TABLE)

    item = {
        'academic_year': timetable.academic_year,
        'school_key': timetable.school_key,
        'time_table_key': timetable.time_table_key,
    }

    if hasattr(timetable, 'class_key') and timetable.class_key is not None:
        item['class_key'] = timetable.class_key

    if hasattr(timetable, 'class_name') and timetable.class_name is not None:
        item['class_name'] = timetable.class_name

    if hasattr(timetable, 'division') and timetable.division is not None:
        item['division'] = timetable.division

    if hasattr(timetable, 'employee_key') and timetable.employee_key is not None:
        item['employee_key'] = timetable.employee_key

    if timetable.timetable is not None:
        item['timetable'] = get_timetable_dict(timetable.timetable)

    if hasattr(timetable, 'config_parameters') and timetable.config_parameters:
        item['config_parameters'] = get_config_parameters_dict(timetable.config_parameters)

    if (hasattr(timetable, 'generation_logs') and timetable.generation_logs is not None
            and len(timetable.generation_logs) > 0):
        item['generation_logs'] = get_generation_logs_dict(timetable.generation_logs)

    table.put_item(
        Item=item
    )


def get_generation_logs_dict(generation_logs):
    generation_logs_items = []
    for generation_log in generation_logs:
        sub_item = {
            'code': generation_log.code,
            'note': generation_log.note
        }
        generation_logs_items.append(sub_item)
    return generation_logs_items


def get_config_parameters_dict(config_parameters):
    item = {
        'subject_preferences': get_subject_preferences_dict(config_parameters.subject_preferences)
    }
    return item


def get_subject_preferences_dict(subject_preferences):
    subject_preferences_items = []
    for subject_preference in subject_preferences:
        sub_item = {
            'subject_code': subject_preference.subject_code,
            'periods_count_per_week': subject_preference.periods_count_per_week
        }
        sub_item['period_preferences'] = get_period_preferences_dict(subject_preference.period_preferences)
        subject_preferences_items.append(sub_item)
    return subject_preferences_items


def get_period_preferences_dict(period_preferences):
    period_preference_items = []
    for period_preference in period_preferences:
        pref_item = {
            'no_of_period': period_preference.no_of_period
        }
        if hasattr(period_preference, 'period_order_index'):
            pref_item['period_order_index'] = period_preference.period_order_index
        if hasattr(period_preference, 'day_codes'):
            pref_item['day_codes'] = period_preference.day_codes
        period_preference_items.append(pref_item)
    return period_preference_items


def get_timetable_dict(timetable):
    item = {
        'day_tables': get_day_tables_dict(timetable.day_tables)
    }
    return item


def get_day_tables_dict(day_tables):
    day_table_items = []
    for day_table in day_tables:
        item = {
            'day_code': day_table.day_code,
            'order_index': day_table.order_index
        }
        periods = []
        for period in day_table.periods:
            periods.append(vars(period))
        item['periods'] = periods
        day_table_items.append(item)
    return day_table_items


def get_timetable_entry(class_key, division):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TIMETABLE_TABLE)
    response = table.query(
        IndexName='class_key-division-index',
        KeyConditionExpression=Key('class_key').eq(class_key) & Key('division').eq(division)
    )
    for item in response['Items']:
        timetable = TimeTable(item)
        return timetable


def get_timetable_entry_by_employee(employee_key, academic_year):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TIMETABLE_TABLE)
    response = table.query(
        IndexName='employee_key-academic_year-index',
        KeyConditionExpression=Key('employee_key').eq(employee_key) & Key('academic_year').eq(academic_year)
    )
    for item in response['Items']:
        timetable = TimeTable(item)
        return timetable


def delete_timetable(time_table_key) :
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TIME_TABLE_TBL)
    response=table.delete_item(
      Key={ 
        'time_table_key':time_table_key
      }
    )
    return response
# def get_academic_config(school_key, academic_year):
#     dynamodb = boto3.resource('dynamodb')
#     table = dynamodb.Table(ACADEMIC_CONFIG)
#     response = table.query(
#         IndexName='school_key-academic_year-index',
#         KeyConditionExpression=Key('school_key').eq(school_key) & Key('academic_year').eq(academic_year)
#     )
#     for item in response['Items']:
#         academic_config = AcademicConfig(item)
#         return academic_config
#
#
# def get_academic_config_metadata_dict(school_key):
#     dynamodb = boto3.resource('dynamodb')
#     table = dynamodb.Table(ACADEMIC_CONFIG)
#     response = table.query(
#         IndexName='school_key-index',
#         KeyConditionExpression=Key('school_key').eq(school_key)
#     )
#     academic_config_dict = {}
#     academic_config_dict = add_academic_config_from_response(response, academic_config_dict)
#     while 'LastEvaluatedKey' in response:
#         response = table.query(
#             IndexName='school_key-index',
#             KeyConditionExpression=Key('school_key').eq(school_key),
#             ExclusiveStartKey=response['LastEvaluatedKey']
#         )
#         academic_config_dict = add_academic_config_from_response(response, academic_config_dict)
#     return academic_config_dict


# def add_academic_config_from_response(response, academic_config_dict):
#     for item in response['Items']:
#         academic_config = AcademicConfig(item)
#         #print(academic_config)
#         if academic_config.code is not None:
#             academic_config_dict[academic_config.code] = academic_config
#     return academic_config_dict
