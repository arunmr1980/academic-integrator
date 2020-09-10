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




def integrate_class_timetable(timetable, academic_configuration,class_calendar_holiday_list,school_calendar_holiday_list):
	class_calendar_dict = {}
	start_date = academic_configuration.start_date
	end_date = academic_configuration.end_date

	gclogger.info("Processing timetable " + timetable.time_table_key + ' between dates ' + start_date + ' - ' + end_date)
	if is_exist_employee_key_and_subject_code(timetable) :
		dates_list = get_dates(start_date,end_date)
		for date in dates_list :
			print(date,'dateeeee')
			gclogger.debug(' date - ' + date)
			day_code = findDay(date).upper()
			# class_calendar = is_class_calendar_exist(date,class_calendar_holiday_list)
			school_calendar = is_school_calendar_exist(date,school_calendar_holiday_list) 
			if school_calendar is not None : 
				start_time_end_time = get_start_time_and_end_time(academic_configuration,day_code[0:3],timetable)
				if start_time_end_time is not None :		
					start_time = start_time_end_time['start_time']
					end_time = start_time_end_time['end_time']
					if (check_full_holiday(start_time,end_time,school_calendar) ) :
						class_calendar = generate_holiday_class_calendar(school_calendar,timetable)

					else :
						partial_holiday_period_list = get_partial_holiday_period_list(school_calendar,academic_configuration,timetable,day_code[0:3])
						other_no_class_events_period_list = get_other_no_class_events_period_list (school_calendar,academic_configuration,timetable,day_code[0:3])
						class_calendar = generate_partial_holiday_class_calendar(day_code[0:3],timetable,date,academic_configuration.time_table_configuration,partial_holiday_period_list)


	# 		if class_calendar :
	# 			start_time_end_time = get_start_time_and_end_time(academic_configuration,day_code[0:3],timetable)
	# 			start_time = start_time_end_time['start_time']
	# 			end_time = start_time_end_time['end_time']
	# 			class_calendar = check_full_holiday(start_time,end_time,class_calendar,day_code[0:3],timetable)
	# 		else :
	# 			class_calendar = generate_class_calendar(day_code[0:3],timetable,date,academic_configuration.time_table_configuration)
	# 		if class_calendar is not None :
	# 			class_calendar_dict[class_calendar.calendar_date] = class_calendar
	# 			gclogger.info("Class calendar generated for " + date + ' claendar key ' + class_calendar.calendar_key)
	# return class_calendar_dict


def get_start_time_and_end_time(academic_configuration,day_code,timetable) :
	start_time_end_time = {}
	time_table_schedule = get_time_table_shedule(academic_configuration,timetable)
	if time_table_schedule :
		day_tables = time_table_schedule.day_tables 
		for day_table in day_tables :
			if day_table.day_code == day_code :
				start_time_end_time['start_time'] = day_table.periods[0].start_time
				start_time_end_time['end_time'] = day_table.periods[-1].end_time
				print('Start time of' + day_code + 'is' + start_time_end_time['start_time'])
				print('End time of' + day_code + 'is' + start_time_end_time['end_time'])
				return start_time_end_time


def get_time_table_shedule(academic_configuration,timetable) :
	if hasattr(academic_configuration.time_table_configuration ,'time_table_schedules') :
		for time_table_schedule in academic_configuration.time_table_configuration.time_table_schedules :
			if hasattr(time_table_schedule,'applied_classes') :
				for class_key in time_table_schedule.applied_classes :
					if class_key == timetable.class_key :
						return time_table_schedule


def is_class_calendar_exist(date,class_calendar_holiday_list) :
	for class_calendar in class_calendar_holiday_list :
		if class_calendar.calendar_date == date :
			return class_calendar


def is_school_calendar_exist(date,school_calendar_holiday_list) :	
	for school_calendar in school_calendar_holiday_list :
		if school_calendar.calendar_date == date :
			print('School calendar exist for the date' + date)
			return school_calendar

def check_partial_holiday(school_calendar) :


def check_full_holiday(start_time,end_time,calendar) :
	print('checking is fullday holiday on date '+ calendar.calendar_date)
	for event in calendar.events :
		
		academic_start_time = get_standard_time(start_time[:-3],calendar.calendar_date)
		academic_end_time = get_standard_time(end_time[:-3],calendar.calendar_date)
		if event.event_type == 'HOLIDAY' and event.from_time == academic_start_time and event.to_time == academic_end_time:
			print(calendar.calendar_date +'is a fullday holiday')
			return True

