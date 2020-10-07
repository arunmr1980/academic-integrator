import boto3
import time
import json
import decimal
from boto3.dynamodb.conditions import Key, Attr
from academics.classinfo.ClassInfo import ClassInfo


CLASSINFO_TABLE = 'ClassInfo'

def get_classinfo_list(school_key, academic_year):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(CLASSINFO_TABLE)
    response = table.query(
        IndexName='school_key-academic_year-index',
        KeyConditionExpression=Key('school_key').eq(school_key) & Key('academic_year').eq(academic_year),
        FilterExpression=(Attr ('type').eq ('regular'))
    )
    classes_list = []
    for i in response['Items']:
        classes_list.append(ClassInfo(i))
    return classes_list


def get_classinfo(class_info_key):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(CLASSINFO_TABLE)
    response = table.get_item(
        Key={
        'class_info_key': class_info_key
        }
    )
    class_info = None
    try:
        class_info = ClassInfo(response['Item'])
    except KeyError:
        print('ClassInfoService - get_classinfo() - KeyError')
    return class_info


def add_or_update_class_info(class_info):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(CLASSINFO_TABLE)
    response = table.put_item(
        Item = class_info
    )
    return response
