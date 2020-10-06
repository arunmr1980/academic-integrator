import datetime 
from academics.TimetableIntegrator import *
import academics.classinfo.ClassInfoDBService as class_info_service
import academics.lessonplan.LessonplanDBService as lessonplan_service
import academics.lessonplan.LessonplanDBService as lessonplan_service
import academics.school.SchoolDBService as school_service
import academics.lessonplan.LessonPlan as lessonplan


def integrate_holiday_lessonplan(event_code,calendar_key) :
	timetable = timetable_service.get_time_table('test-time-table-1')
	school_key = timetable.school_key
	gclogger.info("school key--------------->" + str(school_key))
	academic_configuration = academic_service.get_academig(school_key,'2020-2021')
	updated_lessonplan_list = []
	calendar = calendar_service.get_calendar(calendar_key)
	event = get_event_from_calendar(calendar,event_code)
	gclogger.info("EVENT START TIME AND END TIME ----------------->" + str(event.from_time) + str(event.to_time))
	day_code = findDay(calendar.calendar_date).upper()[0:3]
	subscriber_key = calendar.subscriber_key
	gclogger.info("subscriber_key------------------->>>>" + str(subscriber_key))
	
	if calendar.subscriber_type == 'CLASS-DIV' :
		class_key = subscriber_key[:-2]
		division = subscriber_key[-1:]
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
		school = school_service.get_school(school_key)
		gclogger.info('school --------------->' + str(school.school_id))
		academic_year = get_academic_yr_from_calendar(school,calendar.calendar_date)
		# academic_year = '2020-2021'

		class_info_list = class_info_service.get_classinfo_list(school_key,academic_year)
		gclogger.info('class info list --------------------------------->' + str(class_info_list))		
		for class_info in class_info_list :
			if hasattr(class_info, 'divisions') :
				for div in class_info.divisions :
					division = div.name
					class_key = class_info.class_info_key
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
	return updated_lessonplan_list


def get_academic_yr_from_calendar(school,calendar_date) :
	if hasattr(school,'academic_years') :
		for academic_year in school.academic_years :
			academic_year = find_academic_year(academic_year,calendar_date)
			if academic_year is not None :
				return academic_year


def find_academic_year(academic_year,calendar_date) :
	start_date = academic_year.start_date
	end_date = academic_year.end_date

	start_date_year = int(start_date[-4:])
	start_date_month = int(start_date[3:5])
	start_date_day = int(start_date[:2])

	end_date_year = int(end_date[-4:])
	end_date_month = int(end_date[3:5])
	end_date_day = int(end_date[:2])

	calendar_date_year = int(calendar_date[:4])
	calendar_date_month = int(calendar_date[5:7])
	calendar_date_day = int(calendar_date[-2:])

	start_date = datetime.datetime(start_date_year, start_date_month, start_date_day)
	end_date = datetime.datetime(end_date_year, end_date_month, end_date_day)
	calendar_date = datetime.datetime(calendar_date_year, calendar_date_month, calendar_date_day)

	if start_date <= calendar_date <= end_date :
		return academic_year.code


def get_event_from_calendar(calendar,event_code) :
		for event in calendar.events :
			if event.event_code == event_code :
				return event


def holiday_calendar_to_lessonplan_integrator(current_lessonplan,event,calendar,academic_configuration,timetable,day_code) :	
	gclogger.info("LESSON PLAN KEY------------------->  " + str(current_lessonplan.lesson_plan_key))
	holiday_period_list = generate_holiday_period_list(event,calendar,academic_configuration,timetable,day_code)
	gclogger.info("---------- Holiday Period list is  -----------------")
	for holiday_period in holiday_period_list :
		gclogger.info("---------- Holiday Period list is  " + str(holiday_period.period_code)+' -----------------')
	schedules = find_schedules(current_lessonplan.topics[0].topics,holiday_period_list,calendar.calendar_date)
	gclogger.info("---------- Schedule to remove is   -----------------")
	for schedule in schedules :
		gclogger.info("---------- " + str(holiday_period.period_code) + " ---------")

	current_lessonplan = remove_shedules(schedules,current_lessonplan)
	shedule_list = get_all_remaining_schedules(current_lessonplan)
	current_lessonplan = get_lesson_plan_after_remove_all_shedules(current_lessonplan)
	current_lessonplan = get_updated_lesson_plan(shedule_list,current_lessonplan)
	return current_lessonplan



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

def find_schedules(topics,holiday_period_list,date) :
	schedule_list = []
	for topic in topics :
		for session in topic.sessions :
			schedule = get_schedule(holiday_period_list,session.schedule,date)
			if schedule is not None :
				schedule_list.append(schedule)
	return schedule_list

def remove_shedules(schedules,current_lessonplan) :
	for schedule in schedules :
		schedule_start_time = schedule.start_time
		schedule_end_time = schedule.end_time
		for topic in current_lessonplan.topics[0].topics :
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


