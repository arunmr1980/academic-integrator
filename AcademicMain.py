from academics.TimetableIntegrator import generate_and_save_calenders
import academics.calendar.CalendarDBService as calendar_service
from academics.calendar.CalendarLessonPlanIntegrator import integrate_calendars_to_lesson_plan, integrate_calendar


# time_table_key = '0015857593937522563601DB25-595D-4024-BD9B-2FC6F6E02C2C1293121299'
# academic_year = '2020-2021'
# generate_and_save_calenders(time_table_key,academic_year)

subscriber_key = '001582009928422269B9FFEEB6-FE8C-4457-AE98-D049FAB05AAE-1700915859-A'
subscriber_type = 'CLASS-DIV'
class_calender_list = calendar_service.get_all_class_calendars(subscriber_key,subscriber_type)
integrate_calendars_to_lesson_plan(class_calender_list)
