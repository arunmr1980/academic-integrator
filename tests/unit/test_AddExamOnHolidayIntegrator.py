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
import academics.exam.Exam as exam
import pprint
import copy
import academics.timetable.KeyGeneration as key
pp = pprint.PrettyPrinter(indent=4)

class AddExamIntegratorTest(unittest.TestCase):


	def test_calendars_and_lessonplan(self) :
		series_code = "NEG111"
		class_key = "8B1B22E72AE"
		division = "A"
		subscriber_key = class_key + '-' + division
		updated_class_calendars_list = []
		updated_teacher_calendars_list = []
		updated_lessonplans_list = []
		removed_events = []

		current_class_calendars = self.get_current_class_calendars_list()
		expected_class_calendars_list = self.get_expected_class_calendars_list()
		expected_teacher_calendars_list = self.get_expected_teacher_calendars_list()
		expected_lessonplans_list = self.get_expected_lessonplans_list()
		current_teacher_calendars_list = self.get_current_teacher_calendars_list()
		current_lessonplans_list = self.get_current_lessonplans_list()
		current_class_calendars_list = self.current_class_calendars_perticular_class(subscriber_key,current_class_calendars)
		current_cls_calendars = copy.deepcopy(current_class_calendars_list)
		exams = self.get_exams_list()
		exams_list = self.perticular_exams_for_perticular_class(exams,class_key,division,series_code)
		updated_class_calendars_list = exam_integrator.integrate_class_calendars_on_add_exams(updated_class_calendars_list,exams_list,current_class_calendars_list,removed_events)
		exam_integrator.integrate_teacher_cals_and_lessonplans_on_add_exam(
							updated_class_calendars_list,
							updated_teacher_calendars_list,
							updated_lessonplans_list,
							current_class_calendars_list,
							current_teacher_calendars_list,
							current_lessonplans_list,
							exams_list,
							removed_events
							)



		for updated_class_calendar in updated_class_calendars_list :
			cal = calendar.Calendar(None)
			class_calendar_dict = cal.make_calendar_dict(updated_class_calendar)
			pp.pprint(class_calendar_dict)
			self.check_class_calendars(updated_class_calendar,expected_class_calendars_list)


		for updated_teacher_calendar in updated_teacher_calendars_list :
			cal = calendar.Calendar(None)
			teacher_calendar_dict = cal.make_calendar_dict(updated_teacher_calendar)
			pp.pprint(teacher_calendar_dict)
			self.check_teacher_calendars(updated_teacher_calendar,expected_teacher_calendars_list)

		for updated_lessonplan in updated_lessonplans_list :

			lp = lpnr.LessonPlan(None)
			updated_lessonplan_dict = lp.make_lessonplan_dict(updated_lessonplan)
			pp.pprint(updated_lessonplan_dict)
			self.check_lesson_plans(updated_lessonplan,expected_lessonplans_list)




	def current_class_calendars_perticular_class(self,subscriber_key,current_class_calendars) :
		current_class_calendars_list =[]
		for current_class_calendar in current_class_calendars:
			if current_class_calendar.subscriber_key == subscriber_key :
				current_class_calendars_list.append(current_class_calendar)
		return current_class_calendars_list

	def perticular_exams_for_perticular_class(self,exams,class_key,division,series_code) :
		exams_list =[]
		for exam in exams :
			if exam.division == division and exam.class_key == class_key and exam.series_code == series_code :
				exams_list.append(exam)
		return exams_list
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




	def get_current_lessonplans_list(self) :
		current_lessonplans = []
		with open('tests/unit/fixtures/add-exam-on-holiday-fixtures/current_lessonplans_list.json', 'r') as lessonplans_list:
			lessonplans_list_dict = json.load(lessonplans_list)
		for lessonplan in lessonplans_list_dict :
			current_lessonplans.append(lpnr.LessonPlan(lessonplan))
		return current_lessonplans

	def get_current_teacher_calendars_list(self) :
		current_teacher_calendars = []
		with open('tests/unit/fixtures/add-exam-on-holiday-fixtures/current_teacher_calendars_list.json', 'r') as calendar_list:
			class_calendars_dict = json.load(calendar_list)
		for class_cal in class_calendars_dict :
			current_teacher_calendars.append(calendar.Calendar(class_cal))
		return current_teacher_calendars

	def get_current_class_calendars_list(self) :
		current_class_calendars = []
		with open('tests/unit/fixtures/add-exam-on-holiday-fixtures/current_class_calendars_list.json', 'r') as calendar_list:
			class_calendars_dict = json.load(calendar_list)
		for class_cal in class_calendars_dict :
			current_class_calendars.append(calendar.Calendar(class_cal))
		return current_class_calendars

	def get_expected_class_calendars_list(self) :
		expected_class_calendars = []
		with open('tests/unit/fixtures/add-exam-on-holiday-fixtures/expected_class_calendars_list.json', 'r') as calendar_list:
			class_calendars_dict = json.load(calendar_list)
		for class_cal in class_calendars_dict :
			expected_class_calendars.append(calendar.Calendar(class_cal))
		return expected_class_calendars

	def get_expected_teacher_calendars_list(self) :
		expected_teacher_calendars = []
		with open('tests/unit/fixtures/add-exam-on-holiday-fixtures/expected_teacher_calendars_list.json', 'r') as calendar_list:
			teacher_calendars_dict = json.load(calendar_list)
		for teacher_cal in teacher_calendars_dict :
			expected_teacher_calendars.append(calendar.Calendar(teacher_cal))
		return expected_teacher_calendars

	def get_expected_lessonplans_list(self) :
		expected_lessonplans = []
		with open('tests/unit/fixtures/add-exam-on-holiday-fixtures/expected_lessonplans_list.json', 'r') as lessonplan_list:
			lessonplans_dict = json.load(lessonplan_list)
		for lessonplan in lessonplans_dict :
			expected_lessonplans.append(lpnr.LessonPlan(lessonplan))
		return expected_lessonplans

	def get_exams_list(self) :
		exams_list = []
		with open('tests/unit/fixtures/add-exam-on-holiday-fixtures/exams_list.json', 'r') as exam_list:
			exams_list_dict = json.load(exam_list)
		for exam_dict in exams_list_dict :
			exams_list.append(exam.Exam(exam_dict))
		return exams_list



if __name__ == '__main__':
	unittest.main()
