import academics.calendar.CalendarDBService as calendar_service
import academics.calendar.Calendar as cldr
from datetime import datetime as dt
from academics.logger import GCLogger as gclogger
import academics.academic.AcademicDBService as academic_service
import academics.classinfo.ClassInfoDBService as class_info_service
import academics.timetable.TimeTableDBService as timetable_service
from academics.TimetableIntegrator import *
import academics.TimetableIntegrator as timetable_integrator
from academics.lessonplan.LessonplanIntegrator import *
import academics.lessonplan.LessonPlan as lpnr
import pprint
pp = pprint.PrettyPrinter(indent=4)
import copy

# Remove event calendar integration
def remove_event_integrate_calendars(calendar_key,events) :
	updated_calendars_list = []
	calendar = calendar_service.get_calendar(calendar_key)
	school_key = calendar.institution_key
	calendar_date = calendar.calendar_date
	academic_configuration = academic_service.get_academic_year(school_key,calendar_date)
	academic_year = academic_configuration.academic_year
	day_code = timetable_integrator.findDay(calendar.calendar_date).upper()[0:3]
	class_info_list = class_info_service.get_classinfo_list(school_key,academic_year)
	class_calendars = get_class_calendars(class_info_list,calendar_date)
	if calendar.subscriber_type == 'SCHOOL' :
		for existing_class_calendar in class_calendars :
			subscriber_key = existing_class_calendar.subscriber_key
			update_class_calendars_teacher_calendars(subscriber_key,existing_class_calendar,calendar,academic_configuration,updated_calendars_list,day_code,calendar_date)
	if calendar.subscriber_type == 'CLASS-DIV' and is_class(events[0].params[0]) == True :
		subscriber_key = calendar.subscriber_key
		existing_class_calendar = calendar_service.get_calendar_by_date_and_key(calendar_date, subscriber_key)
		updated_calendars_list.append(existing_class_calendar)
		# self.update_class_calendars_and_teacher_calendars(existing_class_calendar,timetables,calendar,academic_configuration,updated_class_calendars,updated_teacher_calendars,day_code,date,current_teacher_calendars)
	if calendar.subscriber_type == 'CLASS-DIV' and is_class(events[0].params[0]) == False :
		subscriber_key = calendar.subscriber_key
		existing_class_calendar = calendar_service.get_calendar_by_date_and_key(calendar_date, subscriber_key)
		class_key = subscriber_key[:-2]
		division = subscriber_key[-1:]
		timetable = timetable_service.get_timetable_by_class_key_and_division(class_key,division)
		updated_class_calendar = update_class_calendar_by_adding_conflicted_periods(existing_class_calendar,timetable,calendar,events,academic_configuration,updated_calendars_list,day_code)

		updated_class_calendar_events = updated_class_calendar.events
		employee_key_list = get_employee_key_list(updated_class_calendar_events)
		for employee_key in employee_key_list :
			teacher_calendar = get_teacher_calendar_by_emp_key_and_date(employee_key,updated_class_calendar)
			if teacher_calendar is None :
				teacher_calendar = generate_employee_calendar(subscriber_key,updated_class_calendar)
			update_teacher_calendar_by_adding_conflicted_periods(updated_class_calendar_events,teacher_calendar,updated_class_calendar,updated_calendars_list)

	upload_updated_calendars(updated_calendars_list)
	integrate_cancelled_holiday_lessonplan(calendar_key)



