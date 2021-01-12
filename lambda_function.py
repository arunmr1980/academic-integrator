import json
import boto3
import traceback
from academics.TimetableIntegrator import generate_and_save_calenders,update_subject_teacher_integrator
from academics.calendar.CalendarLessonPlanIntegrator import calendars_lesson_plan_integration, calendars_lesson_plan_integration_from_timetable
from academics.calendar.CalendarIntegrator import add_event_integrate_calendars, remove_event_integrate_calendars, integrate_update_period_calendars_and_lessonplans
import academics.logger.GCLogger as logger
from academics.exam.ExamIntegrator import integrate_add_exam_on_calendar,integrate_cancel_exam,integrate_update_exam_on_calendar
from academics.leave.LeaveIntegrator import integrate_add_leave_on_calendar,integrate_leave_cancel
from academics.lessonplan.LessonplanIntegrator import integrate_add_class_session_events

def lambda_handler(event, context):
	for record in event['Records']:
		payload=record["body"]
		request = json.loads(payload)
	try:
		request_type = request['request_type']
		if request_type == 'TIMETABLE_CALENDAR_LESSON_PLAN_GEN':
				timetable_to_calendar_and_lessonplan_integration(request)
		if request_type == 'TIMETABLE_TO_CALENDAR_GEN':
				timetable_to_calendar_integration(request)
		if request_type == 'CALENDAR_TO_LESSON_PLAN_GEN':
				calendar_to_lessonplan_integration(request)
		if request_type == 'HOLIDAY_LESSONPLAN_SYNC':
				add_event_calendar_lessonplan_integration(request)
		if request_type == 'REMOVE_EVENT_LESSONPLAN_SYNC':
				remove_event_calendar_lessonplan_integration(request)
		if request_type == 'PERIOD_UPDATE_SYNC':
				update_period_calendar_lessonplan_integration(request)
		if request_type == 'UPDATE_SUBJECT_TEACHER_SYNC':
				update_subject_teacher_integration(request)
		if request_type == 'EXAM_CALENDAR_SYNC':
				add_exam_integration(request)
		if request_type == 'EXAM-DELETE-SYNC':
				cancel_exam_integration(request)
		if request_type == 'TEACHER_LEAVE_SYNC':
				add_leave_integration(request)
		if request_type == 'TEACHER_LEAVE_CANCEL':
				cancel_leave_integration(request)
		if request_type == 'CLASS_SESSION_EVENT_SYNC':
				special_class_session_integration(request)
		if request_type == 'EXAM_UPDATE_CALENDAR_SYNC':
				update_exam_integration(request)
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


def remove_event_calendar_lessonplan_integration(request) :
	try :
		calendar_key = request['calendar_key']
		remove_event_integrate_calendars(calendar_key)
	except KeyError as ke:
		logger.info("Error in input. calendar_key not present")
		send_response(400,"input validation error")

def update_period_calendar_lessonplan_integration(request) :
	try :
		time_table_key = request['time_table_key']
		period_code = request['period_code']
		integrate_update_period_calendars_and_lessonplans(period_code, time_table_key)
	except KeyError as ke:
		logger.info("Error in input. calendar_key not present")
		send_response(400,"input validation error")


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
		logger.info('Processing for calendar lessonplan integration ' + subscriber_key )
		calendars_lesson_plan_integration(subscriber_key)
		send_response(200,"success")
	except KeyError as ke:
		logger.info("Error in input. time_table_key or academic_year not present")
		send_response(400,"input validation error")
	except:
		logger.info("Unexpected error ...")
		send_response(400,"unexpected error")


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
		logger.info("Unexpected error ...")
		send_response(400,"unexpected error")

def add_exam_integration(request) :
	try :
		series_code = request['series_code']
		class_info_key = request['class_info_key']
		division = request['division']

		integrate_add_exam_on_calendar(series_code,class_info_key,division)
	except KeyError as ke:
		logger.info("Error in input. series_code,class_info_key or division not present")
		send_response(400,"input validation error")

def cancel_exam_integration(request) :
	try :
		exam_series = request['exam_series']
		academic_year = request['academic_year']
		school_key = request['school_key']
		integrate_cancel_exam(exam_series,school_key,academic_year)
	except KeyError as ke:
		logger.info("Error in input. series_code,academic_year,school_key not present")
		send_response(400,"input validation error")

def update_exam_integration(request) :
	try :
		series_code = request['series_code']
		class_info_key = request['class_info_key']
		division = request['division']
		integrate_update_exam_on_calendar(series_code,class_info_key,division)
	except KeyError as ke:
		logger.info("Error in input. series_code,class_info_key or division not present")
		send_response(400,"input validation error")


def add_leave_integration(request) :
	try :
		leave_key= request['leave_key']
		integrate_add_leave_on_calendar(leave_key)
	except KeyError as ke:
		traceback.print_exc()
		logger.info("Error in input. leave key not present")
		send_response(400,"input validation error")

def cancel_leave_integration(request) :
	try :
		leave_key= request['leave_key']
		integrate_leave_cancel(leave_key)
	except KeyError as ke:
		traceback.print_exc()
		logger.info("Error in input. leave key not present")
		send_response(400,"input validation error")

def special_class_session_integration(request) :
	try :
		calendar_key = request['calendar_key']
		events = request['events']
		integrate_add_class_session_events(calendar_key, events)
	except KeyError as ke:
		logger.info("Error in input. events or calendar_key not present")
		send_response(400,"input validation error")

def send_response(status_code, message):
	data = {
		 "message": message
	}
	return {
			'statusCode': status_code,
			'body': {}
	}
