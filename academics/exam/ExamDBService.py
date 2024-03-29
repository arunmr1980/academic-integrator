import boto3
import json
from boto3.dynamodb.conditions import Key,Attr
from academics.logger import GCLogger as logger
import academics.exam.Exam as exm

import operator

EXAM_TBL = 'Exam'


def delete_exam(exam_key) :
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(EXAM_TBL)
    response=table.delete_item(
      Key={
        'exam_key':exam_key
      }
    )
    return response


def add_or_update_exam(exam):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(EXAM_TBL)
    response = table.put_item(
        Item = exam
    )
    return response


def get_exams_by_class_key_and_division(class_key,division) :
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(EXAM_TBL)
    response = table.query(
        IndexName='class_key-index',
        KeyConditionExpression=Key('class_key').eq(class_key) 
    )
    exams_list = []
    if response.__contains__('Items') :
        for item in response['Items'] :
            if item['division'] == division :
                exam = exm.Exam(item)
                exams_list.append(exam)
    return exams_list

def get_all_exams_by_class_key_and_series_code(class_key, series_code):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(EXAM_TBL)
    exams = []
    response = table.query(
        IndexName='class_key-series_code-index',
        KeyConditionExpression=Key('class_key').eq(class_key) & Key('series_code').eq(series_code)
    )
    add_exams_from_response(response, exams)
    logger.debug('Intermediary exams count - ' + str(len(exams)))
    while 'LastEvaluatedKey' in response:
        response = table.query(
            IndexName='class_key-series_code-index',
           KeyConditionExpression=Key('class_key').eq(class_key) & Key('series_code').eq(series_code)
        )
        add_exams_from_response(response, exams)
        logger.debug('Intermediary exams count - ' + str(len(exams)))
    exams.sort(key = operator.itemgetter('date_time'))
    return make_exam_obj(exams)


def add_exams_from_response(response, exams):
    for item in response['Items']:
        exams.append(item)

def make_exam_obj(exams):
    exams_obj_list = []
    for item in exams:
        exam = exm.Exam(item)
        exams_obj_list.append(exam)
    return exams_obj_list




    