def integrate_update_period_calendars_and_lessonplans(period_code,time_table_key) :
	updated_calendars_list =[]
	updated_lessonplan_list = []
	updated_class_calendar_subject_key_list = []
	updated_timetable = timetable_service.get_time_table(time_table_key)
	school_key = updated_timetable.school_key
	class_key = updated_timetable.class_key
	division = updated_timetable.division
	subscriber_key = class_key + '-' + division
	current_class_calendars = calendar_service.get_all_calendars_by_key_and_type(subscriber_key,'CLASS-DIV')

	current_lessonplans = lessonplan_service.get_lesson_plan_list(class_key,division)
	current_class_cals = copy.deepcopy(current_class_calendars)

	current_class_calendars_with_day_code = get_current_class_calendars_with_day_code(period_code[:3],current_class_calendars)
	current_class_calendars_with_day_code_copy = copy.deepcopy(current_class_calendars_with_day_code)
	updated_timetable_period = get_updated_period_from_timetable(period_code,updated_timetable)


	for current_class_calendar in current_class_calendars_with_day_code :
		event = get_event_with_period_code(current_class_calendar,period_code)
		if event is not None :
			existing_event = copy.deepcopy(event)
			updated_class_calendar = update_event(event,current_class_calendar,updated_timetable_period)
			if updated_class_calendar is not None :
				updated_calendars_list.append(updated_class_calendar)

			updated_previous_teacher_calendar = update_previous_teacher_calendar(existing_event,updated_class_calendar)
			if updated_previous_teacher_calendar is not None :
				updated_calendars_list.append(updated_previous_teacher_calendar)

			updated_new_teacher_calendar = update_new_teacher_calendar(updated_class_calendar,period_code)
			if updated_new_teacher_calendar is not None :
				updated_calendars_list.append(updated_new_teacher_calendar)

			updated_previous_subject_lessonplan = update_previous_subject_lessonplan(existing_event,current_lessonplans, updated_class_calendar)
			if updated_previous_subject_lessonplan is not None :
				updated_lessonplan_list.append(updated_previous_subject_lessonplan)

			updated_new_subject_lessonplan = update_new_subject_lessonplan(updated_timetable_period, current_lessonplans, updated_class_calendar)
			if updated_new_subject_lessonplan is not None :
				updated_lessonplan_list.append(updated_new_subject_lessonplan)


	for updated_calendar in updated_calendars_list :
		cal = cldr.Calendar(None)
		calendar_dict = cal.make_calendar_dict(updated_calendar)
		response = calendar_service.add_or_update_calendar(calendar_dict)
		gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' ------- A updated calendar-- ( '+str(calendar_dict['subscriber_type'])+' )  uploaded --------- '+str(calendar_dict['calendar_key']))

	for updated_lessonplan in updated_lessonplan_list :
		lp = lpnr.LessonPlan(None)
		updated_lessonplan_dict = lp.make_lessonplan_dict(updated_lessonplan)
		response = lessonplan_service.create_lessonplan(updated_lessonplan_dict)
		gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' ------- A updated lessonplan uploaded -------- '+str(updated_lessonplan_dict['lesson_plan_key']))

def update_previous_subject_lessonplan(existing_event,current_lessonplans, updated_class_calendar) :
	subject_key = get_subject_key(existing_event.params)
	current_lessonplan = get_current_lesson_plan_with_subject_key(current_lessonplans,subject_key)
	updated_lessonplan = Update_lessonplan(current_lessonplan,updated_class_calendar)
	return updated_lessonplan


def update_new_teacher_calendar(updated_class_calendar, period_code) :
	updated_new_teacher_calendar = None
	updated_class_calendar_events = get_period_code_events(updated_class_calendar, period_code)
	subscriber_key = get_employee_key(updated_class_calendar_events[0].params)
	if subscriber_key is not None :
		new_teacher_calendar = Get_teacher_calendar(updated_class_calendar,subscriber_key)
		updated_new_teacher_calendar = update_teacher_calendar_with_new_event(new_teacher_calendar,updated_class_calendar_events[0],updated_class_calendar)
	return updated_new_teacher_calendar


def update_previous_teacher_calendar(existing_event,current_class_calendar) :

	subscriber_key = get_employee_key(existing_event.params)
	previous_teacher_calendar = calendar_service.get_calendar_by_date_and_key(current_class_calendar.calendar_date,subscriber_key)

	updated_previous_teacher_calendar = update_current_teacher_calendar(existing_event,previous_teacher_calendar,current_class_calendar)
	return updated_previous_teacher_calendar


