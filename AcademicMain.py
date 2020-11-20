from academics.TimetableIntegrator import generate_and_save_calenders
import academics.calendar.CalendarDBService as calendar_service
from academics.calendar.CalendarLessonPlanIntegrator import integrate_calendars_to_lesson_plan, calendars_lesson_plan_integration_from_timetable, integrate_calendar
from academics.calendar.CalendarIntegrator import add_event_integrate_calendars, remove_event_integrate_calendars, integrate_update_period_calendars_and_lessonplans


# timetable_key = '0016041399849397128D980CA2-98CF-40CF-AA3E-922522661A7F427791508'
# academic_year = '2020-2021'
# generate_and_save_calenders(timetable_key,academic_year)

# subscriber_key = '0016041642034456026C6BBEBB-DF16-4ACC-B794-FDA186EC7310-933430547-A'
# subscriber_type = 'CLASS-DIV'
# class_calender_list = calendar_service.get_all_calendars_by_key_and_type(subscriber_key,subscriber_type)
# integrate_calendars_to_lesson_plan(class_calender_list)

# timetable_key = '0015857593937522563601DB25-595D-4024-BD9B-2FC6F6E02C2C1293121299'
# timetable_key = '0016052638719701962C01A5A7-1DF5-4C16-93A2-3D37FEA3F315-551118910'
# calendars_lesson_plan_integration_from_timetable(timetable_key,'2020-2021')

# calendar_key = '001605807225712456C9788445-9704-4D49-9B53-1FCEAA3077A4-1107651807'
# event_code = "695poi-r15e2s"
# add_event_integrate_calendars(event_code,calendar_key)
# remove_event_integrate_calendars(calendar_key)

# time_table_key = '00160397692489898347377F45-7AE0-4328-85CF-0925C31408B5-365640440'
# period_code = "WED-7"
# integrate_update_period_calendars_and_lessonplans(period_code, time_table_key)

	