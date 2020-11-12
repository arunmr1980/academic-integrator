from datetime import date, timedelta
import datetime
from datetime import datetime as dt
import calendar as cal
import academics.timetable.TimeTableDBService as timetable_service
from academics.logger import GCLogger as gclogger
import academics.timetable.TimeTable as ttable
import academics.timetable.KeyGeneration as key
import academics.calendar.Calendar as calendar
import academics.academic.AcademicDBService as academic_service
import academics.calendar.CalendarDBService as calendar_service
import academics.TimetableIntegrator as timetable_integrator
import academics.calendar.CalendarIntegrator as calendar_integrator
import academics.timetable.KeyGeneration as key
import academics.classinfo.ClassInfoDBService as class_info_service
import academics.calendar.Calendar as calendar
from academics.lessonplan.LessonplanIntegrator import *
from academics.exam import ExamDBService as exam_service
from academics.lessonplan import LessonplanDBService as lessonplan_service
import academics.lessonplan.LessonPlan as lpnr
import copy
import pprint
pp = pprint.PrettyPrinter(indent=4)


def integrate_add_exam_on_calendar(series_code,class_key,division) :
	subscriber_key = class_key + '-' + division
	updated_class_calendars_list = []
	updated_teacher_calendars_list = []
	updated_lessonplans_list = []
	removed_events = []
	current_class_calendars_list = calendar_service.get_all_calendars_by_key_and_type(subscriber_key,'CLASS-DIV')
	school_key = current_class_calendars_list[0].institution_key
	current_teacher_calendars_list = calendar_service.get_all_calendars_by_school_key_and_type(school_key,'EMPLOYEE')
	current_cls_calendars = copy.deepcopy(current_class_calendars_list)
	current_lessonplans_list = lessonplan_service.get_lesson_plan_list(class_key,division)
	exams_list = exam_service.get_all_exams_by_class_key_and_series_code(class_key, series_code)
	updated_class_calendars_list = integrate_class_calendar_on_add_exams(updated_class_calendars_list,exams_list,current_class_calendars_list,removed_events)
	current_teacher_calendars_list = get_current_teacher_calendars(removed_events)
	integrate_teacher_cal_and_lessonplan_on_add_exam(
						updated_class_calendars_list,
						updated_teacher_calendars_list,
						updated_lessonplans_list,
						current_class_calendars_list,
						current_teacher_calendars_list,
						current_lessonplans_list,
						exams_list,
						removed_events
						)
	save_updated_calendars_and_lessonplans(updated_class_calendars_list,updated_teacher_calendars_list,updated_lessonplans_list)


def save_updated_calendars_and_lessonplans(updated_class_calendars_list,updated_teacher_calendars_list,updated_lessonplans_list) :
	for updated_class_calendar in updated_class_calendars_list :
		cal = calendar.Calendar(None)
		class_calendar_dict = cal.make_calendar_dict(updated_class_calendar)
		response = calendar_service.add_or_update_calendar(class_calendar_dict)
		gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' ------- A updated class calendar uploaded --------- '+str(class_calendar_dict['calendar_key']))

	for updated_teacher_calendar in updated_teacher_calendars_list :
		cal = calendar.Calendar(None)
		teacher_calendar_dict = cal.make_calendar_dict(updated_teacher_calendar)
		response = calendar_service.add_or_update_calendar(teacher_calendar_dict)
		gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' ------- A updated teacher calendar uploaded --------- '+str(class_calendar_dict['calendar_key']))

	for updated_lessonplan in updated_lessonplans_list :
		cal = lpnr.LessonPlan(None)
		lessonplan_dict = cal.make_lessonplan_dict(updated_lessonplan)
		response = lessonplan_service.create_lessonplan(lessonplan_dict)
		gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' ------- A updated lessonplan uploaded --------- '+str(lessonplan_dict['lesson_plan_key']))

def get_current_teacher_calendars(removed_events) :
	current_teacher_calendars = []
	for event in removed_events :
		event_date = get_event_date(event.from_time)
		employee_key = get_employee_key(event.params)
		if employee_key is not None :
			teacher_calendar = calendar_service.get_calendar_by_date_and_key(event_date, employee_key)
			current_teacher_calendars.append(teacher_calendar)
	return current_teacher_calendars



