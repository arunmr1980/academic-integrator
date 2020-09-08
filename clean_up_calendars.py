import academics.calendar.CalendarDBService as calendar_service



def clean_up_clendars():
    calendar_list = calendar_service.get_all_calendars("1e4d12bc2b58050ff084f8da","EMPLOYEE")
    for calendar in calendar_list:
        calendar_service.delete_calendar(calendar.calendar_key)
        print("-----calendar deleted-----" + calendar.calendar_key)

clean_up_clendars()
