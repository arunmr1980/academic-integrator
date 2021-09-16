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
import academics.leave.LeaveDBService as leave_service
import copy
import pprint
pp = pprint.PrettyPrinter(indent=4)



def integrate_lessonplan_on_substitute_teacher(calendar_key,event_code,substitution_emp_key,previous_substitution_emp_key,previous_substitution_subject_code) :
	gclogger.info("previous_substitution_emp_key inside function ------>>>" + str(previous_substitution_emp_key))
	gclogger.info("previous_substitution_subject_code inside function ---->>>" + str(previous_substitution_subject_code))
	updated_calendar = calendar_service.get_calendar(calendar_key)
	subscriber_key = updated_calendar.subscriber_key
	class_key = subscriber_key[:-2]
	division = subscriber_key[-1:]
	current_lessonplans_list = lessonplan_service.get_lesson_plan_list(class_key, division)
	updated_lessonplans_list = get_updated_lessonplans_on_substitute_teacher(updated_calendar,current_lessonplans_list,event_code,previous_substitution_subject_code)

	save_lessonplans(updated_lessonplans_list)
	

def save_lessonplans(updated_lessonplans_list) :
	for updated_lessonplan in updated_lessonplans_list :		
		lp = lpnr.LessonPlan(None)
		updated_lessonplan_dict = lp.make_lessonplan_dict(updated_lessonplan)
		response = lessonplan_service.create_lessonplan(updated_lessonplan_dict)
		gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' ------- A updated lessonplan uploaded --------- '+str(updated_lessonplan_dict['lesson_plan_key']))


def get_updated_lessonplans_on_substitute_teacher(updated_calendar,current_lessonplans_list,event_code,previous_substitution_subject_code) :
	updated_lessonplans_list = []
	if previous_substitution_subject_code is not None :
		subscriber_key = updated_calendar.subscriber_key
		class_key = subscriber_key[:-2]
		division = subscriber_key[-1:]
		current_lessonplan = get_current_lessonplan(current_lessonplans_list,previous_substitution_subject_code,class_key,division)
		event_to_be_removed = get_event_from_updated_calendar(updated_calendar,event_code)
		schedules_to_be_removed = []
		schedule_to_be_removed = lessonplan_integrator.create_schedule(event_to_be_removed,updated_calendar)
		schedules_to_be_removed.append(schedule_to_be_removed)
		updated_lessonplan = get_removed_event_updated_lessonplan_(current_lessonplan,schedules_to_be_removed)
		gclogger.info(previous_substitution_subject_code +"( Previous subject ) lesson plan updated with deleting event of event_code " + schedule_to_be_removed.event_code + ' ---////--------/////--------////-- ')
		updated_lessonplans_list.append(updated_lessonplan)
	events_to_be_added = []
	subscriber_key = updated_calendar.subscriber_key
	class_key = subscriber_key[:-2]
	division = subscriber_key[-1:]
	event_to_be_added = get_event_from_updated_calendar(updated_calendar,event_code)
	events_to_be_added.append(event_to_be_added)
	subject_key = calendar_integrator.get_subject_key(event_to_be_added.params)
	current_lessonplan = get_current_lessonplan(current_lessonplans_list,subject_key,class_key,division)
	events_to_be_added = events_to_be_added_to_lesson_plan(events_to_be_added,current_lessonplan)
	if len(events_to_be_added) > 0 :
		updated_lessonplan = lessonplan_integrator.add_schedules_and_adjust_lessonplan(current_lessonplan,events_to_be_added,updated_calendar)
		updated_lessonplans_list.append(updated_lessonplan)
	return updated_lessonplans_list



def get_current_lessonplan(current_lessonplans_list,subject_key,class_key,division) :
	for lessonplan in current_lessonplans_list :
		if lessonplan.subject_code == subject_key and lessonplan.class_key == class_key and lessonplan.division == division :
			return lessonplan

