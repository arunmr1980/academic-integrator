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
from academics.calendar.CalendarIntegrator import add_event_integrate_calendars
import academics.calendar.CalendarDBService as calendar_service

import operator
import pprint
pp = pprint.PrettyPrinter(indent=4)



class CalendarAddEventIntegratorTest(unittest.TestCase):
	def setUp(self) :
		academic_configuration = self.get_academic_config_from_json()
		response = academic_service.create_academic_config(academic_configuration)
		gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' -------------  Academic configuration uploaded  ------------- '+str(academic_configuration['academic_config_key']))

		current_class_calendars = self.get_current_class_calendars()
		for current_class_calendar in current_class_calendars :
			cal = calendar.Calendar(None)
			calendar_dict = cal.make_calendar_dict(current_class_calendar)
			response = calendar_service.add_or_update_calendar(calendar_dict)
			gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' ------- A Class calendar uploaded --------- '+str(calendar_dict['calendar_key']))

		current_teacher_calendars = self.get_current_teacher_calendars()
		for current_teacher_calendar in current_teacher_calendars :
			cal = calendar.Calendar(None)
			calendar_dict = cal.make_calendar_dict(current_teacher_calendar)
			response = calendar_service.add_or_update_calendar(calendar_dict)
			gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' ------- A Teacher calendar uploaded --------- '+str(calendar_dict['calendar_key']))

		holiday_calendars = self.get_holiday_calendars()
		for holiday_calendar in holiday_calendars :
			cal = calendar.Calendar(None)
			calendar_dict = cal.make_calendar_dict(holiday_calendar)
			response = calendar_service.add_or_update_calendar(calendar_dict)
			gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' ------- A Holiday calendar uploaded --------- '+str(calendar_dict['calendar_key']))

		class_info_one_dict = self.get_class_info()
		response = class_info_service.add_or_update_class_info(class_info_one_dict)
		gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' ------------- A Class info for uploaded --------- ' +str(class_info_one_dict['class_info_key']) )

	def test_calendars(self) :
		expected_class_calendars_list = self.get_expected_class_calendars()
		expected_teacher_calendars_list = self.get_expected_teacher_calendars()
		event_code = 'event-1'
		calendar_key ='test-key-12'
		calendar = calendar_service.get_calendar(calendar_key)
		school_key = calendar.institution_key
		calendar_date = calendar.calendar_date
		add_event_integrate_calendars(event_code,calendar_key)
		updated_calendars_list = calendar_service.get_all_calendars_by_school_key_and_date(school_key,calendar_date)

		updated_class_calendar_list = self.get_updated_class_calendars(updated_calendars_list)
		updated_teacher_calendar_list = self.get_updated_teacher_calendars(updated_calendars_list)

		for updated_class_calendar in updated_class_calendar_list :
			cal = cldr.Calendar(None)
			calendar_dict = cal.make_calendar_dict(updated_class_calendar)
			pp.pprint(calendar_dict)
			self.check_class_calendars(updated_class_calendar,expected_class_calendars_list)			
			gclogger.info("-----[Integration Test] Class calendar test passed for ----" + updated_class_calendar.calendar_key + "-----------------")

		for updated_teacher_calendar in updated_teacher_calendar_list :
			cal = cldr.Calendar(None)
			calendar_dict = cal.make_calendar_dict(updated_teacher_calendar)
			pp.pprint(calendar_dict)
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




	def check_teacher_calendars(self,updated_teacher_calendar,expected_teacher_calendars_list) :
		for expected_teacher_calendar in expected_teacher_calendars_list :
			if updated_teacher_calendar.calendar_key == expected_teacher_calendar.calendar_key :
				self.assertEqual(expected_teacher_calendar.institution_key,updated_teacher_calendar.institution_key )
				self.assertEqual(expected_teacher_calendar.calendar_date,updated_teacher_calendar.calendar_date )
				self.assertEqual(expected_teacher_calendar.subscriber_key,updated_teacher_calendar.subscriber_key )
				self.assertEqual(expected_teacher_calendar.subscriber_type,updated_teacher_calendar.subscriber_type )
				self.check_events_teacher_calendar(expected_teacher_calendar.events,updated_teacher_calendar.events)


	def check_events_teacher_calendar(self,expected_teacher_calendar_events,updated_teacher_calendar_events) :
		for index in range(0,len(expected_teacher_calendar_events)) :
			self.assertEqual(expected_teacher_calendar_events[index].event_code , updated_teacher_calendar_events[index].event_code)
			self.assertEqual(expected_teacher_calendar_events[index].ref_calendar_key , updated_teacher_calendar_events[index].ref_calendar_key)



	def check_class_calendars(self,updated_class_calendar,expected_class_calendars_list) :
		for expected_class_calendar in expected_class_calendars_list :
			if updated_class_calendar.calendar_key == expected_class_calendar.calendar_key :
				self.assertEqual(expected_class_calendar.institution_key,updated_class_calendar.institution_key )
				self.assertEqual(expected_class_calendar.calendar_date,updated_class_calendar.calendar_date )
				self.assertEqual(expected_class_calendar.subscriber_key,updated_class_calendar.subscriber_key )
				self.assertEqual(expected_class_calendar.subscriber_type,updated_class_calendar.subscriber_type )
				self.check_events(expected_class_calendar.events,updated_class_calendar.events)


	def check_events(self,expected_class_calendar_events,generated_class_calendar_events) :
		for index in range(0,len(expected_class_calendar_events)) :
			self.assertEqual(expected_class_calendar_events[index].event_type , generated_class_calendar_events[index].event_type)
			self.assertEqual(expected_class_calendar_events[index].from_time , generated_class_calendar_events[index].from_time)
			self.assertEqual(expected_class_calendar_events[index].to_time , generated_class_calendar_events[index].to_time)
			self.check_params(expected_class_calendar_events[index].params,generated_class_calendar_events[index].params)


	def check_params(self,expected_class_calendar_event_params,generated_class_calendar_event_params) :
		for index in range(0,len(expected_class_calendar_event_params)) :
			self.assertEqual(expected_class_calendar_event_params[index].key,generated_class_calendar_event_params[index].key)
			self.assertEqual(expected_class_calendar_event_params[index].value,generated_class_calendar_event_params[index].value)


	def tearDown(self) :
		academic_configuration = academic_service.get_academig('test-school-key-3','2020-2021')
		academic_service.delete_academic_config(academic_configuration.academic_config_key)
		gclogger.info("---------------Test Academic Configuration deleted ----------  " + academic_configuration.academic_config_key + "-----------------")

		current_class_calendars = calendar_service.get_all_calendars_by_school_key_and_type('test-school-key-3','CLASS-DIV')
		for calendar in current_class_calendars :
			calendar_service.delete_calendar(calendar.calendar_key)
			gclogger.info("--------------- A class calendar deleted ---------- " + calendar.calendar_key+" -----------------")

		current_school_calendars = calendar_service.get_all_calendars_by_school_key_and_type('test-school-key-3','SCHOOL')
		for calendar in current_class_calendars :
			calendar_service.delete_calendar(calendar.calendar_key)
			gclogger.info("--------------- A school calendar deleted ---------- " + calendar.calendar_key+" -----------------")

		current_teacher_calendars = calendar_service.get_all_calendars_by_school_key_and_type('test-school-key-3','EMPLOYEE')
		for calendar in current_teacher_calendars :
			calendar_service.delete_calendar(calendar.calendar_key)
			gclogger.info("--------------- A Teacher calendar deleted ---------- " + calendar.calendar_key+" -----------------")
		class_info = self.get_class_info()
		response = class_info_service.delete_class_info(class_info['class_info_key'])
		gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' ------------- A Class info for deleted --------- ' +str(class_info['class_info_key']) )


	def get_current_class_calendars(self) :
		class_calendars_list = []
		with open('tests/unit/fixtures/calendar-add-fixtures/current_class_calendars.json', 'r') as calendars:
			class_calendars = json.load(calendars)
		for cal in class_calendars :
			class_calendars_list.append(calendar.Calendar(cal))
		return class_calendars_list

	def get_current_teacher_calendars(self) :
		teacher_calendars_list = []
		with open('tests/unit/fixtures/calendar-add-fixtures/current_teacher_calendars.json', 'r') as calendars:
			teacher_calendars = json.load(calendars)
		for cal in teacher_calendars :
			teacher_calendars_list.append(calendar.Calendar(cal))
		return teacher_calendars_list

	def get_expected_teacher_calendars(self) :
		expected_teacher_calendars_list = []
		with open('tests/unit/fixtures/calendar-add-fixtures/expected_teacher_calendars.json', 'r') as calendars:
			teacher_calendars = json.load(calendars)
		for cal in teacher_calendars :
			expected_teacher_calendars_list.append(calendar.Calendar(cal))
		return expected_teacher_calendars_list

	def get_expected_class_calendars(self) :
		expected_class_calendars_list = []
		with open('tests/unit/fixtures/calendar-add-fixtures/expected_class_calendars.json', 'r') as calendars:
			class_calendars = json.load(calendars)
		for cal in class_calendars :
			expected_class_calendars_list.append(calendar.Calendar(cal))
		return expected_class_calendars_list


	def get_holiday_calendars(self):
		holiday_calendars_list = []
		with open('tests/unit/fixtures/calendar-add-fixtures/current_school_calendars.json', 'r') as calendars:
			holiday_calendars = json.load(calendars)
		for cal in holiday_calendars :
			holiday_calendars_list.append(calendar.Calendar(cal))
		return holiday_calendars_list

	def get_academic_config_from_json(self) :
		with open('tests/unit/fixtures/calendar-add-fixtures/academic_configuration.json', 'r') as academic_configure:
			academic_configuration = json.load(academic_configure)
		return academic_configuration

	def get_class_info(self) :
		with open('tests/unit/fixtures/calendar-add-fixtures/class_info.json', 'r') as class_info_two:
			class_info_two_dict = json.load(class_info_two)
		return class_info_two_dict


if __name__ == '__main__':
	unittest.main()
