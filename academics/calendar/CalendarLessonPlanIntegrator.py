import academics.lessonplan.LessonPlan as lessonplan
from academics.logger import GCLogger as logger
import academics.calendar.CalendarDBService as calendar_service
from academics.lessonplan import LessonplanDBService as lessonplan_service
import academics.timetable.TimeTableDBService as timetable_service
import academics.timetable.KeyGeneration as key
import academics.academic.AcademicDBService as academic_service
from datetime import datetime as dt,date, timedelta
import academics.classinfo.ClassInfoDBService as class_info_service
import academics.calendar.Calendar as cldr
import academics.lessonplan.LessonPlan as lnpr
from academics.TimetableIntegrator import generate_and_save_calenders,update_subject_teacher_integrator

import pprint
pp = pprint.PrettyPrinter(indent=4)



def remove_calendar_lessonplan_integration_by_class_key(class_info_key, school_key,academic_year):
	class_info = class_info_service.get_classinfo(class_info_key)

	logger.info('---Remove_calendar_lessonplan_integration_by_class_key---- ')
	academic_configuration = academic_service.get_academig(school_key,academic_year)
	start_date = academic_configuration.start_date
	end_date = academic_configuration.end_date
	format = '%Y-%m-%d'

	process_start_date = dt.strptime(start_date, format) 
	#   ----------------Need to remove from current date--------------------

	process_start_date = process_start_date.date()

	process_end_date = dt.strptime(end_date, format)
	process_end_date = process_end_date.date() + timedelta(days=1)

	while str(process_end_date) != str(process_start_date):
		for cls in class_info:
			for div in cls.divisions:
				class_calendars =  calendar_service.get_calendar_by_date_and_key(str(process_start_date), str(class_info_key)+'-'+str(div.code) ):
				for calendar in class_calendars:
					removed_event_list = []
					add_event_list = []
					for event in calendar.events:
						if event.event_type == 'CLASS_SESSION':
							removed_event_list.append(event)
						else:
							add_event_list.append(event)
					calendar.events = add_event_list
					cal = cldr.Calendar(None)
					calendar_dict = cal.make_calendar_dict(calendar)
					calendar_service.add_or_update_calendar(calendar_dict)
				
				for event in removed_event_list:
					employee_key = get_employee_key(event.params)
					employee_calendars =  calendar_service.get_calendar_by_date_and_key(str(process_start_date), employee_key ):
					add_event_list = []
					for event in employee_calendars[0].events:
						if event.event_code != event.event_code:
							add_event_list.append(event)
					calendar.events = add_event_list
					cal = cldr.Calendar(None)
					calendar_dict = cal.make_calendar_dict(calendar)
					calendar_service.add_or_update_calendar(calendar_dict)


def get_employee_key(params) :
	for param in params :
		if param.key == 'teacher_emp_key' :
			return param.value


def remove_calendar_lessonplan_integration(school_key,academic_year) :
	logger.info('---Remove_calendar_lessonplan_timetable_integration---- ')
	academic_configuration = academic_service.get_academig(school_key,academic_year)
	start_date = academic_configuration.start_date
	end_date = academic_configuration.end_date
	format = '%Y-%m-%d'

	process_start_date = dt.strptime(start_date, format)
	process_start_date = process_start_date.date()

	process_end_date = dt.strptime(end_date, format)
	process_end_date = process_end_date.date() + timedelta(days=1)

	while str(process_end_date) != str(process_start_date):
		logger.info('---Process on date--- '+str(process_start_date))
		calendars =  calendar_service.get_all_calendars_by_school_key_and_date(school_key, str(process_start_date) )
		for calendar in calendars:
			if calendar.subscriber_type == 'CLASS-DIV':
				event_list = []
				for event in calendar.events:
					if event.event_type != 'CLASS_SESSION':
						event_list.append(event)
				calendar.events = event_list
				cal = cldr.Calendar(None)
				calendar_dict = cal.make_calendar_dict(calendar)
				calendar_service.add_or_update_calendar(calendar_dict)

			elif calendar.subscriber_type == 'EMPLOYEE':
				logger.info('---Deleting employee calender on date--- '+str(process_start_date))
				calendar_service.delete_calendar(calendar.calendar_key)
		process_start_date = process_start_date + timedelta(days=1)


	remove_calendar_schedules_from_lp(school_key,academic_year)
	reintegrate_all_class_timetable_calendar_lessonplan(school_key,academic_year)