def get_event_from_updated_calendar(updated_calendar,event_code) :
	for event in updated_calendar.events :
		if event.event_code == event_code :
			return event


def integrate_leave_cancel(leave_key) :
	removed_events = []
	events_with_sub_key = {}
	class_cals_to_be_updated = []
	updated_class_calendars_list = []
	teacher_cals_to_be_updated = []

	leave = leave_service.get_leave(leave_key)
	from_time = None
	to_time = None
	if hasattr(leave,"from_time") :
		from_time = leave.from_time
	if hasattr(leave,"to_time") :
		to_time = leave.to_time
	if hasattr(leave, 'status') and leave.status == 'CANCELLED':
		employee_key = leave.subscriber_key
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
					gclogger.info(class_event.params[1].value + " subject_key -----------------------__>>>>>>> (1)")
					if from_time is not None and to_time is not None :
						if exam_integrator.check_events_conflict(class_event.from_time,class_event.to_time,from_time,to_time) == True :
							if is_this_event_already_exist(current_class_calendar,class_event,removed_events) == False :
								removed_events.append(class_event)
								if current_class_calendar.subscriber_key in events_with_sub_key :
									events_with_sub_key[current_class_calendar.subscriber_key].append(class_event)
								else :
									events_with_sub_key[current_class_calendar.subscriber_key] = []
									events_with_sub_key[current_class_calendar.subscriber_key].append(class_event)
					else :
						if is_this_event_already_exist(current_class_calendar,class_event,removed_events) == False :
								removed_events.append(class_event)
								if current_class_calendar.subscriber_key in events_with_sub_key :
									events_with_sub_key[current_class_calendar.subscriber_key].append(class_event)
								else :
									events_with_sub_key[current_class_calendar.subscriber_key] = []
									events_with_sub_key[current_class_calendar.subscriber_key].append(class_event)



	updated_removed_events = update_class_cals_on_cancel_leave(removed_events,class_cals_to_be_updated,updated_class_calendars_list,employee_key)
	for class_event in updated_removed_events :
			gclogger.info(class_event.params[1].value + " subject_key -----------------------__>>>>>>>(2)")
	school_key = updated_class_calendars_list[0].institution_key
	updated_teacher_calendars_list = integrate_teacher_calendars_on_cancel_leave(teacher_cals_to_be_updated,updated_class_calendars_list,school_key)
	current_lessonplans = get_lessonplans_list(events_with_sub_key.keys())
	updated_lessonplans_list = update_lessonplans_with_adding_events(current_lessonplans,updated_class_calendars_list,updated_removed_events)

	save_updated_calendars_and_lessonplans(updated_class_calendars_list,updated_teacher_calendars_list,updated_lessonplans_list)



def integrate_teacher_calendars_on_cancel_leave(current_teacher_calendars_list,updated_class_calendars_list,school_key) :
	updated_teacher_calendars_list =[]
	for updated_class_calendar in updated_class_calendars_list :
		for event in updated_class_calendar.events :
			calendar_date = updated_class_calendar.calendar_date
			employee_key = timetable_integrator.get_employee_key(event.params)
			if employee_key is not None :
				current_teacher_calendar = get_teacher_calendar(current_teacher_calendars_list,calendar_date,employee_key,school_key)
				emp_event = make_employee_event(event,updated_class_calendar)
				if is_calendar_already_exist(current_teacher_calendar,updated_teacher_calendars_list) == False :
					updated_teacher_calendars_list.append(current_teacher_calendar)

	for teacher_calendar in updated_teacher_calendars_list :
		for updated_class_calendar in updated_class_calendars_list :
			for event in updated_class_calendar.events :
				calendar_date = updated_class_calendar.calendar_date
				employee_key = timetable_integrator.get_employee_key(event.params)
				if teacher_calendar.calendar_date == calendar_date and teacher_calendar.subscriber_key == employee_key :
					emp_event = make_employee_event(event,updated_class_calendar)
					if is_event_already_exist(emp_event,teacher_calendar.events) == False :
						if hasattr(event, 'status') :
							del event.status

						teacher_calendar.events.append(emp_event)
	return updated_teacher_calendars_list

