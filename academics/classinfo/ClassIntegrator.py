import academics.calendar.CalendarDBService as calendar_service
import academics.calendar.Calendar as cldr
from datetime import datetime as dt
from academics.logger import GCLogger as gclogger
import academics.academic.AcademicDBService as academic_service
import academics.classinfo.ClassInfoDBService as class_info_service
import academics.timetable.TimeTableDBService as timetable_service
from academics.TimetableIntegrator import *
import academics.TimetableIntegrator as timetable_integrator
from academics.lessonplan.LessonplanIntegrator import *
import academics.lessonplan.LessonPlan as lpnr
import pprint
pp = pprint.PrettyPrinter(indent=4)
import copy


def get_subject_teachers_from_class_info(class_div) :
	subject_teachers_list = []
	for subject_teacher in class_div.subject_teachers :
		if check_employee_key_already_exist(subject_teacher.teacher_employee_key,subject_teachers_list) == False :
			subject_teachers_list.append(subject_teacher.teacher_employee_key)
	return subject_teachers_list


def get_division_from_class_info(class_info,division) :
	for div in class_info.divisions :
		if div.code == division and div.name == division :
			return div

def check_employee_key_already_exist(teacher_employee_key,subject_teachers_list) :
	is_exist = False 
	for employee_key in subject_teachers_list :
		if employee_key == teacher_employee_key :
			is_exist = True
	return is_exist