def update_current_teacher_calendar(existing_event,previous_teacher_calendar,current_class_calendar) :
	for event in previous_teacher_calendar.events :
		if event.event_code == existing_event.event_code and event.ref_calendar_key == current_class_calendar.calendar_key :
			previous_teacher_calendar.events.remove(event)
	return previous_teacher_calendar


def update_new_subject_lessonplan(updated_timetable_period, current_lessonplans, updated_class_calendar) :
	updated_class_calendar_events = get_subject_events_matching_period_code(updated_class_calendar, updated_timetable_period.period_code)
	current_lessonplan = get_current_lesson_plan_with_subject_key(current_lessonplans,updated_timetable_period.subject_key)
	if current_lessonplan is not None :
		updated_lessonplan = add_schedules(updated_class_calendar_events,current_lessonplan,updated_class_calendar)
		return updated_lessonplan


def update_teacher_calendar_with_new_event(new_teacher_calendar,calendar_event,updated_class_calendar) :
	if hasattr(new_teacher_calendar, 'events') :
		event_object = cldr.Event(None)
		event_object.event_code = calendar_event.event_code
		event_object.ref_calendar_key = updated_class_calendar.calendar_key
		new_teacher_calendar.events.append(event_object)
	return new_teacher_calendar


def get_updated_existing_teacher_calendar(teacher_calendar,updated_class_calendar_events,updated_class_calendar,subject_code) :
	for event in updated_class_calendar_events :
		employee_key = get_employee_key(event.params)
		if employee_key != teacher_calendar.subscriber_key :
			event_code = event.event_code
			subject_key = get_subject_key(event.params)
			if subject_key == subject_code :
				teacher_calendar_event = get_event(teacher_calendar,event.event_code)
				teacher_calendar.events.remove(teacher_calendar_event)			
	return teacher_calendar

def get_event(calendar,event_code) :
	for existing_event in calendar.events :
		if existing_event.event_code == event_code :
			return existing_event

def get_updated_new_teacher_calendar(teacher_calendar,updated_class_calendar_events,updated_class_calendar) :
	for event in updated_class_calendar_events :
		employee_key = get_employee_key(event.params)
		if employee_key == teacher_calendar.subscriber_key and is_event_already_exist(event,teacher_calendar.events) == False:
			event_object = calendar.Event(None)
			event_object.event_code = event.event_code
			event_object.ref_calendar_key = updated_class_calendar.calendar_key
			teacher_calendar.events.append(event_object)
	return teacher_calendar

def generate_employee_calendar(employee_key,updated_class_calendar) :
	employee_calendar = calendar.Calendar(None)
	employee_calendar.calendar_date = updated_class_calendar.calendar_date
	employee_calendar.calendar_key = key.generate_key(16)
	employee_calendar.institution_key = updated_class_calendar.institution_key
	employee_calendar.subscriber_key = employee_key
	employee_calendar.subscriber_type = 'EMPLOYEE'
	employee_calendar.events = []
	return employee_calendar

def generate_class_calendar(class_key,division,calendar_date,institution_key) :
	class_calendar = calendar.Calendar(None)
	class_calendar.calendar_date = calendar_date
	class_calendar.calendar_key = key.generate_key(16)
	class_calendar.institution_key = institution_key
	class_calendar.subscriber_key = class_key +'-'+ division
	class_calendar.subscriber_type = 'CLASS-DIV'
	class_calendar.events = []
	return class_calendar

def Get_teacher_calendar(updated_class_calendar,subscriber_key) :
	existing_teacher_calendar = calendar_service.get_calendar_by_date_and_key(updated_class_calendar.calendar_date,subscriber_key)
	if existing_teacher_calendar is not None :
		return existing_teacher_calendar
	else :
		employee_calendar = generate_employee_calendar(subscriber_key,updated_class_calendar)
		return employee_calendar

def get_period_code_events(updated_class_calendar, period_code) :
	event_list = []
	if hasattr(updated_class_calendar,'events') :
		for event in updated_class_calendar.events :
			if event.event_type == 'CLASS_SESSION' and is_match_period_code(event, period_code) == True :
				event_list.append(event)
	return event_list



