import unittest
import json
from academics.TimetableIntegrator import integrate_class_timetable,integrate_teacher_timetable
from academics.academic import AcademicConfiguration as academic_config
import academics.timetable.TimeTable as ttable
from academics.logger import GCLogger as gclogger
import academics.calendar.Calendar as calendar
from academics.calendar.CalendarIntegrator import integrate_update_period_calendars_and_lessonplans
import academics.timetable.TimeTableDBService as timetable_service
import academics.calendar.CalendarDBService as calendar_service
from academics.lessonplan import LessonplanDBService as lessonplan_service
import academics.lessonplan.LessonPlan as lpnr
import pprint
import academics.timetable.KeyGeneration as key
pp = pprint.PrettyPrinter(indent=4)

class UpdatePeriodsIntegratorTest(unittest.TestCase):
	def setUp(self) :
		updated_timetable = self.get_timetable_from_json()
		response = timetable_service.create_timetable(updated_timetable)
		gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + '--------- A time table uploaded -------- '+str(updated_timetable['time_table_key']))

		current_class_calendars = self.get_current_class_calendar_list_from_json()
		for calendar in current_class_calendars :
			response = calendar_service.add_or_update_calendar(calendar)
			gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' ------- A class calendar uploaded --------- '+str(calendar['calendar_key']))

		current_teacher_calendars = self.get_current_teacher_calendar_list_from_json()
		for calendar in current_teacher_calendars :
			response = calendar_service.add_or_update_calendar(calendar)
			gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' ------- A teacher calendar uploaded --------- '+str(calendar['calendar_key']))

		current_lessonplans = self.get_current_lessonplans_from_json()
		for current_lessonplan in current_lessonplans :
			response = lessonplan_service.create_lessonplan(current_lessonplan)
			gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' Current lesson plan uploaded '+str(current_lessonplan['lesson_plan_key']))

		
	def test_calendars_and_lessonplans(self) :
		period_code = 'MON-3'
		time_table_key = "time-table-3"	
		integrate_update_period_calendars_and_lessonplans(period_code,time_table_key)
		updated_timetable = timetable_service.get_time_table(time_table_key)
		class_key = updated_timetable.class_key
		division = updated_timetable.division
		school_key = updated_timetable.school_key 
		subscriber_key = class_key + '-' + division
		updated_teacher_calendars = calendar_service.get_all_calendars_by_school_key_and_type(school_key,'EMPLOYEE')
		updated_class_calendars = calendar_service.get_all_calendars_by_key_and_type(subscriber_key,'CLASS-DIV')
		updated_lessonplan_list = lessonplan_service.get_lesson_plan_list(class_key,division)	
		expected_teacher_calendars = self.get_expected_teacher_calendar_list()
		expected_class_calendars = self.get_expected_class_calendar_list()
		expected_lessonplans = self.get_expected_lessonplan_list()
		expected_teacher_calendars_dict = self.make_expected_teacher_calendars_dict(expected_teacher_calendars)
		for updated_teacher_calendar in updated_teacher_calendars :

			cal = calendar.Calendar(None)
			calendar_dict = cal.make_calendar_dict(updated_teacher_calendar)
			pp.pprint(calendar_dict)

			calendar_date = updated_teacher_calendar.calendar_date
			subscriber_key = updated_teacher_calendar.subscriber_key
			teacher_calendar_key = calendar_date + subscriber_key
			expected_teacher_calendar = expected_teacher_calendars_dict[teacher_calendar_key]
			self.assertEqual(expected_teacher_calendar.institution_key,updated_teacher_calendar.institution_key )
			self.assertEqual(expected_teacher_calendar.calendar_date,updated_teacher_calendar.calendar_date )
			self.assertEqual(expected_teacher_calendar.subscriber_key,updated_teacher_calendar.subscriber_key )
			self.assertEqual(expected_teacher_calendar.subscriber_type,updated_teacher_calendar.subscriber_type )
			gclogger.info("-----[ Integration Test ] Teacher calendar test passed for ------" + updated_teacher_calendar.calendar_key + "-----------------")

		for updated_class_calendar in updated_class_calendars :

			cal = calendar.Calendar(None)
			calendar_dict = cal.make_calendar_dict(updated_class_calendar)
			pp.pprint(calendar_dict)

			self.check_class_calendars(updated_class_calendar,expected_class_calendars)	
			gclogger.info("-----[ Integration Test ] Class calendar test passed for ----" + updated_class_calendar.calendar_key + "-----------------")

		for updated_lessonplan in updated_lessonplan_list :

			lp = lpnr.LessonPlan(None)
			updated_lessonplan_dict = lp.make_lessonplan_dict(updated_lessonplan)
			pp.pprint(updated_lessonplan_dict)

			self.check_lesson_plans(updated_lessonplan,expected_lessonplans)




	def check_lesson_plans(self,updated_lesson_plan,expected_lessonplans) :
		for expected_lessonplan in expected_lessonplans :
			if expected_lessonplan.lesson_plan_key == updated_lesson_plan.lesson_plan_key :

				self.assertEqual(updated_lesson_plan.lesson_plan_key,expected_lessonplan.lesson_plan_key)
				self.assertEqual(updated_lesson_plan.class_key,expected_lessonplan.class_key)
				self.assertEqual(updated_lesson_plan.division,expected_lessonplan.division)
				self.assertEqual(updated_lesson_plan.subject_code,expected_lessonplan.subject_code)
				self.assertEqual(updated_lesson_plan.resources,expected_lessonplan.resources)
				self.check_topics(updated_lesson_plan.topics,expected_lessonplan.topics)

		gclogger.info(" -------------------------------- INTEGRATION TEST PASSED FOR LESSONPLAN -----"+ str(updated_lesson_plan.lesson_plan_key)+" ------------------------------ ")

	def check_topics(self,updated_lesson_plan_topics,expected_lesson_plan_topics):
		for index in range(0,len(updated_lesson_plan_topics)) :
			self.assertEqual(updated_lesson_plan_topics[index].code,expected_lesson_plan_topics[index].code)
			self.assertEqual(updated_lesson_plan_topics[index].name,expected_lesson_plan_topics[index].name)
			self.assertEqual(updated_lesson_plan_topics[index].order_index,expected_lesson_plan_topics[index].order_index)
			self.check_topic(updated_lesson_plan_topics[index].topics,expected_lesson_plan_topics[index].topics)

	def check_topic(self,updated_lesson_plan_topic,expected_lesson_plan_topic):
		for index in range(0,len(updated_lesson_plan_topic) - 1 ) :
			self.assertEqual(updated_lesson_plan_topic[index].code,expected_lesson_plan_topic[index].code)
			self.assertEqual(updated_lesson_plan_topic[index].description,expected_lesson_plan_topic[index].description)
			self.assertEqual(updated_lesson_plan_topic[index].name,expected_lesson_plan_topic[index].name)
			self.assertEqual(updated_lesson_plan_topic[index].order_index,expected_lesson_plan_topic[index].order_index)
			self.assertEqual(updated_lesson_plan_topic[index].resources,expected_lesson_plan_topic[index].resources)
			self.check_sessions(updated_lesson_plan_topic[index].sessions,expected_lesson_plan_topic[index].sessions)

	def check_sessions(self,updated_lesson_plan_sessions,expected_lesson_plan_sessions) :
		for index in range(len(updated_lesson_plan_sessions) - 1) :
			self.assertEqual(updated_lesson_plan_sessions[index].code,expected_lesson_plan_sessions[index].code)
			self.assertEqual(updated_lesson_plan_sessions[index].completion_datetime,expected_lesson_plan_sessions[index].completion_datetime)
			self.assertEqual(updated_lesson_plan_sessions[index].completion_status,expected_lesson_plan_sessions[index].completion_status)
			self.assertEqual(updated_lesson_plan_sessions[index].name,expected_lesson_plan_sessions[index].name)
			self.assertEqual(updated_lesson_plan_sessions[index].order_index,expected_lesson_plan_sessions[index].order_index)
			self.check_schedule(updated_lesson_plan_sessions[index].schedule,expected_lesson_plan_sessions[index].schedule)

	def check_schedule(self,updated_lesson_plan_shedule,expected_lesson_plan_shedule) :
		self.assertEqual(updated_lesson_plan_shedule.start_time,expected_lesson_plan_shedule.start_time)
		self.assertEqual(updated_lesson_plan_shedule.end_time,expected_lesson_plan_shedule.end_time)


	def tearDown(self) :
		updated_timetable = timetable_service.get_time_table("time-table-3")
		class_key = updated_timetable.class_key
		division = updated_timetable.division
		school_key = updated_timetable.school_key 
		subscriber_key = class_key + '-' + division
		updated_class_calendars = calendar_service.get_all_calendars_by_key_and_type(subscriber_key,'CLASS-DIV')
		for updated_calendar in updated_class_calendars :
			response = calendar_service.delete_calendar(updated_calendar.calendar_key)
			gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' ------- A updated class calendar deleted --------- '+str(updated_calendar.calendar_key))

		updated_teacher_calendars = calendar_service.get_all_calendars_by_school_key_and_type(school_key,'EMPLOYEE')
		for updated_calendar in updated_teacher_calendars :
			response = calendar_service.delete_calendar(updated_calendar.calendar_key)
			gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' ------- A updated teacher calendar deleted --------- '+str(updated_calendar.calendar_key))

		updated_lessonplan_list = lessonplan_service.get_lesson_plan_list(class_key,division)
		for updated_lessonplan in updated_lessonplan_list :
			lessonplan_service.delete_lessonplan(updated_lessonplan.lesson_plan_key)
			gclogger.info("--------------- Test Lesson Plan deleted --------- " + updated_lessonplan.lesson_plan_key + "-----------------")

		timetable_service.delete_timetable(updated_timetable.time_table_key)
		gclogger.info("--------------- Test Timetable deleted  " + updated_timetable.time_table_key+"  -----------------")


	
	def make_expected_teacher_calendars_dict(self,expected_teacher_calendars) :
		expected_teacher_calendars_dict = {}
		for expected_teacher_calendar in expected_teacher_calendars :
			calendar_date = expected_teacher_calendar.calendar_date
			subscriber_key = expected_teacher_calendar.subscriber_key
			teacher_calendar_key = calendar_date + subscriber_key
			expected_teacher_calendars_dict[teacher_calendar_key] = expected_teacher_calendar
		return expected_teacher_calendars_dict



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

	def get_current_class_calendar_list_from_json(self) :
		with open('tests/unit/fixtures/unassign-to-elective-period-fixtures/current_class_calendars.json', 'r') as calendar_list:
			current_class_calendar_list = json.load(calendar_list)
		return current_class_calendar_list

	def get_current_lessonplans_from_json(self) :
		with open('tests/unit/fixtures/unassign-to-elective-period-fixtures/current_lessonplans.json', 'r') as lessonplans:
			current_lessonplans = json.load(lessonplans)
		return current_lessonplans

	def get_current_teacher_calendar_list_from_json(self) :
		with open('tests/unit/fixtures/unassign-to-elective-period-fixtures/current_teacher_calendars.json', 'r') as calendar_list:
			current_teacher_calendar_list = json.load(calendar_list)
		return current_teacher_calendar_list

	def get_timetable_from_json(self) :
		with open('tests/unit/fixtures/unassign-to-elective-period-fixtures/updated_timetable.json', 'r') as calendar_list:
			timetable = json.load(calendar_list)
		return timetable

	def get_updated_timetable(self):
		with open('tests/unit/fixtures/unassign-to-elective-period-fixtures/updated_timetable.json', 'r') as timetable:
			timetable = json.load(timetable)
		return ttable.TimeTable(timetable)

	def get_current_class_calendar_list(self) :
		current_class_calendars = []
		with open('tests/unit/fixtures/unassign-to-elective-period-fixtures/current_class_calendars.json', 'r') as calendar_list:
			class_calendars_dict = json.load(calendar_list)
		for class_cal in class_calendars_dict :
			current_class_calendars.append(calendar.Calendar(class_cal))
		return current_class_calendars


	def get_current_teacher_calendar_list(self) :
		current_teacher_calendars = []
		with open('tests/unit/fixtures/unassign-to-elective-period-fixtures/current_teacher_calendars.json', 'r') as calendar_list:
			teacher_calendars_dict = json.load(calendar_list)
		for teacher_cal in teacher_calendars_dict :
			current_teacher_calendars.append(calendar.Calendar(teacher_cal))
		return current_teacher_calendars

	def get_expected_lessonplan_list(self) :
		expected_lesson_plan_list =[]
		with open('tests/unit/fixtures/unassign-to-elective-period-fixtures/expected_lessonplans.json', 'r') as lesson_plan_list:
			expected_lessonplan_json_list = json.load(lesson_plan_list)
			for expected_lesson_plan in expected_lessonplan_json_list :
				expected_lesson_plan_list.append(lpnr.LessonPlan(expected_lesson_plan))
		return expected_lesson_plan_list

	def get_expected_teacher_calendar_list(self) :
		expected_teacher_calendars = []
		with open('tests/unit/fixtures/unassign-to-elective-period-fixtures/expected_teacher_calendars.json', 'r') as calendar_list:
			teacher_calendars_dict = json.load(calendar_list)
		for teacher_cal in teacher_calendars_dict :
			expected_teacher_calendars.append(calendar.Calendar(teacher_cal))
		return expected_teacher_calendars


	def get_expected_class_calendar_list(self) :
		expected_class_calendars = []
		with open('tests/unit/fixtures/unassign-to-elective-period-fixtures/expected_class_calendars.json', 'r') as calendar_list:
			class_calendars_dict = json.load(calendar_list)
		for class_cal in class_calendars_dict :
			expected_class_calendars.append(calendar.Calendar(class_cal))
		return expected_class_calendars

if __name__ == '__main__':
    unittest.main()
