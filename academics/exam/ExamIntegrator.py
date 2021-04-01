from datetime import date, timedelta
import datetime
from datetime import datetime as dt
import calendar as cal
import academics.timetable.TimeTableDBService as timetable_service
from academics import TimetableIntegrator as timetable_integrator
from academics.logger import GCLogger as gclogger
import academics.timetable.TimeTable as ttable
import academics.timetable.KeyGeneration as key
import academics.calendar.Calendar as calendar
import academics.academic.AcademicDBService as academic_service
import academics.calendar.CalendarDBService as calendar_service
import academics.calendar.CalendarIntegrator as calendar_integrator
import academics.timetable.KeyGeneration as key
import academics.classinfo.ClassInfoDBService as class_info_service
import academics.calendar.Calendar as calendar
from academics.lessonplan.LessonplanIntegrator import *
import academics.lessonplan.LessonplanIntegrator as lessonplan_integrator
from academics.exam import ExamDBService as exam_service
from academics.exam import SQSService as sqs_service
from academics.lessonplan import LessonplanDBService as lessonplan_service
import academics.academic.AcademicDBService as academic_service
import academics.lessonplan.LessonPlan as lpnr
import academics.lessonplan.LessonplanIntegrator as lesssonplan_integrator
import academics.classinfo.ClassInfoDBService as classinfo_service
import copy
import pprint
pp = pprint.PrettyPrinter(indent=4)

def integrate_cancel_exam(exam_series_list,school_key,academic_year) :
	events_to_be_added = []
	exam_series = make_exam_series_objects(exam_series_list)
	for clazz in exam_series.classes :	
		exams_list = perticular_exams_for_perticular_classes(clazz,exam_series.code)
		current_class_calendars_list = get_affected_class_calendars_list(exams_list)
		if len(current_class_calendars_list) > 0 :
			current_lessonplans_list = get_current_lessonplans(exam_series.classes)
			updated_class_calendars_list = get_updated_class_calendars_list_on_cancel_exam(current_class_calendars_list,exam_series.code,events_to_be_added)
			current_teacher_calendars_list = get_current_teacher_calendars_from_current_class_calendars(current_class_calendars_list,school_key)
			updated_teacher_calendars_list = integrate_teacher_calendars_on_update_exam_and_cancel_exam(current_teacher_calendars_list,updated_class_calendars_list,school_key)
			save_calendars(updated_class_calendars_list,updated_teacher_calendars_list)
	message_body = {
		"request_type" : "NOTIFY_DELETE_EXAM",
		"school_key" : school_key,
		"academic_year" : academic_year,
		"exam_series" : exam_series_list

	}
	sqs_service.send_to_sqs(message_body)

def save_calendars(updated_class_calendars_list,updated_teacher_calendars_list) :
	for updated_class_calendar in updated_class_calendars_list :
		cal = calendar.Calendar(None)
		class_calendar_dict = cal.make_calendar_dict(updated_class_calendar)
		pp.pprint(class_calendar_dict)
		response = calendar_service.add_or_update_calendar(class_calendar_dict)
		gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' ------- A updated class calendar uploaded --------- '+str(class_calendar_dict['calendar_key']))

	for updated_teacher_calendar in updated_teacher_calendars_list :
		cal = calendar.Calendar(None)
		teacher_calendar_dict = cal.make_calendar_dict(updated_teacher_calendar)
		response = calendar_service.add_or_update_calendar(teacher_calendar_dict)
		gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' ------- A updated teacher calendar uploaded --------- '+str(class_calendar_dict['calendar_key']))


def perticular_exams_for_perticular_classes(clazz,series_code) :
	exams_list = []
	division = clazz.division
	class_key = clazz.class_key
	exams = exam_service.get_all_exams_by_class_key_and_series_code(class_key, series_code)
	exams_of_division = get_exams_of_division(exams,division)
	exams_list.extend(exams_of_division)
	return exams_list

def get_exams_of_division(exams,division) :
	exams_of_division = []
	for exam in exams :
		if exam.division == division :
			exams_of_division.append(exam)
	return exams_of_division

def get_current_lessonplans(classes) :
	current_lessonplans_list =[]
	for clazz in classes :
		division = clazz.division
		class_key = clazz.class_key
		current_lessonplans = lessonplan_service.get_lesson_plan_list(class_key, division)
		current_lessonplans_list.extend(current_lessonplans) 
	return current_lessonplans_list



def get_affected_class_calendars_list(exams_list) :
	current_class_calendars_list = []
	for exam in exams_list :
		division = exam.division
		class_key = exam.class_key
		subscriber_key = class_key + '-' + division
		date = exam.date_time
		current_class_calendar = calendar_service.get_calendar_by_date_and_key(date,subscriber_key)
		if current_class_calendar is not None and check_calendar_already_in_list(current_class_calendars_list,current_class_calendar) == False :
			current_class_calendars_list.append(current_class_calendar)
		if hasattr(exam,'previous_schedule') :
			calendar_date = exam.previous_schedule.date_time
			current_class_calendar = calendar_service.get_calendar_by_date_and_key(calendar_date, subscriber_key)
			if check_calendar_already_exist(current_class_calendar,current_class_calendars_list) == False :
				current_class_calendars_list.append(current_class_calendar)
	return current_class_calendars_list


def check_calendar_already_in_list(current_class_calendars_list,current_class_calendar) :
	is_calendar_exist = False
	for calendar in current_class_calendars_list :
		if calendar.calendar_key == current_class_calendar.calendar_key :
			is_calendar_exist = True
	return is_calendar_exist





def make_exam_series_objects(exam_series) :
		exam_series = ExamSeries(exam_series[0])
		return exam_series
		
