import datetime
from academics.TimetableIntegrator import *
import academics.classinfo.ClassInfoDBService as class_info_service
import academics.lessonplan.LessonplanDBService as lessonplan_service
import academics.lessonplan.LessonplanDBService as lessonplan_service
import academics.school.SchoolDBService as school_service
import academics.lessonplan.LessonPlan as lnpr
import academics.academic.AcademicDBService as academic_service
import academics.timetable.KeyGeneration as key
import copy
import pprint
pp = pprint.PrettyPrinter(indent=4)


def is_subject_code_exist_in_event(params,subject_code) :
	for param in params :
		if param.key == 'subject_key' and param.value == subject_code:
			return True
	else :
		return False


def get_event_from_calendar(calendar,event_code) :
	for event in calendar.events :
		if event.event_code == event_code :
			return event

def get_updated_class_calendar(current_class_calendars,calendar_key) :
	for current_class_calendar in current_class_calendars :
		if current_class_calendar.calendar_key == calendar_key :
			return current_class_calendar



def need_remove_schedules(current_lessonplan,schedule,updated_class_calendar) :
	is_remove = False
	calendar_key = schedule.calendar_key
	event_code = schedule.event_code
	subject_code = current_lessonplan.subject_code
	event = get_event_from_calendar(updated_class_calendar,event_code)
	if hasattr(event,'params') :
		if (is_subject_code_exist_in_event(event.params,subject_code)) == False :
			is_remove = True
		return is_remove


def get_subject_key(params) :
	for param in params :
		if param.key == 'subject_key' :
			return param.value

def get_subject_key_list(updated_class_calendars_events) :
		subject_key_list =[]
		for event in updated_class_calendars_events :
			if event.event_type =='CLASS_SESSION':
				subject_key = get_subject_key(event.params)
				if subject_key is not None and subject_key not in subject_key_list :
					subject_key_list.append(subject_key)
		return subject_key_list

def Get_class_session_events(updated_class_calendar) :
	class_session_events = []
	if hasattr(updated_class_calendar,'events') :
		for event in updated_class_calendar.events :
			if event.event_type == 'CLASS_SESSION' :
				class_session_events.append(event)
	return class_session_events

def update_current_class_calendar_with_day_code(period_code,updated_timetable,current_class_calendar,updated_period) :
		current_class_calendar = update_current_class_calendar(updated_period,current_class_calendar,period_code)
		return current_class_calendar

def update_current_class_calendar(updated_period,current_class_calendar,period_code) :
	if hasattr(current_class_calendar,'events') :
		for event in current_class_calendar.events :
			if is_need_update_parms(event,period_code) == True :
				updated_params = update_params(event.params,current_class_calendar,updated_period)
				del event.params
				event.params = updated_params
	return current_class_calendar


def is_need_update_parms(event,period_code) :
		for param in event.params :
			if(param.key == 'period_code') and param.value == period_code :
				return True

def update_params(params,current_class_calendar,updated_period) :
	period_code = updated_period.period_code
	subject_key = updated_period.subject_key
	employee_key = updated_period.employee_key
	params = []
	period_info = calendar.Param(None)
	period_info.key = 'period_code'
	period_info.value = period_code
	params.append(period_info)

	subject_info = calendar.Param(None)
	subject_info.key = 'subject_key'
	subject_info.value = subject_key
	params.append(subject_info)

	employee_info = calendar.Param(None)
	employee_info.key = 'teacher_emp_key'
	employee_info.value = employee_key
	params.append(employee_info)
	return params


def get_updated_period_from_timetable(period_code,updated_timetable) :
	if hasattr(updated_timetable, 'timetable') and updated_timetable.timetable is not None :
		if hasattr(updated_timetable.timetable,'day_tables') and len(updated_timetable.timetable.day_tables) > 0 :
			for day in updated_timetable.timetable.day_tables :
				if hasattr(day,'periods') and len(day.periods) > 0 :
					for period in day.periods :
						if period.period_code == period_code :
							return period
				else :
					gclogger.warn('Periods not existing')

		else:
			gclogger.warn('Days_table not existing')

	else:
		gclogger.warn('Time table not existing')

def get_day_code_from_calendar(current_class_calendar,period_code) :
	for event in current_class_calendar.events :
		if event.params[0].key == 'period_code' and event.params[0].value[:3] == period_code :
			return True

