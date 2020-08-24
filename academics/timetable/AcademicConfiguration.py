import academics.logger.GCLogger as gclogger



class AcademicConfiguration :
    def __init__(self, item):
        if item is None :
            self.start_date = None
            self.end_date = None 
            self.time_table_configuration = None
            self.academic_config_key = None
            self.school_key = None
            self.academic_year = None
        else :
            self.start_date = item["start_date"]
            self.end_date = item["end_date"]
            self.academic_config_key = item["academic_config_key"]
            self.school_key = item["school_key"]
            self.academic_year = item["academic_year"]
            self.time_table_configuration = TimetableConfiguration(item["time_table_configuration"])


class TimetableConfiguration :
    def __init__(self, item):
        if item is None:
            self.time_table_schedules = None
        else:
            try :
                self.time_table_schedules = []
                time_table_schedules = item["time_table_schedules"]
                for time_table_schedule in time_table_schedules :
                    self.time_table_schedules.append(TimeTableSchedule(time_table_schedule))
            except KeyError as ke:
                gclogger.debug(' KeyError in TimetableConfiguration - time_table_schedules not found'.format(str(ke)))
            


class TimeTableSchedule :
    def __init__(self, item):
        if item is None:
            self.applied_classes = []
            self.code = None
            self.day_tables = []
            self.name = None
        else :
            self.applied_classes = item['applied_classes']
            self.code = item['code']
            self.name = item['name']
            self.day_tables = []
            try :
                day_tables = item['day_tables']
                for day_table in day_tables:
                    self.day_tables.append(DayTables(day_table))
            except KeyError as ke:
                gclogger.debug(' KeyError in AppliedClass- day_tables not found'.format(str(ke)))

            

class DayTables :
    def __init__(self, item):
        if item is None:
            self.day_code = None
            self.name = None
            self.order_index = None
            self.periods = []
        else :
            self.day_code = item['day_code']
            self.name = item['name']
            self.order_index = item['order_index']
            self.periods = []
            try:
                periods = item["periods"]
                for period in periods:
                    self.periods.append(Periods(period))
            except KeyError as ke:
                gclogger.debug(' KeyError in DayTables - periods not found'.format(str(ke)))


class Periods :
    def __init__(self, item):
        if item is None:
            self.end_time = None
            self.order_index = None
            self.period_code = None
            self.start_time = None
        else :
            self.end_time = item['end_time']
            self.oreder_index = item['order_index']
            self.period_code = item['period_code']
            self.start_time = item['start_time']







