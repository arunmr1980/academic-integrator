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

import pprint
pp = pprint.PrettyPrinter(indent=4)

def generate_and_save_calenders(time_table_key,academic_year):
	gclogger.info("Generating for timetable " + time_table_key + " academic_year " + academic_year)
	timetable = timetable_service.get_time_table(time_table_key)
	school_key = timetable.school_key
	academic_configuration = academic_service.get_academig(school_key,academic_year)
	school_calendars_list = []
	class_calendars_list = []
	generated_class_calendar_dict = integrate_class_timetable(timetable,academic_configuration, class_calendars_list, school_calendars_list)
	gclogger.info("Number of class calendars generated " + str(len(generated_class_calendar_dict)))
	class_calendar_list = generated_class_calendar_dict.values()

	generated_teacher_calendar_dict = integrate_teacher_timetable(class_calendar_list)
	gclogger.info("Number of teacher calendars generated " + str(len(generated_teacher_calendar_dict)))

	teacher_calendar_list = generated_teacher_calendar_dict.values()

	save_or_update_calendars(class_calendar_list, teacher_calendar_list)


def save_or_update_calendars(class_calendar_list, teacher_calendar_list):
	gclogger.info("------ Saving/Updating calendars ---------------------")
	gclogger.info(" Class calendars - " + str(len(class_calendar_list)))
	gclogger.info(" Teacher calendars - " + str(len(teacher_calendar_list)))
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



def integrate_class_timetable(timetable, academic_configuration, class_calendars_list, school_calendars_list):
	class_calendar_dict = {}
	start_date = academic_configuration.start_date
	end_date = academic_configuration.end_date
	generated_class_calendar = None

	gclogger.info("Processing timetable " + timetable.time_table_key + ' between dates ' + start_date + ' - ' + end_date)
	if is_exist_employee_key_and_subject_code(timetable) :
		dates_list = get_dates(start_date,end_date)
		for date in dates_list :
			gclogger.debug(' date - ' + date)
			gclogger.debug(' date - ' + date)
			day_code = findDay(date).upper()
			set_school_calendar_list(school_calendars_list, timetable, date)
			set_class_calendar_list(class_calendars_list, timetable, date)
			existing_class_calendar = get_class_calendar(date,class_calendars_list)
			existing_school_calendar = get_school_calendar(date,school_calendars_list)
			if existing_school_calendar is not None :
				gclogger.info('School calendar exist for the date ---------->' + date)
				holiday_period_list = generate_holiday_period_list(existing_school_calendar,academic_configuration,timetable,day_code[0:3])
				if existing_class_calendar is not None :
					holiday_period_list_from_class_calendar = generate_holiday_period_list(existing_class_calendar,academic_configuration,timetable,day_code[0:3])
				else :
					holiday_period_list_from_class_calendar = []

				holiday_period_list.extend(holiday_period_list_from_class_calendar)
				generated_class_calendar = generate_class_calendar(day_code[0:3],timetable,date,academic_configuration.time_table_configuration,holiday_period_list,existing_class_calendar)


			elif existing_class_calendar is not None :
				holiday_period_list = generate_holiday_period_list(existing_class_calendar,academic_configuration,timetable,day_code[0:3])
				generated_class_calendar = generate_class_calendar(day_code[0:3],timetable,date,academic_configuration.time_table_configuration,holiday_period_list,existing_class_calendar)

			else :
				holiday_period_list = []
				generated_class_calendar = generate_class_calendar(day_code[0:3],timetable,date,academic_configuration.time_table_configuration,holiday_period_list,existing_class_calendar)


			if generated_class_calendar is not None :
				class_calendar_dict[generated_class_calendar.calendar_date] = generated_class_calendar
				gclogger.info("Class calendar generated for " + date + ' claendar key ' + generated_class_calendar.calendar_key)
	return class_calendar_dict



def set_school_calendar_list(school_calendars_list, timetable, date) :
	gclogger.info("Getting School calendar -------------------------------------------------------------")
	if get_school_calendar(date,school_calendars_list) is None :
		subscriber_key = timetable.school_key
		school_cal = calendar_service.get_calendar_by_date_and_key(date,subscriber_key)
		if school_cal is not None:
			school_calendars_list.append(school_cal)
			gclogger.info("School calendar - Existing in DB "+ date)
	else:
		gclogger.info("School calendar - calendar present in Dict")


