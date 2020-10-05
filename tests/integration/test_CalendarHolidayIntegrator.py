import unittest
import json
from academics.TimetableIntegrator import *
from academics.timetable import AcademicConfiguration as academic_config
import academics.timetable.TimeTable as ttable
from academics.logger import GCLogger as gclogger
import academics.calendar.Calendar as calendar
import academics.lessonplan.LessonPlan as lessonplan
from academics.calendar.CalendarLessonPlanIntegrator import integrate_calendar_to_lesson_plan
import academics.calendar.CalendarDBService as calendar_service
import academics.lessonplan.LessonplanDBService as lessonplan_service
import operator
import pprint
import academics.timetable.TimeTableDBService as timetable_service
import academics.academic.AcademicDBService as academic_service
from academics.lessonplan.LessonplanIntegrator import integrate_holiday_lessonplan,holiday_calendar_to_lessonplan_integrator
import academics.classinfo.ClassInfoDBService as class_info_service
import academics.school.SchoolDBService as school_service
pp = pprint.PrettyPrinter(indent=4)



class CalendarHolidayIntegratorTest(unittest.TestCase):
	
	def setUp(self) :
		school_dict = self.get_school()
		response = school_service.add_or_update_school(school_dict)
		print(str(response['ResponseMetadata']['HTTPStatusCode']) + ' -------------  School Uploaded ' + str(school_dict['school_id']) + '  ------------- ')
		timetable = self.get_timetable_from_json()
		response = timetable_service.create_timetable(timetable)
		print(str(response['ResponseMetadata']['HTTPStatusCode']) + ' -----------  time table uploaded  ---------- '+str(timetable['time_table_key']))
		academic_configuration = self.get_academic_config_from_json()
		response = academic_service.create_academic_config(academic_configuration)
		print(str(response['ResponseMetadata']['HTTPStatusCode']) + ' -------------  Academic configuration uploaded  ------------- '+str(academic_configuration['academic_config_key']))
		holiday_calendars = self.get_holiday_calendars()
		for holiday_calendar in holiday_calendars :
			cal = calendar.Calendar(None)
			calendar_dict = cal.make_calendar_dict(holiday_calendar)
			response = calendar_service.add_or_update_calendar(calendar_dict)
			print(str(response['ResponseMetadata']['HTTPStatusCode']) + ' ------- A Holiday calendar uploaded --------- '+str(calendar_dict['calendar_key']))

		current_lesson_plan_list = self.get_current_lesson_plan_list()
		for current_lesson_plan in current_lesson_plan_list :
			lesson_plan = lessonplan.LessonPlan(None)
			lesson_plan_dict = lesson_plan.make_lessonplan_dict(current_lesson_plan)
			response = lessonplan_service.create_lessonplan(lesson_plan_dict)
			print(str(response['ResponseMetadata']['HTTPStatusCode']) + ' ---------- A Lesson Plan uploaded -------------'+str(lesson_plan_dict['lesson_plan_key']))

		class_info_8B1B22E72AE_dict = self.get_class_info_8B1B22E72AE()
		response = class_info_service.add_or_update_class_info(class_info_8B1B22E72AE_dict)
		print(str(response['ResponseMetadata']['HTTPStatusCode']) + ' -------------  Class info for 8B1B22E72AE uploaded  ------------- ')

		class_info_8B1B22E72AY_dict = self.get_class_info_8B1B22E72AY()
		response = class_info_service.add_or_update_class_info(class_info_8B1B22E72AY_dict)
		print(str(response['ResponseMetadata']['HTTPStatusCode']) + ' -------------  Class info for 8B1B22E72AY uploaded  ------------- ')

		

	def test_lessonplan(self) :
		expected_lesson_plan_list = self.get_expected_lesson_plan_list()
		event_code = 'event-1'
		calendar_key ='test-key-5'
		updated_lessonplan_list = integrate_holiday_lessonplan(event_code,calendar_key)
		for updated_lessonplan in updated_lessonplan_list :
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

		print(" <<<-------------------------------- INTEGRATION TEST PASSED FOR "+ str(updated_lesson_plan.lesson_plan_key)+" ------------------------------>>> ")

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


	@classmethod
	def tearDown(self):
		timetable = timetable_service.get_time_table('test-time-table-1')
		school_key = timetable.school_key
		academic_configuration = academic_service.get_academig(school_key,'2020-2021')

		holiday_calender_list = calendar_service.get_all_calendars('test-school-1','CLASS-DIV')
		for calendar in holiday_calender_list :
			calendar_service.delete_calendar(calendar.calendar_key)
			print("--------------- A Holiday class calendar deleted " + calendar.calendar_key+" -----------------")

		teacher_calender_list = calendar_service.get_all_calendars('test-school-1','SCHOOL')
		for calendar in teacher_calender_list :
			calendar_service.delete_calendar(calendar.calendar_key)
			print("--------------- A Holiday School calendar deleted " + calendar.calendar_key+" -----------------")


		timetable_service.delete_timetable(timetable.time_table_key)
		print("--------------- Test Timetable deleted  " + timetable.time_table_key+"  -----------------")
		academic_service.delete_academic_config(academic_configuration.academic_config_key)
		print("---------------Test Academic Configuration deleted  " + academic_configuration.academic_config_key + "-----------------")
		generated_lesson_plan_list = lessonplan_service.get_lesson_plan_list('8B1B22E72AE','A')
		for generated_lesson_plan in generated_lesson_plan_list :
			lessonplan_service.delete_lessonplan(generated_lesson_plan.lesson_plan_key)
			print("---------------Test Lesson Plan deleted  " + generated_lesson_plan.lesson_plan_key + "-----------------")

		generated_lesson_plan_list = lessonplan_service.get_lesson_plan_list('8B1B22E72AE','B')
		for generated_lesson_plan in generated_lesson_plan_list :
			lessonplan_service.delete_lessonplan(generated_lesson_plan.lesson_plan_key)
			print("---------------Test Lesson Plan deleted  " + generated_lesson_plan.lesson_plan_key + "-----------------")

		generated_lesson_plan_list = lessonplan_service.get_lesson_plan_list('8B1B22E72AY','B')
		for generated_lesson_plan in generated_lesson_plan_list :
			lessonplan_service.delete_lessonplan(generated_lesson_plan.lesson_plan_key)
			print("---------------Test Lesson Plan deleted  " + generated_lesson_plan.lesson_plan_key + "-----------------")


	def get_academic_yr_from_calendar(calendar) :
		pass

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
			# print(start_time,"start time-------------<<<<<")
			# print(end_time,"end time-------------<<<<<")
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


	def get_academic_config_from_json(self) :
		with open('tests/unit/fixtures/academic_configuration.json', 'r') as academic_configure:
			academic_configuration = json.load(academic_configure)
		return academic_configuration

	def get_time_table(self):
		with open('tests/unit/fixtures/timetable.json', 'r') as timetable:
			timetable = json.load(timetable)
		return ttable.TimeTable(timetable)

	def get_timetable_from_json(self) :
		with open('tests/unit/fixtures/timetable.json', 'r') as calendar_list:
			timetable = json.load(calendar_list)
		return timetable

	def get_academic_configuration(self):
		with open('tests/unit/fixtures/academic_configuration.json', 'r') as academic_configuration:
			academic_configuration_dict = json.load(academic_configuration)
			academic_configuration = academic_config.AcademicConfiguration(academic_configuration_dict)
		return academic_configuration


	def get_current_lesson_plan_list(self) :
		current_lesson_plan_list = []
		with open('tests/unit/fixtures/calendar-lessonplan-fixtures/current_lesson_plan.json', 'r') as current_lessonplan:
			current_lessonplan_dict_list = json.load(current_lessonplan)
		for current_lessonplan_dict in current_lessonplan_dict_list :
			current_lesson_plan_list.append(lessonplan.LessonPlan(current_lessonplan_dict))
		return current_lesson_plan_list

	def get_class_info_8B1B22E72AE(self) :
		with open('tests/unit/fixtures/calendar-lessonplan-fixtures/class_info_8B1B22E72AE.json', 'r') as class_info_8B1B22E72AE:
			class_info_8B1B22E72AE_dict = json.load(class_info_8B1B22E72AE)
		return class_info_8B1B22E72AE_dict

	def get_school(self) :
		with open('tests/unit/fixtures/calendar-lessonplan-fixtures/school.json', 'r') as school:
			school_dict = json.load(school)
		return school_dict

	def get_class_info_8B1B22E72AY(self) :
		with open('tests/unit/fixtures/calendar-lessonplan-fixtures/class_info_8B1B22E72AY.json', 'r') as class_info_8B1B22E72AY:
			class_info_8B1B22E72AY_dict = json.load(class_info_8B1B22E72AY)
		return class_info_8B1B22E72AY_dict


	def get_expected_lesson_plan_list(self) :
		expected_lesson_plan_list = []
		with open('tests/unit/fixtures/calendar-lessonplan-fixtures/expected_lesson_plan.json', 'r') as expected_lessonplan:
			expected_lessonplan_dict_list = json.load(expected_lessonplan)
		for expected_lessonplan_dict in expected_lessonplan_dict_list :
			expected_lesson_plan_list.append(lessonplan.LessonPlan(expected_lessonplan_dict))
		return expected_lesson_plan_list


	def get_event_from_calendar(self,calendar,event_code) :
		for event in calendar.events :
			if event.event_code == event_code :
				return event

	def get_holiday_calendar(self,calendar_key,holiday_calendars) :
		for calendar in holiday_calendars :
			if calendar.calendar_key == calendar_key :
				return calendar

	def get_holiday_calendars(self):
		holiday_calendars_list = []
		with open('tests/unit/fixtures/calendar-lessonplan-fixtures/holiday_calendars.json', 'r') as calendars:
			holiday_calendars = json.load(calendars)
		for cal in holiday_calendars :
			holiday_calendars_list.append(calendar.Calendar(cal))
		return holiday_calendars_list




if __name__ == '__main__':
	unittest.main()