def get_event_date(event_from_time) :
	return event_from_time[:10]

def get_employee_key(params) :
	for param in params :
		if param.key == 'teacher_emp_key' :
			return param.value



def integrate_class_calendar_on_add_exams(academic_configuration,timetable,updated_class_calendars_list,exams_list,current_class_calendars_list,removed_events) :
	exam_events = make_exam_events(exams_list)
	update_current_class_calendars(academic_configuration,timetable,updated_class_calendars_list,current_class_calendars_list,exam_events,removed_events,exams_list)
	for i in updated_class_calendars_list :
		cal = calendar.Calendar(None)
		class_calendar_dict = cal.make_calendar_dict(i)
		pp.pprint(class_calendar_dict)
	return updated_class_calendars_list

def integrate_teacher_cal_and_lessonplan_on_add_exam(updated_class_calendars_list,updated_teacher_calendars_list,updated_lessonplans_list,current_class_calendars_list,current_teacher_calendars_list,current_lessonplans_list,exams_list,removed_events) :
	updated_teacher_calendars_list = update_current_teacher_calendars(updated_teacher_calendars_list,current_teacher_calendars_list,updated_class_calendars_list)

	for i in updated_teacher_calendars_list :
		cal = calendar.Calendar(None)
		teacher_calendar_dict = cal.make_calendar_dict(i)
		pp.pprint(teacher_calendar_dict)
	updated_lessonplans_list = update_current_lessonplans(updated_class_calendars_list,current_lessonplans_list,updated_lessonplans_list,removed_events)
	for i in updated_lessonplans_list :
		lp = lnpr.LessonPlan(None)
		updated_lessonplan_dict = lp.make_lessonplan_dict(i)
		pp.pprint(updated_lessonplan_dict)


def make_exam_events(exams_list) :
	exam_events = []
	for exam_info in exams_list :
		exam_event = calendar.Event(None)
		exam_event.event_code = key.generate_key(3)
		exam_event.event_type = 'EXAM'
		exam_event.from_time = get_standard_time(exam_info.from_time,exam_info.date_time)
		exam_event.to_time = get_standard_time(exam_info.to_time,exam_info.date_time)
		exam_event.params = get_params(exam_info.exam_key)
		exam_events.append(exam_event)
	return exam_events

def get_standard_time(time,date) :
	splited_date = date.split('-')
	splited_date = list(map(int,splited_date))
	time_hour = int(time[0:2])
	time_minute = int(time[3:5])
	return datetime.datetime(splited_date[0],splited_date[1],splited_date[2],time_hour,time_minute).isoformat()


def get_params(exam_key) :
	params = []
	param_info = calendar.Param(None)
	param_info.key = 'cancel_class_flag'
	param_info.value = 'true'
	params.append(param_info)
	param_exam_info = calendar.Param(None)
	param_exam_info.key = 'exam_key'
	param_exam_info.value = exam_key
	params.append(param_exam_info)
	

	return params

def update_current_class_calendars(academic_configuration,timetable,updated_class_calendars_list,current_class_calendars_list,exam_events,removed_events,exams_list) :
	for current_class_calendar in current_class_calendars_list :
		periods_to_be_added =[]
		updated_class_calendar = get_previous_exam_events_removed_calendar(academic_configuration,timetable,current_class_calendar,exams_list,periods_to_be_added)
		updated_class_calendar = get_class_session_events_added_calendar(academic_configuration,timetable,periods_to_be_added,updated_class_calendar)
		updated_class_calendar = update_class_calendar_with_exam_events(current_class_calendar,exam_events,removed_events)
		updated_class_calendars_list.append(updated_class_calendar)
		
	

def get_class_session_events_added_calendar(academic_configuration,timetable,periods_to_be_added,current_class_calendar) :
	events = calendar_integrator.make_events(periods_to_be_added,timetable,current_class_calendar.calendar_date)
	updated_class_calendar = calendar_integrator.add_events_to_calendar(events,current_class_calendar)
	return updated_class_calendar
	
