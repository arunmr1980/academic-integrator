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
import academics.exam.ExamIntegrator as exam_integrator
import academics.timetable.KeyGeneration as key
import academics.classinfo.ClassInfoDBService as class_info_service
import academics.calendar.Calendar as calendar
from academics.lessonplan.LessonplanIntegrator import *
import academics.lessonplan.LessonplanIntegrator as lessonplan_integrator
from academics.exam import ExamDBService as exam_service
from academics.leave import LeaveDBService as leave_service
from academics.lessonplan import LessonplanDBService as lessonplan_service
import academics.academic.AcademicDBService as academic_service
import academics.timetable.TimeTableDBService as timetable_service
import academics.lessonplan.LessonPlan as lpnr
import academics.lessonplan.LessonplanIntegrator as lessonplan_integrator
import copy
import pprint
pp = pprint.PrettyPrinter(indent=4)

def integrate_add_leave_on_calendar(leave_key) :
	removed_events = []
	class_cals_to_be_updated = []
	teacher_cals_to_be_updated = []
	updated_class_calendars_list = []
	updated_teacher_calendars_list = []
	updated_lessonplans_list = []
	events_with_sub_key = {}
	
	# current_class_calendars_list= self.get_current_class_calendars_list()
	# current_teacher_calendars_list = self.get_current_teacher_calendars_list()
	# current_lessonplans_list = self.get_current_lessonplans_list()
	# current_teacher_leaves_list = self.get_current_teacher_leaves_list()
	leave = leave_service.get_leave(leave_key)
	employee_key = leave.subscriber_key
	from_time = leave.from_time
	to_time = leave.to_time
	from_date = leave.from_date
	to_date = leave.to_date
	teacher_cals = get_teacher_calendars_on_dates(from_date,to_date,employee_key)
	for teacher_calendar in teacher_cals :
		if teacher_calendar is not None :
			teacher_cals_to_be_updated.append(teacher_calendar)
			for event in teacher_calendar.events :
				calendar_key = event.ref_calendar_key
				event_code = event.event_code
				current_class_calendar = calendar_service.get_calendar(calendar_key) 
				if is_class_class_calendar_already_exist(class_cals_to_be_updated,current_class_calendar) == False :
					class_cals_to_be_updated.append(current_class_calendar)
				class_event = get_class_calendar_event(current_class_calendar,event_code,removed_events)
				if exam_integrator.check_events_conflict(class_event.from_time,class_event.to_time,from_time,to_time) == True :
					if is_this_event_already_exist(current_class_calendar,class_event,removed_events) == False :
						removed_events.append(class_event)
						if current_class_calendar.subscriber_key in events_with_sub_key :
								events_with_sub_key[current_class_calendar.subscriber_key].append(class_event)
						else :
							events_with_sub_key[current_class_calendar.subscriber_key] = []
							events_with_sub_key[current_class_calendar.subscriber_key].append(class_event)
							
	current_lessonplans = get_lessonplans_list(events_with_sub_key.keys())
	update_lessonplans_with_conflicted_events(current_lessonplans,updated_lessonplans_list,events_with_sub_key)
	update_teacher_cals_and_class_cals(removed_events,teacher_cals_to_be_updated,class_cals_to_be_updated,updated_class_calendars_list,updated_teacher_calendars_list)
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



def get_lessonplans_list(subscriber_key_list) :
		current_lessonplans =[]
		for subscriber_key in subscriber_key_list :
			class_key = subscriber_key[:-2]
			division = subscriber_key[-1:]
			lessonplans = lessonplan_service.get_lesson_plan_list(class_key, division)
			current_lessonplans.extend(lessonplans)
		return current_lessonplans

def update_lessonplans_with_conflicted_events(current_lessonplans,updated_lessonplans_list,events_with_sub_key) :
	for lessonplan in current_lessonplans :
		schedules_to_be_removed = []
		get_schedules_to_be_removed(events_with_sub_key,lessonplan,schedules_to_be_removed)
		updated_lessonplan = get_removed_event_updated_lessonplan_(lessonplan,schedules_to_be_removed)
		updated_lessonplans_list.append(updated_lessonplan)
	return updated_lessonplans_list

def get_schedules_to_be_removed(events_with_sub_key,lessonplan,schedules_to_be_removed) :
	for key,values in events_with_sub_key.items() :
		subscriber_key = lessonplan.class_key+'-'+lessonplan.division
		if key == subscriber_key :
			schedules_list = get_schedules_list(key,values)
			schedules_to_be_removed.extend(schedules_list)

