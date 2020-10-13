import datetime
from academics.TimetableIntegrator import *
import academics.classinfo.ClassInfoDBService as class_info_service
import academics.lessonplan.LessonplanDBService as lessonplan_service
import academics.lessonplan.LessonplanDBService as lessonplan_service
import academics.school.SchoolDBService as school_service
import academics.lessonplan.LessonPlan as lessonplan
import academics.academic.AcademicDBService as academic_service


def integrate_holiday_lessonplan(event_code,calendar_key) :
	updated_lessonplan_list = []
	calendar = calendar_service.get_calendar(calendar_key)
	school_key = calendar.institution_key
	academic_configuration = academic_service.get_academic_year(school_key, calendar.calendar_date)
	academic_year = academic_configuration.academic_year
	event = get_event_from_calendar(calendar,event_code)
	gclogger.info("EVENT START TIME AND END TIME ----------------->" + str(event.from_time) + str(event.to_time))
	day_code = findDay(calendar.calendar_date).upper()[0:3]
	subscriber_key = calendar.subscriber_key
	gclogger.info("subscriber_key------------------->>>>" + str(subscriber_key))

	if calendar.subscriber_type == 'CLASS-DIV' :
		class_key = subscriber_key[:-2]
		division = subscriber_key[-1:]
		timetable = timetable_service.get_timetable_entry(class_key, division)
		gclogger.info("school key--------------->" + str(school_key))
		gclogger.info("class keyyyy------>" + str(class_key))
		gclogger.info("Division--------->" + str(division))
		current_lesson_plan_list = lessonplan_service.get_lesson_plan_list(class_key,division)
		for current_lessonplan in current_lesson_plan_list :
			if current_lessonplan.class_key == class_key and current_lessonplan.division == division :
				updated_lessonplan = holiday_calendar_to_lessonplan_integrator(current_lessonplan,event,calendar,academic_configuration,timetable,day_code)
				lp = lessonplan.LessonPlan(None)
				updated_lessonplan_dict = lp.make_lessonplan_dict(updated_lessonplan)
				response = lessonplan_service.create_lessonplan(updated_lessonplan_dict)
				gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' Updated Lesson Plan  uploaded '+str(current_lesson_plan_dict['lesson_plan_key']))
				updated_lessonplan = lessonplan_service.get_lessonplan(updated_lessonplan_dict['lesson_plan_key'])
				updated_lessonplan_list.append(updated_lessonplan)

	else :
		class_info_list = class_info_service.get_classinfo_list(school_key,academic_year)
		for class_info in class_info_list :
			if hasattr(class_info, 'divisions') :
				for div in class_info.divisions :
					division = div.name
					class_key = class_info.class_info_key
					if division != 'NONE':
						timetable = timetable_service.get_timetable_entry(class_key, division)

						gclogger.info("class keyyyy------> " + str(class_key))
						gclogger.info("Division---------> " + str(division))
						current_lesson_plan_list = lessonplan_service.get_lesson_plan_list(class_key,division)
						for current_lessonplan in current_lesson_plan_list :
							updated_lessonplan = holiday_calendar_to_lessonplan_integrator(current_lessonplan,event,calendar,academic_configuration,timetable,day_code)
							lp = lessonplan.LessonPlan(None)
							updated_lessonplan_dict = lp.make_lessonplan_dict(updated_lessonplan)
							response = lessonplan_service.create_lessonplan(updated_lessonplan_dict)
							gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' Updated Lesson Plan  uploaded '+str(updated_lessonplan_dict['lesson_plan_key']))
							updated_lessonplan = lessonplan_service.get_lessonplan(updated_lessonplan_dict['lesson_plan_key'])
							updated_lessonplan_list.append(updated_lessonplan)
	# return updated_lessonplan_list
	upload_updated_lessonplans(updated_lessonplan_list)

def upload_updated_lessonplans(updated_lessonplan_list) :
	for lesson_plan in updated_lessonplan_list :
		lp = lessonplan.LessonPlan(None)
		lessonplan_dict = lp.make_lessonplan_dict(lesson_plan)
		response = lessonplan_service.create_lessonplan(lessonplan_dict)
		gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' Updated lesson plan uploaded '+str(lessonplan_dict['lesson_plan_key']))


