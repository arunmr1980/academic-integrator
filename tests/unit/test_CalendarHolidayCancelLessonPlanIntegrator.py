import unittest
import json
from academics.TimetableIntegrator import *
from academics.academic import AcademicConfiguration as academic_config
import academics.timetable.TimeTable as ttable
from academics.logger import GCLogger as gclogger
import academics.calendar.Calendar as calendar
import academics.lessonplan.LessonPlan as lessonplan
from academics.calendar.CalendarLessonPlanIntegrator import integrate_calendar_to_lesson_plan
from academics.lessonplan.LessonplanIntegrator import cancelled_holiday_calendar_to_lessonplan_integrator
import operator
import pprint
pp = pprint.PrettyPrinter(indent=4)



class CalendarHolidayCancelLesssonPlanlIntegratorTest(unittest.TestCase):
	def test_lessonplan(self) :
		calendar_key ='test-key'
		holiday_cancel_calendars = self.get_holiday_cancel_calendars()
		class_cls_session_calendars = self.get_class_cls_session_calendars()
		calendar = self.get_holiday_cancelled_calendar(calendar_key,holiday_cancel_calendars)
		day_code = findDay(calendar.calendar_date).upper()[0:3]
		subscriber_key = calendar.subscriber_key
		current_lesson_plan_list = self.get_current_lesson_plan_list()
		expected_lesson_plan_list = self.get_expected_lesson_plan_list()
		if calendar.subscriber_type == 'CLASS-DIV' :
			class_key = subscriber_key[:-2]
			division = subscriber_key[-1:]
			class_calendar = self.get_class_calendar_by_subscriber_key(subscriber_key,class_cls_session_calendars)
			for current_lessonplan in current_lesson_plan_list :
				if current_lessonplan.class_key == class_key and current_lessonplan.division == division :

					updated_lessonplan = cancelled_holiday_calendar_to_lessonplan_integrator(current_lessonplan,class_calendar,day_code)

					self.check_lesson_plans(updated_lessonplan,expected_lesson_plan_list)
		else :
			for current_lessonplan in current_lesson_plan_list :
				subscriber_key = current_lessonplan.class_key + '-' + current_lessonplan.division
				class_calendar = self.get_class_calendar_by_subscriber_key(subscriber_key,class_cls_session_calendars)
				updated_lessonplan = cancelled_holiday_calendar_to_lessonplan_integrator(current_lessonplan,class_calendar,day_code)
				lp = lessonplan.LessonPlan(None)
				updated_lessonplan_dict = lp.make_lessonplan_dict(updated_lessonplan)
				pp.pprint(updated_lessonplan_dict)
				self.check_lesson_plans(updated_lessonplan,expected_lesson_plan_list)


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

		gclogger.info(" <<<-------------------------------- UNIT TEST PASSED FOR "+ str(updated_lesson_plan.lesson_plan_key)+" ------------------------------>>> ")

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
			self.check_schedule(updated_lesson_plan_sessions[index].schedule,expected_lesson_plan_sessions[index].schedule)
	def check_root_sessions(self,updated_lesson_plan_sessions,expected_lesson_plan_sessions) :
		for index in range(len(updated_lesson_plan_sessions)) :
			self.assertEqual(updated_lesson_plan_sessions[index].order_index,expected_lesson_plan_sessions[index].order_index)
			self.check_schedule(updated_lesson_plan_sessions[index].schedule,expected_lesson_plan_sessions[index].schedule)

	def check_schedule(self,updated_lesson_plan_shedule,expected_lesson_plan_shedule) :
		self.assertEqual(updated_lesson_plan_shedule.start_time,expected_lesson_plan_shedule.start_time)
		self.assertEqual(updated_lesson_plan_shedule.end_time,expected_lesson_plan_shedule.end_time)





	def get_schedule(self,holiday_period_list,schedule,date) :
		for period in holiday_period_list :
			standard_start_time = get_standard_time(period.start_time,date)
			standard_end_time = get_standard_time(period.end_time,date)
			if standard_start_time == schedule.start_time and standard_end_time ==schedule.end_time :
				return schedule


	def get_class_calendar_by_subscriber_key(self,subscriber_key,class_cls_session_calendars) :
		for class_calendar in class_cls_session_calendars :
			if class_calendar.subscriber_key == subscriber_key :
				return class_calendar




	def get_current_lesson_plan_list(self) :
		current_lesson_plan_list = []
		with open('tests/unit/fixtures/calendar-lessonplan-fixtures/current_lessonplan.json', 'r') as current_lessonplan:
			current_lessonplan_dict_list = json.load(current_lessonplan)
		for current_lessonplan_dict in current_lessonplan_dict_list :
			current_lesson_plan_list.append(lessonplan.LessonPlan(current_lessonplan_dict))
		return current_lesson_plan_list

	def get_expected_lesson_plan_list(self) :
		expected_lesson_plan_list = []
		with open('tests/unit/fixtures/calendar-lessonplan-fixtures/expected_lessonplan.json', 'r') as expected_lessonplan:
			expected_lessonplan_dict_list = json.load(expected_lessonplan)
		for expected_lessonplan_dict in expected_lessonplan_dict_list :
			expected_lesson_plan_list.append(lessonplan.LessonPlan(expected_lessonplan_dict))
		return expected_lesson_plan_list




	def get_holiday_cancelled_calendar(self,calendar_key,holiday_calendars) :
		for calendar in holiday_calendars :
			if calendar.calendar_key == calendar_key :
				return calendar

	def get_holiday_cancel_calendars(self):
		holiday_cancelled_calendars_list = []
		with open('tests/unit/fixtures/calendar-lessonplan-fixtures/holiday_cancelled_calendars.json', 'r') as calendars:
			holiday_cancel_calendars = json.load(calendars)
		for cal in holiday_cancel_calendars :
			holiday_cancelled_calendars_list.append(calendar.Calendar(cal))
		return holiday_cancelled_calendars_list

	def get_class_cls_session_calendars(self):
		class_cls_session_calendars_list = []
		with open('tests/unit/fixtures/calendar-lessonplan-fixtures/class_cls_session_calendars.json', 'r') as calendars:
			class_cls_session_calendars = json.load(calendars)
		for cal in class_cls_session_calendars :
			class_cls_session_calendars_list.append(calendar.Calendar(cal))
		return class_cls_session_calendars_list



if __name__ == '__main__':
	unittest.main()