def set_class_calendar_list(class_calendars_list, timetable, date) :
	gclogger.info("Getting Class calendar -------------------------------------------------------------")
	if get_class_calendar(date,class_calendars_list) is None :
		subscriber_key = timetable.class_key+"-"+timetable.division
		class_cal = calendar_service.get_calendar_by_date_and_key(date,subscriber_key)
		if class_cal is not None:
			class_calendars_list.append(class_cal)
			gclogger.info("Class calendar - Existing in DB "+ date)
	else:
		gclogger.info("Class calendar - calendar present in Dict")


def get_class_calendar(date,class_calendars_list) :
	for class_calendar in class_calendars_list :
		if class_calendar.calendar_date == date :
			return class_calendar


def get_school_calendar(date,school_calendars_list) :
	for school_calendar in school_calendars_list :
		if school_calendar.calendar_date == date :
			return school_calendar


def is_class(param) :
	is_class = None
	if param.key == 'is_class_flag' and param.value == 'false' :
		is_class = False
	else :
		is_class = True
	return is_class


def generate_holiday_period_list(calendar,academic_configuration,timetable,day_code) :
	holiday_period_list =[]
	for event in calendar.events :
		if is_class(event.params[0]) == False :
			start_time = event.from_time
			end_time = event.to_time
			partial_holiday_periods = get_holiday_period_list(start_time,end_time,day_code,academic_configuration,timetable,calendar.calendar_date)
			for partial_holiday_period in partial_holiday_periods :
				holiday_period_list.append(partial_holiday_period)

	return holiday_period_list


def get_holiday_period_list(start_time,end_time,day_code,academic_configuration,timetable,date) :
	partial_holiday_period_list =[]
	if hasattr(academic_configuration.time_table_configuration ,'time_table_schedules') :
		for time_table_schedule in academic_configuration.time_table_configuration.time_table_schedules :
				for class_key in time_table_schedule.applied_classes :
					if class_key == timetable.class_key :
						for day_table in  time_table_schedule.day_tables :
							if day_table.day_code == day_code :
								for period in day_table.periods :
									standard_start_time = get_standard_time(period.start_time,date)
									standard_end_time = get_standard_time(period.end_time,date)
									if check_holiday_time_conflict(start_time,end_time,standard_start_time,standard_end_time) :
										partial_holiday_period_list.append(period)

	return partial_holiday_period_list


def check_holiday_time_conflict(event_start_time,event_end_time,standard_start_time,standard_end_time) :
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

	standard_start_time_year = int(standard_start_time[:4])
	standard_start_time_month = int(standard_start_time[5:7])
	standard_start_time_day = int(standard_start_time[8:10])
	standard_start_time_hour = int(standard_start_time[11:13])
	standard_start_time_min = int(standard_start_time[14:16])
	standard_start_time_sec = int(standard_start_time[-2:])

	standard_end_time_year = int(standard_end_time[:4])
	standard_end_time_month = int(standard_end_time[5:7])
	standard_end_time_day = int(standard_end_time[8:10])
	standard_end_time_hour = int(standard_end_time[11:13])
	standard_end_time_min = int(standard_end_time[14:16])
	standard_end_time_sec = int(standard_end_time[-2:])

	standard_start_time = dt(standard_start_time_year, standard_start_time_month, standard_start_time_day, standard_start_time_hour, standard_start_time_min, standard_start_time_sec, 000000)
	standard_end_time = dt(standard_end_time_year, standard_end_time_month, standard_end_time_day, standard_end_time_hour, standard_end_time_min, standard_end_time_sec, 000000)
	event_start_time = dt(event_start_time_year, event_start_time_month, event_start_time_day, event_start_time_hour, event_start_time_min, event_start_time_sec, 000000)
	event_end_time = dt(event_end_time_year, event_end_time_month, event_end_time_day, event_end_time_hour, event_end_time_min, event_end_time_sec, 000000)

	delta = max(event_start_time,standard_start_time) - min(event_end_time,standard_end_time)
	if delta.days < 0 :
	    is_conflict = True
	else :
	    is_conflict = False

	return is_conflict

	# is_conflict = False
	# off_time_start_hr =  int(event_start_time.split(':',2)[0][-2:])
	# off_time_end_hr = int(event_end_time.split(':',2)[0][-2:])
	# off_time_start_min = int(event_start_time.split(':',2)[1])
	# off_time_end_min = int(event_end_time.split(':',2)[1])
	#
	# standard_start_hr = int(standard_start_time.split(':',2)[0][-2:])
	# standard_end_hr =  int(standard_end_time.split(':',2)[0][-2:])
	# standard_start_min = int(standard_start_time.split(':',2)[1])
	# standard_end_min =  int(standard_end_time.split(':',2)[1])
	#
	# if event_start_time == standard_start_time :
	# 	is_conflict = True
	# 	print(is_conflict,"--1--")
	# elif event_end_time == standard_end_time :
	# 	is_conflict = True
	# 	print(is_conflict,"--2--")
	# elif (off_time_start_hr <= standard_start_hr and off_time_end_hr >= standard_end_hr and off_time_end_min != standard_start_min) :
	# 	is_conflict = True
	# 	print(is_conflict,"--3--")
	# elif (off_time_start_hr <standard_start_hr and off_time_end_hr > standard_end_hr) :
	# 	is_conflict = True
	# 	print(is_conflict,"--4--")
	# elif off_time_start_hr == standard_start_hr and off_time_start_min <  standard_start_min and off_time_end_hr == standard_end_hr and off_time_end_min > standard_end_min:
	# 	is_conflict = True
	# 	print(is_conflict,"--5--")
	# elif off_time_start_hr == standard_start_hr and off_time_end_hr >= standard_end_hr :
	# 	is_conflict = True
	# 	print(is_conflict,"--6--")
	#
	# else:
	# 	is_conflict = False
	# return is_conflict





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