def update_class_calendar_with_exam_events(current_class_calendar,exam_events,removed_events) :
	updated_class_calendar = remove_conflicted_class_events(exam_events,current_class_calendar,removed_events)	
	return current_class_calendar


def get_previous_exam_events_removed_calendar(academic_configuration,timetable,current_class_calendar,exams_list,periods_to_be_added) :
	for exam in exams_list :
		if hasattr(exam,'previous_schedule') and is_schedule_has_same_calendar_key(exam.previous_schedule,current_class_calendar) == True :
			updated_class_calendar = integrate_previous_periods(academic_configuration,timetable,exam,current_class_calendar,periods_to_be_added)


	print(">>>>>>PERIODS TO BE ADDED <<<<<<")
	for i in periods_to_be_added :
		print(i.period_code)

	return current_class_calendar



def is_schedule_has_same_calendar_key(previous_schedule,current_class_calendar) :
	has_same_calendar_date = False
	if previous_schedule.date_time == current_class_calendar.calendar_date :
		has_same_calendar_date = True 
	return has_same_calendar_date


def integrate_previous_periods(academic_configuration,timetable,exam,current_class_calendar,periods_to_be_added) :
	previous_exam_from_time = exam.previous_schedule.from_time
	previous_exam_to_time = exam.previous_schedule.to_time	
	previous_exam_event_from_time = timetable_integrator.get_standard_time(previous_exam_from_time,current_class_calendar.calendar_date)
	previous_exam_event_to_time = timetable_integrator.get_standard_time(previous_exam_to_time,current_class_calendar.calendar_date)
	day_code = timetable_integrator.findDay(current_class_calendar.calendar_date).upper()[0:3]
	period_list = generate_period_list(
										current_class_calendar,
										previous_exam_event_from_time,
										previous_exam_event_to_time,
										academic_configuration,
										timetable,
										day_code
										)
	for period in period_list :
		if is_period_already_exist(period,periods_to_be_added) == False :
			periods_to_be_added.append(period)
	updated_class_calendar = remove_exam_event_of_previous_schedule(current_class_calendar,previous_exam_event_from_time,previous_exam_event_to_time)

	
		
def remove_exam_event_of_previous_schedule(current_class_calendar,previous_exam_event_from_time,previous_exam_event_to_time) :
	for event in current_class_calendar.events :
		if event.event_type == 'EXAM' and is_schedule_matching(event,previous_exam_event_from_time,previous_exam_event_to_time) == True :
			current_class_calendar.events.remove(event)
	return current_class_calendar



def is_schedule_matching(event,previous_exam_event_from_time,previous_exam_event_to_time) :
	is_matching = False
	if event.from_time == previous_exam_event_from_time and event.to_time == previous_exam_event_to_time :
		is_matching = True
	return is_matching


def is_period_already_exist(period,periods_to_be_added) :
	is_period_exist = False
	for existing_period in periods_to_be_added :
		if period.period_code == existing_period.period_code :
			is_period_exist = True
	return is_period_exist

def generate_period_list(calendar,previous_exam_event_from_time,previous_exam_event_to_time,academic_configuration,timetable,day_code) :
	period_list =[]
	periods = get_period_list(
							previous_exam_event_from_time,
							previous_exam_event_to_time,
							day_code,academic_configuration,
							timetable,calendar.calendar_date
							)
	for period in periods :
		period_list.append(period)
	return period_list



def get_period_list(start_time,end_time,day_code,academic_configuration,timetable,date) :
	period_list =[]
	if hasattr(academic_configuration.time_table_configuration ,'time_table_schedules') :
		for time_table_schedule in academic_configuration.time_table_configuration.time_table_schedules :
				for class_key in time_table_schedule.applied_classes :
					if class_key == timetable.class_key :
						for day_table in  time_table_schedule.day_tables :
							if day_table.day_code == day_code :
								for period in day_table.periods :
									standard_start_time = timetable_integrator.get_standard_time(period.start_time,date)
									standard_end_time = timetable_integrator.get_standard_time(period.end_time,date)
									if timetable_integrator.check_holiday_time_conflict(start_time,end_time,standard_start_time,standard_end_time) == True:
										period_list.append(period)
	return period_list