def integrate_update_exam_on_calendar(series_code,class_key,division) :
	subscriber_key = class_key + '-' + division
	updated_class_calendars_list = []
	updated_teacher_calendars_list = []
	updated_lessonplans_list = []
	removed_events = []
	exams_list = exam_service.get_all_exams_by_class_key_and_series_code(class_key, series_code)
	
	timetable = timetable_service.get_timetable_by_class_key_and_division(class_key,division)
	school_key = timetable.school_key
	academic_year = timetable.academic_year
	academic_configuration = academic_service.get_academig(school_key,academic_year)
	events_to_be_added = []
	current_class_calendars_list = get_updated_current_class_calendars_from_exam_and_schedule(exams_list)
	current_teacher_calendars_list = get_current_teacher_calendars_from_current_class_calendars(current_class_calendars_list,school_key)
	current_lessonplans_list = lessonplan_service.get_lesson_plan_list(class_key,division)
	current_class_calendars_list = integrate_class_calendar_on_update_exams(academic_configuration,timetable,exams_list,current_class_calendars_list,events_to_be_added)
	current_teacher_calendars_list = integrate_teacher_calendars_on_update_exam_and_cancel_exam(current_teacher_calendars_list,current_class_calendars_list,school_key)



	# current_lessonplans_list = integrate_lessonplans_on_update_exams(current_lessonplans_list,current_class_calendars_list)
	current_lessonplans_list = integrate_lessonplans_on_update_exams_and_cancel_exam(current_lessonplans_list,events_to_be_added)
	updated_class_calendars_list = integrate_class_calendar_on_add_exams(academic_configuration,timetable,updated_class_calendars_list,exams_list,current_class_calendars_list,removed_events)

	integrate_teacher_cal_and_lessonplan_on_add_exam(
							updated_class_calendars_list,
							updated_teacher_calendars_list,
							updated_lessonplans_list,
							current_class_calendars_list,
							current_teacher_calendars_list,
							current_lessonplans_list,
							exams_list,
							removed_events
							)


	save_updated_calendars_and_lessonplans(updated_class_calendars_list,updated_teacher_calendars_list,updated_lessonplans_list)


def integrate_update_exam(series_code,class_info_key,division) :
	timetable = timetable_service.get_timetable_by_class_key_and_division(class_info_key,division)
	academic_year = timetable.academic_year
	school_key = timetable.school_key
	exam_series = [
	      {
	        "classes": [
	          {
	            "class_key": class_info_key,
	            "division": division
	          }
	        ],
	        "code": series_code,
	        "name": "sample"
	      }
	]
	integrate_cancel_exam(exam_series,school_key,academic_year)
	integrate_add_exam_on_calendar(series_code,class_info_key,division)


def save_updated_calendars_and_lessonplans(updated_class_calendars_list,updated_teacher_calendars_list,updated_lessonplans_list) :
	for updated_class_calendar in updated_class_calendars_list :
		cal = calendar.Calendar(None)
		class_calendar_dict = cal.make_calendar_dict(updated_class_calendar)
		# pp.pprint(class_calendar_dict)
		response = calendar_service.add_or_update_calendar(class_calendar_dict)
		gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' ------- A updated class calendar uploaded --------- '+str(class_calendar_dict['calendar_key']))

	for updated_teacher_calendar in updated_teacher_calendars_list :
		cal = calendar.Calendar(None)
		teacher_calendar_dict = cal.make_calendar_dict(updated_teacher_calendar)
		response = calendar_service.add_or_update_calendar(teacher_calendar_dict)
		gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' ------- A updated teacher calendar uploaded --------- '+str(class_calendar_dict['calendar_key']))

	for updated_lessonplan in updated_lessonplans_list :
		cal = lpnr.LessonPlan(None)
		lessonplan_dict = cal.make_lessonplan_dict(updated_lessonplan)
		response = lessonplan_service.create_lessonplan(lessonplan_dict)
		gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' ------- A updated lessonplan uploaded --------- '+str(lessonplan_dict['lesson_plan_key']))


def get_affected_class_calendars(exams_list) :
	current_class_calendar = None
	current_class_calendars_list = []
	for exam in exams_list :
		class_key = exam.class_key
		division = exam.division
		subscriber_key = class_key + '-' + division
		calendar_date = exam.date_time
		institution_key = exam.institution_key
		current_class_calendar = calendar_service.get_calendar_by_date_and_key(calendar_date, subscriber_key)
		if current_class_calendar is None :
			current_class_calendar = calendar_integrator.generate_class_calendar(class_key,division,calendar_date,institution_key)
		if 	check_calendar_already_exist(current_class_calendar,current_class_calendars_list) == False :
			current_class_calendars_list.append(current_class_calendar)
	return current_class_calendars_list

def get_updated_current_class_calendars_from_exam_and_schedule(exams_list) :
	current_class_calendars_list = []
	for exam in exams_list :
		subscriber_key = exam.class_key + '-' + exam.division
		calendar_date = exam.date_time
		current_class_calendar = calendar_service.get_calendar_by_date_and_key(calendar_date, subscriber_key)
		if 	check_calendar_already_exist(current_class_calendar,current_class_calendars_list) == False :
			current_class_calendars_list.append(current_class_calendar)
		if hasattr(exam,'previous_schedule') :
			calendar_date = exam.previous_schedule.date_time
			current_class_calendar = calendar_service.get_calendar_by_date_and_key(calendar_date, subscriber_key)
			if check_calendar_already_exist(current_class_calendar,current_class_calendars_list) == False :
				current_class_calendars_list.append(current_class_calendar)
	return current_class_calendars_list

def get_current_teacher_calendars_from_current_class_calendars(current_class_calendars_list,school_key) :
	current_teacher_calendars_list = []
	for current_class_calendar in current_class_calendars_list :
		for event in current_class_calendar.events :
			calendar_date = current_class_calendar.calendar_date
			employee_key = timetable_integrator.get_employee_key(event.params)
			if employee_key is not None :
				current_teacher_calendar = get_teacher_calendar(current_teacher_calendars_list,calendar_date,employee_key,school_key)
				emp_event = make_employee_event(event,current_class_calendar)
				if is_calendar_already_exist(current_teacher_calendar,current_teacher_calendars_list) == False :
					current_teacher_calendars_list.append(current_teacher_calendar)
	return current_teacher_calendars_list
	

def check_calendar_already_exist(current_class_calendar,current_class_calendars_list) :
	is_exist = False 
	for calendar in current_class_calendars_list :
		if current_class_calendar.calendar_key == calendar.calendar_key :
			is_exist = True 
	return is_exist
	
def integrate_teacher_calendars_on_update_exam_and_cancel_exam(current_teacher_calendars_list,updated_class_calendars_list,school_key) :
	updated_teacher_calendars_list =[]
	for updated_class_calendar in updated_class_calendars_list :
		for event in updated_class_calendar.events :
			calendar_date = updated_class_calendar.calendar_date
			employee_key = timetable_integrator.get_employee_key(event.params)
			if employee_key is not None :
				current_teacher_calendar = get_teacher_calendar(current_teacher_calendars_list,calendar_date,employee_key,school_key)
				emp_event = make_employee_event(event,updated_class_calendar)
				if is_calendar_already_exist(current_teacher_calendar,updated_teacher_calendars_list) == False :
					updated_teacher_calendars_list.append(current_teacher_calendar)

	for teacher_calendar in updated_teacher_calendars_list :
		for updated_class_calendar in updated_class_calendars_list :
			for event in updated_class_calendar.events :
				calendar_date = updated_class_calendar.calendar_date
				employee_key = timetable_integrator.get_employee_key(event.params)
				if teacher_calendar.calendar_date == calendar_date and teacher_calendar.subscriber_key == employee_key :
					emp_event = make_employee_event(event,updated_class_calendar)
					if is_event_already_exist(emp_event,teacher_calendar.events) == False :
						teacher_calendar.events.append(emp_event)
	return updated_teacher_calendars_list

