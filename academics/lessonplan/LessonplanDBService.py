import boto3
from boto3.dynamodb.conditions import Key, Attr
import academics.lessonplan.LessonPlan as lessonplan


LESSON_PLAN = "LessonPlan"

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