def is_event_already_exist(event,teacher_calendar_events) :
	is_exist = False
	for existing_event in teacher_calendar_events :
		if event.event_code == existing_event.event_code and event.ref_calendar_key == existing_event.ref_calendar_key :
			if hasattr(existing_event,'status') :
				del existing_event.status
			is_exist = True
	return is_exist

def is_calendar_already_exist(current_teacher_calendar,updated_teacher_calendars_list) :
	is_exist = False
	for updated_teacher_calendar in updated_teacher_calendars_list :
		if updated_teacher_calendar.subscriber_key == current_teacher_calendar.subscriber_key and updated_teacher_calendar.calendar_date == current_teacher_calendar.calendar_date:
			is_exist = True
	return is_exist


def make_employee_event(event,updated_class_calendar) :
	if event is not None :
		emp_event = calendar.Event(None)
		emp_event.event_code = event.event_code
		emp_event.ref_calendar_key = updated_class_calendar.calendar_key
	return emp_event


def get_teacher_calendar(teacher_calendars_list,calendar_date,employee_key,school_key) :
	employee_calendar = calendar_service.get_calendar_by_date_and_key(calendar_date, employee_key)
	if employee_calendar is None :
		employee_calendar = generate_employee_calendar(calendar_date,employee_key,school_key)
	return employee_calendar

def generate_employee_calendar(calendar_date,employee_key,school_key) :
	employee_calendar=calendar.Calendar(None)
	employee_calendar.calendar_date = calendar_date
	employee_calendar.calendar_key = key.generate_key(16)
	employee_calendar.institution_key = school_key
	employee_calendar.subscriber_key = employee_key
	employee_calendar.subscriber_type = 'EMPLOYEE'
	employee_calendar.events = []
	return employee_calendar

def get_teacher_leaves_in_academic_year(academic_configuration,subject_teachers) :
	class_teachers_leaves = []
	from_date = academic_configuration.start_date
	to_date = academic_configuration.end_date	
	for employee_key in subject_teachers :
		employee_leaves = leave_service.get_employee_leaves(employee_key,from_date,to_date)
		class_teachers_leaves.extend(employee_leaves)
	return class_teachers_leaves 



def integrate_teacher_timetable(class_calendar_list) :
	teacher_calendars_dict = {}
	teacher_calendar_list = []
	gclogger.info("Processing teacher timetable from class timetables ......")
	for class_calendar in class_calendar_list :
		for event in class_calendar.events :
			employee_key = timetable_integrator.get_employee_key(event.params)
			if employee_key is not None :
				set_teacher_calendar_dict(teacher_calendars_dict,employee_key,class_calendar)
				key = class_calendar.calendar_date + employee_key
				teacher_calendar = teacher_calendars_dict[key]

				event_object = calendar.Event(None)
				event_object.event_code = event.event_code
				event_object.ref_calendar_key = class_calendar.calendar_key
				teacher_calendar.events.append(event_object)
				gclogger.info("Adding event " + event_object.event_code + " to teacher calendar " + teacher_calendar.calendar_key)

	return teacher_calendars_dict


def set_teacher_calendar_dict(teacher_calendars_dict,employee_key,class_calendar) :
	gclogger.info("Getting Teacher calendar -------------------------------------------------------------")
	key = class_calendar.calendar_date + employee_key
	if key not in teacher_calendars_dict:
		teacher_cal = calendar_service.get_calendar_by_date_and_key(class_calendar.calendar_date,employee_key)
		if teacher_cal is None:
			teacher_cal = timetable_integrator.generate_employee_calendar(employee_key,class_calendar)
			gclogger.info("Teacher calendar - New record created in DB")
		else:
			gclogger.info("Teacher calendar - Existing record loaded from DB")

		teacher_calendars_dict[key] = teacher_cal
	else:
		gclogger.info("Teacher calendar present in Dict")


