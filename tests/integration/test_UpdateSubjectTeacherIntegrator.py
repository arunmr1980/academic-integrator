import unittest
import json
from academics.TimetableIntegrator import *
from academics.timetable import AcademicConfiguration as academic_config
import academics.timetable.TimeTable as ttable
from academics.logger import GCLogger as gclogger
import academics.calendar.Calendar as calendar
import academics.lessonplan.LessonPlan as lpnr
from academics.calendar.CalendarIntegrator import *
import academics.classinfo.ClassInfo as classinfo
import academics.classinfo.ClassInfoDBService as class_info_service
import pprint
import copy 
import academics.timetable.KeyGeneration as key
pp = pprint.PrettyPrinter(indent=4)

class UpdateSubjectTeacherIntegratorTest(unittest.TestCase):

	def setUp(self) :
		current_class_timetables_list = self.get_current_class_timetables_list_json()
		for current_class_timetable in current_class_timetables_list :
			response = timetable_service.create_timetable(current_class_timetable)
			gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + '--------- A class time table uploaded -------- '+str(current_class_timetable['time_table_key']))

		current_teacher_timetables_list= self.get_current_teacher_timetables_list_json()
		for current_teacher_timetable in current_teacher_timetables_list :
			response = timetable_service.create_timetable(current_teacher_timetable)
			gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + '--------- A teacher time table uploaded -------- '+str(current_teacher_timetable['time_table_key']))

		current_class_calendars = self.get_current_class_calendars_list_json()
		for current_calendar in current_class_calendars :
			response = calendar_service.add_or_update_calendar(current_calendar)
			gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' ------- A class calendar uploaded --------- '+str(current_calendar['calendar_key']))

		class_info_list = self.get_class_info_list_json()
		for class_info in class_info_list :
			response = class_info_service.add_or_update_class_info(class_info)
			gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' ------------- A Class info for uploaded --------- ' +str(class_info['class_info_key']) )

		
	def test_timetables_and_calendars(self) :
		division = 'A'
		class_info_key = '8B1B22E72AE'	
		subject_code = 'bio3'
		subscriber_key = class_info_key + '-' + division
		current_class_timetable = timetable_service.get_timetable_by_class_key_and_division(class_info_key,division)
		academic_year = current_class_timetable.academic_year
		current_cls_timetable = copy.deepcopy(current_class_timetable)
		update_subject_teacher_integrator(division,class_info_key,subject_code)

		expected_teacher_timetables_list = self.get_expected_teacher_timetables_list()
		expected_class_calendars_list = self.get_expected_class_calendars_list()
		expected_class_timetables_list = self.get_expected_class_timetables_list()

		class_info = class_info_service.get_classinfo(class_info_key)
		updated_class_timetable = timetable_service.get_timetable_by_class_key_and_division(class_info_key,division)
		previous_employee_key = get_previous_employee_key(subject_code,current_cls_timetable)
		updated_previous_teacher_timetable = timetable_service.get_timetable_entry_by_employee(previous_employee_key,academic_year)
		updated_employee_key = get_updated_employee_key(subject_code,class_info,class_info_key,division)
		updated_new_teacher_timetable = timetable_service.get_timetable_entry_by_employee(updated_employee_key,academic_year)
		updated_class_calendars_list = calendar_service.get_all_calendars_by_key_and_type(subscriber_key,'CLASS-DIV')

		self.check_class_timetables(updated_class_timetable,expected_class_timetables_list)
		gclogger.info("-----[UnitTest] class timetable test passed ----------------- "+ str(updated_class_timetable.time_table_key)+" ------------------------------ ")

		for updated_class_calendar in updated_class_calendars_list :
			self.check_class_calendars(updated_class_calendar,expected_class_calendars_list)
			gclogger.info("-----[UnitTest] class calendar test passed ----------------- "+ str(updated_class_calendar.calendar_key)+" ------------------------------ ")

		self.check_teacher_timetables(updated_previous_teacher_timetable,expected_teacher_timetables_list)
		gclogger.info("-----[UnitTest] teacher timetable test passed ----------------- "+ str(updated_previous_teacher_timetable.time_table_key)+" ------------------------------ ")
		self.check_teacher_timetables(updated_new_teacher_timetable,expected_teacher_timetables_list)
		gclogger.info("-----[UnitTest] teacher timetable test passed ----------------- "+ str(updated_new_teacher_timetable.time_table_key)+" ------------------------------ ")
		
		
	def tearDown(self) :
		division = 'A'
		class_info_key = '8B1B22E72AE'	
		subject_code = 'bio3'
		subscriber_key = class_info_key + '-' + division
		updated_class_timetable = timetable_service.get_timetable_by_class_key_and_division(class_info_key,division)
		timetable_service.delete_timetable(updated_class_timetable.time_table_key)
		gclogger.info("--------------- A updated class timetable deleted  " + updated_class_timetable.time_table_key+"  -----------------")

		current_teacher_timetables_list = self.get_current_teacher_timetables_list_json()
		for current_teacher_timetable in current_teacher_timetables_list :
			timetable_service.delete_timetable(current_teacher_timetable["time_table_key"])
			gclogger.info("--------------- A updated teacher Timetable deleted  " + current_teacher_timetable["time_table_key"]+"  -----------------")

		updated_class_calendars_list = calendar_service.get_all_calendars_by_key_and_type(subscriber_key,'CLASS-DIV')
		for updated_class_calendar in updated_class_calendars_list :
			calendar_service.delete_calendar(updated_class_calendar.calendar_key)
			gclogger.info("--------------- A updated class calendar deleted " + updated_class_calendar.calendar_key+" -----------------")



					


	def get_previous_teacher_timetable(self,current_teacher_timetables_list,subject_code,previous_employee_key) :
		for current_teacher_timetable in current_teacher_timetables_list :
			if current_teacher_timetable.employee_key == previous_employee_key :
				return current_teacher_timetable


	def get_new_teacher_timetable(self,current_teacher_timetables_list,updated_employee_key,subject_code,updated_class_timetable) :
		for current_teacher_timetable in current_teacher_timetables_list :
			if current_teacher_timetable.employee_key == updated_employee_key :
				return current_teacher_timetable
		else :
			timetable = get_timetable_from_updated_class_timetable(updated_class_timetable)
			timetable = reset_periods(timetable,updated_employee_key,subject_code)
			teacher_time_table = generate_teacher_timetable(updated_employee_key,timetable,updated_class_timetable)
			return teacher_time_table


	def get_class_timetable(self,class_key,division,current_class_timetables_list) :
		for current_class_timetable in current_class_timetables_list :
			if current_class_timetable.class_key == class_key and current_class_timetable.division == division :
				return current_class_timetable

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


	def check_class_timetables(self,updated_class_timetable,expected_class_timetables_list) :
		for expected_class_timetable in expected_class_timetables_list :
			if updated_class_timetable.time_table_key == expected_class_timetable.time_table_key :
				self.assertEqual(updated_class_timetable.academic_year , expected_class_timetable.academic_year)
				self.assertEqual(updated_class_timetable.class_key , expected_class_timetable.class_key)
				self.assertEqual(updated_class_timetable.class_name , expected_class_timetable.class_name)
				self.assertEqual(updated_class_timetable.division , expected_class_timetable.division)
				self.check_timetable_day_tables(updated_class_timetable.timetable.day_tables,expected_class_timetable.timetable.day_tables)

	def check_teacher_timetables(self,updated_teacher_timetable,expected_teacher_timetables_list) :
		for expected_teacher_timetable in expected_teacher_timetables_list :
			if updated_teacher_timetable.time_table_key == expected_teacher_timetable.time_table_key :
				self.assertEqual(updated_teacher_timetable.academic_year , expected_teacher_timetable.academic_year)
				self.assertEqual(updated_teacher_timetable.school_key , expected_teacher_timetable.school_key)
				self.assertEqual(updated_teacher_timetable.employee_key , expected_teacher_timetable.employee_key)
				self.check_timetable_day_tables(updated_teacher_timetable.timetable.day_tables,expected_teacher_timetable.timetable.day_tables)


	def check_timetable_day_tables(self,updated_day_tables,expected_day_tables) :
		for day in expected_day_tables :
			day_code = day.day_code
			updated_timetable_day = self.get_updated_timetable_day(expected_day_tables,day_code)

			self.assertEqual(updated_timetable_day.day_code , day.day_code)
			self.assertEqual(updated_timetable_day.order_index , day.order_index)
			self.check_timetable_periods(updated_timetable_day.periods,day.periods)

	def check_timetable_periods(self,updated_periods,expected_periods) :
		for period  in expected_periods :
			order_index = period.order_index
			updated_timetable_period = self.get_updated_timetable_period(expected_periods,order_index)
			self.assertEqual(updated_timetable_period.class_info_key,period.class_info_key)
			self.assertEqual(updated_timetable_period.division_code,period.division_code)
			self.assertEqual(updated_timetable_period.employee_key,period.employee_key)
			self.assertEqual(updated_timetable_period.order_index,period.order_index)
			self.assertEqual(updated_timetable_period.period_code,period.period_code)
			self.assertEqual(updated_timetable_period.subject_key,period.subject_key)

	def get_updated_timetable_period(self,expected_periods,order_index) :
		for period in expected_periods :
			if period.order_index == order_index :
				return period

	def get_updated_timetable_day(self,expected_day_tables,day_code) :
		for day in expected_day_tables :
			if day.day_code == day_code :
				return day

	def get_expected_teacher_timetables_list(self) :
		expected_teacher_timetables = []
		with open('tests/unit/fixtures/update-subject-teacher-fixtures/expected_teacher_timetables.json', 'r') as timetables_list:
			teacher_timetables_dict = json.load(timetables_list)
		for current_teacher_timetable in teacher_timetables_dict :
			expected_teacher_timetables.append(ttable.TimeTable(current_teacher_timetable))
		return expected_teacher_timetables


	def get_expected_class_calendars_list(self) :
		expected_class_calendars = []
		with open('tests/unit/fixtures/update-subject-teacher-fixtures/expected_class_calendars.json', 'r') as calendar_list:
			class_calendars_dict = json.load(calendar_list)
		for class_cal in class_calendars_dict :
			expected_class_calendars.append(calendar.Calendar(class_cal))
		return expected_class_calendars

	def get_expected_class_calendars_list(self) :
		expected_class_calendars = []
		with open('tests/unit/fixtures/update-subject-teacher-fixtures/expected_class_calendars.json', 'r') as calendar_list:
			class_calendars_dict = json.load(calendar_list)
		for class_cal in class_calendars_dict :
			expected_class_calendars.append(calendar.Calendar(class_cal))
		return expected_class_calendars

	def get_current_class_calendars_list_json(self) :
		with open('tests/unit/fixtures/update-subject-teacher-fixtures/current_class_calendars.json', 'r') as calendar_list:
			class_calendars_dict = json.load(calendar_list)
		return class_calendars_dict

	def get_expected_class_timetables_list(self) :
		expected_class_timetables = []
		with open('tests/unit/fixtures/update-subject-teacher-fixtures/expected_class_timetables.json', 'r') as timetables_list:
			class_timetables_dict = json.load(timetables_list)
		for current_class_timetable in class_timetables_dict :
			expected_class_timetables.append(ttable.TimeTable(current_class_timetable))
		return expected_class_timetables

	def get_expected_teacher_timetables_list(self) :
		expected_teacher_timetables = []
		with open('tests/unit/fixtures/update-subject-teacher-fixtures/expected_teacher_timetables.json', 'r') as timetables_list:
			teacher_timetables_dict = json.load(timetables_list)
		for current_teacher_timetable in teacher_timetables_dict :
			expected_teacher_timetables.append(ttable.TimeTable(current_teacher_timetable))
		return expected_teacher_timetables

	def get_class_info_list_json(self) :
		with open('tests/unit/fixtures/update-subject-teacher-fixtures/class_info_list.json', 'r') as class_infos:
			class_info_list_dict = json.load(class_infos)
		return class_info_list_dict

	def get_current_class_timetables_list_json(self) :
		with open('tests/unit/fixtures/update-subject-teacher-fixtures/current_class_timetables.json', 'r') as current_class_timetables:
			current_class_timetables_dict = json.load(current_class_timetables)
		return current_class_timetables_dict
			

	def get_current_teacher_timetables_list_json(self) :
		with open('tests/unit/fixtures/update-subject-teacher-fixtures/current_teacher_timetables.json', 'r') as current_teacher_timetables:
			current_teacher_timetables_dict = json.load(current_teacher_timetables)
		return current_teacher_timetables_dict

if __name__ == '__main__':
	unittest.main()