def is_event_already_exist(event,teacher_calendar_events) :
	is_exist = False
	for existing_event in teacher_calendar_events :
		if event.event_code == existing_event.event_code and event.ref_calendar_key == existing_event.ref_calendar_key :
			is_exist = True
	return is_exist

def is_calendar_already_exist(current_teacher_calendar,updated_teacher_calendars_list) :
	is_exist = False
	for updated_teacher_calendar in updated_teacher_calendars_list :
		if updated_teacher_calendar.subscriber_key == current_teacher_calendar.subscriber_key and updated_teacher_calendar.calendar_date == current_teacher_calendar.calendar_date:
			is_exist = True
	return is_exist


def make_employee_event(event,updated_class_calendar) :
	if event is not None :
		emp_event = calendar.Event(None)
		emp_event.event_code = event.event_code
		emp_event.ref_calendar_key = updated_class_calendar.calendar_key
	return emp_event


def get_teacher_calendar(teacher_calendars_list,calendar_date,employee_key,school_key) :
	employee_calendar = calendar_service.get_calendar_by_date_and_key(calendar_date, employee_key)
	if employee_calendar is None :
		employee_calendar = generate_employee_calendar(calendar_date,employee_key,school_key)
	return employee_calendar

def generate_employee_calendar(calendar_date,employee_key,school_key) :
	employee_calendar=calendar.Calendar(None)
	employee_calendar.calendar_date = calendar_date
	employee_calendar.calendar_key = key.generate_key(16)
	employee_calendar.institution_key = school_key
	employee_calendar.subscriber_key = employee_key
	employee_calendar.subscriber_type = 'EMPLOYEE'
	employee_calendar.events = []
	return employee_calendar

def get_current_teacher_calendars(removed_events) :
	current_teacher_calendars = []
	for event in removed_events :
		event_date = get_event_date(event.from_time)
		employee_key = timetable_integrator.get_employee_key(event.params)
		if employee_key is not None :
			teacher_calendar = calendar_service.get_calendar_by_date_and_key(event_date, employee_key)
			current_teacher_calendars.append(teacher_calendar)
	return current_teacher_calendars


def get_event_date(event_from_time) :
	return event_from_time[:10]


def integrate_add_exam_on_calendar(series_code,class_key,division) :
	subscriber_key = class_key + '-' + division
	updated_class_calendars_list = []
	updated_teacher_calendars_list = []
	updated_lessonplans_list = []
	removed_events = []
	exams_list = exam_service.get_all_exams_by_class_key_and_series_code(class_key, series_code)
	current_class_calendars_list = get_affected_class_calendars(exams_list)
	school_key = current_class_calendars_list[0].institution_key
	current_cls_calendars = copy.deepcopy(current_class_calendars_list)
	current_lessonplans_list = lessonplan_service.get_lesson_plan_list(class_key,division)
	updated_class_calendars_list = integrate_class_calendars_on_add_exams(updated_class_calendars_list,exams_list,current_class_calendars_list,removed_events)
	current_teacher_calendars_list = get_current_teacher_calendars(removed_events)
	integrate_teacher_cals_and_lessonplans_on_add_exam(
						updated_class_calendars_list,
						updated_teacher_calendars_list,
						updated_lessonplans_list,
						current_class_calendars_list,
						current_teacher_calendars_list,
						current_lessonplans_list,
						exams_list,
						removed_events
						)
	save_updated_calendars_and_lessonplans(updated_class_calendars_list,updated_teacher_calendars_list,updated_lessonplans_list)

def integrate_class_calendars_on_add_exams(updated_class_calendars_list,exams_list,current_class_calendars_list,removed_events) :
	exam_events = make_exam_events(exams_list)
	# print("----------- EXAM EVENTS -----")
	# for exam_event in exam_events :
	# 	pp.pprint(vars(exam_event))
	updated_class_calendars_list = get_updated_current_class_calendars(updated_class_calendars_list,current_class_calendars_list,exam_events,removed_events)
	return updated_class_calendars_list

def get_updated_current_class_calendars(updated_class_calendars_list,current_class_calendars_list,exam_events,removed_events) :
	for current_class_calendar in current_class_calendars_list :
		updated_class_calendar = get_updated_class_calendar_with_exam_events(current_class_calendar,exam_events,removed_events)
		updated_class_calendars_list.append(updated_class_calendar)
	return updated_class_calendars_list

def get_updated_class_calendar_with_exam_events(current_class_calendar,exam_events,removed_events) :
	updated_class_calendar = get_remove_conflicted_class_events(exam_events,current_class_calendar,removed_events)	
	return current_class_calendar

def get_remove_conflicted_class_events(exam_events,current_class_calendar,removed_events) :
	for exam_event in exam_events :
		updated_class_calendar = get_updated_class_calendar_events(exam_event,current_class_calendar,removed_events)
	return updated_class_calendar