def remove_calendar_schedules_from_lp(school_key,academic_year):
	logger.info('---Removing schedules from lessonplan--- ')
	class_list = class_info_service.get_classinfo_list(school_key,academic_year)
	for cls in class_list:
		for div in cls.divisions:
			lessonplans = lessonplan_service.get_lesson_plan_list(cls.class_info_key,div.code )
			for lessonplan in lessonplans:
				lessonplan.sessions = []
				for topics in lessonplan.topics:
					for topic in topics.topics:
						topic.schedule = None
						for session in topic.sessions:
							session.schedule = None
				lp = lnpr.LessonPlan(None)
				lp_dict = lp.make_lessonplan_dict(lessonplan)
				lessonplan_service.create_lessonplan(lp_dict)

	logger.info('---CALENDAR LESSONPLAN CLEAN UP COMPLETED--- ')


def reintegrate_all_class_timetable_calendar_lessonplan(school_key,academic_year):
	class_list = class_info_service.get_classinfo_list(school_key,academic_year)
	for cls in class_list:
		for div in cls.divisions:
			timetable = timetable_service.get_timetable_by_class_key_and_division(cls.class_info_key, div.code)
			if hasattr(timetable, 'status') and timetable.status == 'PUBLISHED':
				generate_and_save_calenders(timetable.time_table_key, academic_year)
				calendars_lesson_plan_integration_from_timetable(timetable.time_table_key, academic_year)



def integrate_calendar_to_single_lessonplan(lesson_plan_key) :
	current_lessonplan = lessonplan_service.get_lessonplan(lesson_plan_key)
	class_key = current_lessonplan.class_key
	division = current_lessonplan.division
	subscriber_key = class_key +'-' + division
	class_calender_list = calendar_service.get_all_calendars_by_key_and_type(subscriber_key,'CLASS-DIV')
	updated_lessonplan = integrate_calendars_to_single_lessonplan(class_calender_list,current_lessonplan)
	lp = lessonplan.LessonPlan(None)
	updated_lessonplan_dict = lp.make_lessonplan_dict(updated_lessonplan)
	response = lessonplan_service.create_lessonplan(updated_lessonplan_dict)
	# gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' ------- A updated lessonplan uploaded --------- '+str(updated_lessonplan_dict['lesson_plan_key']))

def integrate_calendars_to_single_lessonplan(class_calender_list,current_lesson_plan) :
	for generated_class_calendar in class_calender_list :
		if hasattr(generated_class_calendar ,'events') :
			for event in generated_class_calendar.events :
				schedule_added = False
				subject_code = get_subject_code(event)
				if current_lesson_plan.subject_code == subject_code :
					if hasattr(current_lesson_plan ,'topics') and schedule_added == False:
						for topics in current_lesson_plan.topics :
							for topic in topics.topics :
								if schedule_added == False:
									for session in topic.sessions :
										if schedule_added == False:
											if not hasattr(session ,'schedule') :
												schedule = create_schedule(event,generated_class_calendar)
												session.schedule = schedule
												schedule_added = True
												# logger.info(' ---schedule added for lessonplan ' + str(current_lesson_plan.lesson_plan_key) + ' ---')
						else :
							if schedule_added == False : 
								add_sessions_on_root(current_lesson_plan,event,generated_class_calendar,schedule_added)

	return current_lesson_plan

	


def calendars_lesson_plan_integration(subscriber_key) :
	class_calender_list = calendar_service.get_all_calendars_by_key_and_type(subscriber_key,'CLASS-DIV')
	integrate_calendars_to_lesson_plan(class_calender_list)

def calendars_lesson_plan_integration_from_timetable(timetable_key, academic_year) :
	timetable = timetable_service.get_time_table(timetable_key)
	subscriber_key = timetable.class_key + "-" + timetable.division
	class_calender_list = calendar_service.get_all_calendars_by_key_and_type(subscriber_key,'CLASS-DIV')
	integrate_calendars_to_lesson_plan(class_calender_list)

def integrate_calendar(calendar_key):
	current_calendar = calendar_service.get_calendar(calendar_key)
	generated_class_calendar = current_calendar
	current_lesson_plan_list = []
	current_lesson_plan_list = get_all_lesson_plan_list(current_calendar, current_lesson_plan_list)
	current_lesson_plan_list = integrate_calendar_to_lesson_plan(generated_class_calendar,current_lesson_plan_list)
	generated_lesson_plan_dict_list = get_generated_lesson_plan_dict_list(current_lesson_plan_list)
	update_lesson_plan(generated_lesson_plan_dict_list)


