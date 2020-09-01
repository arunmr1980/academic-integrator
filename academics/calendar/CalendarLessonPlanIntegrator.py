import academics.lessonplan.LessonPlan as lessonplan
from academics.logger import GCLogger as logger
import academics.calendar.CalendarDBService as calendar_service
from academics.lessonplan import LessonplanDBService as lessonplan_service




def integrate_calendar(calendar_key):
	current_calendar = calendar_service.get_calendar(calendar_key)
	generated_class_calendar = current_calendar
	current_lesson_plan_list = []
	current_lesson_plan_list = get_lesson_plan_list(current_calendar, current_lesson_plan_list)
	current_lesson_plan_list = integrate_calendar_to_lesson_plan(generated_class_calendar,current_lesson_plan_list)
	return current_lesson_plan_list


def integrate_calendars_to_lesson_plan(generated_class_calendar_list):
	current_lesson_plan_list = []
	for generated_class_calendar in generated_class_calendar_list :
		current_lesson_plan_list = get_lesson_plan_list(generated_class_calendar, current_lesson_plan_list)
		current_lesson_plan_list = integrate_calendar_to_lesson_plan(generated_class_calendar, current_lesson_plan_list)
	return current_lesson_plan_list


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
										logger.info(' ---schedule added for lessonplan ' + str(current_lesson_plan.lesson_plan_key) + ' ---')
	return current_lesson_plan_list


def get_lesson_plan_list(current_calendar, current_lesson_plan_list):
	class_key = current_calendar.subscriber_key[:-2]
	class_div = current_calendar.subscriber_key[-1:]

	if is_lesson_plan_exist(current_lesson_plan_list, class_key, class_div):
		return current_lesson_plan_list
	else:
		lesson_plan_list = lessonplan_service.get_lesson_plan_list(class_key,class_div)
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
			# print(param.value)
			if param.key == 'subject_key' :
				return param.value
	else :
		gclogger.info('Params not found for event')
