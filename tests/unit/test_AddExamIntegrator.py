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
from academics.exam.ExamIntegrator import integrate_add_exams
import academics.exam.Exam as exam
import pprint
import copy 
import academics.timetable.KeyGeneration as key
pp = pprint.PrettyPrinter(indent=4)

class AddExamIntegratorTest(unittest.TestCase):

		
	def test_calendars_and_lessonplan(self) :
		series_code = "NEG111"
		class_key = "8B1B22E72AE"
		division = "A"
		subscriber_key = class_key + '-' + division
		updated_class_calendars_list = []
		updated_teacher_calendars_list = []
		updated_lessonplans_list = []
		removed_events = []

		current_class_calendars = self.get_current_class_calendars_list()
		current_teacher_calendars_list = self.get_current_teacher_calendars_list()
		current_lessonplans_list = self.get_current_lessonplans_list()
		current_class_calendars_list = self.current_class_calendars_perticular_class(subscriber_key,current_class_calendars)
		current_cls_calendars = copy.deepcopy(current_class_calendars_list)
		exams = self.get_exams_list()
		exams_list = self.perticular_exams_for_perticular_class(exams,class_key,division,series_code)
		integrate_add_exams(
							updated_class_calendars_list,
							updated_teacher_calendars_list,
							updated_lessonplans_list,
							current_class_calendars_list,
							current_teacher_calendars_list,
							current_lessonplans_list,
							exams_list,
							removed_events
							)
	def current_class_calendars_perticular_class(self,subscriber_key,current_class_calendars) :
		current_class_calendars_list =[]
		for current_class_calendar in current_class_calendars:
			if current_class_calendar.subscriber_key == subscriber_key :
				current_class_calendars_list.append(current_class_calendar)
		return current_class_calendars_list

	def perticular_exams_for_perticular_class(self,exams,class_key,division,series_code) :
		exams_list =[]
		for exam in exams :
			if exam.division == division and exam.class_key == class_key and exam.series_code == series_code :
				exams_list.append(exam)
		return exams_list



	



	

	def get_current_lessonplans_list(self) :
		current_lessonplans = []
		with open('tests/unit/fixtures/add-exams-fixtures/current_lessonplans_list.json', 'r') as lessonplans_list:
			lessonplans_list_dict = json.load(lessonplans_list)
		for lessonplan in lessonplans_list_dict :
			current_lessonplans.append(lpnr.LessonPlan(lessonplan))
		return current_lessonplans

	def get_current_teacher_calendars_list(self) :
		current_teacher_calendars = []
		with open('tests/unit/fixtures/add-exams-fixtures/current_teacher_calendars_list.json', 'r') as calendar_list:
			class_calendars_dict = json.load(calendar_list)
		for class_cal in class_calendars_dict :
			current_teacher_calendars.append(calendar.Calendar(class_cal))
		return current_teacher_calendars

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
