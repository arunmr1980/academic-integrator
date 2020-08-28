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
from academics.calendar.CalendarLessonPlanIntegrator import integrate_calendar_to_lesson_plan
import academics.timetable.TimeTableDBService as timetable_service
from academics.TimetableIntegrator import generate_and_save_calenders
import academics.calendar.CalendarDBService as calendar_service





class LessonplanIntegratorTest(unittest.TestCase):

	def setUp(self) :		
		timetable = self.get_timetable_from_json()
		response = timetable_service.create_timetable(timetable)
		gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' time table uploaded '+str(timetable['time_table_key']))	
		academic_configuration = self.get_academic_config_from_json()
		response = academic_service.create_academic_config(academic_configuration)
		gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' Academic configuration uploaded '+str(academic_configuration['academic_config_key']))
		current_lesson_plan_list = self.get_current_lesson_plan_list()
		for current_lesson_plan in current_lesson_plan_list :
			response = lessonplan_service.create_lessonplan(current_lesson_plan)
			gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' Current lesson plan uploaded '+str(current_lesson_plan['lesson_plan_key']))

			


	def test_lessonplan(self) :
		
		class_calendars_dict={}
		timetable = timetable_service.get_time_table('test-time-table-1')
		school_key = timetable.school_key
		academic_configuration = academic_service.get_academig(school_key,'2020-2021')
		generate_and_save_calenders(timetable.time_table_key,academic_configuration.academic_year)
		class_calender_list = calendar_service.get_all_calendars('test-school-1','CLASS-DIV')

		for class_calendar in class_calender_list :
			calendar_date = class_calendar.calendar_date
			class_calendars_dict[calendar_date] = class_calendar

		expected_lesson_plan_list = self.get_expected_lesson_plan_list()
		current_lesson_plan_list = lessonplan_service.get_lesson_plan_list('8B1B22E72AE','A')
		generated_class_calendar_dict = integrate_class_timetable(timetable,academic_configuration)
		generated_lesson_plan_list = integrate_calendar_to_lesson_plan(generated_class_calendar_dict,current_lesson_plan_list)
		generated_lesson_plan_dict_list = self.get_generated_lesson_plan_dict_list(generated_lesson_plan_list)


		for generated_lesson_plan_dict in generated_lesson_plan_dict_list :
			response = lessonplan_service.create_lessonplan(generated_lesson_plan_dict)
			gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' Generated lesson plan uploaded '+str(generated_lesson_plan_dict['lesson_plan_key']))
		
		generated_lesson_plan_list = lessonplan_service.get_lesson_plan_list('8B1B22E72AE','A')	
		generated_lesson_plans_dict = self.get_generated_lesson_plans_dict(generated_lesson_plan_list)
		
		for expected_lesson_plan in expected_lesson_plan_list :
			lesson_plan_key = expected_lesson_plan.lesson_plan_key
			generated_lesson_plan = generated_lesson_plans_dict[lesson_plan_key]
			self.assertEqual(generated_lesson_plan.lesson_plan_key,expected_lesson_plan.lesson_plan_key)
			self.assertEqual(generated_lesson_plan.class_key,expected_lesson_plan.class_key)
			self.assertEqual(generated_lesson_plan.division,expected_lesson_plan.division)
			self.assertEqual(generated_lesson_plan.subject_code,expected_lesson_plan.subject_code)
			self.assertEqual(generated_lesson_plan.resources,expected_lesson_plan.resources)
			self.check_topics(generated_lesson_plan.topics,expected_lesson_plan.topics)

		gclogger.info('--Integration test of calender-lessonplan integration is passed--')


	def tearDown(self):
		timetable = timetable_service.get_time_table('test-time-table-1')
		school_key = timetable.school_key
		academic_configuration = academic_service.get_academig(school_key,'2020-2021')
		class_calender_list = calendar_service.get_all_calendars('test-school-1','CLASS-DIV')
		for calendar in class_calender_list :
			calendar_service.delete_calendar(calendar.calendar_key)
			gclogger.info("--------------- Class calendar deleted " + calendar.calendar_key+" -----------------")


		teacher_calender_list = calendar_service.get_all_calendars('test-school-1','EMPLOYEE')
		for calendar in teacher_calender_list :
			calendar_service.delete_calendar(calendar.calendar_key)
			gclogger.info("--------------- Teacher calendar deleted " + calendar.calendar_key+" -----------------")


		timetable_service.delete_timetable(timetable.time_table_key)
		gclogger.info("--------------- Test Timetable deleted  " + timetable.time_table_key+"  -----------------")
		academic_service.delete_academic_config(academic_configuration.academic_config_key)
		gclogger.info("---------------Test Academic Configuration deleted  " + academic_configuration.academic_config_key + "-----------------")
		generated_lesson_plan_list = lessonplan_service.get_lesson_plan_list('8B1B22E72AE','A')
		for generated_lesson_plan in generated_lesson_plan_list :
			lessonplan_service.delete_lessonplan(generated_lesson_plan.lesson_plan_key)
			gclogger.info("---------------Test Lesson Plan deleted  " + generated_lesson_plan.lesson_plan_key + "-----------------")



	def check_topics(self,generated_lesson_plan_topics,expected_lesson_plan_topics):
		for index in range(0,len(generated_lesson_plan_topics)) :
			self.assertEqual(generated_lesson_plan_topics[index].code,expected_lesson_plan_topics[index].code)
			self.assertEqual(generated_lesson_plan_topics[index].name,expected_lesson_plan_topics[index].name)
			self.assertEqual(generated_lesson_plan_topics[index].order_index,expected_lesson_plan_topics[index].order_index)
			self.check_topic(generated_lesson_plan_topics[index].topics,expected_lesson_plan_topics[index].topics)


	def check_topic(self,generated_lesson_plan_topic,expected_lesson_plan_topic):
		for index in range(0,len(generated_lesson_plan_topic) - 1 ) :
			self.assertEqual(generated_lesson_plan_topic[index].code,expected_lesson_plan_topic[index].code)
			self.assertEqual(generated_lesson_plan_topic[index].description,expected_lesson_plan_topic[index].description)
			self.assertEqual(generated_lesson_plan_topic[index].name,expected_lesson_plan_topic[index].name)
			self.assertEqual(generated_lesson_plan_topic[index].order_index,expected_lesson_plan_topic[index].order_index)
			self.assertEqual(generated_lesson_plan_topic[index].resources,expected_lesson_plan_topic[index].resources)
			self.check_sessions(generated_lesson_plan_topic[index].sessions,expected_lesson_plan_topic[index].sessions)


	def check_sessions(self,generated_lesson_plan_sessions,expected_lesson_plan_sessions) :
		for index in range(len(generated_lesson_plan_sessions) - 1) :
			self.assertEqual(generated_lesson_plan_sessions[index].code,expected_lesson_plan_sessions[index].code)
			self.assertEqual(generated_lesson_plan_sessions[index].completion_datetime,expected_lesson_plan_sessions[index].completion_datetime)
			self.assertEqual(generated_lesson_plan_sessions[index].completion_status,expected_lesson_plan_sessions[index].completion_status)
			self.assertEqual(generated_lesson_plan_sessions[index].name,expected_lesson_plan_sessions[index].name)
			self.assertEqual(generated_lesson_plan_sessions[index].order_index,expected_lesson_plan_sessions[index].order_index)
			self.check_schedule(generated_lesson_plan_sessions[index].schedule,expected_lesson_plan_sessions[index].schedule)
			

	def check_schedule(self,generated_lesson_plan_shedule,expexted_lesson_plan_shedule) :
		self.assertEqual(generated_lesson_plan_shedule.start_time,expexted_lesson_plan_shedule.start_time)
		self.assertEqual(generated_lesson_plan_shedule.end_time,expexted_lesson_plan_shedule.end_time)


	

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

	def get_expected_lesson_plan_list(self) :
		expected_lesson_plan_list =[]
		with open('tests/unit/fixtures/expected_lesson_plan.json', 'r') as lesson_plan_list:
			expected_lessonplan_json_list = json.load(lesson_plan_list)
			for expected_lesson_plan in expected_lessonplan_json_list :
				expected_lesson_plan_list.append(lessonplan.LessonPlan(expected_lesson_plan))
		return expected_lesson_plan_list


	def get_current_lesson_plan_list(self) :
		with open('tests/unit/fixtures/current_lesson_plan.json', 'r') as lesson_plan_list:
			current_lessonplan_json_list = json.load(lesson_plan_list)
		return current_lessonplan_json_list

	def get_teacher_calendar_list(self) :
		with open('tests/unit/fixtures/teacher_calendar_list.json', 'r') as calendar_list:
			teacher_calendar_dict_list = json.load(calendar_list)
		return teacher_calendar_dict_list

	def get_calendar_list(self) :
		with open('tests/unit/fixtures/class_calendar_list.json', 'r') as calendar_list:
			class_calendar_dict_list = json.load(calendar_list)	
		return class_calendar_dict_list


	def get_timetable_from_json(self) :
		with open('tests/unit/fixtures/timetable.json', 'r') as calendar_list:
			timetable = json.load(calendar_list)
		return timetable


	def get_academic_config_from_json(self) :
		with open('tests/unit/fixtures/academic_configuration.json', 'r') as academic_configure:
			academic_configuration = json.load(academic_configure)
		return academic_configuration



if __name__ == '__main__':
    unittest.main()