def remove_conflicted_class_events(exam_events,current_class_calendar,removed_events) :
	for exam_event in exam_events :
		updated_class_calendar = update_class_calendar_events(exam_event,current_class_calendar,removed_events)
	return updated_class_calendar


def update_class_calendar_events(exam_event,current_class_calendar,removed_events) :
	updated_events = []
	for calendar_event in current_class_calendar.events :
		if check_events_conflict(exam_event.from_time,exam_event.to_time,calendar_event.from_time,calendar_event.to_time) == True :
			removed_events.append(calendar_event)
			if exam_event not in updated_events :
				updated_events.append(exam_event)
		else :
			updated_events.append(calendar_event)
	current_class_calendar.events = updated_events
	return current_class_calendar


def update_current_teacher_calendars(updated_teacher_calendars_list,current_teacher_calendars_list,updated_class_calendars_list) :
	for current_teacher_calendar in current_teacher_calendars_list :

		update_teacher_calendar = get_class_session_events_added_teacher_calendar(current_teacher_calendar,updated_class_calendars_list)
		updated_teacher_calendar = remove_events_from_teacher_calendar(current_teacher_calendar,updated_class_calendars_list)
		updated_teacher_calendars_list.append(updated_teacher_calendar)
	return updated_teacher_calendars_list

def remove_events_from_teacher_calendar(current_teacher_calendar,updated_class_calendars_list) :
	updated_event_list = []
	for event in current_teacher_calendar.events :
		if is_event_exist_in_class_calendars(event,updated_class_calendars_list) == True :
			updated_event_list.append(event)
	current_teacher_calendar.events = updated_event_list
	return current_teacher_calendar

def get_class_session_events_added_teacher_calendar(current_teacher_calendar,updated_class_calendars_list) :
	for updated_class_calendar in updated_class_calendars_list :
		updated_event_list = []
		for event in updated_class_calendar.events :
			if is_event_exist_in_teacer_calendars(event,current_teacher_calendar) == True :
				updated_event_list.append(event)
		current_teacher_calendar.events = updated_event_list
	return current_teacher_calendar

def is_event_exist_in_class_calendars(event,updated_class_calendars_list) :
	is_event_exist = False
	for updated_calendar in updated_class_calendars_list :
		for event_info in updated_calendar.events :
			if event_info.event_code == event.event_code :
				is_event_exist = True
	return is_event_exist


def check_events_conflict(event_start_time,event_end_time,class_calendar_event_start_time,class_calendar_event_end_time) :
		is_conflict = None
		event_start_time_year = int(event_start_time[:4])
		event_start_time_month = int(event_start_time[5:7])
		event_start_time_day = int(event_start_time[8:10])
		event_start_time_hour = int(event_start_time[11:13])
		event_start_time_min = int(event_start_time[14:16])
		event_start_time_sec = int(event_start_time[-2:])

		event_end_time_year = int(event_end_time[:4])
		event_end_time_month = int(event_end_time[5:7])
		event_end_time_day = int(event_end_time[8:10])
		event_end_time_hour = int(event_end_time[11:13])
		event_end_time_min = int(event_end_time[14:16])
		event_end_time_sec = int(event_end_time[-2:])

		class_calendar_event_start_time_year = int(class_calendar_event_start_time[:4])
		class_calendar_event_start_time_month = int(class_calendar_event_start_time[5:7])
		class_calendar_event_start_time_day = int(class_calendar_event_start_time[8:10])
		class_calendar_event_start_time_hour = int(class_calendar_event_start_time[11:13])
		class_calendar_event_start_time_min = int(class_calendar_event_start_time[14:16])
		class_calendar_event_start_time_sec = int(class_calendar_event_start_time[-2:])

		class_calendar_event_end_time_year = int(class_calendar_event_end_time[:4])
		class_calendar_event_end_time_month = int(class_calendar_event_end_time[5:7])
		class_calendar_event_end_time_day = int(class_calendar_event_end_time[8:10])
		class_calendar_event_end_time_hour = int(class_calendar_event_end_time[11:13])
		class_calendar_event_end_time_min = int(class_calendar_event_end_time[14:16])
		class_calendar_event_end_time_sec = int(class_calendar_event_end_time[-2:])

		class_calendar_event_start_time = dt(class_calendar_event_start_time_year, class_calendar_event_start_time_month, class_calendar_event_start_time_day, class_calendar_event_start_time_hour, class_calendar_event_start_time_min, class_calendar_event_start_time_sec, 000000)
		class_calendar_event_end_time = dt(class_calendar_event_end_time_year, class_calendar_event_end_time_month, class_calendar_event_end_time_day, class_calendar_event_end_time_hour, class_calendar_event_end_time_min, class_calendar_event_end_time_sec, 000000)
		event_start_time = dt(event_start_time_year, event_start_time_month, event_start_time_day, event_start_time_hour, event_start_time_min, event_start_time_sec, 000000)
		event_end_time = dt(event_end_time_year, event_end_time_month, event_end_time_day, event_end_time_hour, event_end_time_min, event_end_time_sec, 000000)

		delta = max(event_start_time,class_calendar_event_start_time) - min(event_end_time,class_calendar_event_end_time)
		if delta.days < 0 :
			is_conflict = True
		else :
			is_conflict = False
		return is_conflict

	