def get_current_class_calendars_with_day_code(day_code,current_current_class_calendars) :
	current_class_calendars_with_day_code = []
	for current_class_calendar in current_current_class_calendars :
		if (get_day_code_from_calendar(current_class_calendar,day_code) ) == True :
			current_class_calendars_with_day_code.append(current_class_calendar)
	return current_class_calendars_with_day_code

def list_difference(list1,list2):
	return (list(list(set(list1) - set(list2)) + list(set(list2) - set(list1))))

def get_subject_key_from_current_class_calendars(current_class_calendar_event_list) :
	subject_key_list = get_subject_key_list(current_class_calendar_event_list)
	return subject_key_list

def get_current_lesson_plan_with_subject_key(current_lessonplans,subject_key) :
	for current_lessonplan in current_lessonplans :
		if current_lessonplan.subject_code == subject_key :
			return current_lessonplan


def Update_lessonplan(current_lessonplan,updated_class_calendar) :
	if  hasattr(current_lessonplan,'topics') and len(current_lessonplan.topics) > 0 :
			for main_topic in current_lessonplan.topics :
				for topic in main_topic.topics :
					for session in topic.sessions :
						if hasattr(session,'schedule') :
							if(need_remove_schedules(current_lessonplan,session.schedule,updated_class_calendar)) == True :
								gclogger.info("----- A schedule removed ---" + session.schedule.start_time + '---' + session.schedule.end_time +'------')
								del session.schedule
	current_lessonplan = adjust_lessonplan_after_remove_schedule(current_lessonplan)
	return current_lessonplan

def adjust_lessonplan_after_remove_schedule(current_lessonplan) :
	root_sessions = []
	schedule_list = get_all_remaining_schedules(current_lessonplan)
	current_lessonplan = get_lesson_plan_after_remove_all_shedules(current_lessonplan)
	#add root schedule to schedule list and delete all root sessions
	current_lessonplan = add_root_schedule_to_schedule_list(current_lessonplan,schedule_list,root_sessions)
	current_lessonplan = get_updated_lesson_plan(schedule_list,current_lessonplan)
	#create remaining  schedule  on root sesions
	current_lessonplan = create_remaining_sessions_on_root_when_schedule_removed(schedule_list,current_lessonplan,root_sessions)
	return current_lessonplan







def update_lessonplan(current_lessonplan,updated_class_calendar_events,updated_class_calendar) :
	if  hasattr(current_lessonplan,'topics') and len(current_lessonplan.topics) > 0 :
			for main_topic in current_lessonplan.topics :
				for topic in main_topic.topics :
					for session in topic.sessions :
						if hasattr(session , 'schedule') :
							current_lessonplan = add_schedules(updated_class_calendar_events,current_lessonplan,updated_class_calendar)
	return current_lessonplan



def add_schedules(updated_class_calendar_events,current_lessonplan,updated_class_calendar) :
	events_to_add_schedule =[]
	for event in updated_class_calendar_events :
		subject_key = get_subject_key(event.params)
		if subject_key == current_lessonplan.subject_code :
			events_to_add_schedule.append(event)
			add_schedules_and_adjust_lessonplan(current_lessonplan,events_to_add_schedule,updated_class_calendar)
	return current_lessonplan


def add_schedules_and_adjust_lessonplan(current_lessonplan,events,updated_class_calendar) :
	after_calendar_date_schedules_list = []
	root_sessions = []
	gclogger.info("LESSON PLAN KEY ------------------->  " + str(current_lessonplan.lesson_plan_key))
	current_lessonplan = remove_schedule_after_calendar_date(current_lessonplan,events[0].from_time,after_calendar_date_schedules_list)
	current_lessonplan = add_root_schedule_to_schedule_list(current_lessonplan,after_calendar_date_schedules_list,root_sessions)
	current_lessonplan = add_calendar_schedules_to_lesson_plan(current_lessonplan,events,updated_class_calendar)
	current_lessonplan = add_shedule_after_calendar_date(after_calendar_date_schedules_list,current_lessonplan)
	current_lessonplan = create_remaining_sessions_on_root_when_schedule_added(after_calendar_date_schedules_list,current_lessonplan)
	return current_lessonplan