def get_subject_events_matching_period_code(updated_class_calendar, period_code) :
	event_list = []
	if hasattr(updated_class_calendar,'events') :
		for event in updated_class_calendar.events :
			subject_key = find_subject_key(event,period_code)
			if subject_key is not None :
				if event.event_type == 'CLASS_SESSION' and get_subject_key(event.params) == subject_key:
					event_list.append(event)
	return event_list

def find_subject_key(event,period_code) :
	if event.params[0].value == period_code :
		return event.params[1].value

def make_event_objects(events) :
	events_obj = []
	for event in events :		
		event_obj = cldr.Event(event)
		events_obj.append(event_obj)
	print(events_obj)
	return events_obj


def get_subject_key(params) :
	for param in params :
		if(param.key == 'subject_key') :
			return param.value

def get_employee_key_list(updated_class_calendar_events) :
	employee_key_list = []
	for event in updated_class_calendar_events :
		employee_key = get_employee_key(event.params)
		if employee_key not in employee_key_list :
			employee_key_list.append(employee_key)
	return employee_key_list

def get_employee_key(params) :
	for param in params :
		if param.key == 'teacher_emp_key' :
			return param.value

def is_match_period_code(event,period_code) :
		for param in event.params :
			if(param.key == 'period_code') and param.value == period_code :
				return True


def get_event_with_period_code(current_class_calendar,period_code) :
	if hasattr(current_class_calendar,'events') :
		for event in current_class_calendar.events :
			if is_need_update_parms(event,period_code) == True :
				return event


def is_need_update_parms(event,period_code) :
		for param in event.params :
			if(param.key == 'period_code') and param.value == period_code :
				return True

def update_event(event,current_class_calendar,updated_timetable_period) :
	updated_params = update_params(event.params,current_class_calendar,updated_timetable_period)
	del event.params
	event.params = updated_params
	return current_class_calendar


def update_params(params,current_class_calendar,updated_timetable_period) :
	period_code = updated_timetable_period.period_code
	subject_key = updated_timetable_period.subject_key
	employee_key = updated_timetable_period.employee_key
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

def get_current_class_calendars_with_day_code(day_code,current_current_class_calendars) :
	current_class_calendars_with_day_code = []
	for current_class_calendar in current_current_class_calendars :
		if (get_day_code_from_calendar(current_class_calendar,day_code) ) == True :
			current_class_calendars_with_day_code.append(current_class_calendar)
	return current_class_calendars_with_day_code


def get_day_code_from_calendar(current_class_calendar,period_code) :
	for event in current_class_calendar.events :
		if event.params[0].key == 'period_code' and event.params[0].value[:3] == period_code :
			return True


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


def generate_holiday_period_list(calendar,academic_configuration,timetable,day_code) :
	holiday_period_list =[]
	for event in calendar.events :
		if is_class(event.params[0]) == False :
			start_time = event.from_time
			end_time = event.to_time
			partial_holiday_periods = timetable_integrator.get_holiday_period_list(start_time,end_time,day_code,academic_configuration,timetable,calendar.calendar_date)
			for partial_holiday_period in partial_holiday_periods :
				holiday_period_list.append(partial_holiday_period)
	return holiday_period_list


def update_class_calendars_teacher_calendars(subscriber_key,existing_class_calendar,calendar,academic_configuration,updated_calendars_list,day_code,calendar_date) :
	class_key = subscriber_key[:-2]
	division = subscriber_key[-1:]
	timetable = timetable_service.get_timetable_by_class_key_and_division(class_key,division)
	if timetable is not None :
		holiday_period_list = generate_holiday_period_list(calendar,academic_configuration,timetable,day_code)
		updated_class_calendar = timetable_integrator.generate_class_calendar(day_code,timetable,calendar_date,academic_configuration.time_table_configuration,holiday_period_list,existing_class_calendar)
		updated_calendars_list.append(updated_class_calendar)
		updated_class_calendar_events = updated_class_calendar.events
		employee_key_list = get_employee_key_list(updated_class_calendar_events)
		for employee_key in employee_key_list :
			if employee_key is not None :
				teacher_calendar = calendar_service.get_calendar_by_date_and_key(calendar_date,employee_key)
				if teacher_calendar is None :
					teacher_calendar = timetable_integrator.generate_employee_calendar(employee_key,updated_class_calendar)
					updated_teacher_calendar = update_teacher_calendar(teacher_calendar,updated_class_calendar_events,existing_class_calendar)
					updated_calendars_list.append(updated_teacher_calendar)


