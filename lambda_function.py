import json
import boto3
import traceback
from academics.TimetableIntegrator import generate_and_save_calenders,update_subject_teacher_integrator
from academics.calendar.CalendarLessonPlanIntegrator import calendars_lesson_plan_integration, calendars_lesson_plan_integration_from_timetable
from academics.calendar.CalendarIntegrator import add_event_integrate_calendars, remove_event_integrate_calendars, integrate_update_period_calendars_and_lessonplans,make_event_objects
import academics.logger.GCLogger as logger
from academics.exam.ExamIntegrator import integrate_add_exam_on_calendar,integrate_cancel_exam,integrate_update_exam
from academics.leave.LeaveIntegrator import integrate_add_leave_on_calendar,integrate_leave_cancel,integrate_lessonplan_on_substitute_teacher
from academics.lessonplan.LessonplanIntegrator import integrate_add_class_session_events
from academics.classinfo.ClassInfoDBService import get_classinfo 

def lambda_handler(event, context):
	for record in event['Records']:
		payload=record["body"]
		request = json.loads(payload)
	try:
		request_type = request['request_type']
		if request_type == 'TIMETABLE_CALENDAR_LESSON_PLAN_GEN':
				# logger.info("--------- This SQS Request is to generate calendar,lessonplan from timetable ------------")
				timetable_to_calendar_and_lessonplan_integration(request)
		if request_type == 'TIMETABLE_TO_CALENDAR_GEN':
				# logger.info("--------- This SQS Request is to generate calendar from timetable ------------")
				timetable_to_calendar_integration(request)
		if request_type == 'CALENDAR_TO_LESSON_PLAN_GEN':
				# logger.info("--------- This SQS Request is to generate lessnplan from calendar ------------")
				calendar_to_lessonplan_integration(request)
		if request_type == 'HOLIDAY_LESSONPLAN_SYNC':
				# logger.info("--------- This SQS Request is to add holiday on calendar ------------")
				add_event_calendar_lessonplan_integration(request)
		if request_type == 'REMOVE_EVENT_LESSONPLAN_SYNC':
				# logger.info("--------- This SQS Request is to remove an event from calendar ------------")
				remove_event_calendar_lessonplan_integration(request)
		if request_type == 'PERIOD_UPDATE_SYNC':
				# logger.info("--------- This SQS Request is to update period from timetable ------------")
				update_period_calendar_lessonplan_integration(request)
		if request_type == 'UPDATE_SUBJECT_TEACHER_SYNC':
				# logger.info("--------- This SQS Request is to update subject teacher ------------")
				update_subject_teacher_integration(request)
		if request_type == 'EXAM_CALENDAR_SYNC':
				# logger.info("--------- This SQS Request is to add exam in calendar ------------")
				add_exam_integration(request)
		if request_type == 'EXAM-DELETE-SYNC':
				# logger.info("--------- This SQS Request is to delete exam from calendar ------------")
				cancel_exam_integration(request)
		if request_type == 'TEACHER_LEAVE_SYNC':
				# logger.info("--------- This SQS Request is to add teacher leave ------------")
				add_leave_integration(request)
		if request_type == 'TEACHER_LEAVE_CANCEL':
				# logger.info("--------- This SQS Request is to cancel teacher leave ------------")
				cancel_leave_integration(request)
		if request_type == 'CLASS_SESSION_EVENT_SYNC':
				# logger.info("--------- This SQS Request is to add class session on calendar (special class) ------------")
				special_class_session_integration(request)
		if request_type == 'EXAM_UPDATE_CALENDAR_SYNC':
				# logger.info("--------- This SQS Request is to update exam ------------")
				update_exam_integration(request)
		if request_type == 'TEACHER_SUBSTITUTE_SYNC':
				# logger.info("--------- This SQS Request is to substitute teacher ------------")
				teacher_substitution_integration(request)
	except:
		traceback.print_exc()
		logger.info("Unexpected error ...")
		send_response(400,"unexpected error")



def add_event_calendar_lessonplan_integration(request) :
	try :
		calendar_key = request['calendar_key']
		event_code = request['event_code']
		add_event_integrate_calendars(event_code,calendar_key)
	except KeyError as ke:
		logger.info("Error in input. event_code or calendar_key not present")
		send_response(400,"input validation error")
	logger.info(request)
	logger.info("--------- This SQS Request is to add holiday on calendar ------------")
	


def remove_event_calendar_lessonplan_integration(request) :
	try :
		calendar_key = request['calendar_key']
		events = request['events']
		events = make_event_objects(events)
		remove_event_integrate_calendars(calendar_key,events)
	except KeyError as ke:
		logger.info("Error in input. calendar_key not present")
		send_response(400,"input validation error")
	logger.info(request)
	logger.info("--------- This SQS Request is to remove an event from calendar ------------")

def update_period_calendar_lessonplan_integration(request) :
	try :
		time_table_key = request['time_table_key']
		period_code = request['period_code']
		integrate_update_period_calendars_and_lessonplans(period_code, time_table_key)
	except KeyError as ke:
		logger.info("Error in input. calendar_key not present")
		send_response(400,"input validation error")
	logger.info(request)
	logger.info("--------- This SQS Request is to update period from timetable ------------")


def timetable_to_calendar_and_lessonplan_integration(request):
	try:
		timetable_key = request['time_table_key']
		academic_year = request['academic_year']
		logger.info('Processing for timetable, calendar and lessonplan integration ' + timetable_key + ' and academic_year ' + academic_year )
		generate_and_save_calenders(timetable_key, academic_year)
		calendars_lesson_plan_integration_from_timetable(timetable_key, academic_year)
		send_response(200,"success")
	except KeyError as ke:
		logger.info("Error in input. time_table_key or academic_year not present")
		send_response(400,"input validation error")
	except:
		logger.info("Unexpected error ...")
		send_response(400,"unexpected error")
	logger.info(request)
	logger.info("--------- This SQS Request is to generate calendar,lessonplan from timetable ------------")


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
	logger.info(request)
	logger.info("--------- This SQS Request is to generate calendar from timetable ------------")


