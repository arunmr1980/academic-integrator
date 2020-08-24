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


	def test_class_calender(self) :
		time_table=self.get_time_table()
		academic_configuration=self.get_academic_configuration()

		generated_class_calendar_dict = integrate_class_timetable(time_table,academic_configuration)
		class_calendar_dict_list = self.get_calendar_list()
		for class_calendar in class_calendar_dict_list :
			expected_class_calendar = calendar.Calendar(class_calendar)
			calendar_date = expected_class_calendar.calendar_date
			generated_class_calendar = generated_class_calendar_dict[calendar_date]
			self.assertEqual(expected_class_calendar.institution_key,generated_class_calendar.institution_key )
			self.assertEqual(expected_class_calendar.calendar_date,generated_class_calendar.calendar_date )
			self.assertEqual(expected_class_calendar.subscriber_key,generated_class_calendar.subscriber_key )
			self.assertEqual(expected_class_calendar.subscriber_type,generated_class_calendar.subscriber_type )
			self.check_events(expected_class_calendar.events,generated_class_calendar.events)

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


	gclogger.info("--------------- Class calendar test passed -----------------")


	def test_teacher_calender(self) :
		expected_teacher_calendar_dict = {}
		time_table=self.get_time_table()
		academic_configuration=self.get_academic_configuration()
		generated_class_calendar_dict = integrate_class_timetable(time_table,academic_configuration)

		class_calendar_list = generated_class_calendar_dict.values()
		teacher_calendars_dict = integrate_teacher_timetable(class_calendar_list)
		teacher_calendar_dict_list = self.get_teacher_calendar_list()
		for teacher_calendar in teacher_calendar_dict_list :
			teacher_calendar = calendar.Calendar(teacher_calendar)
			calendar_date = teacher_calendar.calendar_date
			subscriber_key = teacher_calendar.subscriber_key
			expected_teacher_calendar_dict[calendar_date + subscriber_key] = teacher_calendar

		for teacher_calendar_key in teacher_calendars_dict :
			expected_teacher_calendar = expected_teacher_calendar_dict[teacher_calendar_key]
			teacher_calendar = teacher_calendars_dict[teacher_calendar_key]
			self.assertEqual(expected_teacher_calendar.institution_key,teacher_calendar.institution_key )
			self.assertEqual(expected_teacher_calendar.calendar_date,teacher_calendar.calendar_date )
			self.assertEqual(expected_teacher_calendar.subscriber_key,teacher_calendar.subscriber_key )
			self.assertEqual(expected_teacher_calendar.subscriber_type,teacher_calendar.subscriber_type )
		gclogger.info("------------------Teacher calendar test passed -----------------")


	def get_teacher_calendar_list(self) :
		with open('tests/unit/fixtures/teacher_calendar_list.json', 'r') as calendar_list:
			teacher_calendar_dict_list = json.load(calendar_list)
		return teacher_calendar_dict_list

	def get_calendar_list(self) :
		with open('tests/unit/fixtures/class_calendar_list.json', 'r') as calendar_list:
			class_calendar_dict_list = json.load(calendar_list)
		return class_calendar_dict_list


	def get_time_table(self):
		with open('tests/unit/fixtures/timetable.json', 'r') as timetable:
			timetable = json.load(timetable)
		return ttable.TimeTable(timetable)


	def get_academic_configuration(self):
		with open('tests/unit/fixtures/academic_configuration.json', 'r') as academic_configuration:
			academic_configuration_dict = json.load(academic_configuration)
			academic_configuration = academic_config.AcademicConfiguration(academic_configuration_dict)
		return academic_configuration



if __name__ == '__main__':
    unittest.main()