def update_class_calendar_by_adding_conflicted_periods(existing_class_calendar,timetable,calendar,events,academic_configuration,updated_calendars_list,day_code) :
	period_list = timetable_integrator.generate_period_list(calendar,events,academic_configuration,timetable,day_code)
	gclogger.info("------ Periods to adde to calendar -------")
	for period in period_list :
		gclogger.info(period.start_time + ' -- '  + period.end_time)
	events = make_events(period_list,timetable,existing_class_calendar.calendar_date)
	updated_class_calendar = add_events_to_calendar(events,existing_class_calendar)
	updated_calendars_list.append(updated_class_calendar)
	return updated_class_calendar

def update_teacher_calendar_by_adding_conflicted_periods(updated_class_calendar_events,teacher_calendar,updated_class_calendar,updated_calendars_list) :
	updated_teacher_calendar = update_teacher_calendar(teacher_calendar,updated_class_calendar_events,updated_class_calendar)
	updated_calendars_list.append(updated_teacher_calendar)


def get_teacher_calendar_by_emp_key_and_date(employee_key,updated_class_calendar) :
	teacher_calendar = calendar_service.get_calendar_by_date_and_key(updated_class_calendar.calendar_date,employee_key)
	if teacher_calendar is None :
		teacher_calendar = timetable_integrator.generate_employee_calendar(employee_key,updated_class_calendar)
	return teacher_calendar


		
def get_time_table_period(period_code,timetable) :
	timetable_configuration_period = None 
	if hasattr(timetable.timetable,'day_tables') :
		days = timetable.timetable.day_tables
		for day in days :
			for time_table_period in day.periods :
				if time_table_period.period_code == period_code :
					return time_table_period

		
def add_events_to_calendar(events,existing_class_calendar) :
	for event in events :
		existing_class_calendar.events.append(event)
	updated_class_calendar = sort_updated_class_calendar_events(existing_class_calendar)
	return updated_class_calendar

	
		
def sort_updated_class_calendar_events(existing_class_calendar) :
	from operator import attrgetter
	soreted_events = sorted(existing_class_calendar.events, key = attrgetter('from_time'))
	existing_class_calendar.events = soreted_events
	return existing_class_calendar


def get_employee_key_list(updated_class_calendar_events) :
	employee_key_list = []
	for event in updated_class_calendar_events :
		employee_key = get_employee_key(event.params)
		if employee_key not in employee_key_list :
			employee_key_list.append(employee_key)
	return employee_key_list




def update_teacher_calendar(teacher_calendar,updated_class_calendar_events,updated_class_calendar) :
	for event in updated_class_calendar_events :
		employee_key = get_employee_key(event.params)
		if employee_key == teacher_calendar.subscriber_key and is_event_already_exist(event,teacher_calendar.events) == False :
			event_object = cldr.Event(None)
			event_object.event_code = event.event_code
			event_object.ref_calendar_key = updated_class_calendar.calendar_key
			teacher_calendar.events.append(event_object)
	return teacher_calendar

def is_event_already_exist(event,events) :
	is_event_exist = False
	for existing_event in events :
		if existing_event.event_code == event.event_code :
			is_event_exist = True
	return is_event_exist