def update_class_cals_on_cancel_leave(removed_events,class_cals,updated_class_calendars_list,employee_key) :
	updated_removed_events = []
	for current_class_calendar in class_cals :
		subscriber_key = current_class_calendar.subscriber_key
		class_key = subscriber_key[:-2]
		division = subscriber_key[-1:]
		timetable = timetable_service.get_timetable_by_class_key_and_division(class_key,division)
		updated_class_calendar = get_updated_class_calendar_on_cancel_leave(current_class_calendar,removed_events,timetable,updated_removed_events,employee_key)
		updated_class_calendars_list.append(updated_class_calendar)
	return updated_removed_events

def integrate_add_leave_on_calendar(leave_key) :
	removed_events = []
	class_cals_to_be_updated = []
	teacher_cals_to_be_updated = []
	updated_class_calendars_list = []
	updated_teacher_calendars_list = []
	updated_lessonplans_list = []
	events_with_sub_key = {}
	leave = leave_service.get_leave(leave_key)
	employee_key = leave.subscriber_key
	from_time = None
	to_time = None
	if hasattr(leave,'from_time') :	
		from_time = leave.from_time
	if hasattr(leave,'to_time') :		
		to_time = leave.to_time
	from_date = leave.from_date
	to_date = leave.to_date
	teacher_cals = get_teacher_calendars_on_dates(from_date,to_date,employee_key)
	for teacher_calendar in teacher_cals :
		if teacher_calendar is not None :
			teacher_cals_to_be_updated.append(teacher_calendar)
			for event in teacher_calendar.events :
				calendar_key = event.ref_calendar_key
				if calendar_key is not None :
					event_code = event.event_code
					current_class_calendar = calendar_service.get_calendar(calendar_key) 
					if current_class_calendar is not None :
						if is_class_class_calendar_already_exist(class_cals_to_be_updated,current_class_calendar) == False :
							class_cals_to_be_updated.append(current_class_calendar)
						class_event = get_class_calendar_event(current_class_calendar,event_code,removed_events)
						if class_event is not None:
							if from_time is not None and to_time is not None :
								if exam_integrator.check_events_conflict(class_event.from_time,class_event.to_time,from_time,to_time) == True :
									if is_this_event_already_exist(current_class_calendar,class_event,removed_events) == False :
										removed_events.append(class_event)
										if current_class_calendar.subscriber_key in events_with_sub_key :
												events_with_sub_key[current_class_calendar.subscriber_key].append(class_event)
										else :
											events_with_sub_key[current_class_calendar.subscriber_key] = []
											events_with_sub_key[current_class_calendar.subscriber_key].append(class_event)
							else :
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

def update_lessonplans_with_adding_events(current_lessonplans,updated_class_calendars_list,removed_events) :
	updated_lessonplan_list = []
	for event in removed_events :
		events_to_be_added = []
		events_to_be_added.append(event)
		updated_class_calendar = find_updated_class_calendar_with_event(event,updated_class_calendars_list)
		class_key = updated_class_calendar.subscriber_key[:-2]
		division = updated_class_calendar.subscriber_key[-1:]
		current_lessonplan = get_lessonplan_with_class_key_and_division_and_subject_code(current_lessonplans,event.params[1].value,class_key,division)

		updated_lessonplan = lessonplan_integrator.add_schedules_and_adjust_lessonplan(current_lessonplan,events_to_be_added,updated_class_calendar)
		updated_lessonplan_list.append(updated_lessonplan)
	return updated_lessonplan_list

def get_lessonplan_with_class_key_and_division_and_subject_code(current_lessonplans,subject_code,class_key,division) :
	for lessonplan in current_lessonplans :
		if lessonplan.class_key == class_key and lessonplan.division == division and lessonplan.subject_code == subject_code :
			return lessonplan


