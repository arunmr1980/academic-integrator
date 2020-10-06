from academics.TimetableIntegrator import generate_and_save_calenders
import academics.calendar.CalendarDBService as calendar_service
from academics.calendar.CalendarLessonPlanIntegrator import integrate_calendars_to_lesson_plan, calendars_lesson_plan_integration_from_timetable, integrate_calendar


# time_table_key = '0015857593937522563601DB25-595D-4024-BD9B-2FC6F6E02C2C1293121299'
# academic_year = '2020-2021'
# generate_and_save_calenders(time_table_key,academic_year)

# subscriber_key = '001582009928422269B9FFEEB6-FE8C-4457-AE98-D049FAB05AAE-1700915859-A'
# subscriber_type = 'CLASS-DIV'
# class_calender_list = calendar_service.get_all_class_calendars(subscriber_key,subscriber_type)
# integrate_calendars_to_lesson_plan(class_calender_list)

# timetable_key = '0015857593937522563601DB25-595D-4024-BD9B-2FC6F6E02C2C1293121299'
timetable_key = '0016006874968973003B532C32-C856-4D0D-9393-4842E439FFF51699906267'
calendars_lesson_plan_integration_from_timetable(timetable_key,'2020-2021')
