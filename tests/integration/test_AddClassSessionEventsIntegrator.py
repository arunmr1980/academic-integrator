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
import academics.calendar.CalendarIntegrator as calendar_integrator
import academics.lessonplan.LessonplanIntegrator as lessonplan_integrator
import academics.TimetableIntegrator as timetable_integrator
import academics.leave.LeaveIntegrator as leave_integrator
import pprint
import copy
import academics.timetable.KeyGeneration as key
pp = pprint.PrettyPrinter(indent=4)

class UpdateSubjectTeacherIntegratorTest(unittest.TestCase):

	def setUp(self) :
		updated_class_calendars = self.get_updated_class_calendars_list_json()
		for updated_calendar in updated_class_calendars :
			response = calendar_service.add_or_update_calendar(updated_calendar)
			gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' ------- A Updated class calendar uploaded --------- '+str(updated_calendar['calendar_key']))


		current_lessonplans = self.get_current_lessonplans_from_json()
		for current_lessonplan in current_lessonplans :
			response = lessonplan_service.create_lessonplan(current_lessonplan)
			gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + '------- Existing lesson plan uploaded -------- '+str(current_lessonplan['lesson_plan_key']))
		

	def test_lessonplans(self) :
		expected_lessonplans_list = self.get_expected_lessonplans_list()
		calendar_key = 'test-key-3'
		events = [
			{
	      		"event_code": "event-8" 
		    },
		    {
		    	"event_code": "event-9" 
		    }
		]
		lessonplan_integrator.integrate_add_class_session_events(calendar_key,events)
		updated_calendar = calendar_service.get_calendar(calendar_key)
		subscriber_key = updated_calendar.subscriber_key
		class_key = subscriber_key[:-2]
		division = subscriber_key[-1:]
		updated_lessonplan_list = lessonplan_service.get_lesson_plan_list(class_key, division)
		for updated_lessonplan in updated_lessonplan_list :		
			lp = lpnr.LessonPlan(None)
			updated_lessonplan_dict = lp.make_lessonplan_dict(updated_lessonplan)
			pp.pprint(updated_lessonplan_dict)
			self.check_lesson_plans(updated_lessonplan,expected_lessonplans_list)

	def tearDown(self) :
		calendar_key = 'test-key-3'
		updated_calendar = calendar_service.get_calendar(calendar_key)
		subscriber_key = updated_calendar.subscriber_key
		class_key = subscriber_key[:-2]
		division = subscriber_key[-1:]
		updated_lessonplan_list = lessonplan_service.get_lesson_plan_list(class_key,division)
		for updated_lessonplan in updated_lessonplan_list :
			lessonplan_service.delete_lessonplan(updated_lessonplan.lesson_plan_key)
			gclogger.info("--------------- Test Lesson Plan deleted --------- " + updated_lessonplan.lesson_plan_key + "-----------------")

		updated_class_calendars_list = calendar_service.get_all_calendars_by_key_and_type(subscriber_key,'CLASS-DIV')
		for updated_class_calendar in updated_class_calendars_list :
			calendar_service.delete_calendar(updated_class_calendar.calendar_key)
			gclogger.info("--------------- A updated class calendar deleted " + updated_class_calendar.calendar_key+" -----------------")

		
	



	def get_updated_class_calendar(self,updated_class_calendars_list,calendar_key) :
		for calendar in updated_class_calendars_list :
			if calendar.calendar_key == calendar_key :
				return calendar 

	def get_event_code_list(self,events,calendar_key,updated_calendar) :
		events_to_be_added = []
		for event in events :
			updated_event = self.get_added_event(event['event_code'],updated_calendar)
			events_to_be_added.append(updated_event)
		return events_to_be_added

	def get_added_event(self,event_code,updated_calendar) :
		for event in updated_calendar.events :
			if event.event_code == event_code :
				return event 
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

		gclogger.info(" --------------------------------  [Integration Test]  TEST PASSED FOR "+ str(updated_lesson_plan.lesson_plan_key)+" ------------------------------ ")

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

	def get_updated_class_calendars_list_json(self) :
		with open('tests/unit/fixtures/add-class-session-events-fixtures/updated_class_calendars_list.json', 'r') as calendar_list:
			updated_class_calendars = json.load(calendar_list)
		return updated_class_calendars

	def get_current_lessonplans_from_json(self) :
		with open('tests/unit/fixtures/add-class-session-events-fixtures/current_lessonplans_list.json', 'r') as lessonplans_list:
			current_lessonplans = json.load(lessonplans_list)
		return current_lessonplans

	def get_current_lessonplans_list(self) :
		current_lessonplans = []
		with open('tests/unit/fixtures/add-class-session-events-fixtures/current_lessonplans_list.json', 'r') as lessonplans_list:
			lessonplans_list_dict = json.load(lessonplans_list)
		for lessonplan in lessonplans_list_dict :
			current_lessonplans.append(lpnr.LessonPlan(lessonplan))
		return current_lessonplans

	def get_updated_class_calendars_list(self) :
		updated_class_calendars = []
		with open('tests/unit/fixtures/add-class-session-events-fixtures/updated_class_calendars_list.json', 'r') as calendar_list:
			class_calendars_dict = json.load(calendar_list)
		for class_cal in class_calendars_dict :
			updated_class_calendars.append(calendar.Calendar(class_cal))
		return updated_class_calendars

	def get_expected_lessonplans_list(self) :
		expected_lesson_plan_list =[]
		with open('tests/unit/fixtures/add-class-session-events-fixtures/expected_lessonplans_list.json', 'r') as lesson_plan_list:
			expected_lessonplan_json_list = json.load(lesson_plan_list)
			for expected_lesson_plan in expected_lessonplan_json_list :
				expected_lesson_plan_list.append(lpnr.LessonPlan(expected_lesson_plan))
		return expected_lesson_plan_list
		
if __name__ == '__main__':
	unittest.main()
