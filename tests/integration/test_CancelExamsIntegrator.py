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
import academics.exam.Exam as exam
import pprint
import copy
import academics.timetable.KeyGeneration as key
pp = pprint.PrettyPrinter(indent=4)

class CancelExamIntegratorTest(unittest.TestCase):
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
		

	def test_calendars_and_lessonplan(self) :
		
		exam_series = [
		      {
		        "classes": [
		          {
		            "class_key": "8B1B22E72AE",
		            "division": "A"
		          },
		          {
		            "class_key": "8B1B22E72AY",
		            "division": "B"
		          }
		        ],
		        "code": "NEG111",
		        "from_date": "2020-08-04",
		        "name": "June Series",
		        "to_date": "2020-08-10",
		      }
		]
		exam_integrator.integrate_cancel_exam(exam_series)
		expected_class_calendars_list = self.get_expected_class_calendars_list()
		expected_teacher_calendars_list = self.get_expected_teacher_calendars_list()
		expected_lessonplans_list = self.get_expected_lessonplans_list()

		exam_series = exam_integrator.make_exam_series_objects(exam_series)
		for clazz in exam_series.classes :
			division = clazz.division
			class_key = clazz.class_key
			subscriber_key = class_key + '-' + division
			updated_lessonplans_list = lessonplan_service.get_lesson_plan_list(class_key,division)
			for updated_lessonplan in updated_lessonplans_list :
				lp = lpnr.LessonPlan(None)
				updated_lessonplan_dict = lp.make_lessonplan_dict(updated_lessonplan)
				pp.pprint(updated_lessonplan_dict)
				self.check_lesson_plans(updated_lessonplan,expected_lessonplans_list)

			updated_class_calendars_list = calendar_service.get_all_calendars_by_key_and_type(subscriber_key,'CLASS-DIV')
			for updated_class_calendar in updated_class_calendars_list :
				cal = calendar.Calendar(None)
				calendar_dict = cal.make_calendar_dict(updated_class_calendar)
				pp.pprint(calendar_dict)
				self.check_class_calendars(updated_class_calendar,expected_class_calendars_list)

		updated_teacher_calendars_list = calendar_service.get_all_calendars_by_school_key_and_type('test-school-1','EMPLOYEE')
		


		for updated_teacher_calendar in updated_teacher_calendars_list :
			cal = calendar.Calendar(None)
			calendar_dict = cal.make_calendar_dict(updated_teacher_calendar)
			pp.pprint(calendar_dict)
			self.check_teacher_calendars(updated_teacher_calendar,expected_teacher_calendars_list)
			


	def tearDown(self) :
		exam_series = [
		      {
		        "classes": [
		          {
		            "class_key": "8B1B22E72AE",
		            "division": "A"
		          },
		          {
		            "class_key": "8B1B22E72AY",
		            "division": "B"
		          }
		        ],
		        "code": "NEG111",
		        "from_date": "2020-08-04",
		        "name": "June Series",
		        "to_date": "2020-08-10",
		      }
		]
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
		exam_series = exam_integrator.make_exam_series_objects(exam_series)
		for clazz in exam_series.classes :
			division = clazz.division
			class_key = clazz.class_key
			subscriber_key = class_key + '-' + division
			updated_lessonplans_list = lessonplan_service.get_lesson_plan_list(class_key,division)
			for updated_lessonplan in updated_lessonplans_list :
				lessonplan_service.delete_lessonplan(updated_lessonplan.lesson_plan_key)
				gclogger.info("--------------- Test Lesson Plan deleted --------- " + updated_lessonplan.lesson_plan_key + "-----------------")

		academic_service.delete_academic_config(academic_configuration.academic_config_key)
		gclogger.info("---------------Test Academic Configuration deleted  " + academic_configuration.academic_config_key + "-----------------")
			

	def make_exam_series_objects(self,exam_series) :
		exam_series = ExamSeries(exam_series[0])
		return exam_series

	def get_affected_class_calendars_list(self,classes,current_class_calendars,from_date,to_date) :
		current_class_calendars_list = []
		dates_list = timetable_integrator.get_dates(from_date,to_date)
		for date in dates_list :	
			for clazz in classes :
				division = clazz.division
				class_key = clazz.class_key
				subscriber_key = class_key + '-' + division
				current_class_calendar = self.get_calendar_by_date_and_key(subscriber_key,date,current_class_calendars)
				if current_class_calendar is not None :
					current_class_calendars_list.append(current_class_calendar)
		return current_class_calendars_list


	def get_calendar_by_date_and_key(self,subscriber_key,date,current_class_calendars) :
		for current_calendar in current_class_calendars :
			if current_calendar.subscriber_key == subscriber_key and current_calendar.calendar_date == date :
				return current_calendar







	def integrate_teacher_calendars_on_update_exam(self,current_teacher_calendars_list,updated_class_calendars_list,school_key) :
			updated_teacher_calendars_list =[]
			for updated_class_calendar in updated_class_calendars_list :
				for event in updated_class_calendar.events :
					calendar_date = updated_class_calendar.calendar_date
					employee_key = self.get_employee_key(event.params)
					if employee_key is not None :
						current_teacher_calendar = self.get_teacher_calendar(current_teacher_calendars_list,calendar_date,employee_key,school_key)
						emp_event = self.make_employee_event(event,updated_class_calendar)
						if self.is_calendar_already_exist(current_teacher_calendar,updated_teacher_calendars_list) == False :
							updated_teacher_calendars_list.append(current_teacher_calendar)

			for teacher_calendar in updated_teacher_calendars_list :
				for updated_class_calendar in updated_class_calendars_list :
					for event in updated_class_calendar.events :
						calendar_date = updated_class_calendar.calendar_date
						employee_key = self.get_employee_key(event.params)
						if teacher_calendar.calendar_date == calendar_date and teacher_calendar.subscriber_key == employee_key :
							emp_event = self.make_employee_event(event,updated_class_calendar)
							if self.is_event_already_exist(emp_event,teacher_calendar.events) == False :
								teacher_calendar.events.append(emp_event)
			return updated_teacher_calendars_list


	def is_event_already_exist(self,event,teacher_calendar_events) :
		is_exist = False
		for existing_event in teacher_calendar_events :
			if event.event_code == existing_event.event_code and event.ref_calendar_key == existing_event.ref_calendar_key :
				is_exist = True
		return is_exist

	def make_employee_event(self,event,updated_class_calendar) :
		if event is not None :
			emp_event = calendar.Event(None)
			emp_event.event_code = event.event_code
			emp_event.ref_calendar_key = updated_class_calendar.calendar_key
		return emp_event

	def is_calendar_already_exist(self,current_teacher_calendar,updated_teacher_calendars_list) :
		is_exist = False
		for updated_teacher_calendar in updated_teacher_calendars_list :
			if updated_teacher_calendar.subscriber_key == current_teacher_calendar.subscriber_key and updated_teacher_calendar.calendar_date == current_teacher_calendar.calendar_date:
				is_exist = True
		return is_exist


	def get_employee_key(self,params) :
		for param in params :
			if param.key == 'teacher_emp_key' :
				return param.value


	def get_teacher_calendar(self,teacher_calendars_list,calendar_date,employee_key,school_key) :
		for teacher_calendar in teacher_calendars_list :
			if teacher_calendar.subscriber_key == employee_key and teacher_calendar.calendar_date == calendar_date :
				teacher_calendar.events = []
				return teacher_calendar
		else :
			employee_calendar = self.generate_employee_calendar(calendar_date,employee_key,school_key)
			return employee_calendar


	def generate_employee_calendar(self,calendar_date,employee_key,school_key) :
		employee_calendar=calendar.Calendar(None)
		employee_calendar.calendar_date = calendar_date
		employee_calendar.calendar_key = key.generate_key(16)
		employee_calendar.institution_key = school_key
		employee_calendar.subscriber_key = employee_key
		employee_calendar.subscriber_type = 'EMPLOYEE'
		employee_calendar.events = []
		return employee_calendar












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


	def get_expected_class_calendars_list(self) :
		expected_class_calendars = []
		with open('tests/unit/fixtures/cancel-exam-fixtures/expected_class_calendars_list.json', 'r') as calendar_list:
			class_calendars_dict = json.load(calendar_list)
		for class_cal in class_calendars_dict :
			expected_class_calendars.append(calendar.Calendar(class_cal))
		return expected_class_calendars

	def get_expected_teacher_calendars_list(self) :
		expected_teacher_calendars = []
		with open('tests/unit/fixtures/cancel-exam-fixtures/expected_teacher_calendars_list.json', 'r') as calendar_list:
			teacher_calendars_dict = json.load(calendar_list)
		for teacher_cal in teacher_calendars_dict :
			expected_teacher_calendars.append(calendar.Calendar(teacher_cal))
		return expected_teacher_calendars

	def get_expected_lessonplans_list(self) :
		expected_lessonplans = []
		with open('tests/unit/fixtures/cancel-exam-fixtures/expected_lessonplans_list.json', 'r') as lessonplan_list:
			lessonplans_dict = json.load(lessonplan_list)
		for lessonplan in lessonplans_dict :
			expected_lessonplans.append(lpnr.LessonPlan(lessonplan))
		return expected_lessonplans
	

	def get_timetables_list_from_json(self) :
		with open('tests/unit/fixtures/cancel-exam-fixtures/test_timetables_list.json', 'r') as calendar_list:
			timetable = json.load(calendar_list)
		return timetable

	def get_academic_config_from_json(self) :
		with open('tests/unit/fixtures/academic_configuration.json', 'r') as academic_configure:
			academic_configuration = json.load(academic_configure)
		return academic_configuration

	def get_current_lessonplans_from_json(self) :
		with open('tests/unit/fixtures/cancel-exam-fixtures/current_lessonplans_list.json', 'r') as lessonplans_list:
			current_lessonplans = json.load(lessonplans_list)
		return current_lessonplans

	def get_current_teacher_calendars_list_json(self) :
		with open('tests/unit/fixtures/cancel-exam-fixtures/current_teacher_calendars_list.json', 'r') as calendar_list:
			current_teacher_calendars = json.load(calendar_list)
		return current_teacher_calendars

	def get_current_class_calendars_list_json(self) :
		with open('tests/unit/fixtures/cancel-exam-fixtures/current_class_calendars_list.json', 'r') as calendar_list:
			current_class_calendars = json.load(calendar_list)
		return current_class_calendars


