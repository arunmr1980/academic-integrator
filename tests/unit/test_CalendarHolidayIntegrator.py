import unittest
import json
from academics.TimetableIntegrator import *
from academics.timetable import AcademicConfiguration as academic_config
import academics.timetable.TimeTable as ttable
from academics.logger import GCLogger as gclogger
import academics.calendar.Calendar as calendar
import academics.lessonplan.LessonPlan as lessonplan
from academics.calendar.CalendarLessonPlanIntegrator import integrate_calendar_to_lesson_plan
import operator
import pprint
pp = pprint.PrettyPrinter(indent=4)



class CalendarHolidayIntegratorTest(unittest.TestCase):
	def test_lessonplan(self) :
		timetable=self.get_time_table()
		academic_configuration=self.get_academic_configuration()
		event_code = 'event-1'
		calendar_key ='test-key-5'
		holiday_calendars = self.get_holiday_calendars()
		calendar = self.get_holiday_calendar(calendar_key,holiday_calendars)
		event = self.get_event_from_calendar(calendar,event_code)
		print("EVENT START TIME AND END TIME ----------------->",event.from_time,event.to_time)
		day_code = findDay(calendar.calendar_date).upper()[0:3]
		subscriber_key = calendar.subscriber_key
		class_key = subscriber_key[:-2]
		division = subscriber_key[-1:]
		current_lesson_plan_list = self.get_current_lesson_plan_list()
		expected_lesson_plan_list = self.get_expected_lesson_plan_list()

		if calendar.subscriber_type == 'CLASS-DIV' :
			for current_lessonplan in current_lesson_plan_list :
				if current_lessonplan.class_key == class_key and current_lessonplan.division == division :
					print("LESSON PLAN KEY------------------->  ",current_lessonplan.lesson_plan_key)
					holiday_period_list = self.generate_holiday_period_list(event,calendar,academic_configuration,timetable,day_code)
					schedules = self.find_schedules(current_lessonplan.topics[0].topics,holiday_period_list,calendar.calendar_date)
					current_lessonplan = self.remove_shedules(schedules,current_lessonplan)
					shedule_list= self.get_all_remaining_schedules(current_lessonplan)
					self.get_lesson_plan_after_remove_all_shedules(current_lessonplan)
					self.get_updated_lesson_plan(shedule_list,current_lessonplan)
					self.check_lesson_plans(current_lessonplan,expected_lesson_plan_list)




		else :
			print(len(current_lesson_plan_list),"lesson plan listttttttttttt")
			for current_lessonplan in current_lesson_plan_list :
				print("LESSON PLAN KEY------------------->  ",current_lessonplan.lesson_plan_key)
				holiday_period_list = self.generate_holiday_period_list(event,calendar,academic_configuration,timetable,day_code)
				schedules = self.find_schedules(current_lessonplan.topics[0].topics,holiday_period_list,calendar.calendar_date)
				current_lessonplan = self.remove_shedules(schedules,current_lessonplan)
				shedule_list= self.get_all_remaining_schedules(current_lessonplan)
				self.get_lesson_plan_after_remove_all_shedules(current_lessonplan)
				self.get_updated_lesson_plan(shedule_list,current_lessonplan)
				self.check_lesson_plans(current_lessonplan,expected_lesson_plan_list)


	def check_lesson_plans(self,updated_lesson_plan,expected_lesson_plan_list) :
		for expected_lesson_plan in expected_lesson_plan_list :
			if expected_lesson_plan.lesson_plan_key == updated_lesson_plan.lesson_plan_key :

				self.assertEqual(updated_lesson_plan.lesson_plan_key,expected_lesson_plan.lesson_plan_key)
				self.assertEqual(updated_lesson_plan.class_key,expected_lesson_plan.class_key)
				self.assertEqual(updated_lesson_plan.division,expected_lesson_plan.division)
				self.assertEqual(updated_lesson_plan.subject_code,expected_lesson_plan.subject_code)
				self.assertEqual(updated_lesson_plan.resources,expected_lesson_plan.resources)
				self.check_topics(updated_lesson_plan.topics,expected_lesson_plan.topics)

		print(" <<<--------------------------------UNIT TEST PASSED------------------------------>>> ")

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




	def get_time_table(self):
		with open('tests/unit/fixtures/timetable.json', 'r') as timetable:
			timetable = json.load(timetable)
		return ttable.TimeTable(timetable)


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