def calendar_to_lessonplan_integration(request):
	try:
		class_info_key = request['class_info_key']
		division = request['division']
		subscriber_key = class_info_key+"-"+division
		logger.info('Processing for calendar lessonplan integration ' + subscriber_key )
		calendars_lesson_plan_integration(subscriber_key)
		send_response(200,"success")
	except KeyError as ke:
		logger.info("Error in input. time_table_key or academic_year not present")
		send_response(400,"input validation error")
	except:
		logger.info("Unexpected error ...")
		send_response(400,"unexpected error")
	logger.info(request)
	logger.info("--------- This SQS Request is to generate lessnplan from calendar ------------")


def update_subject_teacher_integration(request):
	try:
		class_info_key = request['class_info_key']
		division = request['division']
		subject_code = request['subject_code']
		existing_teacher_emp_key = request['existing_teacher_emp_key']
		new_teacher_emp_key = request['new_teacher_emp_key']
		logger.info('Processing for existing emp_key  ' + existing_teacher_emp_key + 'and new teacher emp_key ' + new_teacher_emp_key )
		update_subject_teacher_integrator(division,class_info_key,subject_code,existing_teacher_emp_key,new_teacher_emp_key)
		send_response(200,"success")
	except KeyError as ke:
		logger.info("Error in input. class_info_key ,division,subject_code,existing_teacher_emp_key or new_teacher_emp_key not present")
		send_response(400,"input validation error")
	except:
		traceback.print_exc()
		logger.info("Unexpected error ...")
		send_response(400,"unexpected error")
	logger.info(request)
	logger.info("--------- This SQS Request is to update subject teacher ------------")

def add_exam_integration(request) :
	try :
		series_code = request['series_code']
		class_info_key = request['class_info_key']
		division = request['division']

		integrate_add_exam_on_calendar(series_code,class_info_key,division)
	except KeyError as ke:
		logger.info("Error in input. series_code,class_info_key or division not present")
		send_response(400,"input validation error")
	logger.info(request)
	logger.info("--------- This SQS Request is to add exam in calendar ------------")

def cancel_exam_integration(request) :
	try :
		exam_series = request['exam_series']
		academic_year = request['academic_year']
		school_key = request['school_key']
		integrate_cancel_exam(exam_series,school_key,academic_year)
	except KeyError as ke:
		logger.info("Error in input. series_code,academic_year,school_key not present")
		send_response(400,"input validation error")
	logger.info(request)
	logger.info("--------- This SQS Request is to delete exam from calendar ------------")

def update_exam_integration(request) :
	try :
		series_code = request['series_code']
		classes = request['classes']
		class_key = classes[0]['class_key']
		division = classes[0]['division']
		integrate_update_exam(series_code,class_key,division)

	except KeyError as ke:
		logger.info("Error in input. series_code,class_info_key or division not present")
		send_response(400,"input validation error")
	logger.info(request)
	logger.info("--------- This SQS Request is to update exam ------------")

def teacher_substitution_integration(request) :
	previous_substitution_emp_key = None
	previous_substitution_subject_code = None
	try :
		calendar_key = request['calendar_key']
		event_code = request['event_code']
		substitution_emp_key = request['substitution_emp_key']
		if request.__contains__('previous_substitution_emp_key') and request['previous_substitution_emp_key'] != 'null' :
			previous_substitution_emp_key = request['previous_substitution_emp_key']
		if request.__contains__('previous_substitution_subject_code') and request['previous_substitution_subject_code'] != 'null' :
			previous_substitution_subject_code = request['previous_substitution_subject_code']


		integrate_lessonplan_on_substitute_teacher(calendar_key,event_code,substitution_emp_key,previous_substitution_emp_key,previous_substitution_subject_code)
	except KeyError as ke:
		logger.info("Error in input. calendar_key,event_code,substitution_emp_key,previous_substitution_emp_key or previous_substitution_subject_code not present")
		send_response(400,"input validation error")
	logger.info(request)
	logger.info("--------- This SQS Request is to substitute teacher ------------")

def add_leave_integration(request) :
	try :
		leave_key = request['leave_key']
		integrate_add_leave_on_calendar(leave_key)
	except KeyError as ke:
		traceback.print_exc()
		logger.info("Error in input. leave key not present")
		send_response(400,"input validation error")
	logger.info(request)
	logger.info("--------- This SQS Request is to add teacher leave ------------")

def cancel_leave_integration(request) :
	try :
		leave_key = request['leave_key']
		integrate_leave_cancel(leave_key)
	except KeyError as ke:
		traceback.print_exc()
		logger.info("Error in input. leave key not present")
		send_response(400,"input validation error")
	logger.info(request)
	logger.info("--------- This SQS Request is to cancel teacher leave ------------")

def special_class_session_integration(request) :
	try :
		calendar_key = request['calendar_key']
		events = request['events']
		integrate_add_class_session_events(calendar_key, events)
	except KeyError as ke:
		logger.info("Error in input. events or calendar_key not present")
		send_response(400,"input validation error")
	logger.info(request)
	logger.info("--------- This SQS Request is to add class session on calendar (special class) ------------")

def send_response(status_code, message):
	data = {
		 "message": message
	}
	return {
			'statusCode': status_code,
			'body': {}
	}
