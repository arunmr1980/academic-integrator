import unittest
import json
from academics.TimetableIntegrator import integrate_class_timetable,integrate_teacher_timetable
from academics.timetable import AcademicConfiguration as academic_config
import academics.timetable.TimeTable as ttable
from academics.logger import GCLogger as gclogger
import academics.calendar.Calendar as calendar
import academics.lessonplan.LessonPlan as lpnr
from academics.calendar.CalendarIntegrator import *
import pprint
import copy 
import academics.timetable.KeyGeneration as key
pp = pprint.PrettyPrinter(indent=4)

class UpdatePeriodsIntegratorTest(unittest.TestCase):

		
	def test_calendars_and_lessonplans(self) :
		period_code = 'MON-3'
		time_table_key = "test-time-table-1"	
		updated_class_calendars_list =[]
		updated_teacher_calendars_list =[]
		updated_lessonplan_list = []
		updated_class_calendar_subject_key_list = []
		updated_timetable = self.get_updated_timetable()
		school_key = updated_timetable.school_key
		class_key = updated_timetable.class_key
		division = updated_timetable.division
		subscriber_key = class_key + '-' + division
		current_class_calendars = self.get_current_class_calendar_list()
		current_teacher_calendars = self.get_current_teacher_calendar_list()
		current_lessonplans = self.get_current_lessonplans()
		expected_class_calendars = self.get_expected_class_calendar_list()
		expected_teacher_calendars = self.get_expected_teacher_calendar_list()
		expected_lessonplans = self.get_expected_lessonplan_list()
		current_class_cals = copy.deepcopy(current_class_calendars)

		current_class_calendars_with_day_code = get_current_class_calendars_with_day_code(period_code[:3],current_class_calendars)
		current_class_calendars_with_day_code_copy = copy.deepcopy(current_class_calendars_with_day_code)
		updated_timetable_period = get_updated_period_from_timetable(period_code,updated_timetable)


		for current_class_calendar in current_class_calendars_with_day_code :
			event = get_event_with_period_code(current_class_calendar,period_code)
			existing_event = copy.deepcopy(event)
			updated_class_calendar = update_event(event,current_class_calendar,updated_timetable_period) 
			if updated_class_calendar is not None :
				updated_class_calendars_list.append(updated_class_calendar)

			updated_previous_teacher_calendar = self.update_previous_teacher_calendar(existing_event,updated_class_calendar,current_teacher_calendars)
			if updated_previous_teacher_calendar is not None :
				updated_teacher_calendars_list.append(updated_previous_teacher_calendar)

			updated_new_teacher_calendars = self.update_new_teacher_calendars(updated_class_calendar,period_code,current_teacher_calendars,updated_timetable_period)
			if len(updated_new_teacher_calendars) > 0 :
				for updated_new_teacher_calendar in updated_new_teacher_calendars :
					updated_teacher_calendars_list.append(updated_new_teacher_calendar)

			updated_previous_subject_lessonplan = update_previous_subject_lessonplan(existing_event,current_lessonplans, updated_class_calendar)
			if updated_previous_subject_lessonplan is not None :
				updated_lessonplan_list.append(updated_previous_subject_lessonplan)

			updated_new_subject_lessonplans = update_new_subject_lessonplans(updated_timetable_period, current_lessonplans, updated_class_calendar)
			if len(updated_new_subject_lessonplans) > 0 :
				for updated_new_subject_lessonplan in updated_new_subject_lessonplans :	
					updated_lessonplan_list.append(updated_new_subject_lessonplan)


		for updated_class_calendar in updated_class_calendars_list :
			cal = calendar.Calendar(None)
			calendar_dict = cal.make_calendar_dict(updated_class_calendar)
			pp.pprint(calendar_dict)
			self.check_class_calendars(updated_class_calendar,expected_class_calendars)	
			gclogger.info("-----[ Unit Test ] Class calendar test passed for ----" + updated_class_calendar.calendar_key + "-----------------")

		for updated_teacher_calendar in updated_teacher_calendars_list :
			cal = calendar.Calendar(None)
			calendar_dict = cal.make_calendar_dict(updated_teacher_calendar)
			pp.pprint(calendar_dict)
			self.check_teacher_calendars(updated_teacher_calendar,expected_teacher_calendars)	
			gclogger.info("-----[ Unit Test ] Teacher calendar test passed for ----" + updated_teacher_calendar.calendar_key + "-----------------")


		for updated_lessonplan in updated_lessonplan_list :
			lp = lpnr.LessonPlan(None)
			updated_lessonplan_dict = lp.make_lessonplan_dict(updated_lessonplan)
			pp.pprint(updated_lessonplan_dict)
			self.check_lesson_plans(updated_lessonplan,expected_lessonplans)
			gclogger.info("-----[ Unit Test ] LessonPlan test passed for ----" + updated_lessonplan.lesson_plan_key + "-----------------")


	def update_previous_teacher_calendar(self,existing_event,current_class_calendar,current_teacher_calendars) :
		subscriber_key = get_employee_key(existing_event.params)
		previous_teacher_calendar = self.get_previous_teacher_calendar(subscriber_key,current_class_calendar,current_teacher_calendars)
		updated_previous_teacher_calendar = update_current_teacher_calendar(existing_event,previous_teacher_calendar,current_class_calendar)
		return updated_previous_teacher_calendar



	def get_previous_teacher_calendar(self,subscriber_key,current_class_calendar,current_teacher_calendars) :
		print(subscriber_key,"EXISTING TEACHER CALENDAR KEY -------------")
		for current_teacher_calendar in current_teacher_calendars :
			if current_teacher_calendar.subscriber_key == subscriber_key :
				return current_teacher_calendar


	def get_existing_teacher_calendar(self,subscriber_key,current_teacher_calendars) :
		for current_teacher_calendar in current_teacher_calendars :
			if current_teacher_calendar.subscriber_key == subscriber_key :
				return current_teacher_calendar

	def update_new_teacher_calendars(self,updated_class_calendar, period_code,current_teacher_calendars,updated_timetable_period) :
		updated_new_teacher_calendars_list = []
		if hasattr(updated_timetable_period,"employees") :
			for employee in updated_timetable_period.employees :
				subscriber_key = employee.employee_key
				subject_key = employee.subject_key
				new_teacher_calendar = self.Get_teacher_calendar(updated_class_calendar,subscriber_key,current_teacher_calendars)
				updated_class_calendar_event = get_updated_class_calendar_event(subscriber_key,subject_key,period_code,updated_class_calendar)
				updated_new_teacher_calendar = update_teacher_calendar_with_new_event(new_teacher_calendar,updated_class_calendar_event,updated_class_calendar)
				updated_new_teacher_calendars_list.append(updated_new_teacher_calendar)
		else :
			updated_class_calendar_events = get_period_code_events(updated_class_calendar, period_code)
			subscriber_key = get_employee_key(updated_class_calendar_events[0].params)
			new_teacher_calendar = self.Get_teacher_calendar(updated_class_calendar,subscriber_key,current_teacher_calendars)
			updated_new_teacher_calendar = update_teacher_calendar_with_new_event(new_teacher_calendar,updated_class_calendar_events[0],updated_class_calendar)
			updated_new_teacher_calendars_list.append(updated_new_teacher_calendar)
		return updated_new_teacher_calendars_list

	
	def Get_teacher_calendar(self,updated_class_calendar,subscriber_key,current_teacher_calendars) :
		existing_teacher_calendar = self.get_existing_teacher_calendar(subscriber_key,current_teacher_calendars)
		if existing_teacher_calendar is not None :
			return existing_teacher_calendar
		else :
			employee_calendar = generate_employee_calendar(subscriber_key,updated_class_calendar)
			return employee_calendar

	def check_teacher_calendars(self,updated_teacher_calendar,expected_teacher_calendars_list) :
		for expected_teacher_calendar in expected_teacher_calendars_list :
			if updated_teacher_calendar.calendar_key == expected_teacher_calendar.calendar_key :
				self.assertEqual(expected_teacher_calendar.institution_key,updated_teacher_calendar.institution_key )
				self.assertEqual(expected_teacher_calendar.calendar_date,updated_teacher_calendar.calendar_date )
				self.assertEqual(expected_teacher_calendar.subscriber_key,updated_teacher_calendar.subscriber_key )
				self.assertEqual(expected_teacher_calendar.subscriber_type,updated_teacher_calendar.subscriber_type )
				self.check_events_teacher_calendar(expected_teacher_calendar.events,updated_teacher_calendar.events)

	def check_events_teacher_calendar(self,expected_teacher_calendar_events,updated_teacher_calendar_events) :
		for index in range(0,len(expected_teacher_calendar_events)) :
			self.assertEqual(expected_teacher_calendar_events[index].event_code , updated_teacher_calendar_events[index].event_code)
			self.assertEqual(expected_teacher_calendar_events[index].ref_calendar_key , updated_teacher_calendar_events[index].ref_calendar_key)

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
			if hasattr(updated_lesson_plan_sessions[index],'schedule') :
				self.check_schedule(updated_lesson_plan_sessions[index].schedule,expected_lesson_plan_sessions[index].schedule)

	def check_root_sessions(self,updated_lesson_plan_sessions,expected_lesson_plan_sessions) :
		for index in range(len(updated_lesson_plan_sessions)) :
			self.assertEqual(updated_lesson_plan_sessions[index].order_index,expected_lesson_plan_sessions[index].order_index)
			if hasattr(updated_lesson_plan_sessions[index],'schedule') :
				self.check_schedule(updated_lesson_plan_sessions[index].schedule,expected_lesson_plan_sessions[index].schedule)

	def check_schedule(self,updated_lesson_plan_shedule,expected_lesson_plan_shedule) :
		self.assertEqual(updated_lesson_plan_shedule.start_time,expected_lesson_plan_shedule.start_time)
		self.assertEqual(updated_lesson_plan_shedule.end_time,expected_lesson_plan_shedule.end_time)

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

	
	def get_current_lessonplans(self) :
		current_lesson_plan_list =[]
		with open('tests/unit/fixtures/elective-subject-update-unassign-period-fixtures/current_lessonplans.json', 'r') as lesson_plan_list:
			current_lessonplan_json_list = json.load(lesson_plan_list)
			for current_lesson_plan in current_lessonplan_json_list :
				current_lesson_plan_list.append(lpnr.LessonPlan(current_lesson_plan))
		return current_lesson_plan_list

	def get_expected_lessonplan_list(self) :
		expected_lesson_plan_list =[]
		with open('tests/unit/fixtures/elective-subject-update-unassign-period-fixtures/expected_lessonplans.json', 'r') as lesson_plan_list:
			expected_lessonplan_json_list = json.load(lesson_plan_list)
			for expected_lesson_plan in expected_lessonplan_json_list :
				expected_lesson_plan_list.append(lpnr.LessonPlan(expected_lesson_plan))
		return expected_lesson_plan_list

	def get_updated_timetable(self):
		with open('tests/unit/fixtures/elective-subject-update-unassign-period-fixtures/updated_timetable.json', 'r') as timetable:
			timetable = json.load(timetable)
		return ttable.TimeTable(timetable)

	
	def get_current_class_calendar_list(self) :
		current_class_calendars = []
		with open('tests/unit/fixtures/elective-subject-update-unassign-period-fixtures/current_class_calendars.json', 'r') as calendar_list:
			class_calendars_dict = json.load(calendar_list)
		for class_cal in class_calendars_dict :
			current_class_calendars.append(calendar.Calendar(class_cal))
		return current_class_calendars

	def get_current_teacher_calendar_list(self) :
		current_teacher_calendars = []
		with open('tests/unit/fixtures/elective-subject-update-unassign-period-fixtures/current_teacher_calendars.json', 'r') as calendar_list:
			teacher_calendars_dict = json.load(calendar_list)
		for teacher_cal in teacher_calendars_dict :
			current_teacher_calendars.append(calendar.Calendar(teacher_cal))
		return current_teacher_calendars


	def get_expected_teacher_calendar_list(self) :
		expected_teacher_calendars = []
		with open('tests/unit/fixtures/elective-subject-update-unassign-period-fixtures/expected_teacher_calendars.json', 'r') as calendar_list:
			teacher_calendars_dict = json.load(calendar_list)
		for teacher_cal in teacher_calendars_dict :
			expected_teacher_calendars.append(calendar.Calendar(teacher_cal))
		return expected_teacher_calendars


	def get_expected_class_calendar_list(self) :
		expected_class_calendars = []
		with open('tests/unit/fixtures/elective-subject-update-unassign-period-fixtures/expected_class_calendars.json', 'r') as calendar_list:
			class_calendars_dict = json.load(calendar_list)
		for class_cal in class_calendars_dict :
			expected_class_calendars.append(calendar.Calendar(class_cal))
		return expected_class_calendars

if __name__ == '__main__':
	unittest.main()