def get_updated_class_calendar_events(exam_event,current_class_calendar,removed_events) :
	exam_subject_code = timetable_integrator.get_subject_code(exam_event)
	updated_events = []
	if len(current_class_calendar.events) > 0 :
		for calendar_event in current_class_calendar.events :
			if check_events_conflict(exam_event.from_time,exam_event.to_time,calendar_event.from_time,calendar_event.to_time) == True :
				calendar_exam_subject_code = timetable_integrator.get_subject_code(calendar_event)
				if calendar_event.event_type == "EXAM" :
					subscriber_key = current_class_calendar.subscriber_key
					class_info_key = subscriber_key[:-2]
					class_info = classinfo_service.get_classinfo(class_info_key)
					class_info_subject = get_class_info_subject(calendar_exam_subject_code,class_info)
					if class_info_subject is not None :
						if class_info_subject.type != "ELECTIVE" :
							removed_events.append(calendar_event)
							if exam_event not in updated_events :
								updated_events.append(exam_event)
						else :
							elective_group = get_elective_group(class_info_subject.code,class_info)
							if check_exam_subject_whether_include_in_elective_group_or_not(elective_group,exam_subject_code) == True :
								updated_events.append(calendar_event)
								if exam_event not in updated_events :
									updated_events.append(exam_event)
							else :
								removed_events.append(calendar_event)
								if exam_event not in updated_events :
									updated_events.append(exam_event)
				else :
					removed_events.append(calendar_event)
					if exam_event not in updated_events :
						updated_events.append(exam_event)

			else :
				updated_events.append(calendar_event)
				exam_date = datetime.datetime.strptime(exam_event.from_time[0:10],'%Y-%m-%d')
				calendar_date = datetime.datetime.strptime(current_class_calendar.calendar_date,'%Y-%m-%d')
				if exam_date == calendar_date :
					if exam_event not in updated_events :
						updated_events.append(exam_event)
	else :
		exam_date = datetime.datetime.strptime(exam_event.from_time[0:10],'%Y-%m-%d')
		calendar_date = datetime.datetime.strptime(current_class_calendar.calendar_date,'%Y-%m-%d')
		if exam_date == calendar_date :
			if exam_event not in updated_events :
				updated_events.append(exam_event)


	


	current_class_calendar.events = updated_events
	return current_class_calendar


def get_updated_teacher_calendars_list(current_teacher_calendars_list,removed_events,updated_teacher_calendars_list) :
	for teacher_calendar in current_teacher_calendars_list :
		if teacher_calendar is not None :
			teacher_calendar_events = copy.deepcopy(teacher_calendar.events)
			for event in teacher_calendar.events :
				if is_event_in_remove_events(removed_events,event) == True :
					remove_event_from_teacher_calendar_events(event,teacher_calendar_events)
			teacher_calendar.events = teacher_calendar_events
			updated_teacher_calendars_list.append(teacher_calendar)

def remove_event_from_teacher_calendar_events(event,teacher_calendar_events) :
	for existing_event in teacher_calendar_events :
		if existing_event.event_code == event.event_code :
			teacher_calendar_events.remove(existing_event)
def is_event_in_remove_events(removed_events,event) :
	is_exist = False
	for removed_event in removed_events :
		if removed_event.event_code == event.event_code :
			is_exist = True
	return is_exist
	
def integrate_teacher_cals_and_lessonplans_on_add_exam(updated_class_calendars_list,updated_teacher_calendars_list,updated_lessonplans_list,current_class_calendars_list,current_teacher_calendars_list,current_lessonplans_list,exams_list,removed_events) :
	updated_teacher_calendars_list = get_updated_teacher_calendars_list(current_teacher_calendars_list,removed_events,updated_teacher_calendars_list)
	updated_lessonplans_list = get_updated_current_lessonplans(updated_class_calendars_list,current_lessonplans_list,updated_lessonplans_list,removed_events)

 

def get_updated_current_lessonplans(updated_class_calendars_list,current_lessonplans_list,updated_lessonplans_list,removed_events) :
	for current_lessonplan in current_lessonplans_list :
		subject_code = current_lessonplan.subject_code
		events_to_remove = get_removed_events(subject_code,removed_events)
		updated_lessonplan = get_updated_current_lessonplan(current_lessonplan,events_to_remove)
		updated_lessonplans_list.append(updated_lessonplan)
	return updated_lessonplans_list





def get_updated_class_calendars_list_on_cancel_exam(current_class_calendars_list,exam_series_code,events_to_be_added) :
	updated_class_calendars_list = []
	for current_class_calendar in current_class_calendars_list :
		subscriber_key = current_class_calendar.subscriber_key
		class_key = subscriber_key[:-2]
		division = subscriber_key[-1:]
		timetable = timetable_service.get_timetable_by_class_key_and_division(class_key,division)
		academic_year = timetable.academic_year
		school_key = timetable.school_key
		academic_configuration = academic_service.get_academig(school_key,academic_year)
		get_updated_class_calendars_on_cancel_exam(academic_configuration,timetable,updated_class_calendars_list,current_class_calendar,exam_series_code,events_to_be_added)
	return updated_class_calendars_list

def get_updated_class_calendars_on_cancel_exam(academic_configuration,timetable,updated_class_calendars_list,current_class_calendar,exam_series_code,events_to_be_added) :
	periods_to_be_added =[]
	exam_events_to_be_removed = []
	current_class_calendar = get_previous_events_and_exam_events(academic_configuration,timetable,current_class_calendar,periods_to_be_added,exam_series_code,exam_events_to_be_removed)
	updated_class_calendar = remove_exam_events_of_series_code(exam_events_to_be_removed,current_class_calendar,exam_series_code)
	updated_class_calendar = get_class_session_events_added_calendar(academic_configuration,timetable,periods_to_be_added,updated_class_calendar,events_to_be_added)
	
	updated_class_calendars_list.append(updated_class_calendar)

def remove_exam_events_of_series_code(exam_events_to_be_removed,current_class_calendar,exam_series_code) :
	updated_events = []
	for existing_event in current_class_calendar.events :
		if existing_event.event_type == 'EXAM' :
			previous_exam_event_from_time = existing_event.from_time
			previous_exam_event_to_time = existing_event.to_time
			series_code = get_exam_series_code(existing_event.params)
			if series_code != exam_series_code :
				updated_events.append(existing_event)		
		else :
			updated_events.append(existing_event)
	current_class_calendar.events = updated_events		# updated_class_calendar = exam_integrator.remove_exam_event_of_previous_schedule(current_class_calendar,previous_exam_event_from_time,previous_exam_event_to_time)
	return current_class_calendar


def get_previous_events_and_exam_events(academic_configuration,timetable,current_class_calendar,periods_to_be_added,exam_series_code,exam_events_to_be_removed) :
	for existing_event in current_class_calendar.events :
		if existing_event.event_type == 'EXAM' :
			series_code = get_exam_series_code(existing_event.params)
			if series_code == exam_series_code :
				exam_events_to_be_removed.append(existing_event)
				current_class_calendar = get_previous_periods(academic_configuration,timetable,existing_event,current_class_calendar,periods_to_be_added)
	return current_class_calendar


def get_exam_series_code(params) :
	for param in params :
		if param.key == 'series_code' :
			return param.value

def get_previous_periods(academic_configuration,timetable,existing_event,current_class_calendar,periods_to_be_added) :
	previous_exam_event_from_time = existing_event.from_time
	previous_exam_event_to_time = existing_event.to_time
	day_code = timetable_integrator.findDay(current_class_calendar.calendar_date).upper()[0:3]
	period_list = generate_period_list(
										current_class_calendar,
										previous_exam_event_from_time,
										previous_exam_event_to_time,
										academic_configuration,
										timetable,
										day_code
										)
	for period in period_list :
		if is_period_already_exist(period,periods_to_be_added) == False :
			periods_to_be_added.append(period)
	return current_class_calendar




