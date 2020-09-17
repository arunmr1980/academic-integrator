import json
import boto3

from academics.TimetableIntegrator import generate_and_save_calenders
from academics.calendar.CalendarLessonPlanIntegrator import integrate_calendars_to_lesson_plan
import academics.logger.GCLogger as logger

def lambda_handler(event, context):

    for record in event['Records']:
       payload=record["body"]
       request = json.loads(payload)
       try:
          request_type = request['request_type']
          if request_type = 'TIMETABLE_TO_CALENDAR_GEN':
              timetable_to_calendar_integration(request)
          if request_type = 'CALENDAR_TO_LESSON_PLAN_GEN':
              calendar_to_lessonplan_integration(request)
       except:
          logger.info("Unexpected error ...")
          send_response(400,"unexpected error")


def timetable_to_calendar_integration(request):
       try:
          timetable_key = request['time_table_key']
          academic_year = request['academic_year']
          logger.info('Processing for timetable ' + timetable_key + ' and academic_year ' + academic_year)
          generate_and_save_calenders(timetable_key, academic_year)
          send_response(200,"success")
       except KeyError as ke:
          logger.info("Error in input. time_table_key or academic_year not present")
          send_response(400,"input validation error")
       except:
          logger.info("Unexpected error ...")
          send_response(400,"unexpected error")

def calendar_to_lessonplan_integration(request):
       try:
          class_info_key = request['class_info_key']
          division = request['division']
          subscriber_key = class_info_key+"-"+division
          class_calender_list = calendar_service.get_all_calendars(subscriber_key,'CLASS-DIV')
          logger.info('Processing for calendar lessonplan integartion ' + subscriber_key )
          integrate_calendars_to_lesson_plan(class_calender_list)
          send_response(200,"success")
       except KeyError as ke:
          logger.info("Error in input. time_table_key or academic_year not present")
          send_response(400,"input validation error")
       except:
          logger.info("Unexpected error ...")
          send_response(400,"unexpected error")


def send_response(status_code, message):
    data = {
       "message": message
    }
    return {
        'statusCode': status_code,
        'body': {}
    }