def create_schedule(event,calendar) :
	schedule = lnpr.Schedule(None)
	schedule.calendar_key = calendar.calendar_key
	schedule.event_code = event.event_code
	schedule.start_time = event.from_time
	schedule.end_time = event.to_time
	return schedule

def Add_schedule_to_lessonplan(current_lessonplan,schedule,calendar,event) :
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
	else :
		if schedule_added == False :
			add_sessions_on_root(current_lessonplan,event,calendar,schedule_added)
	return current_lessonplan


def add_sessions_on_root(current_lesson_plan,event,calendar,schedule_added) :
	schedule = create_schedule(event,calendar)
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





def get_current_class_calendars_event_list(current_class_cals) :
	current_class_calendars_event_list = []
	for current_class_cal in current_class_cals :
		if hasattr(current_class_cal,'events') :
			for event in current_class_cal.events :
				if event.event_type == 'CLASS_SESSION' :
					current_class_calendars_event_list.append(event)
	return current_class_calendars_event_list





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
		if timetable is not None :
			gclogger.info("school key--------------->" + str(school_key))
			gclogger.info("class keyyyy------>" + str(class_key))
			gclogger.info("Division--------->" + str(division))
			current_lesson_plan_list = lessonplan_service.get_lesson_plan_list(class_key,division)
			for current_lessonplan in current_lesson_plan_list :
				if current_lessonplan.class_key == class_key and current_lessonplan.division == division :
					updated_lessonplan = holiday_calendar_to_lessonplan_integrator(current_lessonplan,event,calendar,academic_configuration,timetable,day_code)
					lp = lnpr.LessonPlan(None)
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
						if timetable is not None :
							gclogger.info("class keyyyy------> " + str(class_key))
							gclogger.info("Division---------> " + str(division))
							current_lesson_plan_list = lessonplan_service.get_lesson_plan_list(class_key,division)
							for current_lessonplan in current_lesson_plan_list :
								updated_lessonplan = holiday_calendar_to_lessonplan_integrator(current_lessonplan,event,calendar,academic_configuration,timetable,day_code)
								lp = lnpr.LessonPlan(None)
								updated_lessonplan_dict = lp.make_lessonplan_dict(updated_lessonplan)
								response = lessonplan_service.create_lessonplan(updated_lessonplan_dict)
								gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' Updated Lesson Plan  uploaded '+str(updated_lessonplan_dict['lesson_plan_key']))
								updated_lessonplan = lessonplan_service.get_lessonplan(updated_lessonplan_dict['lesson_plan_key'])
								updated_lessonplan_list.append(updated_lessonplan)
	# return updated_lessonplan_list
	upload_updated_lessonplans(updated_lessonplan_list)

def upload_updated_lessonplans(updated_lessonplan_list) :
	for lesson_plan in updated_lessonplan_list :
		lp = lnpr.LessonPlan(None)
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
		subscriber_key = calendar.subscriber_key
		class_key = subscriber_key[:-2]
		division = subscriber_key[-1:]
		# timetable = timetable_service.get_timetable_entry(class_key, division)
		current_lesson_plan_list = lessonplan_service.get_lesson_plan_list(class_key,division)
		for current_lessonplan in current_lesson_plan_list :
			if current_lessonplan.class_key == class_key and current_lessonplan.division == division :
				updated_lessonplan = cancelled_holiday_calendar_to_lessonplan_integrator(current_lessonplan,calendar,day_code)
				lp = lnpr.LessonPlan(None)
				updated_lessonplan_dict = lp.make_lessonplan_dict(updated_lessonplan)
				response = lessonplan_service.create_lessonplan(updated_lessonplan_dict)
				gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' Updated Lesson Plan  uploaded '+str(updated_lessonplan_dict['lesson_plan_key']))
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
						class_subscriber_key = class_key+ '-' +division
						class_calendar = calendar_service.get_calendar_by_date_and_key(calendar.calendar_date,class_subscriber_key)
						if class_calendar is not None :
							gclogger.info("class keyyyy------> " + str(class_key))
							gclogger.info("Division---------> " + str(division))
							current_lesson_plan_list = lessonplan_service.get_lesson_plan_list(class_key,division)
							for current_lessonplan in current_lesson_plan_list :
								updated_lessonplan = cancelled_holiday_calendar_to_lessonplan_integrator(current_lessonplan,class_calendar,day_code)
								lp = lnpr.LessonPlan(None)
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
	root_sessions = []
	gclogger.info("LESSON PLAN KEY------------------->  " + str(current_lessonplan.lesson_plan_key))
	holiday_period_list = generate_holiday_period_list(event,calendar,academic_configuration,timetable,day_code)
	for holiday_period in holiday_period_list :
		gclogger.info("---------- Holiday Period----  " + str(holiday_period.period_code)+' -----------------')
	schedules = find_schedules(current_lessonplan,holiday_period_list,calendar.calendar_date)
	gclogger.info("---------- Schedule to remove is   -----------------")
	for schedule in schedules :
		gclogger.info("---------- " + str(holiday_period.period_code) + " ---------")

	current_lessonplan = remove_shedules(schedules,current_lessonplan)
	schedule_list = get_all_remaining_schedules(current_lessonplan)

	current_lessonplan = get_lesson_plan_after_remove_all_shedules(current_lessonplan)
		#add root schedule to schedule list and delete all root sessions
	current_lessonplan = add_root_schedule_to_schedule_list(current_lessonplan,schedule_list,root_sessions)
	current_lessonplan = get_updated_lesson_plan(schedule_list,current_lessonplan)
	current_lessonplan = create_remaining_sessions_on_root_when_schedule_removed(schedule_list,current_lessonplan,root_sessions)
	return current_lessonplan