def integrate_calendars_to_lesson_plan(generated_class_calendar_list):
	current_lesson_plan_list = []
	for generated_class_calendar in generated_class_calendar_list :
		current_lesson_plan_list = get_all_lesson_plan_list(generated_class_calendar, current_lesson_plan_list)
		current_lesson_plan_list = integrate_calendar_to_lesson_plan(generated_class_calendar, current_lesson_plan_list)

	generated_lesson_plan_dict_list = get_generated_lesson_plan_dict_list(current_lesson_plan_list)
	# logger.info('---Generated lesson plan count--- '+str(len(generated_lesson_plan_dict_list)))
	update_lesson_plan(generated_lesson_plan_dict_list)

def update_lesson_plan(generated_lesson_plan_dict_list) :
	for lesson_plan in generated_lesson_plan_dict_list :
		response = lessonplan_service.create_lessonplan(lesson_plan)
		# logger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' Generated lesson plan uploaded '+str(lesson_plan['lesson_plan_key']))

def get_generated_lesson_plan_dict_list(generated_lesson_plan_list) :
	generated_lesson_plan_dict_list = []
	for generated_lesson_plan in generated_lesson_plan_list :
		generated_lesson_plan_dict = lessonplan.LessonPlan(None)
		generated_lesson_plan_dict = generated_lesson_plan_dict.make_lessonplan_dict(generated_lesson_plan)
		generated_lesson_plan_dict_list.append(generated_lesson_plan_dict)
	return generated_lesson_plan_dict_list

def integrate_calendar_to_lesson_plan(generated_class_calendar,current_lesson_plan_list):
	if hasattr(generated_class_calendar ,'events') :
		for event in generated_class_calendar.events :
			schedule_added = False
			subject_code = get_subject_code(event)
			current_lesson_plan = get_lesson_plan(subject_code,current_lesson_plan_list)
			if hasattr(current_lesson_plan ,'topics') and schedule_added == False:
				for topics in current_lesson_plan.topics :
					for topic in topics.topics :
						if schedule_added == False:
							for session in topic.sessions :
								if schedule_added == False:
									if not hasattr(session ,'schedule') :
										schedule = create_schedule(event,generated_class_calendar)
										session.schedule = schedule
										schedule_added = True
										# logger.info(' ---schedule added for lessonplan ' + str(current_lesson_plan.lesson_plan_key) + ' ---')
				else :
					if schedule_added == False : 
						add_sessions_on_root(current_lesson_plan,event,generated_class_calendar,schedule_added)

	return current_lesson_plan_list

def add_sessions_on_root(current_lesson_plan,event,generated_class_calendar,schedule_added) :
	schedule = create_schedule(event,generated_class_calendar)
	if hasattr(current_lesson_plan,'sessions') :
		session_order_index = len(current_lesson_plan.sessions) + 1
		session = create_session(schedule,session_order_index)
		current_lesson_plan.sessions.append(session)



def create_session(schedule,session_order_index) :
	session = lessonplan.Session(None)
	session.schedule = schedule
	session.order_index = session_order_index
	session.code = key.generate_key(4)
	return session














def get_all_lesson_plan_list(current_calendar, current_lesson_plan_list):
	class_key = current_calendar.subscriber_key[:-2]
	class_div = current_calendar.subscriber_key[-1:]

	if is_lesson_plan_exist(current_lesson_plan_list, class_key, class_div):
		# logger.info(' ---lesson plan exist in list ---')
		return current_lesson_plan_list
	else:
		lesson_plan_list = lessonplan_service.get_lesson_plan_list(class_key,class_div)
		# logger.info(' ---getting lesson plan list from DB ---')
		for lesson_plan in lesson_plan_list:
			current_lesson_plan_list.append(lesson_plan)
		return current_lesson_plan_list


def is_lesson_plan_exist(current_lesson_plan_list, class_key, class_div):
	for lesson_plan in current_lesson_plan_list:
		if lesson_plan.class_key == class_key and lesson_plan.division == class_div:
			return True



def create_schedule(event,generated_class_calendar) :
	schedule = lessonplan.Schedule(None)
	schedule.calendar_key = generated_class_calendar.calendar_key
	schedule.event_code = event.event_code
	schedule.start_time = event.from_time
	schedule.end_time = event.to_time
	return schedule


def get_lesson_plan(subject_code,current_lesson_plan_list) :
		for current_lesson_plan in current_lesson_plan_list :
			if current_lesson_plan.subject_code == subject_code :
				return current_lesson_plan


def get_subject_code(event) :
	if hasattr(event, 'params') :
		for param in event.params :
			if param.key == 'subject_key' :
				return param.value
	# else :
	# 	gclogger.info('Params not found for event')
