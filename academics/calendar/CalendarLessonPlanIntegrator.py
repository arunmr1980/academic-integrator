import academics.lessonplan.LessonPlan as lessonplan
from academics.logger import GCLogger as logger
import academics.calendar.CalendarDBService as calendar_service
from academics.lessonplan import LessonplanDBService as lessonplan_service
import academics.timetable.TimeTableDBService as timetable_service
import academics.timetable.KeyGeneration as key
import pprint
pp = pprint.PrettyPrinter(indent=4)

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
	logger.info('---Generated lesson plan count--- '+str(len(generated_lesson_plan_dict_list)))
	update_lesson_plan(generated_lesson_plan_dict_list)

def update_lesson_plan(generated_lesson_plan_dict_list) :
	for lesson_plan in generated_lesson_plan_dict_list :
		response = lessonplan_service.create_lessonplan(lesson_plan)
		logger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' Generated lesson plan uploaded '+str(lesson_plan['lesson_plan_key']))

def get_generated_lesson_plan_dict_list(generated_lesson_plan_list) :
	generated_lesson_plan_dict_list = []
	for generated_lesson_plan in generated_lesson_plan_list :
		generated_lesson_plan_dict = lessonplan.LessonPlan(None)
		generated_lesson_plan_dict = generated_lesson_plan_dict.make_lessonplan_dict(generated_lesson_plan)
		generated_lesson_plan_dict_list.append(generated_lesson_plan_dict)
	return generated_lesson_plan_dict_list

def integrate_calendar_to_lesson_plan(generated_class_calendar,current_lesson_plan_list):
	print(generated_class_calendar.calendar_key,'CALENDAR KEY---------->>>>')

	if hasattr(generated_class_calendar ,'events') :
		for event in generated_class_calendar.events :
			print(event.from_time,'<---------------------  FROM TIMEEEE')
			print(event.to_time,'<---------------------  TO TIMEEEE')
			print(event.params[1].value,"<<-----------------SUBJECT")
			print(event.params[0].value,"<<---------------PERIOD CODE")
			print('-------------------------------------')
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
										logger.info(' ---schedule added for lessonplan ' + str(current_lesson_plan.lesson_plan_key) + ' ---')
				else :
					if schedule_added == False : 
						add_sessions_on_root(current_lesson_plan,event,generated_class_calendar,schedule_added)

	return current_lesson_plan_list

def add_sessions_on_root(current_lesson_plan,event,generated_class_calendar,schedule_added) :
	schedule = create_schedule(event,generated_class_calendar)
	if hasattr(current_lesson_plan,'sessions') :
		session_order_index = len(current_lesson_plan.sessions) + 1
		session = create_session(schedule,session_order_index)
		if schedule not in current_lesson_plan.sessions :
			current_lesson_plan.sessions.append(session)
			schedule_added = True



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
		logger.info(' ---lesson plan exist in list ---')
		return current_lesson_plan_list
	else:
		lesson_plan_list = lessonplan_service.get_lesson_plan_list(class_key,class_div)
		logger.info(' ---getting lesson plan list from DB ---')
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
	else :
		gclogger.info('Params not found for event')
