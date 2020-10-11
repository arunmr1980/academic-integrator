import unittest
import json
from academics.TimetableIntegrator import *
from academics.timetable import AcademicConfiguration as academic_config
import academics.timetable.TimeTable as ttable
from academics.logger import GCLogger as gclogger
import academics.calendar.Calendar as calendar
import academics.lessonplan.LessonPlan as lessonplan
from academics.calendar.CalendarLessonPlanIntegrator import integrate_calendar_to_lesson_plan
from academics.lessonplan.LessonplanIntegrator import holiday_calendar_to_lessonplan_integrator
from academics.calendar.CalendarIntegrator import integrate_class_calendars,integrate_teacher_calendars
import operator
import pprint
pp = pprint.PrettyPrinter(indent=4)



class CalendarIntegratorTest(unittest.TestCase):
	def setUp(self) :
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

	def test_class_calendar(self) :	
		expected_class_calendars_list = self.get_expected_class_calendars()
		event_code = 'event-1'
		calendar_key ='test-key-12'
		updated_class_calendar_list = integrate_class_calendars(event_code,calendar_key)
		for updated_class_calendar in updated_class_calendar_list :
			self.check_class_calendars(updated_class_calendar,expected_class_calendars_list)
			gclogger.info("-----[Integration Test] Class calendar test passed for ----" + updated_class_calendar.calendar_key + "-----------------")

	def test_teacher_calendar(self) :
		expected_teacher_calendars_list = self.get_expected_teacher_calendars()
		event_code = 'event-1'
		calendar_key ='test-key-12'
		updated_teacher_calendar_list = integrate_teacher_calendars(event_code,calendar_key)
		for updated_teacher_calendar in updated_teacher_calendar_list :
			self.check_teacher_calendars(updated_teacher_calendar,expected_teacher_calendars_list)
			gclogger.info("-----[Integration Test] Teacher calendar test passed for ----" + updated_teacher_calendar.calendar_key + "-----------------")


	def check_class_calendars(self,updated_class_calendar,expected_class_calendars_list) :
		for expected_class_calendar in expected_class_calendars_list :
			if expected_class_calendar.calendar_key == updated_class_calendar.calendar_key :
				self.check_calendars(updated_class_calendar,expected_class_calendars_list)


	def check_teacher_calendars(self,updated_teacher_calendar,expected_teacher_calendars_list) :
			for expected_teacher_calendar in expected_teacher_calendars_list :
				if updated_teacher_calendar.calendar_key == expected_teacher_calendar.calendar_key :
					self.assertEqual(expected_teacher_calendar.institution_key,updated_teacher_calendar.institution_key )
					self.assertEqual(expected_teacher_calendar.calendar_date,updated_teacher_calendar.calendar_date )
					self.assertEqual(expected_teacher_calendar.subscriber_key,updated_teacher_calendar.subscriber_key )
					self.assertEqual(expected_teacher_calendar.subscriber_type,updated_teacher_calendar.subscriber_type )
					self.check_events_teacher_calendar(expected_teacher_calendar.events,updated_teacher_calendar.events) 


	def check_events_teacher_calendar(self,expected_teacher_calendar_events,updated_teacher_calendar_events) :
			for index in range(0,len(expected_teacher_calendar_events) - 1) :
				self.assertEqual(expected_teacher_calendar_events[index].event_code , updated_teacher_calendar_events[index].event_code)
				self.assertEqual(expected_teacher_calendar_events[index].ref_calendar_key , updated_teacher_calendar_events[index].ref_calendar_key)
			

	def check_calendars(self,updated_class_calendar,expected_class_calendars_list) :
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

	
	def tearDown(self) :
		current_class_calendars = calendar_service.get_all_calendars_by_school_key_and_type('test-school-1','CLASS-DIV')
		for calendar in current_class_calendars :
			calendar_service.delete_calendar(calendar.calendar_key)
			gclogger.info("--------------- A class calendar deleted " + calendar.calendar_key+" -----------------")

		current_school_calendars = calendar_service.get_all_calendars_by_school_key_and_type('test-school-1','SCHOOL')
		for calendar in current_class_calendars :
			calendar_service.delete_calendar(calendar.calendar_key)
			gclogger.info("--------------- A school calendar deleted " + calendar.calendar_key+" -----------------")

		current_teacher_calendars = calendar_service.get_all_calendars_by_school_key_and_type('test-school-1','EMPLOYEE')
		for calendar in current_teacher_calendars :
			calendar_service.delete_calendar(calendar.calendar_key)
			gclogger.info("--------------- A Teacher calendar deleted " + calendar.calendar_key+" -----------------")
		

	def get_current_class_calendars(self) :
		class_calendars_list = []
		with open('tests/unit/fixtures/calendar-update-fixtures/current_class_calendars.json', 'r') as calendars:
			class_calendars = json.load(calendars)
		for cal in class_calendars :
			class_calendars_list.append(calendar.Calendar(cal))
		return class_calendars_list

	def get_current_teacher_calendars(self) :
		teacher_calendars_list = []
		with open('tests/unit/fixtures/calendar-update-fixtures/current_teacher_calendars.json', 'r') as calendars:
			teacher_calendars = json.load(calendars)
		for cal in teacher_calendars :
			teacher_calendars_list.append(calendar.Calendar(cal))
		return teacher_calendars_list

	def get_expected_teacher_calendars(self) :
		expected_teacher_calendars_list = []
		with open('tests/unit/fixtures/calendar-update-fixtures/expected_teacher_calendars.json', 'r') as calendars:
			teacher_calendars = json.load(calendars)
		for cal in teacher_calendars :
			expected_teacher_calendars_list.append(calendar.Calendar(cal))
		return expected_teacher_calendars_list
	
	def get_expected_class_calendars(self) :
		expected_class_calendars_list = []
		with open('tests/unit/fixtures/calendar-update-fixtures/expected_class_calendars.json', 'r') as calendars:
			class_calendars = json.load(calendars)
		for cal in class_calendars :
			expected_class_calendars_list.append(calendar.Calendar(cal))
		return expected_class_calendars_list


	def get_holiday_calendars(self):
		holiday_calendars_list = []
		with open('tests/unit/fixtures/calendar-update-fixtures/current_school_calendars.json', 'r') as calendars:
			holiday_calendars = json.load(calendars)
		for cal in holiday_calendars :
			holiday_calendars_list.append(calendar.Calendar(cal))
		return holiday_calendars_list
	




if __name__ == '__main__':
	unittest.main()