def integrate_cancelled_holiday_lessonplan(calendar_key) :
	updated_lessonplan_list = []
	calendar = calendar_service.get_calendar(calendar_key)
	school_key = calendar.institution_key
	academic_configuration = academic_service.get_academic_year(school_key, calendar.calendar_date)
	academic_year = academic_configuration.academic_year
	day_code = findDay(calendar.calendar_date).upper()[0:3]
	if calendar.subscriber_type == 'CLASS-DIV' :
		class_key = subscriber_key[:-2]
		division = subscriber_key[-1:]
		# timetable = timetable_service.get_timetable_entry(class_key, division)
		current_lesson_plan_list = lessonplan_service.get_lesson_plan_list(class_key,division)
		for current_lessonplan in current_lesson_plan_list :
			if current_lessonplan.class_key == class_key and current_lessonplan.division == division :
				updated_lessonplan = cancelled_holiday_calendar_to_lessonplan_integrator(current_lessonplan,calendar,day_code)
				lp = lessonplan.LessonPlan(None)
				updated_lessonplan_dict = lp.make_lessonplan_dict(updated_lessonplan)
				response = lessonplan_service.create_lessonplan(updated_lessonplan_dict)
				gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' Updated Lesson Plan  uploaded '+str(current_lesson_plan_dict['lesson_plan_key']))
				updated_lessonplan = lessonplan_service.get_lessonplan(updated_lessonplan_dict['lesson_plan_key'])
				updated_lessonplan_list.append(updated_lessonplan)
	else :
		class_info_list = class_info_service.get_classinfo_list(school_key,academic_year)
		for class_info in class_info_list :
			if hasattr(class_info, 'divisions') :
				for div in class_info.divisions :
					division = div.name
					class_key = class_info.class_info_key
					if division != 'NONE':
						# timetable = timetable_service.get_timetable_entry(class_key, division)

						gclogger.info("class keyyyy------> " + str(class_key))
						gclogger.info("Division---------> " + str(division))
						current_lesson_plan_list = lessonplan_service.get_lesson_plan_list(class_key,division)
						for current_lessonplan in current_lesson_plan_list :
							updated_lessonplan = cancelled_holiday_calendar_to_lessonplan_integrator(current_lessonplan,calendar,day_code)
							lp = lessonplan.LessonPlan(None)
							updated_lessonplan_dict = lp.make_lessonplan_dict(updated_lessonplan)
							response = lessonplan_service.create_lessonplan(updated_lessonplan_dict)
							gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' Updated Lesson Plan  uploaded '+str(updated_lessonplan_dict['lesson_plan_key']))
							updated_lessonplan = lessonplan_service.get_lessonplan(updated_lessonplan_dict['lesson_plan_key'])
							updated_lessonplan_list.append(updated_lessonplan)
	# return updated_lessonplan_list
	upload_updated_lessonplans(updated_lessonplan_list)




def get_event_from_calendar(calendar,event_code) :
		for event in calendar.events :
			if event.event_code == event_code :
				return event


def holiday_calendar_to_lessonplan_integrator(current_lessonplan,event,calendar,academic_configuration,timetable,day_code) :
	gclogger.info("LESSON PLAN KEY------------------->  " + str(current_lessonplan.lesson_plan_key))
	holiday_period_list = generate_holiday_period_list(event,calendar,academic_configuration,timetable,day_code)
	for holiday_period in holiday_period_list :
		gclogger.info("---------- Holiday Period----  " + str(holiday_period.period_code)+' -----------------')
	schedules = find_schedules(current_lessonplan,holiday_period_list,calendar.calendar_date)
	gclogger.info("---------- Schedule to remove is   -----------------")
	for schedule in schedules :
		gclogger.info("---------- " + str(holiday_period.period_code) + " ---------")

	current_lessonplan = remove_shedules(schedules,current_lessonplan)
	shedule_list = get_all_remaining_schedules(current_lessonplan)
	current_lessonplan = get_lesson_plan_after_remove_all_shedules(current_lessonplan)
	current_lessonplan = get_updated_lesson_plan(shedule_list,current_lessonplan)
	return current_lessonplan

def cancelled_holiday_calendar_to_lessonplan_integrator(current_lessonplan,calendar,day_code) :
	after_calendar_date_schedules_list = []
	events = get_class_session_events(calendar.events)
	gclogger.info("LESSON PLAN KEY ------------------->  " + str(current_lessonplan.lesson_plan_key))
	current_lessonplan = remove_schedule_after_calendar_date(current_lessonplan,calendar.calendar_date,after_calendar_date_schedules_list)
	current_lessonplan = add_calendar_schedules_to_lesson_plan(current_lessonplan,events,calendar)
	current_lessonplan = add_shedule_after_calendar_date(after_calendar_date_schedules_list,current_lessonplan)
	# print(after_calendar_date_schedules_list,"sessions to add on rooot =============<<<<<>>>>>>>>>>")
	return current_lessonplan

def get_class_session_events(events) :
	event_list = []
	for event in events:
		if event.event_type == 'CLASS_SESSION':
			event_list.append(event)
	return event_list

def add_shedule_after_calendar_date(shedule_list,current_lessonplan) :
	gclogger.info('Adding schedules after calendar date -------------')
	index = -1
	for main_topic in current_lessonplan.topics :
		for topic in main_topic.topics :
			for session in topic.sessions :
				if index < len(shedule_list) :
					if not hasattr(session , 'schedule') :
						index += 1
						session.schedule = shedule_list[index]
						# shedule_list.remove(shedule_list[index])
						gclogger.info('A schedule is added ' + str(shedule_list[index].start_time) + ' --- ' + str(shedule_list[index].start_time) )
	return current_lessonplan

