import unittest
import json
from academics.TimetableIntegrator import *
from academics.academic import AcademicConfiguration as academic_config
import academics.timetable.TimeTable as ttable
from academics.logger import GCLogger as gclogger
import academics.calendar.Calendar as cldr
import academics.lessonplan.LessonPlan as lessonplan
from academics.calendar.CalendarLessonPlanIntegrator import integrate_calendar_to_lesson_plan
from academics.lessonplan.LessonplanIntegrator import holiday_calendar_to_lessonplan_integrator
from academics.TimetableIntegrator import generate_holiday_period_list,generate_class_calendar,integrate_teacher_timetable
import academics.TimetableIntegrator as timetable_integrator
import academics.calendar.CalendarIntegrator as calendar_integrator
import operator
import pprint
pp = pprint.PrettyPrinter(indent=4)



class CalendarRemoveEventIntegratorTest(unittest.TestCase):
	def test_calendars(self) :
		updated_class_calendars = []
		updated_teacher_calendars = []
		calendar_key = 'test-key-3'
		events = [
					 {
			            "event_code":"event-1",
			            "event_type":"HOLIDAY",
			            "from_time":"2020-08-10T09:00:00",  
			            "to_time":"2020-08-10T10:40:00",
			            "params": [
			               {
			                  "key" :"cancel_class_flag",
			                  "value" : "true"
			               }
			            ] 
	         		}
			]
		events = self.make_event_objects(events)
		academic_configuration = self.get_academic_configuration()
		timetables = self.get_timetables()

		current_class_calendars = self.get_current_class_calendars()
		current_teacher_calendars = self.get_current_teacher_calendars()
		expected_class_calendars_list = self.get_expected_class_calendars()
		expected_teacher_calendars_list = self.get_expected_teacher_calendars()

		calendar = self.get_event_removed_calendar(calendar_key,current_class_calendars)
		date = calendar.calendar_date
		day_code = findDay(calendar.calendar_date).upper()[0:3]
	
		# if calendar.subscriber_type == 'CLASS-DIV' and is_class(events[0].params[0]) == True :
		# 	existing_class_calendar = self.get_class_calendar_by_subscriber_key_and_date(calendar.subscriber_key,date,current_class_calendars)
		# 	updated_class_calendars.append(existing_class_calendar)
			# self.update_class_calendars_and_teacher_calendars(existing_class_calendar,timetables,calendar,academic_configuration,updated_class_calendars,updated_teacher_calendars,day_code,date,current_teacher_calendars)
		if calendar.subscriber_type == 'CLASS-DIV' and is_class(events[0].params[0]) == False :
			existing_class_calendar = self.get_class_calendar_by_subscriber_key_and_date(calendar.subscriber_key,date,current_class_calendars)
			subscriber_key = existing_class_calendar.subscriber_key
			timetable = self.get_timetable_by_subscriber_key(existing_class_calendar.subscriber_key,timetables)
			updated_class_calendar = calendar_integrator.update_class_calendar_by_adding_conflicted_periods(existing_class_calendar,timetable,calendar,events,academic_configuration,updated_class_calendars,day_code)
			updated_class_calendar_events = updated_class_calendar.events
			employee_key_list = calendar_integrator.get_employee_key_list(updated_class_calendar_events)
			for employee_key in employee_key_list :
				teacher_calendar = self.get_teacher_calendar_by_emp_key_and_date(date,employee_key,current_teacher_calendars,updated_class_calendar)
				calendar_integrator.update_teacher_calendar_by_adding_conflicted_periods(updated_class_calendar_events,teacher_calendar,updated_class_calendar,updated_teacher_calendars)
			
			
		for updated_class_calendar in updated_class_calendars :
			cal = cldr.Calendar(None)
			calendar_dict = cal.make_calendar_dict(updated_class_calendar)
			pp.pprint(calendar_dict)
			self.check_class_calendars(updated_class_calendar,expected_class_calendars_list)
			gclogger.info("-----[UnitTest] Class calendar test passed ----------------- " + updated_class_calendar.calendar_key + "-----------------")


		for updated_teacher_calendar in updated_teacher_calendars :
			cal = cldr.Calendar(None)
			calendar_dict = cal.make_calendar_dict(updated_teacher_calendar)
			pp.pprint(calendar_dict)
			self.check_teacher_calendar(updated_teacher_calendar,expected_teacher_calendars_list)
			gclogger.info("-----[UnitTest] Teacher calendar test passed ----------------- " + updated_teacher_calendar.calendar_key + "-----------------")

	def update_calendars_by_adding_conflicted_periods(self,existing_class_calendar,timetable,calendar,academic_configuration,updated_class_calendars,updated_teacher_calendars,day_code,date,current_teacher_calendars) :
		period_list = generate_period_list(calendar,academic_configuration,timetable,day_code)
		events = self.make_events(period_list,timetable,existing_class_calendar.calendar_date)
		updated_class_calendar = self.add_events_to_calendar(events,existing_class_calendar)
		updated_class_calendars.append(updated_class_calendar)
		updated_class_calendar_events = updated_class_calendar.events
		employee_key_list = self.get_employee_key_list(updated_class_calendar_events)
		for employee_key in employee_key_list :
			teacher_calendar = self.get_teacher_calendar_by_emp_key_and_date(date,employee_key,current_teacher_calendars,updated_class_calendar)
			updated_teacher_calendar = self.update_teacher_calendar(teacher_calendar,updated_class_calendar_events,existing_class_calendar)
			updated_teacher_calendars.append(updated_teacher_calendar)




		





	def add_events_to_calendar(self,events,existing_class_calendar) :
		for event in events :
			existing_class_calendar.events.append(event)
		updated_class_calendar = self.sort_updated_class_calendar_events(existing_class_calendar)
		return updated_class_calendar

	def make_event_objects(self,events) :
		events_obj = []
		for event in events :		
			event_obj = cldr.Event(event)
			events_obj.append(event_obj)
		print(events_obj)
		return events_obj

		
	def sort_updated_class_calendar_events(self,existing_class_calendar) :
		from operator import attrgetter
		soreted_events = sorted(existing_class_calendar.events, key = attrgetter('from_time'))
		existing_class_calendar.events = soreted_events
		return existing_class_calendar



	def make_events(self,period_list,timetable,date) :
		events_list =[]
		for period in period_list :
			event = calendar.Event(None)
			event.event_code = key.generate_key(3)
			event.event_type = 'CLASS_SESSION'
			time_table_period = self.get_time_table_period(period.period_code,timetable)
			event.params = get_params(time_table_period.subject_key , time_table_period.employee_key , time_table_period.period_code)

			event.from_time =  get_standard_time(period.start_time,date)
			event.to_time =  get_standard_time(period.end_time,date)
			gclogger.info("Event created " + event.event_code + ' start ' + event.from_time + ' end ' + event.to_time)
			events_list.append(event)
		return events_list
		
	def get_time_table_period(self,period_code,timetable) :
		timetable_configuration_period = None 
		if hasattr(timetable.timetable,'day_tables') :
			days = timetable.timetable.day_tables
			for day in days :
				for time_table_period in day.periods :
					if time_table_period.period_code == period_code :
						return time_table_period

		

	def update_class_calendars_and_teacher_calendars(self,existing_class_calendar,timetables,calendar,academic_configuration,updated_class_calendars,updated_teacher_calendars,day_code,date,current_teacher_calendars) :
		timetable = self.get_timetable_by_subscriber_key(existing_class_calendar.subscriber_key,timetables)
		holiday_period_list = generate_holiday_period_list(calendar,academic_configuration,timetable,day_code)
		updated_class_calendar = generate_class_calendar(day_code,timetable,date,academic_configuration.time_table_configuration,holiday_period_list,existing_class_calendar)
		updated_class_calendars.append(updated_class_calendar)
		updated_class_calendar_events = updated_class_calendar.events
		employee_key_list = self.get_employee_key_list(updated_class_calendar_events)
		for employee_key in employee_key_list :
			teacher_calendar = self.get_teacher_calendar_by_emp_key_and_date(date,employee_key,current_teacher_calendars,updated_class_calendar)
			updated_teacher_calendar = self.update_teacher_calendar(teacher_calendar,updated_class_calendar_events,existing_class_calendar)
			updated_teacher_calendars.append(updated_teacher_calendar)

	def get_class_calendar_by_subscriber_key_and_date(self,subscriber_key,date,current_class_calendars)	:
		for current_class_calendar in current_class_calendars :
			if current_class_calendar.subscriber_key == subscriber_key and current_class_calendar.calendar_date == date :
				return current_class_calendar

	def update_teacher_calendar(self,teacher_calendar,updated_class_calendar_events,existing_class_calendar) :
		for event in updated_class_calendar_events :
			employee_key = self.get_employee_key(event)
			if employee_key == teacher_calendar.subscriber_key and self.is_event_already_exist(event,teacher_calendar.events) == False :
				event_object = cldr.Event(None)
				event_object.event_code = event.event_code
				event_object.ref_calendar_key = existing_class_calendar.calendar_key
				teacher_calendar.events.append(event_object)
		return teacher_calendar

	def is_event_already_exist(self,event,events) :
		is_event_exist = False
		for existing_event in events :
			if existing_event.event_code == event.event_code :
				is_event_exist = True
		return is_event_exist



	def is_class(self,param) :
		is_class = None
		if param.key == 'cancel_class_flag' and param.value == 'true' :
			is_class = False
		else :
			is_class = True
		return is_class


	def get_teacher_calendar_by_emp_key_and_date(self,date,employee_key,current_teacher_calendars,updated_class_calendar) :
		for current_teacher_calendar in current_teacher_calendars :
			if current_teacher_calendar.calendar_date == date and current_teacher_calendar.subscriber_key == employee_key :
				return current_teacher_calendar
		else :
			current_teacher_calendar = timetable_integrator.generate_employee_calendar(employee_key,updated_class_calendar)
			return current_teacher_calendar


	def get_employee_key_list(self,updated_class_calendar_events) :
		employee_key_list = []
		for event in updated_class_calendar_events :
			employee_key = self.get_employee_key(event)
			if employee_key not in employee_key_list :
				employee_key_list.append(employee_key)
		return employee_key_list



	def get_employee_key(self,event) :
		for param in event.params :
			if param.key == 'teacher_emp_key' :
				return param.value


	# return holiday_period_list
	def check_class_calendars(self,updated_class_calendar,expected_class_calendars_list) :
		for expected_class_calendar in expected_class_calendars_list :
			if updated_class_calendar.calendar_key == expected_class_calendar.calendar_key :
				self.assertEqual(expected_class_calendar.institution_key,updated_class_calendar.institution_key )
				self.assertEqual(expected_class_calendar.calendar_date,updated_class_calendar.calendar_date )
				self.assertEqual(expected_class_calendar.subscriber_key,updated_class_calendar.subscriber_key )
				self.assertEqual(expected_class_calendar.subscriber_type,updated_class_calendar.subscriber_type )
				self.check_events(expected_class_calendar.events,updated_class_calendar.events)

	def check_events(self,expected_class_calendar_events,generated_class_calendar_events) :

		for index in range(0,len(expected_class_calendar_events) - 1) :
			self.assertEqual(expected_class_calendar_events[index].event_type , generated_class_calendar_events[index].event_type)
			self.assertEqual(expected_class_calendar_events[index].from_time , generated_class_calendar_events[index].from_time)
			self.assertEqual(expected_class_calendar_events[index].to_time , generated_class_calendar_events[index].to_time)
			self.check_params(expected_class_calendar_events[index].params,generated_class_calendar_events[index].params)

	def check_params(self,expected_class_calendar_event_params,generated_class_calendar_event_params) :
		for index in range(0,len(expected_class_calendar_event_params) - 1) :
			self.assertEqual(expected_class_calendar_event_params[index].key,generated_class_calendar_event_params[index].key)
			self.assertEqual(expected_class_calendar_event_params[index].value,generated_class_calendar_event_params[index].value)



	def check_teacher_calendar(self,updated_teacher_calendar,expected_teacher_calendars_list) :
		for expected_teacher_calendar in expected_teacher_calendars_list :
			if updated_teacher_calendar.calendar_key == expected_teacher_calendar.calendar_key :
				self.assertEqual(expected_teacher_calendar.institution_key,updated_teacher_calendar.institution_key )
				self.assertEqual(expected_teacher_calendar.calendar_date,updated_teacher_calendar.calendar_date )
				self.assertEqual(expected_teacher_calendar.subscriber_key,updated_teacher_calendar.subscriber_key )
				self.assertEqual(expected_teacher_calendar.subscriber_type,updated_teacher_calendar.subscriber_type )
				self.check_events_teacher_calendar(expected_teacher_calendar.events,updated_teacher_calendar.events)


	def get_timetable_by_subscriber_key(self,subscriber_key,timetables) :
		class_key = subscriber_key[:-2]
		division = subscriber_key[-1:]
		for timetable in timetables :
			if timetable.class_key ==  class_key and timetable.division == division :
				return timetable


	def check_events_teacher_calendar(self,expected_teacher_calendar_events,updated_teacher_calendar_events) :
		for index in range(0,len(expected_teacher_calendar_events) - 1) :
			self.assertEqual(expected_teacher_calendar_events[index].event_code , updated_teacher_calendar_events[index].event_code)
			self.assertEqual(expected_teacher_calendar_events[index].ref_calendar_key , updated_teacher_calendar_events[index].ref_calendar_key)


	def get_event_from_calendar(self,event_code,calendar) :
		for event in calendar.events :
			if event.event_code == event_code :

				return event


	def get_timetables(self) :
		t = []
		with open('tests/unit/fixtures/class-calendar-remove-fixtures/test_timetable_list.json', 'r') as timetable_list:
			timetables = json.load(timetable_list)

		for timetable in timetables :
			t.append(ttable.TimeTable(timetable))
		return t


	def get_academic_configuration(self):
		with open('tests/unit/fixtures/class-calendar-remove-fixtures/academic_configuration.json', 'r') as academic_configuration:
			academic_configuration_dict = json.load(academic_configuration)
			academic_configuration = academic_config.AcademicConfiguration(academic_configuration_dict)
		return academic_configuration

	def get_current_class_calendars(self) :
		class_calendars_list = []
		with open('tests/unit/fixtures/class-calendar-remove-fixtures/current_class_calendars.json', 'r') as calendars:
			class_calendars = json.load(calendars)
		for cal in class_calendars :
			class_calendars_list.append(calendar.Calendar(cal))
		return class_calendars_list

	def get_current_teacher_calendars(self) :
		teacher_calendars_list = []
		with open('tests/unit/fixtures/class-calendar-remove-fixtures/current_teacher_calendars.json', 'r') as calendars:
			teacher_calendars = json.load(calendars)
		for cal in teacher_calendars :
			teacher_calendars_list.append(calendar.Calendar(cal))
		return teacher_calendars_list

	def get_expected_teacher_calendars(self) :
		expected_teacher_calendars_list = []
		with open('tests/unit/fixtures/class-calendar-remove-fixtures/expected_teacher_calendars.json', 'r') as calendars:
			teacher_calendars = json.load(calendars)
		for cal in teacher_calendars :
			expected_teacher_calendars_list.append(calendar.Calendar(cal))
		return expected_teacher_calendars_list

	def get_expected_class_calendars(self) :
		expected_class_calendars_list = []
		with open('tests/unit/fixtures/class-calendar-remove-fixtures/expected_class_calendars.json', 'r') as calendars:
			class_calendars = json.load(calendars)
		for cal in class_calendars :
			expected_class_calendars_list.append(calendar.Calendar(cal))
		return expected_class_calendars_list



	def get_event_removed_calendar(self,calendar_key,holiday_removed_calendars) :
		for calendar in holiday_removed_calendars :
			if calendar.calendar_key == calendar_key :
				return calendar