class ExamSeries :
	def __init__(self, item):
		if item is None:
			
			self.classes = []
			self.code = None
			self.from_date = None
			self.name = None
			self.to_date = None
		else :
			try :
				self.classes = []
				classes = item['classes']
				for clazz in classes :
					self.classes.append(Class(clazz))
			except KeyError as ke:
				logger.debug('[WARN] - KeyError in ExamSeries - classes not present'.format(str (ke)))
			try :
				self.code = item['code']
			except KeyError as ke:
				logger.debug('[WARN] - KeyError in ExamSeries - code not present'.format(str (ke)))
			try :
				self.from_date = item['from_date']
			except KeyError as ke:
				logger.debug('[WARN] - KeyError in ExamSeries - from_date not present'.format(str (ke)))
			try :
				self.to_date = item['to_date']
			except KeyError as ke:
				logger.debug('[WARN] - KeyError in ExamSeries - to_date not present'.format(str (ke)))
			try :
				self.name = item['name']
			except KeyError as ke:
				logger.debug('[WARN] - KeyError in ExamSeries - name not present'.format(str (ke)))


class Class :
	def __init__(self, item):
		if item is None:
			self.class_key = None
			self.division = None
			
		else :
			self.class_key = item['class_key']
			self.division = item['division']

if __name__ == '__main__':
	unittest.main()