def add_schedule_to_lessonplan(current_lessonplan,schedule) :
	schedule_added = False
	for main_topic in current_lessonplan.topics :
		for topic in main_topic.topics :
			if schedule_added == False :
				for session in topic.sessions :
					if schedule_added == False :
						if not hasattr(session , 'schedule') :
							session.schedule = schedule
							schedule_added = True
							gclogger.info(' ------------- schedule added for lessonplan ' + str(current_lessonplan.lesson_plan_key) + ' -------------')

	return current_lessonplan


def create_schedule(event,calendar) :
	schedule = lessonplan.Schedule(None)
	schedule.calendar_key = calendar.calendar_key
	schedule.event_code = event.event_code
	schedule.start_time = event.from_time
	schedule.end_time = event.to_time
	return schedule


def add_calendar_schedules_to_lesson_plan(current_lessonplan,events,calendar) :
	for event in events :
		subject_code = get_subject_code(event)
		if current_lessonplan.subject_code == subject_code :
			schedule = create_schedule(event,calendar)
			add_schedule_to_lessonplan(current_lessonplan,schedule)
	return current_lessonplan

def get_subject_code(event) :
	if hasattr(event, 'params') :
		for param in event.params :
			if param.key == 'subject_key' :
				return param.value
	else :
		gclogger.info('Params not found for event')


def remove_schedule_after_calendar_date(current_lessonplan,calendar_date,after_calendar_date_schedules_list) :
	gclogger.info('Schedules to remove is ----------------------------')
	for main_topic in current_lessonplan.topics :
		for topic in main_topic.topics :
			for session in topic.sessions :
				if hasattr(session , 'schedule') :
					schedule_date = get_schedule_date(session.schedule)
					if is_calendar_date_after_schdule_date(schedule_date,calendar_date) :
						after_calendar_date_schedules_list.append(session.schedule)
						gclogger.info("The schedule " + str(session.schedule.start_time) +' --- '+str(session.schedule.end_time) +' -------')
						del session.schedule



	return current_lessonplan

def is_calendar_date_after_schdule_date(schedule_date,calendar_date) :
	is_delete = False
	schedule_date_year = int(schedule_date[:4])
	schedule_date_month = int(schedule_date[5:7])
	schedule_date_day = int(schedule_date[8:10])

	calendar_date_year = int(calendar_date[:4])
	calendar_date_month = int(calendar_date[5:7])
	calendar_date_day = int(calendar_date[-2:])

	calendar_date = datetime.datetime(calendar_date_year, calendar_date_month, calendar_date_day)
	schedule_date = datetime.datetime(schedule_date_year, schedule_date_month, schedule_date_day)

	if calendar_date <= schedule_date :
		is_delete = True
	return is_delete




def get_schedule_date(schedule) :
	schedule_date = schedule.start_time[0:10]
	return schedule_date

def generate_holiday_period_list(event,calendar,academic_configuration,timetable,day_code) :
	holiday_period_list =[]
	if is_class(event.params[0]) == False :
		start_time = event.from_time
		end_time = event.to_time
		partial_holiday_periods = get_holiday_period_list(start_time,end_time,day_code,academic_configuration,timetable,calendar.calendar_date)
		for partial_holiday_period in partial_holiday_periods :
			holiday_period_list.append(partial_holiday_period)
	return holiday_period_list


def get_schedule(holiday_period_list,schedule,date) :
	for period in holiday_period_list :
		standard_start_time = get_standard_time(period.start_time,date)
		standard_end_time = get_standard_time(period.end_time,date)
		if standard_start_time == schedule.start_time and standard_end_time ==schedule.end_time :
			return schedule

def find_schedules(current_lessonplan,holiday_period_list,date) :
	schedule_list = []
	for main_topic in current_lessonplan.topics :
		for topic in main_topic.topics :
			for session in topic.sessions :
				if hasattr (session,'schedule') :
					schedule = get_schedule(holiday_period_list,session.schedule,date)
					if schedule is not None :
						schedule_list.append(schedule)
	return schedule_list

def remove_shedules(schedules,current_lessonplan) :
	for schedule in schedules :
		schedule_start_time = schedule.start_time
		schedule_end_time = schedule.end_time
		for main_topic in current_lessonplan.topics :
			for topic in main_topic.topics :
				for session in topic.sessions :
					if session.schedule.start_time == schedule_start_time and session.schedule.end_time == schedule_end_time :
						del session.schedule
	return current_lessonplan


def get_all_remaining_schedules(current_lessonplan) :
	schedule_list = []
	for main_topic in current_lessonplan.topics :
		for topic in main_topic.topics :
			for session in topic.sessions :
				if hasattr(session , 'schedule') :
					schedule_list.append(session.schedule)
	return schedule_list

def get_lesson_plan_after_remove_all_shedules(current_lessonplan) :
	for main_topic in current_lessonplan.topics :
		for topic in main_topic.topics :
			for session in topic.sessions :
				if hasattr(session , 'schedule') :
					del session.schedule
	return current_lessonplan

def get_updated_lesson_plan(shedule_list,current_lessonplan) :

	index = -1
	for main_topic in current_lessonplan.topics :
		for topic in main_topic.topics :
			for session in topic.sessions :
				index += 1
				if index < len(shedule_list) :
					session.schedule = shedule_list[index]
	return current_lessonplan
