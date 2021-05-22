import unittest
import json
from academics.TimetableIntegrator import integrate_class_timetable,integrate_teacher_timetable
from academics.timetable import AcademicConfiguration as academic_config
import academics.academic.AcademicDBService as academic_service
import academics.timetable.TimeTable as ttable
from academics.logger import GCLogger as gclogger
import academics.calendar.Calendar as calendar
import academics.lessonplan.LessonPlan as lessonplan
from academics.lessonplan import LessonplanDBService as lessonplan_service
from academics.calendar.CalendarLessonPlanIntegrator import integrate_calendars_to_lesson_plan, integrate_calendar,integrate_calendar_to_single_lessonplan
import academics.timetable.TimeTableDBService as timetable_service
from academics.TimetableIntegrator import generate_and_save_calenders
import academics.calendar.CalendarDBService as calendar_service
import academics.classinfo.ClassInfoDBService as class_info_service
import pprint
pp = pprint.PrettyPrinter(indent=4)


class CalendarLessonplanIntegratorTest(unittest.TestCase):

	def setUp(self) :
		timetable = self.get_timetable_as_json()
		response = timetable_service.create_timetable(timetable)
		gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' time table uploaded '+str(timetable['time_table_key']))
		academic_configuration = self.get_academic_config_as_json()
		response = academic_service.create_academic_config(academic_configuration)
		gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' Academic configuration uploaded '+str(academic_configuration['academic_config_key']))
		current_lesson_plan = self.get_current_lessonplan()
		response = lessonplan_service.create_lessonplan(current_lesson_plan)
		gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' Current lesson plan uploaded '+str(current_lesson_plan['lesson_plan_key']))


		class_info_one_dict = self.get_class_info()
		response = class_info_service.add_or_update_class_info(class_info_one_dict)
		gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' ------------- A Class info for uploaded --------- ' +str(class_info_one_dict['class_info_key']) )

	def test_lessonplan_with_calendar_list(self) :
		lesson_plan_key = "l1"
		timetable = timetable_service.get_time_table('tt-1')
		school_key = timetable.school_key
		academic_configuration = academic_service.get_academig(school_key,'2020-2021')
		expected_lesson_plan = self.get_expected_lesson()
		generate_and_save_calenders(timetable.time_table_key,academic_configuration.academic_year)
		integrate_calendar_to_single_lessonplan(lesson_plan_key)
		class_calender_list = calendar_service.get_all_calendars_by_key_and_type('c-k-2-A','CLASS-DIV')
		for updated_class_calendar in class_calender_list :
			cal = calendar.Calendar(None)
			calendar_dict = cal.make_calendar_dict(updated_class_calendar)
			pp.pprint(calendar_dict)
		updated_lessonplan = lessonplan_service.get_lessonplan(lesson_plan_key)
		lp = lessonplan.LessonPlan(None)
		generated_lesson_plan = lp.make_lessonplan_dict(updated_lessonplan)
		pp.pprint(generated_lesson_plan)
		self.check_root_sessions(updated_lessonplan.sessions,expected_lesson_plan.sessions)
		self.assertEqual(updated_lessonplan.lesson_plan_key,expected_lesson_plan.lesson_plan_key)
		self.assertEqual(updated_lessonplan.class_key,expected_lesson_plan.class_key)
		self.assertEqual(updated_lessonplan.division,expected_lesson_plan.division)
		self.assertEqual(updated_lessonplan.subject_code,expected_lesson_plan.subject_code)
		self.assertEqual(updated_lessonplan.resources,expected_lesson_plan.resources)
		self.check_topics(updated_lessonplan.topics,expected_lesson_plan.topics)
		gclogger.info(" <<<-------------------------------- INTEGRATION TEST PASSED FOR "+ str(updated_lessonplan.lesson_plan_key)+" ------------------------------>>> ")

		

	def check_topics(self,generated_lesson_plan_topics,expected_lesson_plan_topics):
		for index in range(0,len(generated_lesson_plan_topics)) :
			self.assertEqual(generated_lesson_plan_topics[index].code,expected_lesson_plan_topics[index].code)
			self.assertEqual(generated_lesson_plan_topics[index].name,expected_lesson_plan_topics[index].name)
			self.assertEqual(generated_lesson_plan_topics[index].order_index,expected_lesson_plan_topics[index].order_index)
			self.check_topic(generated_lesson_plan_topics[index].topics,expected_lesson_plan_topics[index].topics)


	def check_topic(self,generated_lesson_plan_topic,expected_lesson_plan_topic):
		for index in range(0,len(generated_lesson_plan_topic)) :
			self.assertEqual(generated_lesson_plan_topic[index].code,expected_lesson_plan_topic[index].code)
			self.assertEqual(generated_lesson_plan_topic[index].description,expected_lesson_plan_topic[index].description)
			self.assertEqual(generated_lesson_plan_topic[index].name,expected_lesson_plan_topic[index].name)
			self.assertEqual(generated_lesson_plan_topic[index].order_index,expected_lesson_plan_topic[index].order_index)
			self.assertEqual(generated_lesson_plan_topic[index].resources,expected_lesson_plan_topic[index].resources)
			self.check_sessions(generated_lesson_plan_topic[index].sessions,expected_lesson_plan_topic[index].sessions)


	def check_sessions(self,generated_lesson_plan_sessions,expected_lesson_plan_sessions) :
		for index in range(len(generated_lesson_plan_sessions)) :
			self.assertEqual(generated_lesson_plan_sessions[index].code,expected_lesson_plan_sessions[index].code)
			self.assertEqual(generated_lesson_plan_sessions[index].completion_datetime,expected_lesson_plan_sessions[index].completion_datetime)
			self.assertEqual(generated_lesson_plan_sessions[index].completion_status,expected_lesson_plan_sessions[index].completion_status)
			self.assertEqual(generated_lesson_plan_sessions[index].name,expected_lesson_plan_sessions[index].name)
			self.assertEqual(generated_lesson_plan_sessions[index].order_index,expected_lesson_plan_sessions[index].order_index)
			self.check_schedule(generated_lesson_plan_sessions[index].schedule,expected_lesson_plan_sessions[index].schedule)

	def check_root_sessions(self,updated_lesson_plan_sessions,expected_lesson_plan_sessions) :
		for index in range(len(updated_lesson_plan_sessions)) :
			self.assertEqual(updated_lesson_plan_sessions[index].order_index,expected_lesson_plan_sessions[index].order_index)
			self.check_schedule(updated_lesson_plan_sessions[index].schedule,expected_lesson_plan_sessions[index].schedule)

	def check_schedule(self,generated_lesson_plan_shedule,expexted_lesson_plan_shedule) :
		self.assertEqual(generated_lesson_plan_shedule.start_time,expexted_lesson_plan_shedule.start_time)
		self.assertEqual(generated_lesson_plan_shedule.end_time,expexted_lesson_plan_shedule.end_time)

	def tearDown(self):
		timetable = timetable_service.get_time_table('tt-1')
		school_key = timetable.school_key
		academic_configuration = academic_service.get_academig(school_key,'2020-2021')
		class_calender_list = calendar_service.get_all_calendars_by_key_and_type('c-k-2-A','CLASS-DIV')
		for calendar in class_calender_list :
			calendar_service.delete_calendar(calendar.calendar_key)
			gclogger.info("--------------- Class calendar deleted " + calendar.calendar_key+" -----------------")


		teacher_calender_list = calendar_service.get_all_calendars_by_school_key_and_type('s-k-2','EMPLOYEE')
		for calendar in teacher_calender_list :
			calendar_service.delete_calendar(calendar.calendar_key)
			gclogger.info("--------------- Teacher calendar deleted " + calendar.calendar_key+" -----------------")


		timetable_service.delete_timetable(timetable.time_table_key)
		gclogger.info("--------------- Test Timetable deleted  " + timetable.time_table_key+"  -----------------")
		academic_service.delete_academic_config(academic_configuration.academic_config_key)
		gclogger.info("---------------Test Academic Configuration deleted  " + academic_configuration.academic_config_key + "-----------------")
		generated_lesson_plan_list = lessonplan_service.get_lesson_plan_list('c-k-2','A')
		for generated_lesson_plan in generated_lesson_plan_list :
			lessonplan_service.delete_lessonplan(generated_lesson_plan.lesson_plan_key)
			gclogger.info("---------------Test Lesson Plan deleted  " + generated_lesson_plan.lesson_plan_key + "-----------------")
		class_info = self.get_class_info()
		response = class_info_service.delete_class_info(class_info['class_info_key'])
		gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' ------------- A Class info for deleted --------- ' +str(class_info['class_info_key']) )

	def get_generated_lesson_plan_dict_list(self,generated_lesson_plan_list) :
		generated_lesson_plan_dict_list = []
		for generated_lesson_plan in generated_lesson_plan_list :
			generated_lesson_plan_dict = lessonplan.LessonPlan(None)
			generated_lesson_plan_dict = generated_lesson_plan_dict.make_lessonplan_dict(generated_lesson_plan)
			generated_lesson_plan_dict_list.append(generated_lesson_plan_dict)
		return generated_lesson_plan_dict_list

	def get_generated_lesson_plans_dict(self,generated_lesson_plan_list) :
		generated_lesson_plans_dict ={}
		for generated_lesson_plan in generated_lesson_plan_list :
			generated_lesson_plans_dict[generated_lesson_plan.lesson_plan_key] =  generated_lesson_plan
		return generated_lesson_plans_dict

	def get_expected_lesson(self) :
		with open('tests/integration/fixtures/calendar-lessonplan-fixtures/expected_lesson_plan.json', 'r') as lesson_plan:
			expected_lessonplan_dict = json.load(lesson_plan)
			expected_lessonplan = lessonplan.LessonPlan(expected_lessonplan_dict)
		return expected_lessonplan

	def get_expected_lesson_plan_single_calendar(self) :
		expected_lesson_plan_list =[]
		with open('tests/integration/fixtures/calendar-lessonplan-fixtures/expected_lesson_plan_single_cal.json', 'r') as lesson_plan_list:
			expected_lessonplan_json_list = json.load(lesson_plan_list)
			for expected_lesson_plan in expected_lessonplan_json_list :
				expected_lesson_plan_list.append(lessonplan.LessonPlan(expected_lesson_plan))
		return expected_lesson_plan_list


	def get_current_lessonplan(self) :
		with open('tests/integration/fixtures/calendar-lessonplan-fixtures/current_lesson_plan.json', 'r') as lesson_plan:
			current_lessonplan = json.load(lesson_plan)
		return current_lessonplan




	def get_timetable_as_json(self) :
		with open('tests/integration/fixtures/calendar-lessonplan-fixtures/timetable.json', 'r') as calendar_list:
			timetable = json.load(calendar_list)
		return timetable


	def get_academic_config_as_json(self) :
		with open('tests/integration/fixtures/calendar-lessonplan-fixtures/academic_configuration.json', 'r') as academic_configure:
			academic_configuration = json.load(academic_configure)
		return academic_configuration

	def get_class_info(self) :
		with open('tests/integration/fixtures/calendar-lessonplan-fixtures/class_info.json', 'r') as class_info_two:
			class_info_two_dict = json.load(class_info_two)
		return class_info_two_dict


if __name__ == '__main__':
    unittest.main()