def add_root_schedule_to_schedule_list(current_lessonplan,schedule_list,root_sessions) :
	sessions_count = len(current_lessonplan.sessions )
	root_sessions.append(sessions_count)
	if hasattr(current_lessonplan,'sessions') :
		for session in current_lessonplan.sessions :
			if hasattr(session,"schedule") :
				schedule_list.append(session.schedule)
	current_lessonplan.sessions = []
	return current_lessonplan


def cancelled_holiday_calendar_to_lessonplan_integrator(current_lessonplan,calendar,day_code) :
	after_calendar_date_schedules_list = []
	root_sessions = []
	events = get_class_session_events(calendar.events)
	gclogger.info("LESSON PLAN KEY ------------------->  " + str(current_lessonplan.lesson_plan_key))
	current_lessonplan = remove_schedule_after_calendar_date(current_lessonplan,events[0].from_time,after_calendar_date_schedules_list)
	# current_lessonplan = delete_calendar_schedules_of_calendar_date(calendar.calendar_date,current_lessonplan)
	current_lessonplan = add_root_schedule_to_schedule_list(current_lessonplan,after_calendar_date_schedules_list,root_sessions)
	current_lessonplan = add_calendar_schedules_to_lesson_plan(current_lessonplan,events,calendar)
	current_lessonplan = add_shedule_after_calendar_date(after_calendar_date_schedules_list,current_lessonplan)
	current_lessonplan = create_remaining_sessions_on_root_when_schedule_added(after_calendar_date_schedules_list,current_lessonplan)
	return current_lessonplan


def create_remaining_sessions_on_root_when_schedule_removed(after_calendar_date_schedules_list,current_lessonplan,root_sessions) :
	empty_sessions_count = int(root_sessions[0]) - len(after_calendar_date_schedules_list)
	for schedule in after_calendar_date_schedules_list :
		session_order_index = after_calendar_date_schedules_list.index(schedule) + 1
		session = create_session(schedule,session_order_index)
		if hasattr(current_lessonplan,'sessions') :
			current_lessonplan.sessions.append(session)
	for empty_session in range(empty_sessions_count):
		session_order_index = len(current_lessonplan.sessions) + 1
		session = create_empty_session(session_order_index)
		if hasattr(current_lessonplan,'sessions') :
			current_lessonplan.sessions.append(session)
	return current_lessonplan

def create_remaining_sessions_on_root_when_schedule_added(after_calendar_date_schedules_list,current_lessonplan) :
	for schedule in after_calendar_date_schedules_list :
		session_order_index = after_calendar_date_schedules_list.index(schedule) + 1
		session = create_session(schedule,session_order_index)
		if hasattr(current_lessonplan,'sessions') :
			current_lessonplan.sessions.append(session)
	return current_lessonplan


