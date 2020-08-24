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