# Add event calendar integration
def add_event_integrate_calendars(event_code,calendar_key) :
	updated_calendars_list = []
	calendar = calendar_service.get_calendar(calendar_key)
	school_key = calendar.institution_key
	calendar_date = calendar.calendar_date
	academic_configuration = academic_service.get_academic_year(school_key,calendar_date)
	academic_year = academic_configuration.academic_year
	event = get_event_from_calendar(calendar,event_code)

	gclogger.info("EVENT START TIME AND END TIME ----------------->" + str(event.from_time) + str(event.to_time))
	class_info_list = class_info_service.get_classinfo_list(school_key,academic_year)
	class_calendars = get_class_calendars(class_info_list,calendar_date)
	teacher_calendars_list =[]
	if calendar.subscriber_type == 'SCHOOL' and is_class(event.params[0]) == False :
		for class_calendar in class_calendars :
			updated_calendars = update_class_calendars_and_teacher_calendars(class_calendar,event,teacher_calendars_list)
			updated_calendars_list.extend(updated_calendars)

	if calendar.subscriber_type == 'CLASS-DIV' and is_class(event.params[0]) == False :
		updated_calendars = update_class_calendars_and_teacher_calendars(calendar,event,teacher_calendars_list)
		updated_calendars_list.extend(updated_calendars)

	upload_updated_calendars(updated_calendars_list)
	integrate_holiday_lessonplan(event_code,calendar_key)


def get_class_calendars(class_info_list,calendar_date) :
	class_calendars = []
	for class_info in class_info_list :
		if hasattr(class_info, 'divisions') :
			for div in class_info.divisions :
				subscriber_key = str(class_info.class_info_key +'-'+ div.name)
				current_class_calendar = calendar_service.get_calendar_by_date_and_key(calendar_date,subscriber_key)
				if current_class_calendar is not None :
					class_calendars.append(current_class_calendar)

	return class_calendars

def get_event_from_calendar(calendar,event_code) :
	for event in calendar.events :
		if event.event_code == event_code :
			return event

def upload_updated_calendars(updated_calendars_list) :
	for calendar in updated_calendars_list :
		cal = cldr.Calendar(None)
		calendar_dict = cal.make_calendar_dict(calendar)
		# pp.pprint(calendar_dict)
		response = calendar_service.add_or_update_calendar(calendar_dict)
		gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' ------- A calendar uploaded --------- ' +str(calendar_dict['subscriber_type']) + '-' + str(calendar_dict['calendar_key']))


def get_updated_teacher_event(events_to_remove_list,teacher_calendar) :
	events_list = []
	for teacher_event in teacher_calendar.events :
		if not do_remove_event(teacher_event,events_to_remove_list) == True :
			gclogger.info("---THIS EVENT IS NOT NEEDED TO REMOVE ---" + teacher_event.event_code)
			events_list.append(teacher_event)
	return events_list


def do_remove_event(event,events_to_remove_list) :
	for remove_event in events_to_remove_list :
		if remove_event.event_code == event.event_code :
			return True


def get_class_calendars_on_calendar_date(calendar,current_class_calendars) :
	class_calendars =[]
	for current_class_calendar in current_class_calendars :
		if calendar.calendar_date == current_class_calendar.calendar_date :
			class_calendars.append(current_class_calendar)
	return class_calendars

def get_teacher_calendars_on_calendar_date(calendar,current_teacher_calendars) :
	teacher_calendars =[]
	for current_teacher_calendar in current_teacher_calendars :
		if calendar.calendar_date == current_teacher_calendar.calendar_date :
			teacher_calendars.append(current_teacher_calendar)
	return teacher_calendars

def update_class_calendars_and_teacher_calendars(class_calendar,event,teacher_calendars_list) :
	updated_calendars = []
	calendar_date = class_calendar.calendar_date
	events_to_remove_list = get_events_to_remove(class_calendar,event)
	updated_class_calendar = remove_events_from_class_calendar(events_to_remove_list,class_calendar)
	updated_calendars.append(updated_class_calendar)
	for event in events_to_remove_list :
		employee_key = get_employee_key(event.params)
		if employee_key is not None :
			teacher_calendar = get_teacher_calendar(teacher_calendars_list,employee_key,calendar_date)
			updated_teacher_calendar = Update_teacher_calendar(events_to_remove_list,teacher_calendar)
			updated_calendars.append(updated_teacher_calendar)
	return updated_calendars

