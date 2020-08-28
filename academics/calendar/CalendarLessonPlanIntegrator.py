import academics.lessonplan.LessonPlan as lessonplan
from academics.logger import GCLogger as logger




def integrate_calendar(calendar_key):
	pass

def integrate_calendar_to_lesson_plan(generated_class_calendar_dict,current_lesson_plan_list):
	for generated_class_calendar in generated_class_calendar_dict.values() :
			if hasattr(generated_class_calendar ,'events') :
				for event in generated_class_calendar.events :
					schedule_added = True
					subject_code = get_subject_code(event)
					current_lesson_plan = get_lesson_plan(subject_code,current_lesson_plan_list)
					if hasattr(current_lesson_plan ,'topics') and schedule_added == True:
						for topics in current_lesson_plan.topics :
							for topic in topics.topics :
								if schedule_added == True:
									for session in topic.sessions :
										if schedule_added == True:
											if not hasattr(session ,'schedule') :
												schedule = create_schedule(event,generated_class_calendar)
												session.schedule = schedule
												schedule_added = False
												logger.info(' ---schedule added for lessonplan ' + str(current_lesson_plan.lesson_plan_key) + ' ---')


	return current_lesson_plan_list
												

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






