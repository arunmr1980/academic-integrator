import unittest
import json
import academics.calendar.Calendar as calendar
import academics.calendar.CalendarDBService as calendar_service

import academics.academic.AcademicDBService as academic_service
import academics.timetable.TimeTableDBService as timetable_service
from academics.timetable.TimeTable import TimeTable
import academics.timetable.TimeTableDBService as timetable_service
from academics.TimetableIntegrator import generate_and_save_calenders
import operator
from academics.logger import GCLogger as gclogger
import pprint
pp = pprint.PrettyPrinter(indent=4)

class TimetableIntegratorTest(unittest.TestCase):

	@classmethod
	def setUpClass(self) :
		gclogger.info(" ")
		gclogger.info(" Setting up timetable integrator test......")
		timetable = self.get_timetable_from_json(self)
		response = timetable_service.create_timetable(timetable)
		academic_configuration = self.get_academic_config_from_json(self)
		response = academic_service.create_academic_config(academic_configuration)
		class_calendar_holiday_list = self.get_holiday_class_calendar_list_from_json(self)

		school_calendar_holiday_list = self.get_holiday_school_calendar_list_from_json(self)

		for calendar in class_calendar_holiday_list :
			response = calendar_service.add_or_update_calendar(calendar)

		for calendar in school_calendar_holiday_list :
			response = calendar_service.add_or_update_calendar(calendar)


		gclogger.info(" Setup complete ......")
		gclogger.info(" ")

	# def class_calendar(self) :
	# 	class_calendars_dict={}
	# 	class_calendar_list = []
	# 	timetable = timetable_service.get_time_table('test-time-table-1')
	# 	school_key = timetable.school_key
	# 	academic_configuration = academic_service.get_academig(school_key,'2020-2021')
	# 	generate_and_save_calenders(timetable.time_table_key,academic_configuration.academic_year)
	# 	class_calender_list = calendar_service.get_all_calendars_by_key_and_type('8B1B22E72AE-A','CLASS-DIV')

	# 	for class_calendar in class_calender_list :
	# 		calendar_date = class_calendar.calendar_date
	# 		class_calendars_dict[calendar_date] = class_calendar

	# 	expected_class_calendar_list = []
	# 	expected_class_calendar_dict_list = self.get_class_calendar_list()
	# 	for class_calendar in expected_class_calendar_dict_list :
	# 		class_calendar = calendar.Calendar(class_calendar)
	# 		expected_class_calendar_list.append(class_calendar)

	# 	for expected_class_calendar in expected_class_calendar_list :
	# 		calendar_date = expected_class_calendar.calendar_date
	# 		generated_class_calendar = class_calendars_dict[calendar_date]
	# 		self.assertEqual(expected_class_calendar.institution_key,generated_class_calendar.institution_key )
	# 		self.assertEqual(expected_class_calendar.calendar_date,generated_class_calendar.calendar_date )
	# 		self.assertEqual(expected_class_calendar.subscriber_key,generated_class_calendar.subscriber_key )
	# 		self.assertEqual(expected_class_calendar.subscriber_type,generated_class_calendar.subscriber_type )
	# 		self.check_events(expected_class_calendar.events,generated_class_calendar.events)


	# 	gclogger.info(" ----------- [IntegrationTest] --------------- Class calendar test passed -----------------")


	# def check_events(self,expected_class_calendar_events,generated_class_calendar_events) :
	# 	for index in range(0,len(expected_class_calendar_events)) :
	# 		self.assertEqual(expected_class_calendar_events[index].event_type , generated_class_calendar_events[index].event_type)
	# 		self.assertEqual(expected_class_calendar_events[index].from_time , generated_class_calendar_events[index].from_time)

	# 		self.assertEqual(expected_class_calendar_events[index].to_time , generated_class_calendar_events[index].to_time)
	# 		self.check_params(expected_class_calendar_events[index].params,generated_class_calendar_events[index].params)


	# def check_params(self,expected_class_calendar_event_params,generated_class_calendar_event_params) :
	# 	for index in range(0,len(expected_class_calendar_event_params)) :
	# 		self.assertEqual(expected_class_calendar_event_params[index].key,generated_class_calendar_event_params[index].key)
	# 		self.assertEqual(expected_class_calendar_event_params[index].value,generated_class_calendar_event_params[index].value)




	def teacher_calendar(self) :
		# expected_teacher_calendars_dict = {}
		# teacher_calendars_dict = {}

		# expected_teacher_calendar_list = []
		# expected_teacher_calendar_dict_list = self.get_expected_teacher_calendar_list()
		# for teacher_calendar in expected_teacher_calendar_dict_list :
		# 	teacher_calendar = calendar.Calendar(teacher_calendar)
		# 	expected_teacher_calendar_list.append(teacher_calendar)

		# for expected_teacher_calendar in expected_teacher_calendar_list :
		# 	subscriber_key = expected_teacher_calendar.subscriber_key
		# 	calendar_date = expected_teacher_calendar.calendar_date
		# 	expected_teacher_calendars_dict[calendar_date + subscriber_key] = expected_teacher_calendar

		class_calendar_list = calendar_service.get_all_calendars_by_key_and_type('001610357616442257365E3740-01D7-4920-BDA7-0BC669CDCFCA-168810859-A','CLASS-DIV')
		teacher_calendar_list = calendar_service.get_all_calendars_by_school_key_and_type('1e4d12bc2b58050ff084f8da','EMPLOYEE')
		for teacher_calendar in teacher_calendar_list :
			cal = calendar.Calendar(None)
			calendar_dict = cal.make_calendar_dict(teacher_calendar)	
			pp.pprint(calendar_dict)
			for event in teacher_calendar.events :
				class_calendar_key = event.ref_calendar_key
				event_code = event.event_code
				class_calendar = self.get_class_calendar(class_calendar_list,class_calendar_key)
				self.assertIsNotNone(class_calendar,"referenced calendar not None")
				is_exist = self.is_event_code_exist_in_class_calendar(class_calendar,event_code)
				self.assertEqual(is_exist,True)
			gclogger.info("-----[IntegrationTest] Teacher calendar test passed for teacher calendar " + teacher_calendar.calendar_key + " -----------------")

	def is_event_code_exist_in_class_calendar(self,class_calendar,event_code) :
		is_exist = False
		for existing_event in class_calendar.events :
			if existing_event.event_code == event_code :
				is_exist = True
		return is_exist

	def get_class_calendar(self,class_calendar_list,class_calendar_key) :
		for class_calendar in class_calendar_list :
			if class_calendar.calendar_key == class_calendar_key :
				return class_calendar


	# @classmethod
	# def tearDownClass(self):
	# 	gclogger.info(" ")
	# 	gclogger.info(" Tear down timetable integrator test ......")
	# 	timetable = timetable_service.get_time_table('test-time-table-1')
	# 	school_key = timetable.school_key
	# 	academic_configuration = academic_service.get_academig(school_key,'2020-2021')
	# 	class_calender_list = calendar_service.get_all_calendars_by_key_and_type('8B1B22E72AE-A','CLASS-DIV')
	# 	for calendar in class_calender_list :
	# 		calendar_service.delete_calendar(calendar.calendar_key)
	# 		gclogger.info("--------------- Class calendar deleted " + calendar.calendar_key+" -----------------")


	# 	teacher_calender_list = calendar_service.get_all_calendars_by_school_key_and_type('test-school-1','EMPLOYEE')
	# 	for calendar in teacher_calender_list :
	# 		calendar_service.delete_calendar(calendar.calendar_key)
	# 		gclogger.info("--------------- Teacher calendar deleted " + calendar.calendar_key+" -----------------")

	# 	school_calender_list = calendar_service.get_all_calendars_by_school_key_and_type('test-school-1','SCHOOL')
	# 	for calendar in school_calender_list :
	# 		calendar_service.delete_calendar(calendar.calendar_key)
	# 		gclogger.info("--------------- School calendar deleted " + calendar.calendar_key+" -----------------")


	# 	timetable_service.delete_timetable(timetable.time_table_key)
	# 	gclogger.info("--------------- Test Timetable deleted  " + timetable.time_table_key+"  -----------------")
	# 	academic_service.delete_academic_config(academic_configuration.academic_config_key)
	# 	gclogger.info("---------------Test Academic Configuration deleted  " + academic_configuration.academic_config_key + "-----------------")



	def get_timetable_from_json(self) :
		with open('tests/unit/fixtures/error-in-teacher-calendar/timetable.json', 'r') as calendar_list:
			timetable = json.load(calendar_list)
		return timetable

	def get_holiday_class_calendar_list_from_json(self) :
		with open('tests/unit/fixtures/error-in-teacher-calendar/class_calendar_holiday_list.json', 'r') as calendar_list:
			class_calendar_holiday_list = json.load(calendar_list)
		return class_calendar_holiday_list

	def get_holiday_school_calendar_list_from_json(self) :
		with open('tests/unit/fixtures/error-in-teacher-calendar/school_calendar_holiday_list.json', 'r') as calendar_list:
			school_calendar_holiday_list = json.load(calendar_list)
		return school_calendar_holiday_list


	def get_academic_config_from_json(self) :
		with open('tests/unit/fixtures/error-in-teacher-calendar/academic_configuration.json', 'r') as academic_configure:
			academic_configuration = json.load(academic_configure)
		return academic_configuration


	def get_expected_teacher_calendar_list(self) :
		with open('tests/unit/fixtures/error-in-teacher-calendar/teacher_calendar_list.json', 'r') as calendar_list:
			teacher_calendar_dict_list = json.load(calendar_list)
		return teacher_calendar_dict_list


	def get_class_calendar_list(self) :
		with open('tests/unit/fixtures/error-in-teacher-calendar/class_calendar_list.json', 'r') as calendar_list:
			class_calendar_dict_list = json.load(calendar_list)
		return class_calendar_dict_list




if __name__ == '__main__':
    unittest.main()