def get_holiday_events(school_calendar_event) :
	event_list = []
	event = calendar.Event(None)
	event.event_code = key.generate_key(3)
	event.event_type = school_calendar_event.event_type
	event.from_time = school_calendar_event.from_time
	event.to_time = school_calendar_event.to_time
	event_list.append(event)
	return event_list



def generate_class_calendar(day_code,time_table,date,timetable_configuration,partial_holiday_period_list,existing_class_calendar):
	timetable_configuration_periods = None
	class_calendar = None
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
					if not period_exist_or_not(time_table_period,partial_holiday_period_list):
						if timetable_configuration_periods is not None:
							event = get_event(time_table_period,timetable_configuration_periods,date)

							events_list.append(event)
				if (day.day_code == day_code):
					if existing_class_calendar is not None :
						for event in events_list :
							existing_class_calendar = check_is_event_exist_and_remove(event, existing_class_calendar)
							existing_class_calendar.events.append(event)
						class_calendar = existing_class_calendar
						return class_calendar
					else :
						if len(events_list) > 0 :
							class_calendar=calendar.Calendar(None)
							class_calendar.institution_key = time_table.school_key
							class_calendar.calendar_date = date
							class_calendar.calendar_key = key.generate_key(16)
							class_calendar.subscriber_key = str(class_key + '-' + division)
							class_calendar.subscriber_type = "CLASS-DIV"
							class_calendar.events = events_list
					if class_calendar is not None :
						c = calendar.Calendar(None)
						class_calendar_dict = c.make_calendar_dict(class_calendar)
					return class_calendar

def check_is_event_exist_and_remove(event,existing_class_calendar) :
	for event_info in existing_class_calendar.events :
		if hasattr(event_info, 'params'):
			for param in event_info.params :
				if param.value == get_period_param(event) :
					existing_class_calendar.events.remove(event_info)
	return existing_class_calendar

def get_period_param(event) :
	for param in event.params :
		if(param.key == 'period_code') :
			return param.value



def integrate_teacher_timetable(class_calendar_list) :
	teacher_calendars_dict = {}
	teacher_calendar_list = []
	gclogger.info("Processing teacher timetable from class timetables ......")
	for class_calendar in class_calendar_list :
		for event in class_calendar.events :
			employee_key = get_employee_key(event.params)
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


def get_employee_key(params) :

	for param in params :
		if param.key == 'teacher_emp_key' :
			return param.value



def period_exist_or_not(time_table_period,partial_holiday_period_list) :
	period_exist = False
	for no_class_period in partial_holiday_period_list :
		if no_class_period.period_code == time_table_period.period_code :
			period_exist = True
	return period_exist


def set_teacher_calendar_dict(teacher_calendars_dict,employee_key,class_calendar) :
	gclogger.info("Getting Teacher calendar -------------------------------------------------------------")
	key = class_calendar.calendar_date + employee_key
	if key not in teacher_calendars_dict:
		teacher_cal = calendar_service.get_calendar_by_date_and_key(class_calendar.calendar_date,employee_key)
		if teacher_cal is None:
			teacher_cal = generate_employee_calendar(employee_key,class_calendar)
			gclogger.info("Teacher calendar - New record created in DB")
		else:
			gclogger.info("Teacher calendar - Existing record loaded from DB")
		teacher_calendars_dict[key] = teacher_cal
	else:
		gclogger.info("Teacher calendar present in Dict")


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