def get_removed_event_updated_lessonplan_(current_lessonplan,schedules_to_be_removed) :
	gclogger.info(current_lessonplan.lesson_plan_key + '----------------------------LESSONPLAN KEY -----------------------')
	for schedule in schedules_to_be_removed :
		gclogger.info(schedule.event_code + " --- EVENT CODE TO BE REMOVED ---------------------")
		root_sessions = []
		schedules = []
		schedules.append(schedule)
		current_lessonplan = lessonplan_integrator.remove_shedules(schedules,current_lessonplan)
		schedule_list = lessonplan_integrator.get_all_remaining_schedules(current_lessonplan)
		current_lessonplan = lessonplan_integrator.get_lesson_plan_after_remove_all_shedules(current_lessonplan)
		current_lessonplan = lessonplan_integrator.add_root_schedule_to_schedule_list(current_lessonplan,schedule_list,root_sessions)
		current_lessonplan = lessonplan_integrator.get_updated_lesson_plan(schedule_list,current_lessonplan)
		current_lessonplan = lessonplan_integrator.create_remaining_sessions_on_root_when_schedule_removed(schedule_list,current_lessonplan,root_sessions)
	return current_lessonplan

def get_schedules_list(key,values) :
	schedul_list = []
	for value in values :
		schedule = create_schedule(key,value)
		if schedule_already_exist(schedul_list,schedule) == False :
			schedul_list.append(schedule)
	return schedul_list

		
def schedule_already_exist(schedul_list,schedule) :
	is_exist = False
	for existing_schedule in schedul_list :
		if existing_schedule.event_code == schedule.event_code and existing_schedule.start_time == schedule.start_time and existing_schedule.end_time == schedule.end_time :
			is_exist = True
	return is_exist

def create_schedule(key,event) :
	schedule = lpnr.Schedule(None)
	schedule.calendar_key = 'tset'
	schedule.event_code = event.event_code
	schedule.start_time = event.from_time
	schedule.end_time = event.to_time
	return schedule

def update_teacher_cals_and_class_cals(removed_events,teacher_cals,class_cals,updated_class_calendars_list,updated_teacher_calendars_list) :
	for current_class_calendar in class_cals :
		updated_class_calendar = get_updated_class_calendar(current_class_calendar,removed_events)
		updated_class_calendars_list.append(updated_class_calendar)

	for current_teacher_calendar in teacher_cals :
		updated_teacher_calendar = get_updated_teacher_calendar(current_teacher_calendar,removed_events)
		updated_teacher_calendars_list.append(updated_teacher_calendar)
	
		

def is_class_class_calendar_already_exist(class_cals,current_class_calendar) :
	is_exist = False
	for calendar in class_cals :
		if calendar.calendar_key == current_class_calendar.calendar_key :
			is_exist = True
	return is_exist

def get_class_calendar_event(current_class_calendar,event_code,removed_events) :
	for event in current_class_calendar.events :
		if event.event_code == event_code :
			return event

def is_this_event_already_exist(current_class_calendar,class_event,removed_events) :
	is_already_exist = False
	for event in removed_events :
		if event.event_code == class_event.event_code and event.from_time[:10] == current_class_calendar.calendar_date :
			is_already_exist = True
	return is_already_exist

def get_updated_class_calendar(current_class_calendar,removed_events) :
	for event in removed_events :
		 current_class_calendar = get_event_removed_class_calendar(event,current_class_calendar)
	return current_class_calendar
def get_updated_teacher_calendar(current_teacher_calendar,removed_events) :
	for event in removed_events :
		 current_teacher_calendar = get_event_removed_teacher_calendar(event,current_teacher_calendar)
	return current_teacher_calendar

def get_event_removed_class_calendar(event,current_class_calendar) :
	for existing_event in current_class_calendar.events :
		if existing_event.event_code == event.event_code and existing_event.from_time == event.from_time :
			current_class_calendar.events.remove(existing_event)
	return current_class_calendar


def get_event_removed_teacher_calendar(event,current_teacher_calendar) :
	for existing_event in current_teacher_calendar.events :
		if event.event_code == existing_event.event_code :
			current_teacher_calendar.events.remove(existing_event)
	return current_teacher_calendar


def get_teacher_calendars_on_dates(from_date,to_date,employee_key) :
		teacher_cals = []
		dates_list = timetable_integrator.get_dates(from_date,to_date)
		for cal_date in dates_list :
			teacher_calendar = calendar_service.get_calendar_by_date_and_key(cal_date, employee_key)
			teacher_cals.append(teacher_calendar)
		return teacher_cals
			

									
	
