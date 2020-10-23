import unittest
import json
from academics.TimetableIntegrator import integrate_class_timetable,integrate_teacher_timetable
from academics.timetable import AcademicConfiguration as academic_config
import academics.timetable.TimeTable as ttable
from academics.logger import GCLogger as gclogger
import academics.calendar.Calendar as calendar
import academics.lessonplan.LessonPlan as lpnr
import pprint
import copy 
import academics.timetable.KeyGeneration as key
pp = pprint.PrettyPrinter(indent=4)

class UpdatePeriodsIntegratorTest(unittest.TestCase):


	



	def test_calendars(self) :
		expected_teacher_calendars_dict = {}
		period_code = 'MON-3'
		updated_timetable = self.get_updated_timetable()
		current_class_calendars = self.get_current_class_calendar_list()
		current_teacher_calendars = self.get_current_teacher_calendar_list()
		expected_class_calendars = self.get_expected_class_calendar_list()
		expected_teacher_calendars = self.get_expected_teacher_calendar_list()
		for expected_teacher_calendar in expected_teacher_calendars :
			calendar_date = expected_teacher_calendar.calendar_date
			subscriber_key = expected_teacher_calendar.subscriber_key
			expected_teacher_calendars_dict[calendar_date + subscriber_key] = expected_teacher_calendar

		current_class_calendars_with_day_code = self.get_current_class_calendars_with_day_code(period_code[:3],current_class_calendars)
		updated_period = self.get_updated_period_from_timetable(period_code,updated_timetable)
		for current_class_calendar in current_class_calendars_with_day_code :
			updated_class_calendar = self.update_current_class_calendar_with_day_code(period_code,updated_timetable,current_class_calendar,updated_period)
			# cal = calendar.Calendar(None)
			# calendar_dict = cal.make_calendar_dict(updated_class_calendar)
			# pp.pprint(calendar_dict)
			self.check_class_calendars(updated_class_calendar,expected_class_calendars)


			updated_class_calendar_events = self.get_class_session_events(updated_class_calendar)
			employee_key_list = self.get_employee_key_list(updated_class_calendar_events)
			for employee_key in employee_key_list :
				teacher_calendar = self.get_teacher_calendar(employee_key,current_teacher_calendars,updated_class_calendar)
				del teacher_calendar.events
				updated_teacher_calendar = self.update_teacher_calendar(teacher_calendar,updated_class_calendar_events,updated_class_calendar)
				teacher_calendar_key = updated_teacher_calendar.calendar_date + updated_teacher_calendar.subscriber_key
				expected_teacher_calendar = expected_teacher_calendars_dict[teacher_calendar_key]

				# cal = calendar.Calendar(None)
				# calendar_dict = cal.make_calendar_dict(updated_teacher_calendar)
				# pp.pprint(calendar_dict)

				self.assertEqual(expected_teacher_calendar.institution_key,updated_teacher_calendar.institution_key )
				self.assertEqual(expected_teacher_calendar.calendar_date,updated_teacher_calendar.calendar_date )
				self.assertEqual(expected_teacher_calendar.subscriber_key,updated_teacher_calendar.subscriber_key )
				self.assertEqual(expected_teacher_calendar.subscriber_type,updated_teacher_calendar.subscriber_type )
				gclogger.info("-----[UnitTest] Teacher calendar test passed ----------------- "+ str(updated_teacher_calendar.calendar_key)+" ------------------------------ ")

	def test_lessonplans(self) :
		updated_lessonplan_list = []
		updated_class_calendar_subject_key_list = []	
		period_code = 'MON-3'
		current_lessonplans = self.get_current_lessonplans()
		updated_timetable = self.get_updated_timetable()
		current_class_calendars = self.get_current_class_calendar_list()
		current_class_cals = copy.deepcopy(current_class_calendars)
		expected_lessonplans = self.get_expected_lessonplan_list()
		current_class_calendars_with_day_code = self.get_current_class_calendars_with_day_code(period_code[:3],current_class_calendars)
		updated_period = self.get_updated_period_from_timetable(period_code,updated_timetable)
		for current_class_calendar in current_class_calendars_with_day_code :
			updated_class_calendar = self.update_current_class_calendar_with_day_code(period_code,updated_timetable,current_class_calendar,updated_period)
			updated_class_calendar_events = self.get_class_session_events(updated_class_calendar)

			sub_key_list = self.get_subject_key_list(updated_class_calendar_events)
			updated_class_calendar_subject_key_list.extend(sub_key_list)
			for subject_key in updated_class_calendar_subject_key_list :
				current_lessonplan = self.get_current_lesson_plan_with_subject_key(current_lessonplans,subject_key) 
				updated_lessonplan = self.update_lessonplan(current_lessonplan,updated_class_calendar_events,updated_class_calendar)
				if updated_lessonplan is not None :
					updated_lessonplan_list.append(updated_lessonplan)
					# lp = lpnr.LessonPlan(None)
					# updated_lessonplan_dict = lp.make_lessonplan_dict(updated_lessonplan)
					# pp.pprint(updated_lessonplan_dict)
		current_class_calendars_event_list = self.get_current_class_calendars_event_list(current_class_cals)
		current_class_calendar_subject_key_list = self.get_subject_key_from_current_class_calendar(current_class_calendars_event_list)
		remaining_subject_key_list = self.list_difference(updated_class_calendar_subject_key_list,current_class_calendar_subject_key_list)
		for subject_key in remaining_subject_key_list :
			current_lessonplan = self.get_current_lesson_plan_with_subject_key(current_lessonplans,subject_key) 
			updated_lessonplan = self.Update_lessonplan(current_lessonplan,current_class_calendars)
			if updated_lessonplan is not None :
				updated_lessonplan_list.append(updated_lessonplan)
				# lp = lpnr.LessonPlan(None)
				# updated_lessonplan_dict = lp.make_lessonplan_dict(current_lessonplan)
				# pp.pprint(updated_lessonplan_dict)
		for updated_lessonplan in updated_lessonplan_list :
			self.check_lesson_plans(updated_lessonplan,expected_lessonplans)


		

	def list_difference(self,list1,list2):
		return (list(list(set(list1) - set(list2)) + list(set(list2) - set(list1))))

	def get_current_class_calendars_event_list(self,current_class_cals) :
		current_class_calendars_event_list = [] 
		for current_class_cal in current_class_cals :
			if hasattr(current_class_cal,'events') :
				for event in current_class_cal.events :
					if len(event.params)> 1:
						if event.event_type == 'CLASS_SESSION' :
							current_class_calendars_event_list.append(event) 
		return current_class_calendars_event_list


	def get_subject_key_from_current_class_calendar(self,current_class_calendar_event_list) :	
		subject_key_list = self.get_subject_key_list(current_class_calendar_event_list)
		return subject_key_list

	def Update_lessonplan(self,current_lessonplan,current_class_calendars) :
		if  hasattr(current_lessonplan,'topics') and len(current_lessonplan.topics) > 0 :	
				for main_topic in current_lessonplan.topics :
					for topic in main_topic.topics :
						for session in topic.sessions :
							if hasattr(session,'schedule') :
								if(self.is_remove_schedules(current_lessonplan,session.schedule,current_class_calendars)) == True :
									gclogger.info("----- A schedule removed ---" + session.schedule.start_time + '---' + session.schedule.end_time +'------')
									del session.schedule

		return current_lessonplan

	def is_remove_schedules(self,current_lessonplan,schedule,current_class_calendars) :
		is_remove = False
		calendar_key = schedule.calendar_key
		event_code = schedule.event_code
		subject_code = current_lessonplan.subject_code
		updated_class_calendar = self.get_updated_class_calendar(current_class_calendars,calendar_key)
		event = self.get_event_from_calendar(updated_class_calendar,event_code)
		if (self.is_subject_code_exist_in_event(event.params,subject_code)) == False :
			is_remove = True
		return is_remove
			




	def is_subject_code_exist_in_event(self,params,subject_code) :
		for param in params :
			if param.key == 'subject_key' and param.value == subject_code:
				return True
		else :
			return False


	def get_event_from_calendar(self,calendar,event_code) :
		for event in calendar.events :
			if event.event_code == event_code :
				return event

	def get_updated_class_calendar(self,current_class_calendars,calendar_key) :
		for current_class_calendar in current_class_calendars :
			if current_class_calendar.calendar_key == calendar_key :
				return current_class_calendar

	def update_lessonplan(self,current_lessonplan,updated_class_calendar_events,updated_class_calendar) :
		if  hasattr(current_lessonplan,'topics') and len(current_lessonplan.topics) > 0 :	
				for main_topic in current_lessonplan.topics :
					for topic in main_topic.topics :
						for session in topic.sessions :
							if not hasattr(session ,'schedule') :
								current_lessonplan = self.add_schedules(updated_class_calendar_events,current_lessonplan,updated_class_calendar)
		return current_lessonplan
								
	def add_schedules(self,updated_class_calendar_events,current_lessonplan,updated_class_calendar) :
		for event in updated_class_calendar_events :
			subject_key = self.get_subject_key(event.params)
			if subject_key == current_lessonplan.subject_code :
				schedule = self.create_schedule(event,updated_class_calendar)
				current_lessonplan = self.add_schedule_to_lessonplan(current_lessonplan,schedule)


		return current_lessonplan




	def add_schedule_to_lessonplan(self,current_lessonplan,schedule) :
		schedule_added = False
		for main_topic in current_lessonplan.topics :
			for topic in main_topic.topics :
				if schedule_added == False :
					for session in topic.sessions :
						if schedule_added == False :
							if not hasattr(session , 'schedule') :
								session.schedule = schedule
								schedule_added = True
								gclogger.info(' ------------- schedule added for lessonplan ' + str(current_lessonplan.lesson_plan_key) + ' -------------')

		return current_lessonplan						


	def create_schedule(self,event,calendar) :
		schedule = lpnr.Schedule(None)
		schedule.calendar_key = calendar.calendar_key
		schedule.event_code = event.event_code
		schedule.start_time = event.from_time
		schedule.end_time = event.to_time
		return schedule


	def get_current_lesson_plan_with_subject_key(self,current_lessonplans,subject_key) :
		for current_lessonplan in current_lessonplans :
			if current_lessonplan.subject_code == subject_key :
				return current_lessonplan


	def get_subject_key_list(self,updated_class_calendars_events) :
		subject_key_list =[]
		for event in updated_class_calendars_events :
			if event.event_type =='CLASS_SESSION':
				subject_key = self.get_subject_key(event.params)
				if subject_key is not None and subject_key not in subject_key_list :
					subject_key_list.append(subject_key)
		return subject_key_list



	def update_teacher_calendar(self,teacher_calendar,updated_class_calendar_events,updated_class_calendar) :
		teacher_calendar.events = []
		for event in updated_class_calendar_events :
			employee_key = self.get_employee_key(event.params)
			if employee_key == teacher_calendar.subscriber_key :
				event_object = calendar.Event(None)
				event_object.event_code = event.event_code
				event_object.ref_calendar_key = updated_class_calendar.calendar_key
				teacher_calendar.events.append(event_object)
		return teacher_calendar

	def get_employee_key_list(self,updated_class_calendar_events) :
		employee_key_list = []
		for event in updated_class_calendar_events :
			employee_key = self.get_employee_key(event.params)
			if employee_key not in employee_key_list :
				employee_key_list.append(employee_key)
		return employee_key_list


	def get_teacher_calendar(self,employee_key,current_teacher_calendars,updated_class_calendar) :
		for current_teacher_calendar in current_teacher_calendars :
			if current_teacher_calendar.subscriber_key == employee_key :
				return current_teacher_calendar
		else :
			employee_calendar = self.generate_employee_calendar(employee_key,updated_class_calendar)
			return employee_calendar



	def generate_employee_calendar(self,employee_key,updated_class_calendar) :
		employee_calendar=calendar.Calendar(None)
		employee_calendar.calendar_date = updated_class_calendar.calendar_date
		employee_calendar.calendar_key = key.generate_key(16)
		employee_calendar.institution_key = updated_class_calendar.institution_key
		employee_calendar.subscriber_key = employee_key
		employee_calendar.subscriber_type = 'EMPLOYEE'
		employee_calendar.events = []
		return employee_calendar




	def get_class_session_events(self,updated_class_calendar) :
		class_session_events = []
		if hasattr(updated_class_calendar,'events') :
			for event in updated_class_calendar.events :
				if event.event_type == 'CLASS_SESSION' :
					class_session_events.append(event)
		return class_session_events


	def get_employee_key(self,params) :
		for param in params :
			if param.key == 'teacher_emp_key' :
				return param.value

	def get_subject_key(self,params) :
		for param in params :
			if param.key == 'subject_key' :
				return param.value




	def get_events_from_class_calendars(self,current_class_calendars_with_day_code,period_code) :
		events_list = []
		for current_class_calendar in current_class_calendars_with_day_code :
			if hasattr(current_class_calendar,'events') :
				for event in current_class_calendar.events :
					if (self.is_event_with_period_code(event,period_code)) == True :
						events_list.append(event)
		return events_list

			
	def is_event_with_period_code(self,event,period_code) :
		for param in event.params :
			if(param.key == 'period_code') and param.value == period_code :
				return True		

	
	def update_current_class_calendar_with_day_code(self,period_code,updated_timetable,current_class_calendar,updated_period) :
		current_class_calendar = self.update_current_class_calendar(updated_period,current_class_calendar,period_code)
		return current_class_calendar


	def update_current_class_calendar(self,updated_period,current_class_calendar,period_code) :
		if hasattr(current_class_calendar,'events') :
			for event in current_class_calendar.events :
				if self.is_need_update_parms(event,period_code) == True :
					updated_params = self.update_params(event.params,current_class_calendar,updated_period)
					del event.params
					event.params = updated_params
		return current_class_calendar



	def update_params(self,params,current_class_calendar,updated_period) :
		period_code = updated_period.period_code
		subject_key = updated_period.subject_key
		employee_key = updated_period.employee_key
		params = []
		period_info = calendar.Param(None)
		period_info.key = 'period_code'
		period_info.value = period_code
		params.append(period_info)

		subject_info = calendar.Param(None)
		subject_info.key = 'subject_key'
		subject_info.value = subject_key
		params.append(subject_info)

		employee_info = calendar.Param(None)
		employee_info.key = 'teacher_emp_key'
		employee_info.value = employee_key
		params.append(employee_info)
		return params




	def is_need_update_parms(self,event,period_code) :
		for param in event.params :
			if(param.key == 'period_code') and param.value == period_code :
				return True		


	def get_updated_period_from_timetable(self,period_code,updated_timetable) :
		if hasattr(updated_timetable, 'timetable') and updated_timetable.timetable is not None :
			if hasattr(updated_timetable.timetable,'day_tables') and len(updated_timetable.timetable.day_tables) > 0 :
				for day in updated_timetable.timetable.day_tables :
					if hasattr(day,'periods') and len(day.periods) > 0 :
						for period in day.periods :
							if period.period_code == period_code :
								return period
					else :
						gclogger.warn('Periods not existing')

			else:
				gclogger.warn('Days_table not existing')

		else:
			gclogger.warn('Time table not existing')



	def get_current_class_calendars_with_day_code(self,day_code,current_current_class_calendars) :
		current_class_calendars_with_day_code = []
		for current_class_calendar in current_current_class_calendars :
			if (self.get_day_code_from_calendar(current_class_calendar,day_code) ) == True :
				current_class_calendars_with_day_code.append(current_class_calendar)
		return current_class_calendars_with_day_code


	def get_day_code_from_calendar(self,current_class_calendar,period_code) :
		for event in current_class_calendar.events :
			if event.params[0].key == 'period_code' and event.params[0].value[:3] == period_code :
				return True
	

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
		with open('tests/unit/fixtures/update-period-fixtures/current_lessonplans.json', 'r') as lesson_plan_list:
			current_lessonplan_json_list = json.load(lesson_plan_list)
			for current_lesson_plan in current_lessonplan_json_list :
				current_lesson_plan_list.append(lpnr.LessonPlan(current_lesson_plan))
		return current_lesson_plan_list

	def get_expected_lessonplan_list(self) :
		expected_lesson_plan_list =[]
		with open('tests/unit/fixtures/update-period-fixtures/expected_lessonplans.json', 'r') as lesson_plan_list:
			expected_lessonplan_json_list = json.load(lesson_plan_list)
			for expected_lesson_plan in expected_lessonplan_json_list :
				expected_lesson_plan_list.append(lpnr.LessonPlan(expected_lesson_plan))
		return expected_lesson_plan_list

	def get_updated_timetable(self):
		with open('tests/unit/fixtures/update-period-fixtures/updated_timetable.json', 'r') as timetable:
			timetable = json.load(timetable)
		return ttable.TimeTable(timetable)

	
	def get_current_class_calendar_list(self) :
		current_class_calendars = []
		with open('tests/unit/fixtures/update-period-fixtures/current_class_calendars.json', 'r') as calendar_list:
			class_calendars_dict = json.load(calendar_list)
		for class_cal in class_calendars_dict :
			current_class_calendars.append(calendar.Calendar(class_cal))
		return current_class_calendars

	def get_current_teacher_calendar_list(self) :
		current_teacher_calendars = []
		with open('tests/unit/fixtures/update-period-fixtures/current_teacher_calendars.json', 'r') as calendar_list:
			teacher_calendars_dict = json.load(calendar_list)
		for teacher_cal in teacher_calendars_dict :
			current_teacher_calendars.append(calendar.Calendar(teacher_cal))
		return current_teacher_calendars


	def get_expected_teacher_calendar_list(self) :
		expected_teacher_calendars = []
		with open('tests/unit/fixtures/update-period-fixtures/expected_teacher_calendars.json', 'r') as calendar_list:
			teacher_calendars_dict = json.load(calendar_list)
		for teacher_cal in teacher_calendars_dict :
			expected_teacher_calendars.append(calendar.Calendar(teacher_cal))
		return expected_teacher_calendars


	def get_expected_class_calendar_list(self) :
		expected_class_calendars = []
		with open('tests/unit/fixtures/update-period-fixtures/expected_class_calendars.json', 'r') as calendar_list:
			class_calendars_dict = json.load(calendar_list)
		for class_cal in class_calendars_dict :
			expected_class_calendars.append(calendar.Calendar(class_cal))
		return expected_class_calendars

if __name__ == '__main__':
	unittest.main()
