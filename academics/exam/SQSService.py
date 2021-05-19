from datetime import date, timedelta
import datetime
from datetime import datetime as dt
import calendar as cal
import academics.timetable.TimeTableDBService as timetable_service
import academics.TimetableIntegrator as timetable_integrator
from academics.logger import GCLogger as gclogger
import academics.timetable.TimeTable as ttable
import academics.timetable.KeyGeneration as key
import academics.calendar.Calendar as calendar
import academics.academic.AcademicDBService as academic_service
import academics.calendar.CalendarDBService as calendar_service
import academics.TimetableIntegrator as timetable_integrator
import academics.calendar.CalendarIntegrator as calendar_integrator
import academics.timetable.KeyGeneration as key
import academics.classinfo.ClassInfoDBService as class_info_service
import academics.calendar.Calendar as calendar
import academics.lessonplan.LessonplanIntegrator as lessonplan_integrator
from academics.exam import ExamDBService as exam_service
from academics.lessonplan import LessonplanDBService as lessonplan_service
import academics.academic.AcademicDBService as academic_service
import academics.lessonplan.LessonPlan as lpnr
import academics.lessonplan.LessonplanIntegrator as lesssonplan_integrator
import copy
import pprint
import boto3
import json
from boto3.dynamodb.conditions import Key,Attr
import os
pp = pprint.PrettyPrinter(indent=4)




# queue_url = os.environ.get('QUEUE_URL')
# queue_name = os.environ.get('QUEUE_EXAM_REPORTS')

queue_url = 'https://sqs.us-west-2.amazonaws.com/272936841180/exam-reports' 
queue_name = 'exam-reports'

sqs = boto3.client('sqs')

def send_to_sqs(message_body):
	deduplication_id = key.generate_key(16)
    response = sqs.send_message(
        QueueUrl = queue_url,
        MessageGroupId = queue_name,
        MessageDeduplicationId = deduplication_id,
        MessageBody = (
             json.dumps(message_body)
            )
    )
    gclogger.info(str(response) + " ---------------- SQS RESPONSE --------------------")



