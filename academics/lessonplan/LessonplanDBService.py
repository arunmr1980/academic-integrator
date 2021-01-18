import boto3
from boto3.dynamodb.conditions import Key, Attr
import academics.lessonplan.LessonPlan as lessonplan


LESSON_PLAN = "LessonPlan"


def get_lessonplan(lesson_plan_key) :
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(LESSON_PLAN)
    response=table.get_item(
      Key={
        'lesson_plan_key':lesson_plan_key
      }
    )
    if response['Item'] is not None:
        return lessonplan.LessonPlan(response['Item'])

def create_lessonplan(lessonplan):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(LESSON_PLAN)
    response = table.put_item(
        Item = lessonplan
    )
    return response


def get_lesson_plan_list(class_key, division):
    dynamo_db = boto3.resource('dynamodb')
    table = dynamo_db.Table(LESSON_PLAN)
    response = table.query(
        KeyConditionExpression=Key('class_key').eq(class_key) & Key('division').eq(division),
        IndexName='class_key-division-index'
    )
    lesson_plan_list = []
    for item in response['Items']:
        lesson_plan = lessonplan.LessonPlan(item)
        lesson_plan_list.append(lesson_plan)
    return lesson_plan_list


def delete_lessonplan(lesson_plan_key) :
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(LESSON_PLAN)
    response=table.delete_item(
      Key={
        'lesson_plan_key':lesson_plan_key
      }
    )
    return response

def get_lessonplan_by_school_key(school_key) :
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(LESSON_PLAN)
    response = table.query(
        IndexName='school_key-index',
        KeyConditionExpression=Key('school_key').eq(school_key) 
    )
    lesson_plan_list = []
    for item in response['Items']:
        lesson_plan = lessonplan.LessonPlan(item)
        lesson_plan_list.append(lesson_plan)
    return lesson_plan_list
