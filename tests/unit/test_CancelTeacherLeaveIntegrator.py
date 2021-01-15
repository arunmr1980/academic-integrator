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
import academics.lessonplan.LessonplanIntegrator as lessonplan_integrator
import academics.leave.Leave as leave
import academics.leave.LeaveIntegrator as leave_integrator
import academics.exam.Exam as exam
import pprint
import copy
import academics.timetable.KeyGeneration as key
pp = pprint.PrettyPrinter(indent=4)

class CancelLeaveIntegratorTest(unittest.TestCase):


	def test_calendars_and_lessonplan(self) :
		leave_key = 'test-leave-key-1'
		removed_events = []
		events_with_sub_key = {}
		class_cals_to_be_updated = []
		updated_class_calendars_list = []
		expected_teacher_calendar_dict = {}
		timetables = self.get_timetables_list()
		expected_teacher_calendars_list = self.get_expected_teacher_calendars_list()
		expected_lessonplans_list = self.get_expected_lessonplans_list()
		expected_class_calendars_list = self.get_expected_class_calendars_list()
		for teacher_calendar in expected_teacher_calendars_list :
			calendar_date = teacher_calendar.calendar_date
			subscriber_key = teacher_calendar.subscriber_key
			expected_teacher_calendar_dict[calendar_date + subscriber_key] = teacher_calendar
		current_class_calendars_list= self.get_current_class_calendars_list()
		current_teacher_calendars_list = self.get_current_teacher_calendars_list()
		current_lessonplans_list = self.get_current_lessonplans_list()
		current_teacher_leaves_list = self.get_current_teacher_leaves_list()
		from_time = None
		to_time = None
		leave = self.get_leave(leave_key,current_teacher_leaves_list)
		if hasattr(leave,"from_time") :
			from_time = leave.from_time
		if hasattr(leave,"to_time") :
			to_time = leave.to_time
		if hasattr(leave, 'status') and leave.status =='CANCELLED':
			employee_key = leave.subscriber_key
			
			from_date = leave.from_date
			to_date = leave.to_date
			teacher_cals = self.get_teacher_calendars_on_dates(from_date,to_date,employee_key,current_teacher_calendars_list)
			for teacher_calendar in teacher_cals :
				if teacher_calendar is not None :
					for event in teacher_calendar.events :
						calendar_key = event.ref_calendar_key
						event_code = event.event_code
						current_class_calendar = self.get_class_calendar_with_cal_key(calendar_key,current_class_calendars_list)
						if self.is_class_class_calendar_already_exist(class_cals_to_be_updated,current_class_calendar) == False :
							class_cals_to_be_updated.append(current_class_calendar)
						class_event = self.get_class_calendar_event(current_class_calendar,event_code,removed_events)
						if from_time is not None and to_time is not None :
							if exam_integrator.check_events_conflict(class_event.from_time,class_event.to_time,from_time,to_time) == True :
								if self.is_this_event_already_exist(current_class_calendar,class_event,removed_events) == False :
									removed_events.append(class_event)
									if current_class_calendar.subscriber_key in events_with_sub_key :
										events_with_sub_key[current_class_calendar.subscriber_key].append(class_event)
									else :
										events_with_sub_key[current_class_calendar.subscriber_key] = []
										events_with_sub_key[current_class_calendar.subscriber_key].append(class_event)
						else :
							if self.is_this_event_already_exist(current_class_calendar,class_event,removed_events) == False :
									removed_events.append(class_event)
									if current_class_calendar.subscriber_key in events_with_sub_key :
										events_with_sub_key[current_class_calendar.subscriber_key].append(class_event)
									else :
										events_with_sub_key[current_class_calendar.subscriber_key] = []
										events_with_sub_key[current_class_calendar.subscriber_key].append(class_event)




		
		self.update_class_cals_on_cancel_leave(removed_events,class_cals_to_be_updated,updated_class_calendars_list,timetables)
		school_key = updated_class_calendars_list[0].institution_key
		updated_teacher_calendars_list = self.integrate_teacher_calendars_on_cancel_leave(current_teacher_calendars_list,updated_class_calendars_list,school_key)
		current_lessonplans = self.get_lessonplans_list(events_with_sub_key.keys(),current_lessonplans_list)
		updated_lessonplans_list = leave_integrator.update_lessonplans_with_adding_events(current_lessonplans,updated_class_calendars_list,removed_events)
		for updated_teacher_calendar in updated_teacher_calendars_list :
			cal = calendar.Calendar(None)
			teacher_calendar_dict = cal.make_calendar_dict(updated_teacher_calendar)
			pp.pprint(teacher_calendar_dict)
		



		for teacher_calendar in updated_teacher_calendars_list :
			teacher_calendar_key = teacher_calendar.calendar_date + teacher_calendar.subscriber_key
			expected_teacher_calendar = expected_teacher_calendar_dict[teacher_calendar_key]

			self.assertEqual(expected_teacher_calendar.institution_key,teacher_calendar.institution_key )
			self.assertEqual(expected_teacher_calendar.calendar_date,teacher_calendar.calendar_date )
			self.assertEqual(expected_teacher_calendar.subscriber_key,teacher_calendar.subscriber_key )
			self.assertEqual(expected_teacher_calendar.subscriber_type,teacher_calendar.subscriber_type )
			# self.check_events_teacher_calendar(expected_teacher_calendar.events,teacher_calendar.events)
			gclogger.info("-----[UnitTest] teacher calendar test passed ----------------- "+ str(teacher_calendar.calendar_key)+" ------------------------------ ")

		for updated_class_calendar in current_class_calendars_list :
			cal = calendar.Calendar(None)
			class_calendar_dict = cal.make_calendar_dict(updated_class_calendar)
			pp.pprint(class_calendar_dict)
			self.check_class_calendars(updated_class_calendar,expected_class_calendars_list)

		

		for updated_lessonplan in updated_lessonplans_list :
			lp = lpnr.LessonPlan(None)
			updated_lessonplan_dict = lp.make_lessonplan_dict(updated_lessonplan)
			pp.pprint(updated_lessonplan_dict)
			self.check_lesson_plans(updated_lessonplan,expected_lessonplans_list)
 
	def integrate_teacher_calendars_on_cancel_leave(self,current_teacher_calendars_list,updated_class_calendars_list,school_key) :
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












	def update_class_cals_on_cancel_leave(self,removed_events,class_cals,updated_class_calendars_list,timetables) :
		for current_class_calendar in class_cals :
			subscriber_key = current_class_calendar.subscriber_key
			class_key = subscriber_key[:-2]
			division = subscriber_key[-1:]
			timetable = self.get_timetable_by_class_key_and_division(class_key,division,timetables)
			updated_class_calendar = leave_integrator.get_updated_class_calendar_on_cancel_leave(current_class_calendar,removed_events,timetable)
			updated_class_calendars_list.append(updated_class_calendar)


	def get_timetable_by_class_key_and_division(self,class_key,division,timetables) :
		for timetable in timetables :
			if timetable.class_key == class_key and timetable.division == division :
				return timetable

	def get_lessonplans_list(self,subscriber_key_list,current_lessonplans_list) :
		current_lessonplans =[]
		for subscriber_key in subscriber_key_list :
			class_key = subscriber_key[:-2]
			division = subscriber_key[-1:]
			lessonplans = self.get_lessonplan_by_class_key_and_division(class_key,division,current_lessonplans_list)
			current_lessonplans.extend(lessonplans)
		return current_lessonplans

	def get_lessonplan_by_class_key_and_division(self,class_key,division,current_lessonplans_list) :
		lessonplans =[]
		for lessonplan in current_lessonplans_list :
			if lessonplan.class_key == class_key and lessonplan.division == division :
				if self.is_lessonplan_already_exist(lessonplans,lessonplan) == False :
					lessonplans.append(lessonplan)
		return lessonplans

	def is_lessonplan_already_exist(self,lessonplans,lessonplan) :
		is_exist = False
		for current_lesson in lessonplans :
			if current_lesson.lesson_plan_key == lessonplan.lesson_plan_key :
				is_exist = True
		return is_exist



	def is_class_class_calendar_already_exist(self,class_cals,current_class_calendar) :
		is_exist = False
		for calendar in class_cals :
			if calendar.calendar_key == current_class_calendar.calendar_key :
				is_exist = True
		return is_exist
		
			

	def is_this_event_already_exist(self,current_class_calendar,class_event,removed_events) :
		is_already_exist = False
		for event in removed_events :
			if event.event_code == class_event.event_code and event.from_time[:10] == current_class_calendar.calendar_date :
				is_already_exist = True
		return is_already_exist


	def get_class_calendar_event(self,current_class_calendar,event_code,removed_events) :
		for event in current_class_calendar.events :
			if event.event_code == event_code :
				return event

	

	def get_class_calendar_with_cal_key(self,calendar_key,current_class_calendars_list) :
		for current_clas_calendar in current_class_calendars_list :
			if current_clas_calendar.calendar_key == calendar_key :
				return current_clas_calendar

	def get_teacher_calendars_on_dates(self,from_date,to_date,employee_key,current_teacher_calendars_list) :
		teacher_cals = []
		dates_list = timetable_integrator.get_dates(from_date,to_date)
		for cal_date in dates_list :
			teacher_calendar = self.get_teacher_calendar_with_date_and_emp_key(cal_date,employee_key,current_teacher_calendars_list)
			teacher_cals.append(teacher_calendar)
		return teacher_cals
			



	def get_teacher_calendar_with_date_and_emp_key(self,cal_date,employee_key,current_teacher_calendars_list) :
		for current_teacher_calendar in current_teacher_calendars_list :
			if current_teacher_calendar.calendar_date == cal_date and current_teacher_calendar.subscriber_key == employee_key :
				return  current_teacher_calendar

	def get_leave(self,leave_key,current_teacher_leaves_list) :
		for teacher_leave in current_teacher_leaves_list :
			if teacher_leave.leave_key == leave_key :
				return teacher_leave


	
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


	def get_timetables_list(self) :
		timetable_list = []
		with open('tests/unit/fixtures/cancel-leave-fixtures/test_timetables_list.json', 'r') as test_timetables_list:
			timetables_dict = json.load(test_timetables_list)
			for timetable in timetables_dict :
				timetable_list.append(ttable.TimeTable(timetable))
		return timetable_list

	def get_current_lessonplans_list(self) :
		current_lessonplans = []
		with open('tests/unit/fixtures/cancel-leave-fixtures/current_lessonplans_list.json', 'r') as lessonplans_list:
			lessonplans_list_dict = json.load(lessonplans_list)
		for lessonplan in lessonplans_list_dict :
			current_lessonplans.append(lpnr.LessonPlan(lessonplan))
		return current_lessonplans

	def get_current_teacher_calendars_list(self) :
		current_teacher_calendars = []
		with open('tests/unit/fixtures/cancel-leave-fixtures/current_teacher_calendars_list.json', 'r') as calendar_list:
			class_calendars_dict = json.load(calendar_list)
		for class_cal in class_calendars_dict :
			current_teacher_calendars.append(calendar.Calendar(class_cal))
		return current_teacher_calendars

	def get_current_class_calendars_list(self) :
		current_class_calendars = []
		with open('tests/unit/fixtures/cancel-leave-fixtures/current_class_calendars_list.json', 'r') as calendar_list:
			class_calendars_dict = json.load(calendar_list)
		for class_cal in class_calendars_dict :
			current_class_calendars.append(calendar.Calendar(class_cal))
		return current_class_calendars

	def get_current_teacher_leaves_list(self) :
		current_teacher_leaves = []
		with open('tests/unit/fixtures/cancel-leave-fixtures/current_teacher_leaves_list.json', 'r') as leaves_list:
			teacher_leaves_dict = json.load(leaves_list)
		for teacher_leave in teacher_leaves_dict :
			current_teacher_leaves.append(leave.Leave(teacher_leave))
		return current_teacher_leaves


	def get_expected_class_calendars_list(self) :
		expected_class_calendars = []
		with open('tests/unit/fixtures/cancel-leave-fixtures/expected_class_calendars_list.json', 'r') as calendar_list:
			class_calendars_dict = json.load(calendar_list)
		for class_cal in class_calendars_dict :
			expected_class_calendars.append(calendar.Calendar(class_cal))
		return expected_class_calendars

	def get_expected_teacher_calendars_list(self) :
		expected_teacher_calendars = []
		with open('tests/unit/fixtures/cancel-leave-fixtures/expected_teacher_calendars_list.json', 'r') as calendar_list:
			teacher_calendars_dict = json.load(calendar_list)
		for teacher_cal in teacher_calendars_dict :
			expected_teacher_calendars.append(calendar.Calendar(teacher_cal))
		return expected_teacher_calendars

	def get_expected_lessonplans_list(self) :
		expected_lessonplans = []
		with open('tests/unit/fixtures/cancel-leave-fixtures/expected_lessonplans_list.json', 'r') as lessonplan_list:
			lessonplans_dict = json.load(lessonplan_list)
		for lessonplan in lessonplans_dict :
			expected_lessonplans.append(lpnr.LessonPlan(lessonplan))
		return expected_lessonplans

	


if __name__ == '__main__':
	unittest.main()
