from datetime import date, timedelta
import datetime
import calendar as cal
import academics.timetable.TimeTableDBService as timetable_service
from academics.logger import GCLogger as gclogger
import academics.timetable.TimeTable as ttable
import academics.timetable.KeyGeneration as key
import academics.calendar.Calendar as calendar
import academics.academic.AcademicDBService as academic_service
import academics.calendar.CalendarDBService as calendar_service




def generate_and_save_calenders(time_table_key,academic_year):
	timetable = timetable_service.get_time_table(time_table_key)
	school_key = timetable.school_key
	academic_configuration = academic_service.get_academig(school_key,academic_year)
	generated_class_calendar_dict = integrate_class_timetable(timetable,academic_configuration)
	class_calendar_list = []
	for generated_class_calendar in generated_class_calendar_dict.values() :
		class_calendar_list.append(generated_class_calendar)

	generated_teacher_calendar_dict = integrate_teacher_timetable(class_calendar_list)

	teacher_calendar_list = []
	for generated_teacher_calendar in generated_teacher_calendar_dict.values() :
		teacher_calendar_list.append(generated_teacher_calendar)
	for class_calendar in class_calendar_list :
		class_calendar_dict = calendar.Calendar(None)
		class_calendar_dict = class_calendar_dict.make_calendar_dict(class_calendar)
		calendar_service.add_or_update_calendar(class_calendar_dict)
		gclogger.info('A class calendar uploaded for '+ class_calendar_dict['calendar_key'])
	for teacher_calendar in teacher_calendar_list :
		teacher_calendar_dict = calendar.Calendar(None)
		teacher_calendar_dict = teacher_calendar_dict.make_calendar_dict(teacher_calendar)
		calendar_service.add_or_update_calendar(teacher_calendar_dict)
		gclogger.info('A Teacher calendar uploaded for '+ teacher_calendar_dict['calendar_key'])




def integrate_class_timetable(timetable, academic_configuration):
	class_calendar_dict = {}
	start_date = academic_configuration.start_date
	end_date = academic_configuration.end_date

	gclogger.info("Processing timetable " + timetable.time_table_key + ' between dates ' + start_date + ' - ' + end_date)
	if is_exist_employee_key_and_subject_code(timetable) :
		dates_list = get_dates(start_date,end_date)
		for date in dates_list :
			gclogger.debug(' date - ' + date)
			day_code = findDay(date).upper()

			class_calendar=generate_class_calendar(day_code[0:3],timetable,date,academic_configuration.time_table_configuration)
			if class_calendar is not None :
				class_calendar_dict[class_calendar.calendar_date] = class_calendar
				gclogger.info("Class calendar generated for " + date + ' claendar key ' + class_calendar.calendar_key)
	return class_calendar_dict



def get_event(time_table_period,timetable_configuration_periods,date):

	current_configuration_period = None
	if timetable_configuration_periods is not None :
		for timetable_configuration_period in timetable_configuration_periods :
			if timetable_configuration_period.period_code == time_table_period.period_code :
				current_configuration_period = timetable_configuration_period

		if current_configuration_period is not None :
			event = calendar.Event(None)
			event.event_code = key.generate_key(3)
			event.event_type = 'CLASS_SESSION'
			event.params = get_params(time_table_period.subject_key , time_table_period.employee_key , time_table_period.period_code)

			event.from_time = get_standard_time(current_configuration_period.start_time,date)
			event.to_time = get_standard_time(current_configuration_period.end_time,date)
			gclogger.info("Event created " + event.event_code + ' start ' + event.from_time + ' end ' + event.to_time)
			return event


def get_standard_time(time,date) :

	splited_date = date.split('-')
	splited_date = list(map(int,splited_date))
	time_hour = int(time[0:2])
	time_minute = int(time[3:5])
	return datetime.datetime(splited_date[0],splited_date[1],splited_date[2],time_hour,time_minute).isoformat()


def get_params(subject_key,employee_key,period_code) :

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