def get_other_no_class_events_period_list(school_calendar,academic_configuration,timetable,day_code) :
	print('checking is other events holiday on date '+ school_calendar.calendar_date)
	no_class_events_period_list =[]
	for event in school_calendar.events :
		if event.event_type != 'HOLIDAY' and event.is_class == False:
			start_time = event.from_time 	
			end_time = event.to_time 	
			no_class_events_period_list = start_period_end_period(start_time,end_time,day_code,academic_configuration,timetable,school_calendar.calendar_date)
	return no_class_events_period_list

def get_partial_holiday_period_list(school_calendar,academic_configuration,timetable,day_code) :
	print('checking is partial holiday on date '+ school_calendar.calendar_date)
	partial_holiday_period_list =[]
	for event in school_calendar.events :
		if event.event_type == 'HOLIDAY' :
			start_time = event.from_time 	
			end_time = event.to_time 	
			partial_holiday_period_list = start_period_end_period(start_time,end_time,day_code,academic_configuration,timetable,school_calendar.calendar_date)
	return partial_holiday_period_list

			
def start_period_end_period(start_time,end_time,day_code,academic_configuration,timetable,date) :

	start_period_order_index = None
	end_period_order_index = None
	partial_holiday_period_list =[]
	if hasattr(academic_configuration.time_table_configuration ,'time_table_schedules') :
		for time_table_schedule in academic_configuration.time_table_configuration.time_table_schedules :
				for class_key in time_table_schedule.applied_classes :
					if class_key == timetable.class_key :
						for day_table in  time_table_schedule.day_tables :
							if day_table.day_code == day_code :
								for period in day_table.periods :
									standard_start_time = get_standard_time(period.start_time,date)
									if standard_start_time == start_time  :
										order_index = period.order_index
										start_period_order_index = order_index
										print(start_period_order_index,'start_period_order_index,,,,,,,,,,,,,,,,,')
									standard_end_time = get_standard_time(period.end_time,date)
									if standard_end_time == end_time  :
										order_index = period.order_index
										end_period_order_index = order_index
										print(end_period_order_index,'end_period_order_index,,,,,,,,,,,,,,,,,')

	if hasattr(academic_configuration.time_table_configuration ,'time_table_schedules') :
		for time_table_schedule in academic_configuration.time_table_configuration.time_table_schedules :
				for class_key in time_table_schedule.applied_classes :
					if class_key == timetable.class_key :
						for day_table in  time_table_schedule.day_tables :
							if day_table.day_code == day_code :	
								if start_period_order_index == end_period_order_index :
									print(start_period_order_index,',,,,,,,,,,,,,,,,,')
									partial_holiday_period_list.append(day_table.periods[start_period_order_index - 1])
								else :
									for index in range(start_period_order_index,end_period_order_index) :
										partial_holiday_period_list.append(day_table.period[index])

	return partial_holiday_period_list
										


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


def generate_holiday_class_calendar(school_calendar,timetable):
	class_calendar=calendar.Calendar(None)
	class_calendar.institution_key = timetable.school_key
	class_calendar.calendar_date = school_calendar.calendar_date
	class_calendar.calendar_key = key.generate_key(16)
	class_calendar.subscriber_key = str(timetable.class_key + '-' + timetable.division)
	class_calendar.subscriber_type = "CLASS-DIV"
	class_calendar.events = get_holiday_events(school_calendar.events[0])
	print('generated class calendar' + class_calendar.calendar_key + str(school_calendar.calendar_date))
	return class_calendar


def get_holiday_events(school_calendar_event) :
	event_list = []
	event = calendar.Event(None)
	event.event_code = key.generate_key(3)
	event.event_type = school_calendar_event.event_type
	event.from_time = school_calendar_event.from_time
	event.to_time = school_calendar_event.to_time
	event_list.append(event)
	return event_list

def generate_class_calendar(day_code,time_table,date,timetable_configuration):
	# print(timetable_configuration.time_table_schedules.day_tables)

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


def generate_partial_holiday_class_calendar(day_code,time_table,date,timetable_configuration,partial_holiday_period_list):
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
					if not period_exist_or_not(time_table_period,partial_holiday_period_list):
						if timetable_configuration_periods is not None:
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



def period_exist_or_not(time_table_period,partial_holiday_period_list) :
	period_exist = False
	for partial_holiday_period in partial_holiday_period_list :
		if partial_holiday_period.period_code == time_table_period.period_code :
			period_exist = True
	return period_exist

def get_teacher_calendar(teacher_calendar_list,employee_key, class_calendar) :
	teacher_calendar_result = None
	for teacher_calendar in teacher_calendar_list :
		if teacher_calendar.subscriber_key == employee_key and teacher_calendar.calendar_date == class_calendar.calendar_date :
			teacher_calendar_result = teacher_calendar

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