def integrate_class_calendar_on_update_exams(academic_configuration,timetable,exams_list,current_class_calendars_list,events_to_be_added) :
	updated_class_calendars_list = get_previous_events_added_class_calendars(academic_configuration,timetable,current_class_calendars_list,exams_list,events_to_be_added)
	return updated_class_calendars_list

def integrate_class_calendar_on_add_exams(academic_configuration,timetable,updated_class_calendars_list,exams_list,current_class_calendars_list,removed_events) :
	exam_events = make_exam_events(exams_list)
	updated_class_calendars_list = update_current_class_calendars(academic_configuration,timetable,updated_class_calendars_list,current_class_calendars_list,exam_events,removed_events,exams_list)
	return updated_class_calendars_list

def integrate_teacher_cal_and_lessonplan_on_add_exam(updated_class_calendars_list,updated_teacher_calendars_list,updated_lessonplans_list,current_class_calendars_list,current_teacher_calendars_list,current_lessonplans_list,exams_list,removed_events) :
	updated_teacher_calendars = update_current_teacher_calendars(updated_teacher_calendars_list,current_teacher_calendars_list,updated_class_calendars_list)
	updated_teacher_calendars_list.extend(updated_teacher_calendars)
	update_current_lessonplans(updated_class_calendars_list,current_lessonplans_list,updated_lessonplans_list,removed_events)

def integrate_lessonplans_on_update_exams_and_cancel_exam(current_lessonplans_list,events_to_be_added) :
	updated_lessonplans = []
	for current_lessonplan in current_lessonplans_list :
		for events in events_to_be_added :
			events_to_add_schedule =[]
			for event in events :
				subject_key = lesssonplan_integrator.get_subject_key(event.params)
				if subject_key == current_lessonplan.subject_code :
					events_to_add_schedule.append(event)
					print("Adding event to lesson plan ------------------------__:::::::>>>>>>",event.event_code)
					if check_already_added_or_not(event,current_lessonplan) == False :
						add_schedules_and_adjust_lessonplan(current_lessonplan,events_to_add_schedule)
		updated_lessonplans.append(current_lessonplan)
	return updated_lessonplans

def check_already_added_or_not(event,current_lessonplan) :
	is_exist = False 
	if hasattr(current_lessonplan,'topics') and len(current_lessonplan.topics) > 0 :
			for main_topic in current_lessonplan.topics :
				for topic in main_topic.topics :
					for session in topic.sessions :
						if hasattr(session,'schedule') :
							if session.schedule.event_code == event.event_code :
								is_exist = True
	return is_exist



def integrate_lessonplans_on_update_exams(current_lessonplans_list,current_class_calendars_list) :
	updated_lessonplans = []
	for current_lessonplan in current_lessonplans_list :
		current_lessonplan = remove_all_existing_schedules(current_lessonplan)
		updated_lessonplan = get_updated_lessonplan_with_previous_schedules(current_lessonplan,current_class_calendars_list)
		updated_lessonplans.append(updated_lessonplan)
	return updated_lessonplans






def add_schedules(updated_class_calendar_events,current_lessonplan) :
	events_to_add_schedule =[]
	for event in updated_class_calendar_events :
		subject_key = lesssonplan_integrator.get_subject_key(event.params)
		if subject_key == current_lessonplan.subject_code :
			events_to_add_schedule.append(event)
			add_schedules_and_adjust_lessonplan(current_lessonplan,events_to_add_schedule)
	return current_lessonplan


def add_schedules_and_adjust_lessonplan(current_lessonplan,events) :
	after_calendar_date_schedules_list = []
	root_sessions = []
	gclogger.info("LESSON PLAN KEY ------------------->  " + str(current_lessonplan.lesson_plan_key))
	current_lessonplan = lessonplan_integrator.remove_schedule_after_calendar_date(current_lessonplan,events[0].from_time,after_calendar_date_schedules_list)
	current_lessonplan = lessonplan_integrator.add_root_schedule_to_schedule_list(current_lessonplan,after_calendar_date_schedules_list,root_sessions)
	current_lessonplan = add_calendar_schedules_to_lesson_plan(current_lessonplan,events)
	current_lessonplan = lessonplan_integrator.add_shedule_after_calendar_date(after_calendar_date_schedules_list,current_lessonplan)
	current_lessonplan = lessonplan_integrator.create_remaining_sessions_on_root_when_schedule_added(after_calendar_date_schedules_list,current_lessonplan)
	return current_lessonplan


def add_calendar_schedules_to_lesson_plan(current_lessonplan,events) :
	for event in events :
		subject_code = get_subject_code(event)
		if current_lessonplan.subject_code == subject_code :
			schedule = create_schedule(event)
			Add_schedule_to_lessonplan(current_lessonplan,schedule,event)
	return current_lessonplan


def create_schedule(event) :
	schedule = lpnr.Schedule(None)
	schedule.calendar_key = event.ref_calendar_key
	schedule.event_code = event.event_code
	schedule.start_time = event.from_time
	schedule.end_time = event.to_time
	return schedule

def Add_schedule_to_lessonplan(current_lessonplan,schedule,event) :
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
	else :
		if schedule_added == False :
			add_sessions_on_root(current_lessonplan,event,schedule_added)
	return current_lessonplan


def add_sessions_on_root(current_lesson_plan,event,schedule_added) :
	schedule = create_schedule(event)
	if hasattr(current_lesson_plan,'sessions') :
		session_order_index = len(current_lesson_plan.sessions) + 1
		session = lessonplan_integrator.create_session(schedule,session_order_index)
		if schedule not in current_lesson_plan.sessions :
			current_lesson_plan.sessions.append(session)
			schedule_added = True




def remove_all_existing_schedules(current_lessonplan) :
	if  hasattr(current_lessonplan,'topics') and len(current_lessonplan.topics) > 0 :
			for main_topic in current_lessonplan.topics :
				for topic in main_topic.topics :
					for session in topic.sessions :
						if hasattr(session,'schedule') :
							del session.schedule

	if hasattr(current_lessonplan,'sessions') and len(current_lessonplan.sessions) > 0 :
			for session in topic.sessions :
				if hasattr(session,'schedule') :
					del session.schedule
	return current_lessonplan



