import unittest
import json
from academics.TimetableIntegrator import *
from academics.academic import AcademicConfiguration as academic_config
import academics.timetable.TimeTable as ttable
from academics.logger import GCLogger as gclogger
import academics.calendar.Calendar as cldr
import academics.lessonplan.LessonPlan as lessonplan
from academics.calendar.CalendarLessonPlanIntegrator import integrate_calendar_to_lesson_plan
import academics.calendar.CalendarDBService as calendar_service
import academics.lessonplan.LessonplanDBService as lessonplan_service
import operator
import pprint
import academics.timetable.TimeTableDBService as timetable_service
import academics.academic.AcademicDBService as academic_service
from academics.lessonplan.LessonplanIntegrator import integrate_holiday_lessonplan,holiday_calendar_to_lessonplan_integrator,integrate_cancelled_holiday_lessonplan
import academics.classinfo.ClassInfoDBService as class_info_service
import academics.school.SchoolDBService as school_service
pp = pprint.PrettyPrinter(indent=4)



class CalendarHolidayCancelLessonPlanIntegratorTest(unittest.TestCase):

	def setUp(self) :
		test_timetable_one = self.get_test_timetable_one_as_json()
		response = timetable_service.create_timetable(test_timetable_one)
		gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' -----------  time table one uploaded  ---------- '+str(test_timetable_one['time_table_key']))

		test_timetable_two = self.get_test_timetable_two_as_json()
		response = timetable_service.create_timetable(test_timetable_two)
		gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' -----------  time table two uploaded  ---------- '+str(test_timetable_two['time_table_key']))

		test_timetable_three = self.get_test_timetable_three_as_json()
		response = timetable_service.create_timetable(test_timetable_three)
		gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' -----------  time table three uploaded  ---------- '+str(test_timetable_three['time_table_key']))

		academic_configuration = self.get_academic_config_as_json()
		response = academic_service.create_academic_config(academic_configuration)
		gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' -------------  Academic configuration uploaded  ------------- '+str(academic_configuration['academic_config_key']))
		holiday_cancelled__calendars = self.get_cancelled_holiday_calendars()
		for holiday_cancelled__calendar in holiday_cancelled__calendars :
			cal = calendar.Calendar(None)
			calendar_dict = cal.make_calendar_dict(holiday_cancelled__calendar)
			response = calendar_service.add_or_update_calendar(calendar_dict)
			gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' ------- A Holiday cancelled calendar uploaded --------- '+str(calendar_dict['calendar_key']))

		current_lesson_plan_list = self.get_current_lesson_plan_list()
		for current_lesson_plan in current_lesson_plan_list :
			lesson_plan = lessonplan.LessonPlan(None)
			lesson_plan_dict = lesson_plan.make_lessonplan_dict(current_lesson_plan)
			response = lessonplan_service.create_lessonplan(lesson_plan_dict)
			gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' ---------- A Lesson Plan uploaded ------------- '+str(lesson_plan_dict['lesson_plan_key']))

		class_info_one_dict = self.get_class_info_one()
		response = class_info_service.add_or_update_class_info(class_info_one_dict)
		gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' ------------- A Class info for uploaded --------- ' +str(class_info_one_dict['class_info_key']) )

		class_info_two_dict = self.get_class_info_two()
		response = class_info_service.add_or_update_class_info(class_info_two_dict)
		gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' ------------- A Class info for uploaded -------------- ' +str(class_info_one_dict['class_info_key']) )

		current_class_calendars = self.get_current_class_calendars()
		for current_class_calendar in current_class_calendars :
			cal = cldr.Calendar(None)
			calendar_dict = cal.make_calendar_dict(current_class_calendar)
			response = calendar_service.add_or_update_calendar(calendar_dict)
			gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' ------- A Class calendar uploaded --------- '+str(calendar_dict['calendar_key']))



	def test_lessonplan(self) :
		expected_lesson_plan_list = self.get_expected_lesson_plan_list()
		calendar_key ='test-key'
		updated_lessonplan_list = []
		integrate_cancelled_holiday_lessonplan(calendar_key)
		calendar = calendar_service.get_calendar(calendar_key)
		school_key = calendar.institution_key
		academic_configuration = academic_service.get_academic_year(school_key, calendar.calendar_date)
		academic_year = academic_configuration.academic_year
		class_info_list = class_info_service.get_classinfo_list(school_key,academic_year)
		for class_info in class_info_list :
			if hasattr(class_info, 'divisions') :
				for div in class_info.divisions :
					division = div.name
					class_key = class_info.class_info_key
					if division != 'NONE':
						lessonplan_list = lessonplan_service.get_lesson_plan_list(class_key, division)
						for lesson_plan in lessonplan_list :
							updated_lessonplan_list.append(lesson_plan)
		for updated_lessonplan in updated_lessonplan_list :
			lp = lessonplan.LessonPlan(None)
			updated_lessonplan_dict = lp.make_lessonplan_dict(updated_lessonplan)
			pp.pprint(updated_lessonplan_dict)
			self.check_lesson_plans(updated_lessonplan,expected_lesson_plan_list)



	def check_lesson_plans(self,updated_lesson_plan,expected_lesson_plan_list) :
		for expected_lesson_plan in expected_lesson_plan_list :
			if expected_lesson_plan.lesson_plan_key == updated_lesson_plan.lesson_plan_key :	
				self.assertEqual(updated_lesson_plan.lesson_plan_key,expected_lesson_plan.lesson_plan_key)
				self.assertEqual(updated_lesson_plan.class_key,expected_lesson_plan.class_key)
				self.assertEqual(updated_lesson_plan.division,expected_lesson_plan.division)
				self.assertEqual(updated_lesson_plan.subject_code,expected_lesson_plan.subject_code)
				self.assertEqual(updated_lesson_plan.resources,expected_lesson_plan.resources)
				self.check_topics(updated_lesson_plan.topics,expected_lesson_plan.topics)
				self.check_root_sessions(updated_lesson_plan.sessions,expected_lesson_plan.sessions)

		gclogger.info(" <<<-------------------------------- INTEGRATION TEST PASSED FOR "+ str(updated_lesson_plan.lesson_plan_key)+" ------------------------------>>> ")

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

	def check_root_sessions(self,updated_lesson_plan_sessions,expected_lesson_plan_sessions) :
		for index in range(len(updated_lesson_plan_sessions)) :
			self.assertEqual(updated_lesson_plan_sessions[index].order_index,expected_lesson_plan_sessions[index].order_index)
			self.check_schedule(updated_lesson_plan_sessions[index].schedule,expected_lesson_plan_sessions[index].schedule)

	def check_schedule(self,updated_lesson_plan_shedule,expected_lesson_plan_shedule) :
		self.assertEqual(updated_lesson_plan_shedule.start_time,expected_lesson_plan_shedule.start_time)
		self.assertEqual(updated_lesson_plan_shedule.end_time,expected_lesson_plan_shedule.end_time)


	@classmethod
	def tearDown(self):
		test_timetable_one = timetable_service.get_time_table('test-time-table-1')
		test_timetable_two = timetable_service.get_time_table('test-time-table-2')
		test_timetable_three = timetable_service.get_time_table('test-time-table-3')
		school_key = test_timetable_one.school_key
		academic_configuration = academic_service.get_academig(school_key,'2020-2021')

		holiday_calender_list = calendar_service.get_all_calendars_by_school_key_and_type('test-school-1','CLASS-DIV')
		for calendar in holiday_calender_list :
			calendar_service.delete_calendar(calendar.calendar_key)
			gclogger.info("--------------- A Holiday class calendar deleted " + calendar.calendar_key+" -----------------")

		teacher_calender_list = calendar_service.get_all_calendars_by_school_key_and_type('test-school-1','SCHOOL')
		for calendar in teacher_calender_list :
			calendar_service.delete_calendar(calendar.calendar_key)
			gclogger.info("--------------- A Holiday School calendar deleted " + calendar.calendar_key+" -----------------")


		timetable_service.delete_timetable(test_timetable_one.time_table_key)
		gclogger.info("--------------- Test Timetable deleted  " + test_timetable_one.time_table_key+"  -----------------")
		timetable_service.delete_timetable(test_timetable_two.time_table_key)
		gclogger.info("--------------- Test Timetable deleted  " + test_timetable_two.time_table_key+"  -----------------")
		timetable_service.delete_timetable(test_timetable_three.time_table_key)
		gclogger.info("--------------- Test Timetable deleted  " + test_timetable_three.time_table_key+"  -----------------")

		academic_service.delete_academic_config(academic_configuration.academic_config_key)
		gclogger.info("---------------Test Academic Configuration deleted  " + academic_configuration.academic_config_key + "-----------------")
		generated_lesson_plan_list = lessonplan_service.get_lesson_plan_list('8B1B22E72AE','A')
		for generated_lesson_plan in generated_lesson_plan_list :
			lessonplan_service.delete_lessonplan(generated_lesson_plan.lesson_plan_key)
			gclogger.info("---------------Test Lesson Plan deleted  " + generated_lesson_plan.lesson_plan_key + "-----------------")

		generated_lesson_plan_list = lessonplan_service.get_lesson_plan_list('8B1B22E72AE','B')
		for generated_lesson_plan in generated_lesson_plan_list :
			lessonplan_service.delete_lessonplan(generated_lesson_plan.lesson_plan_key)
			gclogger.info("---------------Test Lesson Plan deleted  " + generated_lesson_plan.lesson_plan_key + "-----------------")

		generated_lesson_plan_list = lessonplan_service.get_lesson_plan_list('8B1B22E72AY','B')
		for generated_lesson_plan in generated_lesson_plan_list :
			lessonplan_service.delete_lessonplan(generated_lesson_plan.lesson_plan_key)
			gclogger.info("---------------Test Lesson Plan deleted  " + generated_lesson_plan.lesson_plan_key + "-----------------")




	def get_lesson_plan_after_remove_all_shedules(self,current_lessonplan) :
		for main_topic in current_lessonplan.topics :
			for topic in main_topic.topics :
				for session in topic.sessions :
					if hasattr(session , 'schedule') :
						del session.schedule




	def get_updated_lesson_plan(self,shedule_list,current_lessonplan) :
		index = -1
		for main_topic in current_lessonplan.topics :
			for topic in main_topic.topics :
				for session in topic.sessions :
					index += 1
					if index < len(shedule_list) :
						session.schedule = shedule_list[index]



	def get_all_remaining_schedules(self,current_lessonplan) :
		schedule_list = []
		for main_topic in current_lessonplan.topics :
			for topic in main_topic.topics :
				for session in topic.sessions :
					if hasattr(session , 'schedule') :
						schedule_list.append(session.schedule)
		return schedule_list



	def remove_shedules(self,schedules,current_lessonplan) :
		for schedule in schedules :
			schedule_start_time = schedule.start_time
			schedule_end_time = schedule.end_time
			for topic in current_lessonplan.topics[0].topics :
				for session in topic.sessions :
					if session.schedule.start_time == schedule_start_time and session.schedule.end_time == schedule_end_time :
						del session.schedule
		return current_lessonplan



	def generate_holiday_period_list(self,event,calendar,academic_configuration,timetable,day_code) :

		holiday_period_list =[]
		if is_class(event.params[0]) == False :
			start_time = event.from_time
			end_time = event.to_time
			partial_holiday_periods = get_holiday_period_list(start_time,end_time,day_code,academic_configuration,timetable,calendar.calendar_date)
			for partial_holiday_period in partial_holiday_periods :
				holiday_period_list.append(partial_holiday_period)
		return holiday_period_list



	def find_schedules(self,topics,holiday_period_list,date) :
		schedule_list = []
		for topic in topics :
			for session in topic.sessions :
				schedule = self.get_schedule(holiday_period_list,session.schedule,date)
				if schedule is not None :
					schedule_list.append(schedule)
		return schedule_list



	def get_schedule(self,holiday_period_list,schedule,date) :
		for period in holiday_period_list :
			standard_start_time = get_standard_time(period.start_time,date)
			standard_end_time = get_standard_time(period.end_time,date)
			if standard_start_time == schedule.start_time and standard_end_time ==schedule.end_time :
				return schedule


	def get_academic_config_as_json(self) :
		with open('tests/unit/fixtures/calendar-lessonplan-fixtures/academic_configuration.json', 'r') as academic_configure:
			academic_configuration = json.load(academic_configure)
		return academic_configuration

	

	def get_test_timetable_one_as_json(self) :
		with open('tests/unit/fixtures/calendar-lessonplan-fixtures/test_timetable_one.json', 'r') as calendar_list:
			timetable = json.load(calendar_list)
		return timetable

	def get_test_timetable_two_as_json(self) :
		with open('tests/unit/fixtures/calendar-lessonplan-fixtures/test_timetable_two.json', 'r') as calendar_list:
			timetable = json.load(calendar_list)
		return timetable

	def get_test_timetable_three_as_json(self) :
		with open('tests/unit/fixtures/calendar-lessonplan-fixtures/test_timetable_three.json', 'r') as calendar_list:
			timetable = json.load(calendar_list)
		return timetable


	def get_current_lesson_plan_list(self) :
		current_lesson_plan_list = []
		with open('tests/unit/fixtures/calendar-lessonplan-fixtures/current_lessonplan.json', 'r') as current_lessonplan:
			current_lessonplan_dict_list = json.load(current_lessonplan)
		for current_lessonplan_dict in current_lessonplan_dict_list :
			current_lesson_plan_list.append(lessonplan.LessonPlan(current_lessonplan_dict))
		return current_lesson_plan_list

	def get_class_info_one(self) :
		with open('tests/unit/fixtures/calendar-lessonplan-fixtures/class_info_one.json', 'r') as class_info_one:
			class_info_one_dict = json.load(class_info_one)
		return class_info_one_dict


	def get_class_info_two(self) :
		with open('tests/unit/fixtures/calendar-lessonplan-fixtures/class_info_two.json', 'r') as class_info_two:
			class_info_two_dict = json.load(class_info_two)
		return class_info_two_dict


	def get_current_class_calendars(self) :
		class_calendars_list = []
		with open('tests/unit/fixtures/calendar-lessonplan-fixtures/class_cls_session_calendars.json', 'r') as calendars:
			class_calendars = json.load(calendars)
		for cal in class_calendars :
			class_calendars_list.append(calendar.Calendar(cal))
		return class_calendars_list

	def get_expected_lesson_plan_list(self) :
		expected_lesson_plan_list = []
		with open('tests/unit/fixtures/calendar-lessonplan-fixtures/expected_lessonplan.json', 'r') as expected_lessonplan:
			expected_lessonplan_dict_list = json.load(expected_lessonplan)
		for expected_lessonplan_dict in expected_lessonplan_dict_list :
			expected_lesson_plan_list.append(lessonplan.LessonPlan(expected_lessonplan_dict))
		return expected_lesson_plan_list


	def get_event_from_calendar(self,calendar,event_code) :
		for event in calendar.events :
			if event.event_code == event_code :
				return event

	def get_cancelled_holiday_calendar(self,calendar_key,holiday_calendars) :
		for calendar in holiday_calendars :
			if calendar.calendar_key == calendar_key :
				return calendar

	def get_cancelled_holiday_calendars(self):
		holiday_cancelled_calendars_list = []
		with open('tests/unit/fixtures/calendar-lessonplan-fixtures/holiday_cancelled_calendars.json', 'r') as calendars:
			holidaycancelled__calendars = json.load(calendars)
		for cal in holidaycancelled__calendars :
			holiday_cancelled_calendars_list.append(calendar.Calendar(cal))
		return holiday_cancelled_calendars_list




if __name__ == '__main__':
	unittest.main()
