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
import academics.timetable.KeyGeneration as key
import academics.classinfo.ClassInfoDBService as class_info_service
import academics.calendar.Calendar as calendar
import copy
import pprint
pp = pprint.PrettyPrinter(indent=4)



def integrate_add_exams(updated_class_calendars_list,updated_teacher_calendars_list,updated_lessonplans_list,current_class_calendars_list,current_teacher_calendars_list,current_lessonplans_list,exams_list,removed_events) :
	exam_events = make_exam_events(exams_list)
	updated_class_calendars_list = update_current_class_calendars(updated_class_calendars_list,current_class_calendars_list,exam_events,removed_events)

	for i in updated_class_calendars_list :
		cal = calendar.Calendar(None)
		class_calendar_dict = cal.make_calendar_dict(i)
		pp.pprint(class_calendar_dict)

	updated_teacher_calendars_list = update_current_teacher_calendars(updated_teacher_calendars_list,current_teacher_calendars_list,updated_class_calendars_list)

	for i in updated_teacher_calendars_list :
		cal = calendar.Calendar(None)
		class_calendar_dict = cal.make_calendar_dict(i)
		pp.pprint(class_calendar_dict)
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
		exam_event.params = get_params()
		exam_events.append(exam_event)
	return exam_events

def get_standard_time(time,date) :
	splited_date = date.split('-')
	splited_date = list(map(int,splited_date))
	time_hour = int(time[0:2])
	time_minute = int(time[3:5])
	return datetime.datetime(splited_date[0],splited_date[1],splited_date[2],time_hour,time_minute).isoformat()


def get_params() :
	params = []
	period_info = calendar.Param(None)
	period_info.key = 'is_cancel_flag'
	period_info.value = 'true'
	params.append(period_info)
	return params

def update_current_class_calendars(updated_class_calendars_list,current_class_calendars_list,exam_events,removed_events) :
	for current_class_calendar in current_class_calendars_list :
		updated_class_calendar = update_class_calendar_with_exam_events(current_class_calendar,exam_events,removed_events)
		updated_class_calendars_list.append(updated_class_calendar)
	return updated_class_calendars_list

def update_class_calendar_with_exam_events(current_class_calendar,exam_events,removed_events) :
	updated_class_calendar = remove_conflicted_class_events(exam_events,current_class_calendar,removed_events)	
	return current_class_calendar


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


	