def get_updated_lessonplan_with_previous_schedules(current_lessonplan,current_class_calendars_list) :
	for current_class_calendar in current_class_calendars_list :
		for event in current_class_calendar.events :
			events_to_add = []
			if need_add_this_event(event,current_lessonplan,current_class_calendar) == True :
				events_to_add.append(event)
				current_lessonplan = lesssonplan_integrator.add_schedules_and_adjust_lessonplan(current_lessonplan,events_to_add,current_class_calendar)
	return current_lessonplan




def need_add_this_event(event,current_lessonplan,current_class_calendar) :
	do_add = True
	if  hasattr(current_lessonplan,'topics') and len(current_lessonplan.topics) > 0 :
			for main_topic in current_lessonplan.topics :
				for topic in main_topic.topics :
					for session in topic.sessions :
						if hasattr(session,'schedule') and is_shedule_exist(event,session.schedule,current_class_calendar) == True :
							do_add = False
	elif hasattr(current_lessonplan,'sessions') and len(current_lessonplan.sessions) > 0 :
			for session in topic.sessions :
				if hasattr(session,'schedule') and is_shedule_exist(event,session.schedule,current_class_calendar) == True :
					do_add = False
	return do_add


def is_shedule_exist(event,schedule,current_class_calendar) :
	is_schedule = False
	if event.from_time == schedule.start_time and event.to_time == schedule.end_time and event.event_code == schedule.event_code :
		is_schedule = False
	return is_schedule







def make_exam_events(exams_list) :
	exam_events = []
	for exam_info in exams_list :
		exam_event_info_from_time = timetable_integrator.convert24Hr(exam_info.from_time)
		exam_event_info_to_time = timetable_integrator.convert24Hr(exam_info.to_time)
		exam_event = calendar.Event(None)
		exam_event.event_code = key.generate_key(3)
		exam_event.event_type = 'EXAM'
		exam_event.from_time = get_standard_time(exam_event_info_from_time,exam_info.date_time)
		exam_event.to_time = get_standard_time(exam_event_info_to_time,exam_info.date_time)
		exam_event.params = get_params(exam_info.exam_key,exam_info.series_code,exam_info.subject_code)
		exam_events.append(exam_event)
	return exam_events

def get_standard_time(time,date) :
	splited_date = date.split('-')
	splited_date = list(map(int,splited_date))
	time_hour = int(time[0:2])
	time_minute = int(time[3:5])
	return datetime.datetime(splited_date[0],splited_date[1],splited_date[2],time_hour,time_minute).isoformat()


def get_params(exam_key,series_code,subject_code) :
	params = []
	param_info = calendar.Param(None)
	param_info.key = 'cancel_class_flag'
	param_info.value = 'true'
	params.append(param_info)
	param_exam_info = calendar.Param(None)
	param_exam_info.key = 'exam_key'
	param_exam_info.value = exam_key
	params.append(param_exam_info)
	param_exam_info = calendar.Param(None)
	param_exam_info.key = 'series_code'
	param_exam_info.value = series_code
	params.append(param_exam_info)
	param_exam_info = calendar.Param(None)
	param_exam_info.key = 'subject_key'
	param_exam_info.value = subject_code
	params.append(param_exam_info)
	return params



def get_previous_events_added_class_calendars(academic_configuration,timetable,current_class_calendars_list,exams_list,events_to_be_added) :
	updated_class_calendars_list = []
	for current_class_calendar in current_class_calendars_list :
		periods_to_be_added =[]
		updated_class_calendar = get_previous_exam_events_removed_calendar(academic_configuration,timetable,current_class_calendar,exams_list,periods_to_be_added)
		updated_class_calendar = get_class_session_events_added_calenda(academic_configuration,timetable,periods_to_be_added,updated_class_calendar,events_to_be_added)
		updated_class_calendars_list.append(updated_class_calendar)
	return updated_class_calendars_list

def get_class_session_events_added_calenda(academic_configuration,timetable,periods_to_be_added,current_class_calendar,events_to_be_added) :
	events = make_events_to_add_schdule(periods_to_be_added,timetable,current_class_calendar)
	events_to_be_added.append(events)
	updated_class_calendar = calendar_integrator.add_events_to_calendar(events,current_class_calendar)
	return updated_class_calendar

def update_current_class_calendars(academic_configuration,timetable,updated_class_calendars_list,current_class_calendars_list,exam_events,removed_events,exams_list) :
	updated_class_calendars =[]
	for current_class_calendar in current_class_calendars_list :
		updated_class_calendar = update_class_calendar_with_exam_events(current_class_calendar,exam_events,removed_events)
		updated_class_calendars.append(updated_class_calendar)
	updated_class_calendars_list = updated_class_calendars
	return updated_class_calendars_list



def get_class_session_events_added_calendar(academic_configuration,timetable,periods_to_be_added,current_class_calendar,events_to_be_added) :
	events = make_events_to_add_schdule_and_update_lessonplans(periods_to_be_added,timetable,current_class_calendar)
	events_to_be_added.append(events)
	updated_class_calendar = calendar_integrator.add_events_to_calendar(events,current_class_calendar)
	return updated_class_calendar

def make_events_to_add_schdule_and_update_lessonplans(period_list,timetable,class_calendar) :
	events_list =[]
	for period in period_list :
		event = calendar.Event(None)
		event.event_code = key.generate_key(3)
		event.event_type = 'CLASS_SESSION'
		event.ref_calendar_key = class_calendar.calendar_key
		time_table_period = calendar_integrator.get_time_table_period(period.period_code,timetable)
		try :
			event.params = timetable_integrator.get_params(time_table_period.subject_key , time_table_period.employee_key , time_table_period.period_code)
			event.from_time =  timetable_integrator.get_standard_time(period.start_time,class_calendar.calendar_date)
			event.to_time =  timetable_integrator.get_standard_time(period.end_time,class_calendar.calendar_date)
			gclogger.info("Event created " + event.event_code + ' start ' + event.from_time + ' end ' + event.to_time)
			events_list.append(event)
			update_lesson_plan_on_cancel_exam(event,class_calendar)
		except AttributeError :
			events = timetable_integrator.get_event_list(time_table_period,period_list,date)
			events_list.extend(events)
			for event in events :
				update_lesson_plan_on_cancel_exam(event,class_calendar)

	return events_list

