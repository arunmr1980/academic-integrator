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
import academics.exam.Exam as exam
import pprint
import copy 
import academics.timetable.KeyGeneration as key
pp = pprint.PrettyPrinter(indent=4)

class AddExamIntegratorTest(unittest.TestCase):

		
	def test_calendars_and_lessonplan(self) :
		updated_class_calendars_list = []
		updated_teacher_calendars_list = []
		current_class_calendars_list = self.get_current_class_calendars_list()
		exams_list = self.get_exams_list()
		exam_events = self.make_exam_events(exams_list)

		for current_class_calendar in current_class_calendars_list :
			print("CURRENT CALENDAR ---- ",current_class_calendar.calendar_key)
			updated_class_calendar = self.update_class_calendar_with_exam_events(current_class_calendar,exam_events)
			updated_class_calendars_list.append(updated_class_calendar)
		for i in updated_class_calendars_list :
			cal = calendar.Calendar(None)
			class_calendar_dict = cal.make_calendar_dict(i)
			pp.pprint(class_calendar_dict)

		

	
	#code to be moved to integration algorithm
	def update_class_calendar_with_exam_events(self,current_class_calendar,exam_events) :
		updated_class_calendar = self.remove_conflicted_class_events(exam_events,current_class_calendar)	
		return current_class_calendar


	def remove_conflicted_class_events(self,exam_events,current_class_calendar) :
		for exam_event in exam_events :
			updated_class_calendar = self.update_class_calendar_events(exam_event,current_class_calendar)
		return updated_class_calendar

		
	def update_class_calendar_events(self,exam_event,current_class_calendar) :
		print(exam_event.from_time,exam_event.to_time," ------ EXAM EVENT")
		updated_events = []
		for calendar_event in current_class_calendar.events :
			print(calendar_event.from_time,'--',calendar_event.to_time)
			if self.check_events_conflict(exam_event.from_time,exam_event.to_time,calendar_event.from_time,calendar_event.to_time) == True :
				if exam_event not in updated_events :
					updated_events.append(exam_event)
			else :
				updated_events.append(calendar_event)
		del current_class_calendar.events
		current_class_calendar.events = updated_events
		return current_class_calendar




	def check_events_conflict(self,event_start_time,event_end_time,class_calendar_event_start_time,class_calendar_event_end_time) :
		is_conflict = None
		event_start_time_year = int(event_start_time[:4])
		event_start_time_month = int(event_start_time[5:7])
		event_start_time_day = int(event_start_time[8:10])
		event_start_time_hour = int(event_start_time[11:13])
		event_start_time_min = int(event_start_time[14:16])
		event_start_time_sec = int(event_start_time[-2:])

		event_end_time_year = int(event_end_time[:4])
		event_end_time_month = int(event_end_time[5:7])
		event_end_time_day = int(event_end_time[8:10])
		event_end_time_hour = int(event_end_time[11:13])
		event_end_time_min = int(event_end_time[14:16])
		event_end_time_sec = int(event_end_time[-2:])

		class_calendar_event_start_time_year = int(class_calendar_event_start_time[:4])
		class_calendar_event_start_time_month = int(class_calendar_event_start_time[5:7])
		class_calendar_event_start_time_day = int(class_calendar_event_start_time[8:10])
		class_calendar_event_start_time_hour = int(class_calendar_event_start_time[11:13])
		class_calendar_event_start_time_min = int(class_calendar_event_start_time[14:16])
		class_calendar_event_start_time_sec = int(class_calendar_event_start_time[-2:])

		class_calendar_event_end_time_year = int(class_calendar_event_end_time[:4])
		class_calendar_event_end_time_month = int(class_calendar_event_end_time[5:7])
		class_calendar_event_end_time_day = int(class_calendar_event_end_time[8:10])
		class_calendar_event_end_time_hour = int(class_calendar_event_end_time[11:13])
		class_calendar_event_end_time_min = int(class_calendar_event_end_time[14:16])
		class_calendar_event_end_time_sec = int(class_calendar_event_end_time[-2:])

		class_calendar_event_start_time = dt(class_calendar_event_start_time_year, class_calendar_event_start_time_month, class_calendar_event_start_time_day, class_calendar_event_start_time_hour, class_calendar_event_start_time_min, class_calendar_event_start_time_sec, 000000)
		class_calendar_event_end_time = dt(class_calendar_event_end_time_year, class_calendar_event_end_time_month, class_calendar_event_end_time_day, class_calendar_event_end_time_hour, class_calendar_event_end_time_min, class_calendar_event_end_time_sec, 000000)
		event_start_time = dt(event_start_time_year, event_start_time_month, event_start_time_day, event_start_time_hour, event_start_time_min, event_start_time_sec, 000000)
		event_end_time = dt(event_end_time_year, event_end_time_month, event_end_time_day, event_end_time_hour, event_end_time_min, event_end_time_sec, 000000)

		delta = max(event_start_time,class_calendar_event_start_time) - min(event_end_time,class_calendar_event_end_time)
		if delta.days < 0 :
			is_conflict = True
		else :
			is_conflict = False
		return is_conflict

	def make_exam_events(self,exams_list) :
		exam_events = []
		for exam_info in exams_list :
			exam_event = calendar.Event(None)
			exam_event.event_code = key.generate_key(3)
			exam_event.event_type = 'EXAM'
			exam_event.from_time = get_standard_time(exam_info.from_time,exam_info.date_time)
			exam_event.to_time = get_standard_time(exam_info.to_time,exam_info.date_time)
			exam_event.params = self.get_params()
			exam_events.append(exam_event)
		return exam_events



	def get_standard_time(self,time,date) :
		splited_date = date.split('-')
		splited_date = list(map(int,splited_date))
		time_hour = int(time[0:2])
		time_minute = int(time[3:5])
		return datetime.datetime(splited_date[0],splited_date[1],splited_date[2],time_hour,time_minute).isoformat()


	def get_params(self) :
		params = []
		period_info = calendar.Param(None)
		period_info.key = 'is_cancel_flag'
		period_info.value = 'true'
		params.append(period_info)
		return params

	def get_current_class_calendars_list(self) :
		current_class_calendars = []
		with open('tests/unit/fixtures/add-exams-fixtures/current_class_calendars_list.json', 'r') as calendar_list:
			class_calendars_dict = json.load(calendar_list)
		for class_cal in class_calendars_dict :
			current_class_calendars.append(calendar.Calendar(class_cal))
		return current_class_calendars

	def get_exams_list(self) :
		exams_list = []
		with open('tests/unit/fixtures/add-exams-fixtures/exams_list.json', 'r') as exam_list:
			exams_list_dict = json.load(exam_list)
		for exam_dict in exams_list_dict :
			exams_list.append(exam.Exam(exam_dict))
		return exams_list

	

if __name__ == '__main__':
	unittest.main()
