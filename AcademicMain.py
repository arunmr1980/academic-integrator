from academics.TimetableIntegrator import generate_and_save_calenders
import academics.calendar.CalendarDBService as calendar_service
from academics.calendar.CalendarLessonPlanIntegrator import integrate_calendars_to_lesson_plan, calendars_lesson_plan_integration_from_timetable, integrate_calendar
from academics.calendar.CalendarIntegrator import add_event_integrate_calendars, remove_event_integrate_calendars, integrate_update_period_calendars_and_lessonplans


# time_table_key = '001604166781163221F2E5F2D3-7981-4461-BB51-4B8346A2AABE-451130953'
# academic_year = '2020-2021'
# generate_and_save_calenders(time_table_key,academic_year)

# subscriber_key = '0016041642034456026C6BBEBB-DF16-4ACC-B794-FDA186EC7310-933430547-A'
# subscriber_type = 'CLASS-DIV'
# class_calender_list = calendar_service.get_all_calendars_by_key_and_type(subscriber_key,subscriber_type)
# integrate_calendars_to_lesson_plan(class_calender_list)

# timetable_key = '0015857593937522563601DB25-595D-4024-BD9B-2FC6F6E02C2C1293121299'
# timetable_key = '0016006874968973003B532C32-C856-4D0D-9393-4842E439FFF51699906267'
# calendars_lesson_plan_integration_from_timetable(timetable_key,'2020-2021')

# calendar_key = '0016042517249439435FA0ABC6-78D6-412E-B326-1196121BD65A1412087506'
# event_code = "g7pc0i-bf46kp"
# add_event_integrate_calendars(event_code,calendar_key)
# remove_event_integrate_calendars(calendar_key)

# time_table_key = '001600758904519334F80F12C9-087F-4A68-A332-9C5F928ED0FF169892635'
# period_code = "MON-3"
# integrate_update_period_calendars_and_lessonplans(period_code, time_table_key)