def delete_calendar_schedules_of_calendar_date(calendar_date,current_lessonplan) :
	for main_topic in current_lessonplan.topics :
		for topic in main_topic.topics :
			for session in topic.sessions :
				if hasattr(session , 'schedule') :
					if is_schedule_on_calendar_date(session.schedule,calendar_date) == True :
						print("DELETED SHEDULE ----",session.schedule.start_time,'--',session.schedule.end_time)
						del session.schedule
	return current_lessonplan

def is_schedule_on_calendar_date(schedule,calendar_date) :
	if schedule.start_time[:10] == calendar_date and schedule.end_time[:10] == calendar_date :
		return True


def create_session(schedule,session_order_index) :
	session = lnpr.Session(None)
	session.schedule = schedule
	session.order_index = session_order_index
	session.code = key.generate_key(4)
	return session

def create_empty_session(session_order_index) :
	session = lnpr.Session(None)
	session.order_index = session_order_index
	session.code = key.generate_key(4)
	return session

def get_class_session_events(events) :
	event_list = []
	for event in events:
		if event.event_type == 'CLASS_SESSION':
			event_list.append(event)
	return event_list

def add_shedule_after_calendar_date(schedule_list,current_lessonplan) :
	gclogger.info('Adding schedules after calendar date -------------')
	for main_topic in current_lessonplan.topics :
		for topic in main_topic.topics :
			for session in topic.sessions :
				if not hasattr(session , 'schedule') :
					if len(schedule_list) > 0 :
						session.schedule = schedule_list[0]
						gclogger.info('A schedule is added ' + str(schedule_list[0].start_time) + ' --- ' + str(schedule_list[0].start_time) )
						schedule_list.remove(schedule_list[0])


	return current_lessonplan


def create_schedule(event,calendar) :
	schedule = lnpr.Schedule(None)
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
			Add_schedule_to_lessonplan(current_lessonplan,schedule,calendar,event)
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

	#check is there sessions and schedule if there append to  after_calendar_date_schedules_list and delete root session
	return current_lessonplan

def is_calendar_date_after_schdule_date(schedule_date,calendar_date) :
	is_delete = False
	schedule_date_year = int(schedule_date[:4])
	schedule_date_month = int(schedule_date[5:7])
	schedule_date_day = int(schedule_date[8:10])
	schedule_date_hour = int(schedule_date[11:13])
	schedule_date_min = int(schedule_date[14:16])
	schedule_date_sec = int(schedule_date[-2:])

	calendar_date_year = int(calendar_date[:4])
	calendar_date_month = int(calendar_date[5:7])
	calendar_date_day = int(calendar_date[8:10])
	calendar_date_hour = int(calendar_date[11:13])
	calendar_date_min = int(calendar_date[14:16])
	calendar_date_sec = int(calendar_date[-2:])


	calendar_date = datetime.datetime(calendar_date_year,calendar_date_month,calendar_date_day,calendar_date_hour,calendar_date_min,calendar_date_sec,000000)

	schedule_date = datetime.datetime(schedule_date_year, schedule_date_month, schedule_date_day,schedule_date_hour,schedule_date_min,schedule_date_sec,000000)
	

	if calendar_date < schedule_date :
		is_delete = True
	return is_delete




def get_schedule_date(schedule) :
	schedule_date = schedule.start_time
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
					if hasattr (session,'schedule') :
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

def get_updated_lesson_plan(schedule_list,current_lessonplan) :
	for main_topic in current_lessonplan.topics :
		for topic in main_topic.topics :
			for session in topic.sessions :
				if not hasattr(session , 'schedule') :
					if len(schedule_list) > 0 :
						session.schedule = schedule_list[0]
						if session.schedule is not None :
							gclogger.info('A schedule is added ' + str(schedule_list[0].start_time) + ' --- ' + str(schedule_list[0].start_time) )
							schedule_list.remove(schedule_list[0])
	return current_lessonplan

def add_shedule_after_calendar_date(schedule_list,current_lessonplan) :
	gclogger.info('Adding schedules after calendar date -------------')
	for main_topic in current_lessonplan.topics :
		for topic in main_topic.topics :
			for session in topic.sessions :
				if not hasattr(session , 'schedule') :
					if len(schedule_list) > 0 :
						session.schedule = schedule_list[0]
						gclogger.info('A schedule is added ' + str(schedule_list[0].start_time) + ' --- ' + str(schedule_list[0].start_time) )
						schedule_list.remove(schedule_list[0])


	return current_lessonplan