def update_current_lessonplans(updated_class_calendars_list,current_lessonplans_list,updated_lessonplans_list,removed_events) :
	for current_lessonplan in current_lessonplans_list :
		subject_code = current_lessonplan.subject_code
		events_to_remove = get_removed_events(subject_code,removed_events)
		updated_lessonplan = update_current_lessonplan(current_lessonplan,events_to_remove)
		updated_lessonplans_list.append(updated_lessonplan)
	return updated_lessonplans_list



def get_removed_events(subject_code,removed_events) :
	events_to_remove = []
	for event in removed_events :
		subject_key = get_subject_code(event)
		if subject_key == subject_code :
			events_to_remove.append(event)
	return events_to_remove


def get_subject_code(event) :
	if hasattr(event, 'params') :
		for param in event.params :
			if param.key == 'subject_key' :
				return param.value



def update_current_lessonplan(current_lessonplan,events_to_remove) :
	for event in events_to_remove :
		updated_lessonplan = remove_event_schedule_from_lessonplan(current_lessonplan,event)
		print(updated_lessonplan,"ERRORRRRRRR------------------")
	return updated_lessonplan
			
def is_need_remove_schedule(event,schedule) :
		is_need_remove = False 
		if event.from_time == schedule.start_time and event.to_time == schedule.end_time :
			is_need_remove = True
		return is_need_remove

def remove_event_schedule_from_lessonplan(current_lessonplan,event) :
	if  hasattr(current_lessonplan,'topics') and len(current_lessonplan.topics) > 0 :
			for main_topic in current_lessonplan.topics :
				for topic in main_topic.topics :
					for session in topic.sessions :
						if hasattr(session,'schedule') :
							if is_need_remove_schedule(event,session.schedule) == True :
								print("----- A schedule removed ---" + session.schedule.start_time + '---' + session.schedule.end_time +'------')
								del session.schedule
	current_lessonplan = adjust_lessonplan_after_remove_schedule(current_lessonplan)
	return current_lessonplan

def adjust_lessonplan_after_remove_schedule(current_lessonplan) :
	schedule_list = get_all_remaining_schedules(current_lessonplan)
	current_lessonplan = get_lesson_plan_after_remove_all_shedules(current_lessonplan)
	#add root schedule to schedule list and delete all root sessions
	current_lessonplan = add_root_schedule_to_schedule_list(current_lessonplan,schedule_list)
	current_lessonplan = get_updated_lesson_plan(schedule_list,current_lessonplan)
	#create remaining  schedule  on root sesions
	current_lessonplan = create_remaining_sessions_on_root(schedule_list,current_lessonplan)
	return current_lessonplan


	