def update_lesson_plan_on_cancel_exam(event,class_calendar) :
	subject_key = get_subject_code(event)
	subscriber_key = class_calendar.subscriber_key
	class_key = subscriber_key[:-2]
	division = subscriber_key[-1:]
	current_lessonplans_list = lessonplan_service.get_lesson_plan_list(class_key, division)
	current_lessonplan = lessonplan_integrator.get_lessonplan_by_subject_key(current_lessonplans_list,subject_key)
	if current_lessonplan is not None :
		updated_lessonplan = lessonplan_integrator.update_lessonplan_on_add_class_session_events(event,class_calendar,current_lessonplan)
		lp = lpnr.LessonPlan(None)
		updated_lessonplan_dict = lp.make_lessonplan_dict(updated_lessonplan)
		response = lessonplan_service.create_lessonplan(updated_lessonplan_dict)
		gclogger.info(str(response['ResponseMetadata']['HTTPStatusCode']) + ' Updated Lesson Plan  uploaded '+str(updated_lessonplan_dict['lesson_plan_key']))

def make_events_to_add_schdule(period_list,timetable,class_calendar) :
	events_list =[]
	for period in period_list :
		event = calendar.Event(None)
		event.event_code = key.generate_key(3)
		event.event_type = 'CLASS_SESSION'
		event.ref_calendar_key = class_calendar.calendar_key
		time_table_period = calendar_integrator.get_time_table_period(period.period_code,timetable)
		event.params = timetable_integrator.get_params(time_table_period.subject_key , time_table_period.employee_key , time_table_period.period_code)

		event.from_time =  timetable_integrator.get_standard_time(period.start_time,class_calendar.calendar_date)
		event.to_time =  timetable_integrator.get_standard_time(period.end_time,class_calendar.calendar_date)
		gclogger.info("Event created " + event.event_code + ' start ' + event.from_time + ' end ' + event.to_time)
		events_list.append(event)
	return events_list
def update_class_calendar_with_exam_events(current_class_calendar,exam_events,removed_events) :
	updated_class_calendar = remove_conflicted_class_events(exam_events,current_class_calendar,removed_events)
	return current_class_calendar


def get_previous_exam_events_removed_calendar(academic_configuration,timetable,current_class_calendar,exams_list,periods_to_be_added) :
	for exam in exams_list :
		if hasattr(exam,'previous_schedule') and is_schedule_has_same_calendar_key(exam.previous_schedule,current_class_calendar) == True :
			updated_class_calendar = integrate_previous_periods(academic_configuration,timetable,exam,current_class_calendar,periods_to_be_added)

	return current_class_calendar



def is_schedule_has_same_calendar_key(previous_schedule,current_class_calendar) :
	has_same_calendar_date = False
	if previous_schedule.date_time == current_class_calendar.calendar_date :
		has_same_calendar_date = True
	return has_same_calendar_date


def integrate_previous_periods(academic_configuration,timetable,exam,current_class_calendar,periods_to_be_added) :
	previous_exam_from_time = timetable_integrator.convert24Hr(exam.previous_schedule.from_time)
	previous_exam_to_time = timetable_integrator.convert24Hr(exam.previous_schedule.to_time)
	previous_exam_event_from_time = timetable_integrator.get_standard_time(previous_exam_from_time,current_class_calendar.calendar_date)
	previous_exam_event_to_time = timetable_integrator.get_standard_time(previous_exam_to_time,current_class_calendar.calendar_date)
	day_code = timetable_integrator.findDay(current_class_calendar.calendar_date).upper()[0:3]
	period_list = generate_period_list(
										current_class_calendar,
										previous_exam_event_from_time,
										previous_exam_event_to_time,
										academic_configuration,
										timetable,
										day_code
										)
	for period in period_list :
		if is_period_already_exist(period,periods_to_be_added) == False :
			periods_to_be_added.append(period)
	updated_class_calendar = remove_exam_event_of_previous_schedule(current_class_calendar,previous_exam_event_from_time,previous_exam_event_to_time)



def remove_exam_event_of_previous_schedule(current_class_calendar,previous_exam_event_from_time,previous_exam_event_to_time) :
	for event in current_class_calendar.events :
		if event.event_type == 'EXAM' and is_schedule_matching(event,previous_exam_event_from_time,previous_exam_event_to_time) == True :
			current_class_calendar.events.remove(event)
	return current_class_calendar



def is_schedule_matching(event,previous_exam_event_from_time,previous_exam_event_to_time) :
	is_matching = False
	if event.from_time == previous_exam_event_from_time and event.to_time == previous_exam_event_to_time :
		is_matching = True
	return is_matching


def is_period_already_exist(period,periods_to_be_added) :
	is_period_exist = False
	for existing_period in periods_to_be_added :
		if period.period_code == existing_period.period_code :
			is_period_exist = True
	return is_period_exist

def generate_period_list(calendar,previous_exam_event_from_time,previous_exam_event_to_time,academic_configuration,timetable,day_code) :
	period_list =[]
	periods = get_period_list(
							previous_exam_event_from_time,
							previous_exam_event_to_time,
							day_code,academic_configuration,
							timetable,calendar.calendar_date
							)
	for period in periods :
		period_list.append(period)
	return period_list



def get_period_list(start_time,end_time,day_code,academic_configuration,timetable,date) :
	period_list =[]
	if hasattr(academic_configuration.time_table_configuration ,'time_table_schedules') :
		for time_table_schedule in academic_configuration.time_table_configuration.time_table_schedules :
				for class_key in time_table_schedule.applied_classes :
					if class_key == timetable.class_key :
						for day_table in  time_table_schedule.day_tables :
							if day_table.day_code == day_code :
								for period in day_table.periods :
									standard_start_time = timetable_integrator.get_standard_time(period.start_time,date)
									standard_end_time = timetable_integrator.get_standard_time(period.end_time,date)
									if timetable_integrator.check_holiday_time_conflict(start_time,end_time,standard_start_time,standard_end_time) == True:
										period_list.append(period)
	return period_list


def remove_conflicted_class_events(exam_events,current_class_calendar,removed_events) :
	for exam_event in exam_events :
		updated_class_calendar = update_class_calendar_events(exam_event,current_class_calendar,removed_events)
	return updated_class_calendar


def update_class_calendar_events(exam_event,current_class_calendar,removed_events) :
	updated_events = []
	for calendar_event in current_class_calendar.events :
		if check_events_conflict(exam_event.from_time,exam_event.to_time,calendar_event.from_time,calendar_event.to_time) == True :
			removed_events.append(calendar_event)
			if exam_event not in updated_events :
				updated_events.append(exam_event)
		else :
			updated_events.append(calendar_event)
	current_class_calendar.events = updated_events
	return current_class_calendar