def update_teacher_calendar(events_to_remove_list,teacher_calendar) :
	event_list = get_updated_teacher_event(events_to_remove_list,teacher_calendar)
	del teacher_calendar.events
	teacher_calendar.events = event_list
	return teacher_calendar


def get_updated_teacher_event(events_to_remove_list,teacher_calendar) :
	events_list = []
	for teacher_event in teacher_calendar.events :
		if not do_remove_event(teacher_event,events_to_remove_list) == True :
			events_list.append(teacher_event)
	return events_list


def do_remove_event(event,events_to_remove_list) :
	for remove_event in events_to_remove_list :
		if remove_event.event_code == event.event_code :
			return True


def get_all_events_to_remove(class_calendars,event) :
	events_to_remove_list = []
	for class_calendar in class_calendars :
		gclogger.info(" Updating calendar" + class_calendar.calendar_key +'--------------')
		events_list = get_events_to_remove(class_calendar,event)
		events_to_remove_list = events_to_remove_list + events_list
	return events_to_remove_list







def is_class(param) :
	is_class = False
	if param.key == 'cancel_class_flag' and param.value == 'true' :
		is_class = False
	else :
		is_class = True
	return is_class

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


def remove_events_from_class_calendar(events_to_remove_list,class_calendar) :
	event_list = get_updated_event(class_calendar,events_to_remove_list)
	del class_calendar.events
	class_calendar.events = event_list
	return class_calendar


def get_updated_event(class_calendar,events_to_remove_list) :
	event_list = []
	for event in class_calendar.events :
		if not event in events_to_remove_list :
			event_list.append(event)
	return event_list


def get_events_to_remove(class_calendar,event) :
	events_to_remove_list = []
	calendar_event_start_time = event.from_time
	calendar_event_end_time = event.to_time
	gclogger.info('Holiday calendar event ------------------')
	gclogger.info('START ' + calendar_event_start_time)
	gclogger.info('END ' + calendar_event_end_time)
	gclogger.info('')
	for event in class_calendar.events :
		class_calendar_event_start_time = event.from_time
		class_calendar_event_end_time = event.to_time
		if check_events_conflict(calendar_event_start_time,calendar_event_end_time,class_calendar_event_start_time,class_calendar_event_end_time) :
			gclogger.info("----------THIS EVENT NEED TO REMOVE ----------" +event.event_code + '----')
			events_to_remove_list.append(event)
		else :
			gclogger.info("----------THIS EVENT  NOT NEED TO REMOVE ----------" + event.event_code+ '----')
	return events_to_remove_list




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




if __name__ == '__main__':
	unittest.main()