def generate_class_calendar(day_code,time_table,date,timetable_configuration):

	timetable_configuration_periods = None
	if hasattr(timetable_configuration , 'time_table_schedules'):
		if hasattr(timetable_configuration.time_table_schedules[0],'day_tables'):
			for day in timetable_configuration.time_table_schedules[0].day_tables :
				if (day.day_code == day_code) :
					timetable_configuration_periods = day.periods
	else:
		gclogger.warn("Time table schedules not present in configuration. Can not process")
		return

	if hasattr(time_table, 'timetable') and time_table.timetable is not None :
		class_key=time_table.class_key
		division=time_table.division
		if hasattr(time_table.timetable,'day_tables') and len(time_table.timetable.day_tables) > 0 :
			for day in time_table.timetable.day_tables :
				periods = day.periods
				events_list = []
				for time_table_period in periods :
					if 	timetable_configuration_periods is not None:
						event = get_event(time_table_period,timetable_configuration_periods,date)
						events_list.append(event)
				if (day.day_code == day_code):
					class_calendar=calendar.Calendar(None)
					class_calendar.institution_key = time_table.school_key
					class_calendar.calendar_date = date
					class_calendar.calendar_key = key.generate_key(16)
					class_calendar.subscriber_key = str(class_key + '-' + division)
					class_calendar.subscriber_type = "CLASS-DIV"
					class_calendar.events = events_list
					return class_calendar


def integrate_teacher_timetable(class_calendar_list) :
	teacher_calendars_dict = {}
	teacher_calendar_list = []
	gclogger.info("Processing teacher timetable from class timetables ......")
	for class_calendar in class_calendar_list :
		for event in class_calendar.events :
			employee_key = get_employee_key(event.params)
			teacher_calendar = get_teacher_calendar(teacher_calendar_list,employee_key,class_calendar)
			event_object = calendar.Event(None)
			event_object.event_code = event.event_code
			event_object.ref_calendar_key = class_calendar.calendar_key
			teacher_calendar.events.append(event_object)
			gclogger.info("Adding event " + event_object.event_code + " to teacher calendar " + teacher_calendar.calendar_key)
	for teacher_calendar in teacher_calendar_list :
		calendar_date = teacher_calendar.calendar_date
		subscriber_key = teacher_calendar.subscriber_key
		teacher_calendars_dict[calendar_date + subscriber_key] = teacher_calendar
	return teacher_calendars_dict


def get_employee_key(params) :

	for param in params :
		if param.key == 'teacher_emp_key' :
			return param.value


def get_teacher_calendar(teacher_calendar_list,employee_key, class_calendar) :
	teacher_calendar_result = None
	for teacher_calendar in teacher_calendar_list :
		if teacher_calendar.subscriber_key == employee_key and teacher_calendar.calendar_date == class_calendar.calendar_date :
			teacher_calendar_result = teacher_calendar
		else :
			teacher_calendar_result = calendar_service.get_calendar_by_date_and_key(class_calendar.calendar_date,employee_key)

	if teacher_calendar_result is None:
		teacher_calendar_result = generate_employee_calendar(employee_key,class_calendar)
		teacher_calendar_list.append(teacher_calendar_result)
	return teacher_calendar_result


def generate_employee_calendar(employee_key,class_calendar) :
	employee_calendar=calendar.Calendar(None)
	employee_calendar.calendar_date = class_calendar.calendar_date
	employee_calendar.calendar_key = key.generate_key(16)
	employee_calendar.institution_key = class_calendar.institution_key
	employee_calendar.subscriber_key = employee_key
	employee_calendar.subscriber_type = 'EMPLOYEE'
	employee_calendar.events = []

	return employee_calendar


def get_dates(start_date,end_date):
	splited_start_date = start_date.split('-')
	splited_end_date = end_date.split('-')

	splited_start_date = list(map(int,splited_start_date))
	splited_end_date = list(map(int,splited_end_date))

	sdate = date(splited_start_date[0],splited_start_date[1],splited_start_date[2])
	edate = date(splited_end_date[0],splited_end_date[1],splited_end_date[2])
	return get_all_dates(sdate,edate)


def get_all_dates(sdate,edate):
	dates_list = []
	delta = edate - sdate       # as timedelta
	for i in range(delta.days + 1):
		day = sdate + timedelta(days = i)
		day = day.strftime('%Y-%m-%d')
		dates_list.append(day)
	return dates_list


def findDay(date):
	born = datetime.datetime.strptime(date,'%Y-%m-%d').weekday()
	return (cal.day_name[born])


def is_exist_employee_key_and_subject_code(time_table) :
	if hasattr(time_table, 'timetable') and time_table.timetable is not None :
		if hasattr(time_table.timetable,'day_tables') and len(time_table.timetable.day_tables) > 0 :
			for day in time_table.timetable.day_tables :
				if hasattr(day,'periods') and len(day.periods) > 0 :
					for period in day.periods :
						if hasattr(period ,'subject_key') and hasattr(period,'employee_key'):
							return True
						else:
							gclogger.warn('Subject_key or employee key not existing')

				else :
					gclogger.warn('Periods not existing')

		else:
			gclogger.warn('Days_table not existing')

	else:
		gclogger.warn('Time table not existing')
