import academics.calendar.CalendarDBService as calendar_service
import academics.calendar.Calendar as cldr
from datetime import datetime as dt
from academics.logger import GCLogger as gclogger
import academics.academic.AcademicDBService as academic_service
import academics.classinfo.ClassInfoDBService as class_info_service
import academics.timetable.TimeTableDBService as timetable_service
from academics.TimetableIntegrator import *
from academics.lessonplan.LessonplanIntegrator import integrate_holiday_lessonplan,integrate_cancelled_holiday_lessonplan
import pprint
pp = pprint.PrettyPrinter(indent=4)

# Remove event calendar integration
def remove_event_integrate_calendars(calendar_key) :
	updated_calendars_list = []
	calendar = calendar_service.get_calendar(calendar_key)
	school_key = calendar.institution_key
	calendar_date = calendar.calendar_date
	academic_configuration = academic_service.get_academic_year(school_key,calendar_date)
	academic_year = academic_configuration.academic_year
	day_code = findDay(calendar.calendar_date).upper()[0:3]
	class_info_list = class_info_service.get_classinfo_list(school_key,academic_year)
	class_calendars = get_class_calendars(class_info_list,calendar_date)
	if calendar.subscriber_type == 'SCHOOL' :
		for existing_class_calendar in class_calendars :
			subscriber_key = existing_class_calendar.subscriber_key
			update_class_calendars_teacher_calendars(subscriber_key,existing_class_calendar,calendar,academic_configuration,updated_calendars_list,day_code,calendar_date)

	else :
		if calendar.subscriber_type == 'CLASS-DIV' :
			subscriber_key = calendar.subscriber_key
			existing_class_calendar = calendar_service.get_calendar_by_date_and_key(calendar_date, subscriber_key)
			update_class_calendars_teacher_calendars(subscriber_key,existing_class_calendar,calendar,academic_configuration,updated_calendars_list,day_code,calendar_date)

	upload_updated_calendars(updated_calendars_list)
	integrate_cancelled_holiday_lessonplan(calendar_key)



def update_class_calendars_teacher_calendars(subscriber_key,existing_class_calendar,calendar,academic_configuration,updated_calendars_list,day_code,calendar_date) :
	class_key = subscriber_key[:-2]
	division = subscriber_key[-1:]
	timetable = timetable_service.get_timetable_by_class_key_and_division(class_key,division)
	if timetable is not None :
		holiday_period_list = generate_holiday_period_list(calendar,academic_configuration,timetable,day_code)
		updated_class_calendar = generate_class_calendar(day_code,timetable,calendar_date,academic_configuration.time_table_configuration,holiday_period_list,existing_class_calendar)
		updated_calendars_list.append(updated_class_calendar)
		updated_class_calendar_events = updated_class_calendar.events
		employee_key_list = get_employee_key_list(updated_class_calendar_events)
		for employee_key in employee_key_list :
			teacher_calendar = calendar_service.get_calendar_by_date_and_key(calendar_date,employee_key)
			updated_teacher_calendar = update_teacher_calendar(teacher_calendar,updated_class_calendar_events,existing_class_calendar)
			updated_calendars_list.append(updated_teacher_calendar)



def update_teacher_calendar(teacher_calendar,updated_class_calendar_events,existing_class_calendar) :
	for event in updated_class_calendar_events :
		employee_key = get_employee_key(event)
		if employee_key == teacher_calendar.subscriber_key :
			event_object = cldr.Event(None)
			event_object.event_code = event.event_code
			event_object.ref_calendar_key = existing_class_calendar.calendar_key
			teacher_calendar.events.append(event_object)
	return teacher_calendar

def get_employee_key_list(updated_class_calendar_events) :
	employee_key_list = []
	for event in updated_class_calendar_events :
		employee_key = get_employee_key(event)
		if employee_key not in employee_key_list :
			employee_key_list.append(employee_key)
	return employee_key_list


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
		response = calendar_service.add_or_update_calendar(calendar_dict)
		gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' ------- A Class calendar uploaded --------- '+str(calendar_dict['calendar_key']))


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
		employee_key = get_employee_key(event)
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
	for teacher_calendar in teacher_calendars_list :
		if teacher_calendar.subscriber_key == employee_key and teacher_calendar.calendar_date == calendar_date :
			return teacher_calendar
	else :
		teacher_calendar = calendar_service.get_calendar_by_date_and_key(calendar_date,employee_key)
		teacher_calendars_list.append(teacher_calendar)
		return teacher_calendar


def get_employee_key(event) :
	for param in event.params :
		if param.key == 'teacher_emp_key' :
			return param.value

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
