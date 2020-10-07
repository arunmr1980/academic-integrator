import datetime
from academics.timetable.AcademicConfiguration import AcademicConfiguration
from academics.timetable.TimeTable import TimeTable
import boto3
from boto3.dynamodb.conditions import Key,Attr

ACADEMIC_CONFIG_TBL = 'AcademicConfig'


def get_academig(school_key, academic_year):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(ACADEMIC_CONFIG_TBL)
    response = table.query(
        IndexName = 'school_key-academic_year-index',
        KeyConditionExpression = Key('school_key').eq(school_key) & Key('academic_year').eq(academic_year)
    )
    for item in response['Items']:
        academic_config = AcademicConfiguration(item)
        return academic_config


def get_academic_year(school_key, calendar_date):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(ACADEMIC_CONFIG_TBL)
    response = table.query(
        IndexName = 'school_key-index',
        KeyConditionExpression = Key('school_key').eq(school_key) 
    )
    for item in response['Items']:
        academic_config = AcademicConfiguration(item)
        academic_year = find_academic_year(academic_config,calendar_date)
        if academic_year is not None :
            return academic_config


def find_academic_year(academic_config,calendar_date) :
    start_date = academic_config.start_date
    end_date = academic_config.end_date

    start_date_year = int(start_date[:4])
    start_date_month = int(start_date[5:7])
    start_date_day = int(start_date[-2:])

    end_date_year = int(end_date[:4])
    end_date_month = int(end_date[5:7])
    end_date_day = int(end_date[-2:])

    calendar_date_year = int(calendar_date[:4])
    calendar_date_month = int(calendar_date[5:7])
    calendar_date_day = int(calendar_date[-2:])

    start_date = datetime.datetime(start_date_year, start_date_month, start_date_day)
    end_date = datetime.datetime(end_date_year, end_date_month, end_date_day)
    calendar_date = datetime.datetime(calendar_date_year, calendar_date_month, calendar_date_day)

    if start_date <= calendar_date <= end_date :
        return academic_config.academic_year



def create_academic_config(academic_configuration):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(ACADEMIC_CONFIG_TBL)
    response = table.put_item(
        Item = academic_configuration
    )
    return response



def delete_academic_config(academic_config_key) :
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(ACADEMIC_CONFIG_TBL)
    response=table.delete_item(
      Key={ 
        'academic_config_key':academic_config_key
      }
    )
    return response





