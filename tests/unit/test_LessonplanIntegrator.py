import unittest
import json
from academics.TimetableIntegrator import integrate_class_timetable,integrate_teacher_timetable
from academics.academic import AcademicConfiguration as academic_config
import academics.timetable.TimeTable as ttable
from academics.logger import GCLogger as gclogger
import academics.calendar.Calendar as calendar
import academics.lessonplan.LessonPlan as lessonplan
from academics.calendar.CalendarLessonPlanIntegrator import integrate_calendar_to_lesson_plan
import operator
import pprint
pp = pprint.PrettyPrinter(indent=4)



class LessonplanIntegratorTest(unittest.TestCase):


	def test_lessonplan(self) :
		expected_lesson_plan_list = self.get_expected_lesson_plan_list()
		current_lesson_plan_list = self.get_current_lesson_plan_list()
		class_calendar = self.get_current_class_calendar()
		generated_lesson_plan_list = integrate_calendar_to_lesson_plan(class_calendar,current_lesson_plan_list)

		generated_lesson_plans_dict = self.get_generated_lesson_plans_dict(generated_lesson_plan_list)
		for expected_lesson_plan in expected_lesson_plan_list :
			lesson_plan_key = expected_lesson_plan.lesson_plan_key
			generated_lesson_plan = generated_lesson_plans_dict[lesson_plan_key]

			lp = lessonplan.LessonPlan(None)
			updated_lessonplan_dict = lp.make_lessonplan_dict(generated_lesson_plan)
			pp.pprint(updated_lessonplan_dict)
			
			self.check_root_sessions(generated_lesson_plan.sessions,expected_lesson_plan.sessions)
			self.assertEqual(generated_lesson_plan.lesson_plan_key,expected_lesson_plan.lesson_plan_key)
			self.assertEqual(generated_lesson_plan.class_key,expected_lesson_plan.class_key)
			self.assertEqual(generated_lesson_plan.division,expected_lesson_plan.division)
			self.assertEqual(generated_lesson_plan.subject_code,expected_lesson_plan.subject_code)
			self.assertEqual(generated_lesson_plan.resources,expected_lesson_plan.resources)
			self.check_topics(generated_lesson_plan.topics,expected_lesson_plan.topics)
		gclogger.info('--Unit test of calender-lessonplan integration is passed--')

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
			if hasattr(generated_lesson_plan_sessions[index],'schedule') :
				self.check_schedule(generated_lesson_plan_sessions[index].schedule,expected_lesson_plan_sessions[index].schedule)

	def check_root_sessions(self,updated_lesson_plan_sessions,expected_lesson_plan_sessions) :
		for index in range(len(updated_lesson_plan_sessions)) :
			self.assertEqual(updated_lesson_plan_sessions[index].order_index,expected_lesson_plan_sessions[index].order_index)
			self.check_schedule(updated_lesson_plan_sessions[index].schedule,expected_lesson_plan_sessions[index].schedule)

	def check_schedule(self,generated_lesson_plan_shedule,expected_lesson_plan_shedule) :
		self.assertEqual(generated_lesson_plan_shedule.start_time,expected_lesson_plan_shedule.start_time)
		self.assertEqual(generated_lesson_plan_shedule.end_time,expected_lesson_plan_shedule.end_time)




	def get_generated_lesson_plans_dict(self,generated_lesson_plan_list) :
		generated_lesson_plans_dict = {}
		for generated_lesson_plan in generated_lesson_plan_list :
			generated_lesson_plans_dict[generated_lesson_plan.lesson_plan_key] =  generated_lesson_plan
		return generated_lesson_plans_dict


	def get_expected_lesson_plan_list(self) :
		expected_lesson_plan_list = []
		with open('tests/unit/fixtures/calendar-to-lessonplan-fixtures/expected_lesson_plan_single_cal.json', 'r') as lesson_plan_list:
			expected_lessonplan_json_list = json.load(lesson_plan_list)
			for expected_lesson_plan in expected_lessonplan_json_list :
				expected_lesson_plan_list.append(lessonplan.LessonPlan(expected_lesson_plan))
		return expected_lesson_plan_list


	def get_current_lesson_plan_list(self) :
		current_lesson_plan_list = []
		with open('tests/unit/fixtures/calendar-to-lessonplan-fixtures/current_lesson_plan_single_session.json', 'r') as lesson_plan_list:
			current_lessonplan_json_list = json.load(lesson_plan_list)
			for current_lesson_plan in current_lessonplan_json_list :
				current_lesson_plan_list.append(lessonplan.LessonPlan(current_lesson_plan))
		return current_lesson_plan_list



	def get_current_class_calendar(self) :
	    with open('tests/unit/fixtures/calendar-to-lessonplan-fixtures/current_class_calendar.json', 'r') as calendar_json:
		    class_calendar_dict = json.load(calendar_json)
		    class_calendar = calendar.Calendar(class_calendar_dict)
	    return class_calendar

	



if __name__ == '__main__':
    unittest.main()
