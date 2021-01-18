import unittest
import json
from academics.TimetableIntegrator import integrate_class_timetable,integrate_teacher_timetable
from academics.timetable import AcademicConfiguration as academic_config
import academics.timetable.TimeTable as ttable
from academics.logger import GCLogger as gclogger
import academics.calendar.Calendar as calendar
import pprint
pp = pprint.PrettyPrinter(indent=4)

class TimetableIntegratorTest(unittest.TestCase):


	# def test_class_calender(self) :
	# 	gclogger.info("")
	# 	gclogger.info("[UnitTest] testing class calendar .....")
	# 	time_table=self.get_time_table()
	# 	academic_configuration=self.get_academic_configuration()
	# 	class_calendar_holiday_list=self.class_calendar_holiday_list()
	# 	school_calendar_holiday_list=self.school_calendar_holiday_list()
	# 	generated_class_calendar_dict = integrate_class_timetable(time_table,academic_configuration,class_calendar_holiday_list,school_calendar_holiday_list)
	# 	class_calendar_list = generated_class_calendar_dict.values()
	# 	# for class_calendar in class_calendar_list :	
	# 	# 	cal = calendar.Calendar(None)
	# 	# 	calendar_dict = cal.make_calendar_dict(class_calendar)	
	# 	# 	pp.pprint(calendar_dict)

	# 	class_calendar_dict_list = self.get_calendar_list()
	# 	for class_calendar in class_calendar_dict_list :
	# 		expected_class_calendar = calendar.Calendar(class_calendar)
	# 		calendar_date = expected_class_calendar.calendar_date
	# 		generated_class_calendar = generated_class_calendar_dict[calendar_date]
	# 		self.assertEqual(expected_class_calendar.institution_key,generated_class_calendar.institution_key )
	# 		self.assertEqual(expected_class_calendar.calendar_date,generated_class_calendar.calendar_date )
	# 		self.assertEqual(expected_class_calendar.subscriber_key,generated_class_calendar.subscriber_key )
	# 		self.assertEqual(expected_class_calendar.subscriber_type,generated_class_calendar.subscriber_type )
	# 		self.check_events(expected_class_calendar.events,generated_class_calendar.events)

	# def check_events(self,expected_class_calendar_events,generated_class_calendar_events) :

	# 	for index in range(0,len(expected_class_calendar_events) - 1) :
	# 		self.assertEqual(expected_class_calendar_events[index].event_type , generated_class_calendar_events[index].event_type)
	# 		self.assertEqual(expected_class_calendar_events[index].from_time , generated_class_calendar_events[index].from_time)
	# 		self.assertEqual(expected_class_calendar_events[index].to_time , generated_class_calendar_events[index].to_time)
	# 		self.check_params(expected_class_calendar_events[index].params,generated_class_calendar_events[index].params)

	# def check_params(self,expected_class_calendar_event_params,generated_class_calendar_event_params) :
	# 	for index in range(0,len(expected_class_calendar_event_params) - 1) :
	# 		self.assertEqual(expected_class_calendar_event_params[index].key,generated_class_calendar_event_params[index].key)
	# 		self.assertEqual(expected_class_calendar_event_params[index].value,generated_class_calendar_event_params[index].value)


	# gclogger.info("-----[Unit Test] Class calendar test passed -----------------")


	def test_teacher_calender(self) :
		gclogger.info("")
		gclogger.info("[UnitTest] testing teacher calendar .....")

		time_table = self.get_time_table()
		academic_configuration=self.get_academic_configuration()
		class_calendar_holiday_list=self.class_calendar_holiday_list()
		school_calendar_holiday_list=self.school_calendar_holiday_list()
		generated_class_calendar_dict = integrate_class_timetable(time_table,academic_configuration,class_calendar_holiday_list,school_calendar_holiday_list)

		class_calendar_list = generated_class_calendar_dict.values()
		for class_calendar in class_calendar_list :	
			cal = calendar.Calendar(None)
			calendar_dict = cal.make_calendar_dict(class_calendar)	
			pp.pprint(calendar_dict)

		teacher_calendars_dict = integrate_teacher_timetable(class_calendar_list)
		teacher_calendar_list = teacher_calendars_dict.values()
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
			gclogger.info("----- [UnitTest] Teacher calendar test passed for teacher calendar --> " + teacher_calendar.calendar_key + " -----------------")


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


	def class_calendar_holiday_list(self) :
		class_calendar_holiday_list = []
		with open('tests/unit/fixtures/error-in-teacher-calendar/class_calendar_holiday_list.json', 'r') as calendar_list:
			class_calendar_holiday_json_list = json.load(calendar_list)
		for class_calendar_holiday in class_calendar_holiday_json_list :
			class_calendar_holiday = calendar.Calendar(class_calendar_holiday)
			class_calendar_holiday_list.append(class_calendar_holiday)
		return class_calendar_holiday_list

	def school_calendar_holiday_list(self) :
		school_calendar_holiday_list = []
		with open('tests/unit/fixtures/error-in-teacher-calendar/school_calendar_holiday_list.json', 'r') as calendar_list:
			school_calendar_holiday_json_list = json.load(calendar_list)
		for school_calendar_holiday in school_calendar_holiday_json_list :
			school_calendar_holiday = calendar.Calendar(school_calendar_holiday)
			school_calendar_holiday_list.append(school_calendar_holiday)
		return school_calendar_holiday_list

	def get_calendar_list(self) :
		with open('tests/unit/fixtures/error-in-teacher-calendar/class_calendar_list.json', 'r') as calendar_list:
			class_calendar_dict_list = json.load(calendar_list)
		return class_calendar_dict_list


	def get_time_table(self):
		with open('tests/unit/fixtures/error-in-teacher-calendar/timetable.json', 'r') as timetable:
			timetable = json.load(timetable)
		return ttable.TimeTable(timetable)


	def get_academic_configuration(self):
		with open('tests/unit/fixtures/error-in-teacher-calendar/academic_configuration.json', 'r') as academic_configuration:
			academic_configuration_dict = json.load(academic_configuration)
			academic_configuration = academic_config.AcademicConfiguration(academic_configuration_dict)
		return academic_configuration



if __name__ == '__main__':
    unittest.main()
