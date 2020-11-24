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
import academics.exam.ExamIntegrator as exam_integrator
import academics.TimetableIntegrator as timetable_integrator
import academics.lessonplan.LessonplanIntegrator as lessonplan_integrator
import academics.leave.Leave as leave
import academics.leave.LeaveDBService as leave_service
import academics.leave.LeaveIntegrator as leave_integrator
import academics.exam.Exam as exam
import pprint
import copy
import academics.timetable.KeyGeneration as key
pp = pprint.PrettyPrinter(indent=4)

class CancelLeaveIntegratorTest(unittest.TestCase):
	def setUp(self) :

		timetables = self.get_timetables_list_from_json()
		for timetable in timetables :
			response = timetable_service.create_timetable(timetable)
			gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' time table uploaded '+str(timetable['time_table_key']))
		academic_configuration = self.get_academic_config_from_json()
		response = academic_service.create_academic_config(academic_configuration)
		gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' Academic configuration uploaded '+str(academic_configuration['academic_config_key']))

		current_class_calendars = self.get_current_class_calendars_list_json()
		for current_calendar in current_class_calendars :
			response = calendar_service.add_or_update_calendar(current_calendar)
			gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' ------- A Existing class calendar uploaded --------- '+str(current_calendar['calendar_key']))

		current_teachers_calendars = self.get_current_teacher_calendars_list_json()
		for current_calendar in current_teachers_calendars :
			response = calendar_service.add_or_update_calendar(current_calendar)
			gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' ------- A Existing teacher calendar uploaded --------- '+str(current_calendar['calendar_key']))

		current_lessonplans = self.get_current_lessonplans_from_json()
		for current_lessonplan in current_lessonplans :
			response = lessonplan_service.create_lessonplan(current_lessonplan)
			gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' Existing lesson plan uploaded '+str(current_lessonplan['lesson_plan_key']))

		current_teacher_leaves = self.get_current_teacher_leaves_list_json()
		for teacher_leave in current_teacher_leaves :
			response = leave_service.add_or_update_leave(teacher_leave)
			gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' Existing leave uploaded '+str(teacher_leave['leave_key']))

		class_info_one_dict = self.get_class_info()
		response = class_info_service.add_or_update_class_info(class_info_one_dict)
		gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' ------------- A Class info for uploaded --------- ' +str(class_info_one_dict['class_info_key']) )


		

	def test_calendars_and_lessonplan(self) :
		leave_key = 'test-leave-key-1'


		leave_integrator.integrate_leave_cancel(leave_key)	
		expected_teacher_calendars_list = self.get_expected_teacher_calendars_list()
		expected_lessonplans_list = self.get_expected_lessonplans_list()
		expected_class_calendars_list = self.get_expected_class_calendars_list()
		expected_teacher_calendar_dict = {}
		for teacher_calendar in expected_teacher_calendars_list :
			calendar_date = teacher_calendar.calendar_date
			subscriber_key = teacher_calendar.subscriber_key
			expected_teacher_calendar_dict[calendar_date + subscriber_key] = teacher_calendar
		
		
			gclogger.info("-----[UnitTest] teacher calendar test passed ----------------- "+ str(teacher_calendar.calendar_key)+" ------------------------------ ")
		updated_teacher_calendars_list = calendar_service.get_all_calendars_by_school_key_and_type('test-school-1','EMPLOYEE')
		updated_class_calendars_list = calendar_service.get_all_calendars_by_school_key_and_type('test-school-1','CLASS-DIV')
		class_info_list = class_info_service.get_classinfo_list('test-school-1', '2020-2021')
		for class_info in class_info_list :
			if hasattr(class_info, 'divisions') :
				for div in class_info.divisions :
					division = div.name
					class_key = class_info.class_info_key
					print("CLASS KEY ________",class_key)
					print("DIVISION-_______",division)
					updated_lessonplans_list = lessonplan_service.get_lesson_plan_list(class_key, division)
					for updated_lessonplan in updated_lessonplans_list :
						lp = lpnr.LessonPlan(None)
						updated_lessonplan_dict = lp.make_lessonplan_dict(updated_lessonplan)
						pp.pprint(updated_lessonplan_dict)
						self.check_lesson_plans(updated_lessonplan,expected_lessonplans_list)

		for updated_class_calendar in updated_class_calendars_list :
			cal = calendar.Calendar(None)
			class_calendar_dict = cal.make_calendar_dict(updated_class_calendar)
			pp.pprint(class_calendar_dict)
			self.check_class_calendars(updated_class_calendar,expected_class_calendars_list)
		for teacher_calendar in updated_teacher_calendars_list :
			
			teacher_calendar_key = teacher_calendar.calendar_date + teacher_calendar.subscriber_key
			expected_teacher_calendar = expected_teacher_calendar_dict[teacher_calendar_key]

			self.assertEqual(expected_teacher_calendar.institution_key,teacher_calendar.institution_key )
			self.assertEqual(expected_teacher_calendar.calendar_date,teacher_calendar.calendar_date )
			self.assertEqual(expected_teacher_calendar.subscriber_key,teacher_calendar.subscriber_key )
			self.assertEqual(expected_teacher_calendar.subscriber_type,teacher_calendar.subscriber_type )
			self.check_events_teacher_calendar(expected_teacher_calendar.events,teacher_calendar.events)
			gclogger.info("-----[UnitTest] teacher calendar test passed ----------------- "+ str(teacher_calendar.calendar_key)+" ------------------------------ ")


		
 
	def tearDown(self) :
		
		timetables = self.get_timetables_list_from_json()
		for timetable in timetables :
			timetable_service.delete_timetable(timetable['time_table_key'])
			gclogger.info("--------------- Test Timetable deleted  " + timetable['time_table_key']+"  -----------------")
		school_key = timetable['school_key']
		academic_configuration = academic_service.get_academig('test-school-1','2020-2021')
		updated_class_calendars_list = calendar_service.get_all_calendars_by_school_key_and_type('test-school-1','CLASS-DIV')
		for updated_class_calendar in updated_class_calendars_list :
			calendar_service.delete_calendar(updated_class_calendar.calendar_key)
			gclogger.info("--------------- A updated class calendar deleted " + updated_class_calendar.calendar_key+" -----------------")
		updated_teacher_calendars_list = calendar_service.get_all_calendars_by_school_key_and_type(school_key,'EMPLOYEE')
		for updated_teacher_calendar in updated_teacher_calendars_list :
			calendar_service.delete_calendar(updated_teacher_calendar.calendar_key)
			gclogger.info("--------------- A updated teacher calendar deleted " + updated_teacher_calendar.calendar_key+" -----------------")
		

		academic_service.delete_academic_config(academic_configuration.academic_config_key)
		gclogger.info("---------------Test Academic Configuration deleted  " + academic_configuration.academic_config_key + "-----------------")
		current_teacher_leaves = self.get_current_teacher_leaves_list_json()
		for leave in current_teacher_leaves :
			leave_service.delete_leave(leave['leave_key'])
			gclogger.info("--------------- Test Leave deleted  " + leave['leave_key']+"  -----------------")

		class_info = self.get_class_info()
		response = class_info_service.delete_class_info(class_info['class_info_key'])
		gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' ------------- A Class info for deleted --------- ' +str(class_info['class_info_key']) )

	
	def check_lesson_plans(self,updated_lesson_plan,expected_lesson_plan_list) :
		for expected_lesson_plan in expected_lesson_plan_list :
			if expected_lesson_plan.lesson_plan_key == updated_lesson_plan.lesson_plan_key :
				self.check_root_sessions(updated_lesson_plan.sessions,expected_lesson_plan.sessions)
				self.assertEqual(updated_lesson_plan.lesson_plan_key,expected_lesson_plan.lesson_plan_key)
				self.assertEqual(updated_lesson_plan.class_key,expected_lesson_plan.class_key)
				self.assertEqual(updated_lesson_plan.division,expected_lesson_plan.division)
				self.assertEqual(updated_lesson_plan.subject_code,expected_lesson_plan.subject_code)
				self.assertEqual(updated_lesson_plan.resources,expected_lesson_plan.resources)
				self.check_topics(updated_lesson_plan.topics,expected_lesson_plan.topics)

		gclogger.info(" <<<-------------------------------- UNIT TEST PASSED FOR "+ str(updated_lesson_plan.lesson_plan_key)+" ------------------------------ ")

	def check_topics(self,updated_lesson_plan_topics,expected_lesson_plan_topics):
		for index in range(0,len(updated_lesson_plan_topics)) :
			self.assertEqual(updated_lesson_plan_topics[index].code,expected_lesson_plan_topics[index].code)
			self.assertEqual(updated_lesson_plan_topics[index].name,expected_lesson_plan_topics[index].name)
			self.assertEqual(updated_lesson_plan_topics[index].order_index,expected_lesson_plan_topics[index].order_index)
			self.check_topic(updated_lesson_plan_topics[index].topics,expected_lesson_plan_topics[index].topics)

	def check_topic(self,updated_lesson_plan_topic,expected_lesson_plan_topic):
		for index in range(0,len(updated_lesson_plan_topic)) :
			self.assertEqual(updated_lesson_plan_topic[index].code,expected_lesson_plan_topic[index].code)
			self.assertEqual(updated_lesson_plan_topic[index].description,expected_lesson_plan_topic[index].description)
			self.assertEqual(updated_lesson_plan_topic[index].name,expected_lesson_plan_topic[index].name)
			self.assertEqual(updated_lesson_plan_topic[index].order_index,expected_lesson_plan_topic[index].order_index)
			self.assertEqual(updated_lesson_plan_topic[index].resources,expected_lesson_plan_topic[index].resources)
			self.check_sessions(updated_lesson_plan_topic[index].sessions,expected_lesson_plan_topic[index].sessions)

	def check_sessions(self,updated_lesson_plan_sessions,expected_lesson_plan_sessions) :
		for index in range(len(updated_lesson_plan_sessions)) :
			self.assertEqual(updated_lesson_plan_sessions[index].code,expected_lesson_plan_sessions[index].code)
			self.assertEqual(updated_lesson_plan_sessions[index].completion_datetime,expected_lesson_plan_sessions[index].completion_datetime)
			self.assertEqual(updated_lesson_plan_sessions[index].completion_status,expected_lesson_plan_sessions[index].completion_status)
			self.assertEqual(updated_lesson_plan_sessions[index].name,expected_lesson_plan_sessions[index].name)
			self.assertEqual(updated_lesson_plan_sessions[index].order_index,expected_lesson_plan_sessions[index].order_index)
			if hasattr(updated_lesson_plan_sessions[index],'schedule') and hasattr(expected_lesson_plan_sessions[index],'schedule'):
				self.check_schedule(updated_lesson_plan_sessions[index].schedule,expected_lesson_plan_sessions[index].schedule)
	def check_root_sessions(self,updated_lesson_plan_sessions,expected_lesson_plan_sessions) :
		for index in range(len(updated_lesson_plan_sessions)) :
			self.assertEqual(updated_lesson_plan_sessions[index].order_index,expected_lesson_plan_sessions[index].order_index)
			if hasattr(updated_lesson_plan_sessions[index],'schedule') and hasattr(expected_lesson_plan_sessions[index],'schedule'):
				self.check_schedule(updated_lesson_plan_sessions[index].schedule,expected_lesson_plan_sessions[index].schedule)

	def check_schedule(self,updated_lesson_plan_shedule,expected_lesson_plan_shedule) :
		self.assertEqual(updated_lesson_plan_shedule.start_time,expected_lesson_plan_shedule.start_time)
		self.assertEqual(updated_lesson_plan_shedule.end_time,expected_lesson_plan_shedule.end_time)

	def check_teacher_calendars(self,updated_teacher_calendar,expected_teacher_calendars_list) :
		for expected_teacher_calendar in expected_teacher_calendars_list :
			if updated_teacher_calendar.calendar_key == expected_teacher_calendar.calendar_key :
				self.assertEqual(expected_teacher_calendar.institution_key,updated_teacher_calendar.institution_key )
				self.assertEqual(expected_teacher_calendar.calendar_date,updated_teacher_calendar.calendar_date )
				self.assertEqual(expected_teacher_calendar.subscriber_key,updated_teacher_calendar.subscriber_key )
				self.assertEqual(expected_teacher_calendar.subscriber_type,updated_teacher_calendar.subscriber_type )
				self.check_events_teacher_calendar(expected_teacher_calendar.events,updated_teacher_calendar.events)
				gclogger.info("-----[UnitTest] teacher test passed ----------------- "+ str(updated_teacher_calendar.calendar_key)+" ------------------------------ ")




	def check_events_teacher_calendar(self,expected_teacher_calendar_events,updated_teacher_calendar_events) :
		for index in range(0,len(expected_teacher_calendar_events) - 1) :
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
				gclogger.info("-----[UnitTest] class calendar test passed ----------------- "+ str(updated_class_calendar.calendar_key)+" ------------------------------ ")

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


	def get_timetables_list(self) :
		timetable_list = []
		with open('tests/unit/fixtures/cancel-leave-fixtures/test_timetables_list.json', 'r') as test_timetables_list:
			timetables_dict = json.load(test_timetables_list)
			for timetable in timetables_dict :
				timetable_list.append(ttable.TimeTable(timetable))
		return timetable_list

	def get_current_lessonplans_list(self) :
		current_lessonplans = []
		with open('tests/unit/fixtures/cancel-leave-fixtures/current_lessonplans_list.json', 'r') as lessonplans_list:
			lessonplans_list_dict = json.load(lessonplans_list)
		for lessonplan in lessonplans_list_dict :
			current_lessonplans.append(lpnr.LessonPlan(lessonplan))
		return current_lessonplans

	def get_current_teacher_calendars_list(self) :
		current_teacher_calendars = []
		with open('tests/unit/fixtures/cancel-leave-fixtures/current_teacher_calendars_list.json', 'r') as calendar_list:
			class_calendars_dict = json.load(calendar_list)
		for class_cal in class_calendars_dict :
			current_teacher_calendars.append(calendar.Calendar(class_cal))
		return current_teacher_calendars

	def get_current_class_calendars_list(self) :
		current_class_calendars = []
		with open('tests/unit/fixtures/cancel-leave-fixtures/current_class_calendars_list.json', 'r') as calendar_list:
			class_calendars_dict = json.load(calendar_list)
		for class_cal in class_calendars_dict :
			current_class_calendars.append(calendar.Calendar(class_cal))
		return current_class_calendars

	def get_current_teacher_leaves_list_json(self) :
		with open('tests/unit/fixtures/cancel-leave-fixtures/current_teacher_leaves_list.json', 'r') as leaves_list:
			teacher_leaves_dict = json.load(leaves_list)
		return teacher_leaves_dict


	def get_expected_class_calendars_list(self) :
		expected_class_calendars = []
		with open('tests/unit/fixtures/cancel-leave-fixtures/expected_class_calendars_list.json', 'r') as calendar_list:
			class_calendars_dict = json.load(calendar_list)
		for class_cal in class_calendars_dict :
			expected_class_calendars.append(calendar.Calendar(class_cal))
		return expected_class_calendars

	def get_expected_teacher_calendars_list(self) :
		expected_teacher_calendars = []
		with open('tests/unit/fixtures/cancel-leave-fixtures/expected_teacher_calendars_list.json', 'r') as calendar_list:
			teacher_calendars_dict = json.load(calendar_list)
		for teacher_cal in teacher_calendars_dict :
			expected_teacher_calendars.append(calendar.Calendar(teacher_cal))
		return expected_teacher_calendars

	def get_expected_lessonplans_list(self) :
		expected_lessonplans = []
		with open('tests/unit/fixtures/cancel-leave-fixtures/expected_lessonplans_list.json', 'r') as lessonplan_list:
			lessonplans_dict = json.load(lessonplan_list)
		for lessonplan in lessonplans_dict :
			expected_lessonplans.append(lpnr.LessonPlan(lessonplan))
		return expected_lessonplans

	def get_timetables_list_from_json(self) :
		with open('tests/unit/fixtures/cancel-leave-fixtures/test_timetables_list.json', 'r') as calendar_list:
			timetable = json.load(calendar_list)
		return timetable

	def get_academic_config_from_json(self) :
		with open('tests/unit/fixtures/academic_configuration.json', 'r') as academic_configure:
			academic_configuration = json.load(academic_configure)
		return academic_configuration

	def get_current_lessonplans_from_json(self) :
		with open('tests/unit/fixtures/cancel-leave-fixtures/current_lessonplans_list.json', 'r') as lessonplans_list:
			current_lessonplans = json.load(lessonplans_list)
		return current_lessonplans

	def get_current_teacher_calendars_list_json(self) :
		with open('tests/unit/fixtures/cancel-leave-fixtures/current_teacher_calendars_list.json', 'r') as calendar_list:
			current_teacher_calendars = json.load(calendar_list)
		return current_teacher_calendars

	def get_current_class_calendars_list_json(self) :
		with open('tests/unit/fixtures/cancel-leave-fixtures/current_class_calendars_list.json', 'r') as calendar_list:
			current_class_calendars = json.load(calendar_list)
		return current_class_calendars

	def get_class_info(self) :
		with open('tests/unit/fixtures/add-teacher-leave-fixtures/class_info.json', 'r') as class_info_two:
			class_info_two_dict = json.load(class_info_two)
		return class_info_two_dict


if __name__ == '__main__':
	unittest.main()
