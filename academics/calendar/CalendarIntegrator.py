import academics.calendar.CalendarDBService as calendar_service
import academics.calendar.Calendar as cldr
from datetime import datetime as dt
from academics.logger import GCLogger as gclogger
import pprint
pp = pprint.PrettyPrinter(indent=4)


def integrate_class_calendars(event_code,calendar_key) :
	updated_class_calendar_list = []
	calendar = calendar_service.get_calendar(calendar_key)	
	current_class_calendars = calendar_service.get_all_calendars_by_school_key_and_type(calendar.institution_key,'CLASS-DIV')
	class_calendars = get_class_calendars_on_calendar_date(calendar,current_class_calendars)
	if calendar.subscriber_type == 'SCHOOL' and is_class(calendar.events[0].params[0]) == False :
		for class_calendar in class_calendars :
			updated_class_calendar = update_class_calendar(class_calendar,calendar)
			updated_class_calendar_list.append(updated_class_calendar)
	return updated_class_calendar_list

def integrate_teacher_calendars(event_code,calendar_key) :
	updated_teacher_calendar_list = []
	calendar = calendar_service.get_calendar(calendar_key)
	current_class_calendars = calendar_service.get_all_calendars_by_school_key_and_type(calendar.institution_key,'CLASS-DIV')
	class_calendars = get_class_calendars_on_calendar_date(calendar,current_class_calendars)
	current_teacher_calendars = calendar_service.get_all_calendars_by_school_key_and_type(calendar.institution_key,'EMPLOYEE')
	teacher_calendars = get_teacher_calendars_on_calendar_date(calendar,current_teacher_calendars)
	if calendar.subscriber_type == 'SCHOOL' and is_class(calendar.events[0].params[0]) == False :	
			events_to_remove_list = get_all_events_to_remove(class_calendars,calendar)
			for teacher_calendar in teacher_calendars :
				updated_teacher_calendar = update_teacher_calendar(events_to_remove_list,teacher_calendar)
				updated_teacher_calendar_list.append(updated_teacher_calendar)
	return updated_teacher_calendar_list


def update_teacher_calendar(events_to_remove_list,teacher_calendar) :
	event_list = get_updated_teacher_event(events_to_remove_list,teacher_calendar)
	del teacher_calendar.events
	teacher_calendar.events = event_list
	return teacher_calendar

def get_updated_teacher_event(events_to_remove_list,teacher_calendar) :
	events_list = []
	for teacher_event in teacher_calendar.events :
		if not do_remove_event(teacher_event,events_to_remove_list) == True :
			gclogger.info("THIS EVENT IS NOT NEEDED TO REMOVE ---" + teacher_event.event_code)
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

def update_class_calendar(class_calendar,calendar) :
	event = calendar.events[0]		
	events_to_remove_list = get_events_to_remove(class_calendar,event)
	updated_class_calendar = remove_events_from_class_calendar(events_to_remove_list,class_calendar)
	return updated_class_calendar

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
			gclogger.info("-------------NO CONFLICT WITH THE EVENT ---------- " + event.event_code)
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