def find_updated_class_calendar_with_event(event,updated_class_calendars_list) :
	for updated_class_calendar in updated_class_calendars_list :
		for existing_event in updated_class_calendar.events :
			if existing_event.event_code == event.event_code and existing_event.from_time == event.from_time :
				return updated_class_calendar


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
		 current_class_calendar = get_event_updated_class_calendar(event,current_class_calendar)
	return current_class_calendar

def get_updated_class_calendar_on_cancel_leave(current_class_calendar,removed_events,timetable,updated_removed_events,employee_key) :
	for event in removed_events :
		 current_class_calendar = get_event_updated_class_calendar_on_leave_cancel(event,current_class_calendar,timetable,updated_removed_events,employee_key)
	return current_class_calendar
	

def get_updated_teacher_calendar(current_teacher_calendar,removed_events) :
	for event in removed_events :
		 current_teacher_calendar = get_event_updated_teacher_calendar(event,current_teacher_calendar)
	return current_teacher_calendar

def get_updated_teacher_calendar_on_cancel_leave(current_teacher_calendar,removed_events) :
	for event in removed_events :
		 current_teacher_calendar = get_event_updated_teacher_calendar_on_leave(event,current_teacher_calendar)
	return current_teacher_calendar

def get_event_updated_class_calendar(event,current_class_calendar) :
	for existing_event in current_class_calendar.events :
		if existing_event.event_code == event.event_code and existing_event.from_time == event.from_time :
			# current_class_calendar.events.remove(existing_event)
			existing_event.status = 'UN-ASSIGNED'
			existing_event.params[1].value = 'null'
			existing_event.params[2].value = 'null'

	return current_class_calendar

def get_event_updated_class_calendar_on_leave_cancel(event,current_class_calendar,timetable,updated_removed_events,employee_key) :
	
	for existing_event in current_class_calendar.events :
		event_period_code = existing_event.params[0].value
		if existing_event.event_code == event.event_code and existing_event.from_time == event.from_time :
			gclogger.info(" UPDATING EVENT WITH EVENT CODE ------ "+ existing_event.event_code)
			gclogger.info("EXISTING SUBJECT KEY ------- "+ existing_event.params[1].value)
			gclogger.info("EXISTING EMPLOYEE KEY ------- "+ existing_event.params[2].value)
			gclogger.info("CURRENT CLASS CALENDAR -- "+ current_class_calendar.calendar_key)
			gclogger.info("TIMETABLE CLASS KEY -- "+ timetable.class_key)
			gclogger.info("TIMETABLE DIVISION -- "+ timetable.division)
			timetable_period = get_period_code_from_timetable(timetable,event_period_code)
			gclogger.info("TIMETABLE PERIOD CODE -- "+ timetable_period.period_code)
			gclogger.info("TIMETABLE SUBJECT KEY -- "+ timetable_period.subject_key)
			# gclogger.info("TIMETABLE EMPLOYEE KEY -- "+ timetable_period.employee_key)	
			
			del existing_event.status
			remove_events_from_substituted_teacher_calendar_and_lessonplan(existing_event,current_class_calendar)
			try :
				if timetable_period.employee_key is None :
					raise AttributeError("getting employee key None ")
				else :
					existing_event.params[1].value = timetable_period.subject_key
					existing_event.params[2].value = timetable_period.employee_key

			except AttributeError :
				employee = get_subscriber(timetable_period,employee_key)
				if employee is not None :
					existing_event.params[1].value = employee.subject_key
					existing_event.params[2].value = employee_key

			updated_removed_events.append(existing_event)
	return current_class_calendar


def get_period_code_from_timetable(current_class_timetable,event_period_code) :
	if hasattr(current_class_timetable, 'timetable') and current_class_timetable.timetable is not None :
		if hasattr(current_class_timetable.timetable,'day_tables') and len(current_class_timetable.timetable.day_tables) > 0 :
			for day in current_class_timetable.timetable.day_tables :
				if hasattr(day,'periods') and len(day.periods) > 0 :
					for period in day.periods :
						if period.period_code == event_period_code :
							return period
				else :
					gclogger.warn('Periods not existing')
		else:
			gclogger.warn('Days_table not existing')
	else:
		gclogger.warn('Time table not existing')

	return current_class_timetable



