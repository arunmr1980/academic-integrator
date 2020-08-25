import unittest
import json
from academics.TimetableIntegrator import integrate_class_timetable,integrate_teacher_timetable
from academics.timetable import AcademicConfiguration as academic_config
import academics.timetable.TimeTable as ttable 
from academics.logger import GCLogger as gclogger
import academics.calendar.Calendar as calendar
import pprint 
pp = pprint.PrettyPrinter(indent=4)



class LessonplanIntegratorTest(unittest.TestCase):


	def test_lessonplan(self) :
		current_lesson_plan_list = self.get_current_lesson_plan_list()
		time_table=self.get_time_table()
		academic_configuration=self.get_academic_configuration()
		generated_class_calendar_dict = integrate_class_timetable(time_table,academic_configuration)
		for generated_class_calendar in generated_class_calendar_dict.values() :
			if hasattr(generated_class_calendar ,'events') :
				for event in generated_class_calendar.events :
					subject_code = self.get_subject_code(event)
					current_lesson_plan = self.get_lesson_plan(subject_code)
					if current_lesson_plan is None :
						gclogger.info('----Lesson plan not found for '+str(subject_code) +'----')
						return
					else :
						pass






	def get_lesson_plan(subject_code) :
		for current_lesson_plan in current_lesson_plan_list :
			if hasattr(current_lesson_plan,'subject_code') :
				return current_lesson_plan
			else :
				return None


	def get_subject_code(self,event) :
		if hasattr(event, 'params') :
			for param in event.params :
				if param.key == 'subject_key' :
					return param.values
		else :
			gclogger.info('Params not found for event')
						
	
	def get_current_lesson_plan_list(self) :
		with open('tests/unit/fixtures/current_lessonplan.json', 'r') as lesson_plan_list:
			teacher_calendar_dict_list = json.load(lesson_plan_list)
		return lesson_plan_list_list

	def get_teacher_calendar_list(self) :
		with open('tests/unit/fixtures/teacher_calendar_list.json', 'r') as calendar_list:
			teacher_calendar_dict_list = json.load(calendar_list)
		return teacher_calendar_dict_list

	def get_calendar_list(self) :
		with open('tests/unit/fixtures/class_calendar_list.json', 'r') as calendar_list:
			class_calendar_dict_list = json.load(calendar_list)	
		return class_calendar_dict_list


	def get_time_table(self):
		with open('tests/unit/fixtures/timetable.json', 'r') as timetable:
			timetable = json.load(timetable)	
		return ttable.TimeTable(timetable)


	def get_academic_configuration(self):
		with open('tests/unit/fixtures/academic_configuration.json', 'r') as academic_configuration:
			academic_configuration_dict = json.load(academic_configuration)
			academic_configuration = academic_config.AcademicConfiguration(academic_configuration_dict)
		return academic_configuration



if __name__ == '__main__':
    unittest.main()







