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
		exam_events = self.make_exam_ecvents(exams_list)
		for exam_event in exam_events :



#code to be moved to integration algorithm
	def make_exam_events(self,exams_list) :
		exam_events = []
		for exam_info in exams_list :
			exam_event = calendar.Event(None)
			event.event_code = key.generate_key(3)
			event.event_type = 'EXAM'
			event.from_time = exam_info.from_time
			event.to_time = exam_info.to_time
			event.params = self.get_params()



	# def get_standard_time(self,time,date) :
	# 	splited_date = date.split('-')
	# 	splited_date = list(map(int,splited_date))
	# 	time_hour = int(time[0:2])
	# 	time_minute = int(time[3:5])
	# 	return datetime.datetime(splited_date[0],splited_date[1],splited_date[2],time_hour,time_minute).isoformat()


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