def get_event_updated_teacher_calendar(event,current_teacher_calendar) :
	for existing_event in current_teacher_calendar.events :
		if event.event_code == existing_event.event_code :
			# current_teacher_calendar.events.remove(existing_event)
			existing_event.status = "LEAVE"
	return current_teacher_calendar

def get_event_updated_teacher_calendar_on_leave(event,current_teacher_calendar) :
	for existing_event in current_teacher_calendar.events :
		if event.event_code == existing_event.event_code :
			# current_teacher_calendar.events.remove(existing_event)
			del existing_event.status
	return current_teacher_calendar


def get_teacher_calendars_on_dates(from_date,to_date,employee_key) :
		teacher_cals = []
		dates_list = timetable_integrator.get_dates(from_date,to_date)
		for cal_date in dates_list :
			teacher_calendar = calendar_service.get_calendar_by_date_and_key(cal_date, employee_key)
			teacher_cals.append(teacher_calendar)
		return teacher_cals
			

									
	
def get_subscriber(timetable_period,employee_key) :
	for employee in timetable_period.employees :
		if employee.employee_key == employee_key :
			return employee

def events_to_be_added_to_lesson_plan(events_to_be_added,current_lessonplan) :
	updated_events = []
	for event in events_to_be_added :
		if lessonplan_integrator.event_exist_in_lessonplan(event,current_lessonplan) == False :
			updated_events.append(event)
	return updated_events


def remove_events_from_substituted_teacher_calendar_and_lessonplan(existing_event,current_class_calendar) :
	if existing_event.params[2].value != 'null' :
		substituted_employee_key = existing_event.params[2].value 
		calendar_date = current_class_calendar.calendar_date
		event_code = existing_event.event_code
		gclogger.info(" REMOVING EVENT FROM " + substituted_employee_key + "T CALENDAR " + "EVENT CODE " + event_code + " DATE --->>" + calendar_date)
		remove_event_from_substituted_employee_calendar(substituted_employee_key,calendar_date,event_code)
	if existing_event.params[1].value != 'null' :
		substituted_subject_key = existing_event.params[1].value 
		subscriber_key = current_class_calendar.subscriber_key
		class_key = subscriber_key[:-2]
		division = subscriber_key[-1:]
		lessonplan_list = lessonplan_service.get_lesson_plan_list(class_key,division)
		for lessonplan in lessonplan_list :
			if lessonplan.subject_code == substituted_subject_key :
				gclogger.info(" REMOVING EVENT " + existing_event.event_code + "FROM "+ lessonplan.lesson_plan_key  )
				updated_lessonplan = lessonplan_integrator.cancel_class_session_to_lessonplan_integrator(lessonplan,existing_event,current_class_calendar)
				lp = lpnr.LessonPlan(None)
				updated_lessonplan_dict = lp.make_lessonplan_dict(updated_lessonplan)
				lessonplan_service.create_lessonplan(updated_lessonplan_dict)
				gclogger.info(" UPDATED LESSONPLAN UPDATED ------>> "+ updated_lessonplan.lesson_plan_key)

def remove_event_from_substituted_employee_calendar(substituted_employee_key,calendar_date,event_code) :
	teacher_calendar = calendar_service.get_calendar_by_date_and_key(calendar_date,substituted_employee_key)
	updated_events = []
	for event in teacher_calendar.events :
		if event.event_code != event_code :
			updated_events.append(event)
	teacher_calendar.events = updated_events
	cal = calendar.Calendar(None)
	teacher_calendar_dict = cal.make_calendar_dict(teacher_calendar)

	calendar_service.add_or_update_calendar(teacher_calendar_dict)
	gclogger.info(" UPDATED TEACHER CALENDAR UPDATED ------>> "+ teacher_calendar.calendar_key)	

