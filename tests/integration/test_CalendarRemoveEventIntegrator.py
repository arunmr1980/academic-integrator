import unittest
import json
from academics.TimetableIntegrator import *
from academics.timetable import AcademicConfiguration as academic_config
import academics.timetable.TimeTable as ttable
from academics.logger import GCLogger as gclogger
import academics.calendar.Calendar as cldr
import academics.lessonplan.LessonPlan as lessonplan
from academics.calendar.CalendarLessonPlanIntegrator import integrate_calendar_to_lesson_plan
from academics.lessonplan.LessonplanIntegrator import holiday_calendar_to_lessonplan_integrator
from academics.TimetableIntegrator import generate_holiday_period_list,generate_class_calendar,integrate_teacher_timetable
import academics.timetable.TimeTable as ttable
import academics.timetable.TimeTableDBService as timetable_service
from academics.calendar.CalendarIntegrator import remove_event_integrate_calendars
import operator
import pprint
pp = pprint.PrettyPrinter(indent=4)



class CalendarRemoveEventIntegratorTest(unittest.TestCase):

	def setUp(self) :
		timetables = self.get_timetables()
		for timetable in timetables :
			t = ttable.TimeTable(None)
			timetable_dict = t.make_timetable_dict(timetable)
			response = timetable_service.create_timetable(timetable_dict)
			gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' ------- A Time table uploaded --------- '+str(timetable_dict['time_table_key']))

		academic_configuration = self.get_academic_config_from_json()
		response = academic_service.create_academic_config(academic_configuration)
		gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' -------------  Academic configuration uploaded  ------------- '+str(academic_configuration['academic_config_key']))

		current_class_calendars = self.get_current_class_calendars()
		for current_class_calendar in current_class_calendars :
			cal = cldr.Calendar(None)
			calendar_dict = cal.make_calendar_dict(current_class_calendar)
			response = calendar_service.add_or_update_calendar(calendar_dict)
			gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' ------- A Class calendar uploaded --------- '+str(calendar_dict['calendar_key']))

		current_teacher_calendars = self.get_current_teacher_calendars()
		for current_teacher_calendar in current_teacher_calendars :
			cal = cldr.Calendar(None)
			calendar_dict = cal.make_calendar_dict(current_teacher_calendar)
			response = calendar_service.add_or_update_calendar(calendar_dict)
			gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' ------- A Teacher calendar uploaded --------- '+str(calendar_dict['calendar_key']))

		holiday_removed_calendars = self.get_holiday_removed_calendars()
		for holiday_removed_calendar in holiday_removed_calendars :
			cal = cldr.Calendar(None)
			calendar_dict = cal.make_calendar_dict(holiday_removed_calendar)
			response = calendar_service.add_or_update_calendar(calendar_dict)
			gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' ------- A Holiday cancelled calendar uploaded --------- '+str(calendar_dict['calendar_key']))

	def test_calendars(self) :
		expected_class_calendars_list = self.get_expected_class_calendars()
		expected_teacher_calendars_list = self.get_expected_teacher_calendars()
		calendar_key ='test-key-11'
		calendar = calendar_service.get_calendar(calendar_key)
		school_key = calendar.institution_key
		calendar_date = calendar.calendar_date
		remove_event_integrate_calendars(calendar_key)
		updated_calendars_list = calendar_service.get_all_calendars_by_school_key_and_date(school_key,calendar_date)
		
		updated_class_calendar_list = self.get_updated_class_calendars(updated_calendars_list)
		updated_teacher_calendar_list = self.get_updated_teacher_calendars(updated_calendars_list)

		for updated_class_calendar in updated_class_calendar_list :
			self.check_class_calendars(updated_class_calendar,expected_class_calendars_list)	
			gclogger.info("-----[Integration Test] Class calendar test passed for ----" + updated_class_calendar.calendar_key + "-----------------")

		for updated_teacher_calendar in updated_teacher_calendar_list :
			self.check_teacher_calendars(updated_teacher_calendar,expected_teacher_calendars_list)
			gclogger.info("-----[Integration Test] Teacher calendar test passed for ----" + updated_teacher_calendar.calendar_key + "-----------------")




	def get_updated_class_calendars(self,updated_calendars_list) :
		updated_class_calendar_list = []
		for updated_calendar in updated_calendars_list :
			if updated_calendar.subscriber_type == 'CLASS-DIV' :
				updated_class_calendar_list.append(updated_calendar)
		return updated_class_calendar_list

	def get_updated_teacher_calendars(self,updated_calendars_list) :
		updated_teacher_calendar_list = []
		for updated_calendar in updated_calendars_list :
			if updated_calendar.subscriber_type == 'EMPLOYEE' :
				updated_teacher_calendar_list.append(updated_calendar)
		return updated_teacher_calendar_list




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



	def check_teacher_calendars(self,updated_teacher_calendar,expected_teacher_calendars_list) :
		for expected_teacher_calendar in expected_teacher_calendars_list :
			if updated_teacher_calendar.calendar_key == expected_teacher_calendar.calendar_key :
				self.assertEqual(expected_teacher_calendar.institution_key,updated_teacher_calendar.institution_key )
				self.assertEqual(expected_teacher_calendar.calendar_date,updated_teacher_calendar.calendar_date )
				self.assertEqual(expected_teacher_calendar.subscriber_key,updated_teacher_calendar.subscriber_key )
				self.assertEqual(expected_teacher_calendar.subscriber_type,updated_teacher_calendar.subscriber_type )
				self.check_events_teacher_calendars(expected_teacher_calendar.events,updated_teacher_calendar.events)

	def check_events_teacher_calendars(self,expected_teacher_calendar_events,updated_teacher_calendar_events) :
		for index in range(0,len(expected_teacher_calendar_events)) :
			self.assertEqual(expected_teacher_calendar_events[index].ref_calendar_key , updated_teacher_calendar_events[index].ref_calendar_key)

	def get_timetables(self) :
		t = []
		with open('tests/unit/fixtures/calendar-remove-fixtures/test_timetable_list.json', 'r') as timetable_list:
			timetables = json.load(timetable_list)

		for timetable in timetables :
			t.append(ttable.TimeTable(timetable))
		return t


	def get_academic_configuration(self):
		with open('tests/unit/fixtures/academic_configuration.json', 'r') as academic_configuration:
			academic_configuration_dict = json.load(academic_configuration)
			academic_configuration = academic_config.AcademicConfiguration(academic_configuration_dict)
		return academic_configuration

	def get_academic_config_from_json(self) :
		with open('tests/unit/fixtures/academic_configuration.json', 'r') as academic_configure:
			academic_configuration = json.load(academic_configure)
		return academic_configuration

	def get_current_class_calendars(self) :
		class_calendars_list = []
		with open('tests/unit/fixtures/calendar-remove-fixtures/current_class_calendars.json', 'r') as calendars:
			class_calendars = json.load(calendars)
		for cal in class_calendars :
			class_calendars_list.append(calendar.Calendar(cal))
		return class_calendars_list

	def get_current_teacher_calendars(self) :
		teacher_calendars_list = []
		with open('tests/unit/fixtures/calendar-remove-fixtures/current_teacher_calendars.json', 'r') as calendars:
			teacher_calendars = json.load(calendars)
		for cal in teacher_calendars :
			teacher_calendars_list.append(calendar.Calendar(cal))
		return teacher_calendars_list

	def get_expected_teacher_calendars(self) :
		expected_teacher_calendars_list = []
		with open('tests/unit/fixtures/calendar-remove-fixtures/expected_teacher_calendars.json', 'r') as calendars:
			teacher_calendars = json.load(calendars)
		for cal in teacher_calendars :
			expected_teacher_calendars_list.append(calendar.Calendar(cal))
		return expected_teacher_calendars_list

	def get_expected_class_calendars(self) :
		expected_class_calendars_list = []
		with open('tests/unit/fixtures/calendar-remove-fixtures/expected_class_calendars.json', 'r') as calendars:
			class_calendars = json.load(calendars)
		for cal in class_calendars :
			expected_class_calendars_list.append(calendar.Calendar(cal))
		return expected_class_calendars_list


	def get_holiday_removed_calendars(self):
		holiday_calendars_list = []
		with open('tests/unit/fixtures/calendar-remove-fixtures/cancell_holiday_event_calendars.json', 'r') as calendars:
			holiday_calendars = json.load(calendars)
		for cal in holiday_calendars :
			holiday_calendars_list.append(calendar.Calendar(cal))
		return holiday_calendars_list


	def get_holiday_removed_calendar(self,calendar_key,holiday_removed_calendars) :
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