def Update_teacher_calendar(events_to_remove_list,teacher_calendar) :
	event_list = get_updated_teacher_event(events_to_remove_list,teacher_calendar)
	del teacher_calendar.events
	teacher_calendar.events = event_list
	return teacher_calendar

def get_teacher_calendar(teacher_calendars_list,employee_key,calendar_date) :
	teacher_calendar = None
	for calendar in teacher_calendars_list :
		if calendar.subscriber_key == employee_key and calendar.calendar_date == calendar_date :
			teacher_calendar = calendar
	if teacher_calendar is None :
		teacher_calendar = calendar_service.get_calendar_by_date_and_key(calendar_date,employee_key)
		teacher_calendars_list.append(teacher_calendar)
	return teacher_calendar


def get_all_events_to_remove(class_calendars,calendar) :
	event = calendar.events[0]
	events_to_remove_list = []
	for class_calendar in class_calendars :
		events_list = get_events_to_remove(class_calendar,event)
		events_to_remove_list = events_to_remove_list + events_list
	return events_to_remove_list

def get_updated_event(class_calendar,events_to_remove_list) :
	event_list = []
	for event in class_calendar.events :
		if not event in events_to_remove_list :
			event_list.append(event)
	return event_list

def is_class(param) :
	is_class = False
	if param.key == 'cancel_class_flag' and param.value == 'true' :
		is_class = False
	else :
		is_class = True
	return is_class

def make_events(period_list,timetable,date) :
	events_list =[]
	for period in period_list :
		event = calendar.Event(None)
		event.event_code = key.generate_key(3)
		event.event_type = 'CLASS_SESSION'
		time_table_period = get_time_table_period(period.period_code,timetable)
		event.params = timetable_integrator.get_params(time_table_period.subject_key , time_table_period.employee_key , time_table_period.period_code)

		event.from_time =  timetable_integrator.get_standard_time(period.start_time,date)
		event.to_time =  timetable_integrator.get_standard_time(period.end_time,date)
		gclogger.info("Event created " + event.event_code + ' start ' + event.from_time + ' end ' + event.to_time)
		events_list.append(event)
	return events_list
		
def get_time_table_period(period_code,timetable) :
	timetable_configuration_period = None 
	if hasattr(timetable.timetable,'day_tables') :
		days = timetable.timetable.day_tables
		for day in days :
			for time_table_period in day.periods :
				if time_table_period.period_code == period_code :
					return time_table_period

		
def add_events_to_calendar(events,existing_class_calendar) :
	for event in events :
		existing_class_calendar.events.append(event)
	updated_class_calendar = sort_updated_class_calendar_events(existing_class_calendar)
	return updated_class_calendar

	
		
def sort_updated_class_calendar_events(existing_class_calendar) :
	from operator import attrgetter
	soreted_events = sorted(existing_class_calendar.events, key = attrgetter('from_time'))
	existing_class_calendar.events = soreted_events
	return existing_class_calendar









def get_events_to_remove(class_calendar,event) :
	events_to_remove_list = []
	calendar_event_start_time = event.from_time
	calendar_event_end_time = event.to_time
	gclogger.info("Updating Calendar " + class_calendar.calendar_key +'--------------')
	gclogger.info('Holiday calendar event------------------')
	gclogger.info('START ' + calendar_event_start_time)
	gclogger.info('END ' + calendar_event_end_time)
	gclogger.info('')
	for event in class_calendar.events :
		class_calendar_event_start_time = event.from_time
		class_calendar_event_end_time = event.to_time
		if check_events_conflict(calendar_event_start_time,calendar_event_end_time,class_calendar_event_start_time,class_calendar_event_end_time) :
			gclogger.info("-----------NEED TO REMOVE THE EVENT  ----------" +event.event_code + '----')
			events_to_remove_list.append(event)
		else :
			gclogger.info("------------- NO CONFLICT WITH THE EVENT ---------- " + event.event_code)
	return events_to_remove_list


def remove_events_from_class_calendar(events_to_remove_list,class_calendar) :
	event_list = get_updated_event(class_calendar,events_to_remove_list)
	del class_calendar.events
	class_calendar.events = event_list
	return class_calendar

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