def update_current_teacher_calendars(updated_teacher_calendars_list,current_teacher_calendars_list,updated_class_calendars_list) :
	updated_teacher_calendars = []
	for current_teacher_calendar in current_teacher_calendars_list :
		updated_teacher_calendar = get_removed_events_from_teacher_calendar(current_teacher_calendar,updated_class_calendars_list)
		updated_teacher_calendars.append(updated_teacher_calendar)
		updated_teacher_calendars_list = updated_teacher_calendars
	return updated_teacher_calendars_list

def get_removed_events_from_teacher_calendar(current_teacher_calendar,updated_class_calendars_list) :
	updated_event_list = []
	for event in current_teacher_calendar.events :
		if check_event_exist_in_class_calendars(event,updated_class_calendars_list) == True :
			updated_event_list.append(event)
	current_teacher_calendar.events = updated_event_list
	return current_teacher_calendar


def check_event_exist_in_class_calendars(event,updated_class_calendars_list) :
	is_event_exist = False
	for updated_calendar in updated_class_calendars_list :
		for event_info in updated_calendar.events :
			if event_info.event_code == event.event_code :
				is_event_exist = True
	return is_event_exist



def check_events_conflict(event_start_time,event_end_time,class_calendar_event_start_time,class_calendar_event_end_time) :
	# print("EXAM EVENT START TIME ----->",event_start_time)
	# print("EXAM EVENT START TIME ----->",event_end_time)
	# print("CLASS SESSION  START TIME ------>",class_calendar_event_start_time)
	# print("CLASS SESSION END TIME ------>",class_calendar_event_end_time)
	is_conflict = False
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
	# print("CONFLICT VALUE",is_conflict)
	return is_conflict


def update_current_lessonplans(updated_class_calendars_list,current_lessonplans_list,updated_lessonplans_list,removed_events) :
	for current_lessonplan in current_lessonplans_list :
		subject_code = current_lessonplan.subject_code
		events_to_remove = get_removed_events(subject_code,removed_events)
		updated_lessonplan = get_updated_current_lessonplan(current_lessonplan,events_to_remove)
		updated_lessonplans_list.append(updated_lessonplan)
	return updated_lessonplans_list



def get_removed_events(subject_code,removed_events) :
	events_to_remove = []
	for event in removed_events :
		subject_key = get_subject_code(event)
		if subject_key == subject_code :
			events_to_remove.append(event)
	return events_to_remove


def get_subject_code(event) :
	if hasattr(event, 'params') :
		for param in event.params :
			if param.key == 'subject_key' :
				return param.value



def get_updated_current_lessonplan(current_lessonplan,events_to_remove) :
	for event in events_to_remove :
		current_lessonplan = remove_event_schedule_from_lessonplan(current_lessonplan,event)
	return current_lessonplan

def is_need_remove_schedule(event,schedule) :
	is_need_remove = False
	if hasattr(schedule,"start_time") and hasattr(schedule,"end_time") :
		if event.from_time == schedule.start_time and event.to_time == schedule.end_time :
			is_need_remove = True
	return is_need_remove

def remove_event_schedule_from_lessonplan(current_lessonplan,event) :
	if  hasattr(current_lessonplan,'topics') and len(current_lessonplan.topics) > 0 :
			for main_topic in current_lessonplan.topics :
				for topic in main_topic.topics :
					for session in topic.sessions :
						if hasattr(session,'schedule') :
							if is_need_remove_schedule(event,session.schedule) == True :
								del session.schedule

	if hasattr(current_lessonplan,'sessions') and len(current_lessonplan.sessions) > 0 :
		for session in current_lessonplan.sessions :
			if hasattr(session,'schedule') and session.schedule is not None :
				if is_need_remove_schedule(event,session.schedule) == True :
					del session.schedule
	current_lessonplan = lessonplan_integrator.adjust_lessonplan_after_remove_schedule(current_lessonplan)
	return current_lessonplan


def adjust_lessonplan_after_remove_schedule(current_lessonplan) :
	root_sessions = []
	schedule_list = get_all_remaining_schedules(current_lessonplan)
	current_lessonplan = get_lesson_plan_after_remove_all_shedules(current_lessonplan)
	#add root schedule to schedule list and delete all root sessions
	current_lessonplan = add_root_schedule_to_schedule_list(current_lessonplan,schedule_list,root_sessions)
	current_lessonplan = get_updated_lesson_plan(schedule_list,current_lessonplan)
	#create remaining  schedule  on root sesions
	current_lessonplan = create_remaining_sessions_on_root_when_schedule_removed(schedule_list,current_lessonplan,root_sessions)
	return current_lessonplan

class ExamSeries :
	def __init__(self, item):
		if item is None:
			
			self.classes = []
			self.code = None
			self.from_date = None
			self.name = None
			self.to_date = None
		else :
			try :
				self.classes = []
				classes = item['classes']
				for clazz in classes :
					self.classes.append(Class(clazz))
			except KeyError as ke:
				gclogger.debug('[WARN] - KeyError in ExamSeries - classes not present'.format(str (ke)))
			try :
				self.code = item['code']
			except KeyError as ke:
				gclogger.debug('[WARN] - KeyError in ExamSeries - code not present'.format(str (ke)))
			try :
				self.from_date = item['from_date']
			except KeyError as ke:
				gclogger.debug('[WARN] - KeyError in ExamSeries - from_date not present'.format(str (ke)))
			try :
				self.to_date = item['to_date']
			except KeyError as ke:
				gclogger.debug('[WARN] - KeyError in ExamSeries - to_date not present'.format(str (ke)))
			try :
				self.name = item['name']
			except KeyError as ke:
				gclogger.debug('[WARN] - KeyError in ExamSeries - name not present'.format(str (ke)))


class Class :
	def __init__(self, item):
		if item is None:
			self.class_key = None
			self.division = None
			
		else :
			self.class_key = item['class_key']
			self.division = item['division']

def get_class_info_subject(calendar_exam_subject_code,class_info) :
	if hasattr(class_info,"subjects") :
		for subject in class_info.subjects :
			if subject.code == calendar_exam_subject_code :
				return subject

def get_elective_group(code,class_info) :
	for subject in class_info.subjects :
		if hasattr(subject,"elective_subjects") :
			for elective_subject in subject.elective_subjects :
				if elective_subject.code == code :
					return subject

def check_exam_subject_whether_include_in_elective_group_or_not(elective_group,exam_subject_code) :
	is_exist = False
	if hasattr(elective_group,"elective_subjects") :
		for elective_subject in elective_group.elective_subjects :
			if elective_subject.code == exam_subject_code :
				is_exist = True
	return is_exist

