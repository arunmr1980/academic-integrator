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
import academics.calendar.CalendarIntegrator as calendar_integrator
import academics.lessonplan.LessonplanIntegrator as lessonplan_integrator
import academics.TimetableIntegrator as timetable_integrator
import academics.leave.LeaveIntegrator as leave_integrator
import pprint
import copy
import academics.timetable.KeyGeneration as key
pp = pprint.PrettyPrinter(indent=4)

class UpdateSubjectTeacherIntegratorTest(unittest.TestCase):


	def test_lessonplans(self) :
		updated_class_calendars_list = self.get_updated_class_calendars_list()
		current_lessonplans_list = self.get_current_lessonplans_list()
		calendar_key = 'test-key-3'
		events = [
			{
	      		"event_code": "event-8" 
		    },
		    {
		    	"event_code": "event-9" 
		    }
		]
		updated_calendar = self.get_updated_class_calendar(updated_class_calendars_list,calendar_key)
		subscriber_key = updated_calendar.subscriber_key
		class_key = subscriber_key[:-2]
		division = subscriber_key[-1:]
		events_to_be_added = self.get_event_code_list(events,calendar_key,updated_calendar)
		for event in events_to_be_added :
			subject_key = timetable_integrator.get_subject_code(event)
			current_lessonplan = leave_integrator.get_current_lessonplan(current_lessonplans_list,subject_key,class_key,division)

			updated_lessonplan = lessonplan_integrator.integrate_add_class_session_events(event,calendar_key,current_lessonplan)



	def get_updated_class_calendar(self,updated_class_calendars_list,calendar_key) :
		for calendar in updated_class_calendars_list :
			if calendar.calendar_key == calendar_key :
				return calendar 

	def get_event_code_list(self,events,calendar_key,updated_calendar) :
		events_to_be_added = []
		for event in events :
			updated_event = self.get_added_event(event['event_code'],updated_calendar)
			events_to_be_added.append(updated_event)
		return events_to_be_added

	def get_added_event(self,event_code,updated_calendar) :
		for event in updated_calendar.events :
			if event.event_code == event_code :
				return event 

	def get_current_lessonplans_list(self) :
		current_lessonplans = []
		with open('tests/unit/fixtures/add-class-session-events-fixtures/current_lessonplans_list.json', 'r') as lessonplans_list:
			lessonplans_list_dict = json.load(lessonplans_list)
		for lessonplan in lessonplans_list_dict :
			current_lessonplans.append(lpnr.LessonPlan(lessonplan))
		return current_lessonplans

	def get_updated_class_calendars_list(self) :
		updated_class_calendars = []
		with open('tests/unit/fixtures/add-class-session-events-fixtures/updated_class_calendars_list.json', 'r') as calendar_list:
			class_calendars_dict = json.load(calendar_list)
		for class_cal in class_calendars_dict :
			updated_class_calendars.append(calendar.Calendar(class_cal))
		return updated_class_calendars
		
if __name__ == '__main__':
	unittest.main()
