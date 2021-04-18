from academics.logger import GCLogger as logger
import pprint
pp = pprint.PrettyPrinter(indent=4)

class TimeTable:

    def __init__(self, item):
        if item is None:
            self.class_key = None
            self.academic_year = None
            self.employee_key = None
            self.class_name = None
            self.division = None
            self.school_key = None
            self.time_table_key = None
            self.timetable = {}
            self.config_parameters = {}
            self.generation_logs = []
        else:
           
            self.school_key = item['school_key']
            self.time_table_key = item['time_table_key']
            self.academic_year = None

            try:
                self.academic_year = item['academic_year']
            except KeyError:
                logger.debug('[WARN] - KeyError in TimeTable - academic_year not found')

            try:
                self.class_key = item['class_key']
            except KeyError:
                logger.debug('[WARN] - KeyError in TimeTable - class_key not found')
            try:
                self.class_name = item['class_name']
            except KeyError:
                logger.debug('[WARN] - KeyError in TimeTable - class_name not found')
            try:
                self.division = item['division']
            except KeyError:
                logger.debug('[WARN] - KeyError in TimeTable - division not found')

            try:
                self.employee_key = item['employee_key']
            except KeyError:
                logger.debug('[WARN] - KeyError in TimeTable - employee_key not found')

            try:
                self.timetable = TimeTable.TimeTable(item['timetable'])
            except KeyError:
                logger.debug('[WARN] - KeyError in TimeTable - TimeTable not found')

            try:
                self.config_parameters = TimeTable.ConfigParameter(item['config_parameters'])
            except KeyError:
                logger.debug('[WARN] - KeyError in TimeTable - ConfigParameter not found')

            try:
                generation_log_items = item['generation_logs']
                self.generation_logs = []
                for generation_log_item in generation_log_items:
                    self.generation_logs.append(TimeTable.GenerationLog(generation_log_item))
            except KeyError:
                logger.debug('[WARN] - KeyError in TimeTable - GenerationLogs not found')

  

    def make_timetable_dict (self , timetable) :
        if timetable is not None :
            item = {
                'academic_year': timetable.academic_year,
                'school_key': timetable.school_key,
                'time_table_key': timetable.time_table_key,
            }

            if hasattr(timetable,'class_key') and timetable.class_key is not None:
                item['class_key'] = timetable.class_key

            if hasattr(timetable,'class_name') and timetable.class_name is not None:
                item['class_name'] = timetable.class_name

            if hasattr(timetable,'division') and timetable.division is not None:
                item['division'] = timetable.division

            if hasattr(timetable,'employee_key') and timetable.employee_key is not None:
                item['employee_key'] = timetable.employee_key

            if timetable.timetable is not None:
                item['timetable'] = self.get_timetable_dict(timetable.timetable)

            if hasattr(timetable, 'config_parameters') and timetable.config_parameters:
                item['config_parameters'] = self.get_config_parameters_dict(timetable.config_parameters)

            if hasattr(timetable, 'generation_logs') and timetable.generation_logs is not None and len(timetable.generation_logs) > 0:
                item['generation_logs'] = self.get_generation_logs_dict(timetable.generation_logs)
            return item


    def get_timetable_dict(self,timetable):
        item = {
            'day_tables': self.get_day_tables_dict(timetable.day_tables)
        }
        return item


    def get_config_parameters_dict(self,config_parameters):
        item = {
            'subject_preferences': self.get_subject_preferences_dict(config_parameters.subject_preferences)
        }
        return item


    def get_generation_logs_dict(self,generation_logs):
        generation_logs_items = []
        for generation_log in generation_logs:
            sub_item = {
                'code': generation_log.code,
                'note': generation_log.note
            }
            generation_logs_items.append(sub_item)
        return generation_logs_items
    def get_day_tables_dict(self,day_tables):
        day_table_items = []
        for day_table in day_tables:
            item = {
                'day_code': day_table.day_code,
                'order_index': day_table.order_index
            }
            periods = []
            for period in day_table.periods:
                if hasattr(period,'employees') :
                    period = self.get_period_dict(period)
                    periods.append(period)
                else :
                    periods.append(vars(period))
            item['periods'] = periods
            day_table_items.append(item)
        return day_table_items;

    def get_period_dict(self,period) :
        period_dict = {
            'class_info_key' : period.class_info_key,
            'division_code' : period.division_code,
            'period_code' : period.period_code
        }
        if hasattr(period,"order_index") :
           period_dict['order_index'] : period.order_index
        period_dict['employees'] = self.get_employees(period.employees)
        return period_dict

    def get_employees(self,employees) :
        employees_list =[]
        for employee in employees :
            employee_dict = {
                'employee_key' : employee.employee_key,
                'subject_key' : employee.subject_key
            }
            employees_list.append(employee_dict)
        return employees_list



    def get_subject_preferences_dict(self,subject_preferences):
        subject_preferences_items = []
        for subject_preference in subject_preferences:
            sub_item = {
                'subject_code': subject_preference.subject_code,
                'periods_count_per_week': subject_preference.periods_count_per_week
            }
            sub_item['period_preferences'] = self.get_period_preferences_dict(subject_preference.period_preferences)
            subject_preferences_items.append(sub_item)
        return subject_preferences_items


    def get_period_preferences_dict(self,period_preferences):
        period_preference_items = []
        for period_preference in period_preferences:
            pref_item = {
                'no_of_period': period_preference.no_of_period
            }
            if hasattr(period_preference, 'period_order_index'):
                pref_item['period_order_index'] = period_preference.period_order_index
            if hasattr(period_preference, 'day_codes'):
                pref_item['day_codes'] = period_preference.day_codes
            period_preference_items.append(pref_item)
        return period_preference_items


    def new_period():
        return TimeTable.Period(None)

    def new_time_table():
        return TimeTable.TimeTable(None)

    def new_generation_log():
        return TimeTable.GenerationLog(None)
    class ConfigParameter:

        def __init__(self, item):
            if item is None:
                self.subject_preferences = []
            else:
                try:
                    subject_preference_items = item['subject_preferences']
                    self.subject_preferences = []
                    for subject_preference_item in subject_preference_items:
                        self.subject_preferences.append(TimeTable.SubjectPreference(subject_preference_item))
                except KeyError:
                    logger.debug('[WARN] - KeyError in TimeTable - SubjectPreferences not found')

    class SubjectPreference:

        def __init__(self, item):
            if item is None:
                self.period_preferences = []
                self.periods_count_per_week = None
                self.subject_code = None
            else:
                # self.period_preferences = []
                self.periods_count_per_week = item['periods_count_per_week']
                self.subject_code = item['subject_code']
                try:
                    period_preference_items = item['period_preferences']
                    self.period_preferences = []
                    for period_preference_item in period_preference_items:
                        self.period_preferences.append(TimeTable.PeriodPreference(period_preference_item))
                except KeyError:
                    logger.debug('[WARN] - KeyError in TimeTable - PeriodPreferences not found')

    class PeriodPreference:

        def __init__(self, item):
            if item is None:
                self.day_codes = []
                self.no_of_period = None
                self.period_order_index = None
            else:
                # self.day_codes = []
                self.no_of_period = item['no_of_period']
                try:
                    self.period_order_index = item['period_order_index']
                except KeyError:
                    logger.debug('[WARN] - KeyError in TimeTable - period_order_index not found')
                try:
                    day_code_items = item['day_codes']
                    self.day_codes = []
                    for day_code_item in day_code_items:
                        self.day_codes.append(day_code_item)
                except KeyError:
                    logger.debug('[WARN] - KeyError in TimeTable - DayCodes not found')

    class TimeTable:

        def __init__(self, item):
            if item is None:
                self.day_tables = []
            else:
                try:
                    day_tables = item['day_tables']
                    self.day_tables = []
                    for day_table in day_tables:
                        self.day_tables.append(TimeTable.DayTable(day_table))
                except Exception:
                    logger.debug('KeyError in TimeTable - day_tables not found')

    class DayTable:

        def __init__(self, item):
            if item is None:
                self.day_code = None
                self.order_index = None
                self.periods = []
            else:
                self.day_code = item['day_code']
                self.order_index = item['order_index']
                try:
                    periods = item['periods']
                    self.periods = []
                    for period in periods:      
                        self.periods.append(TimeTable.Period(period))
                except Exception:
                    logger.debug('KeyError in DayTable - periods not found')

    class Period:

        def __init__(self, item):
            if item is None:
                self.employee_key = None
                self.period_code = None
                self.subject_key = None
                self.order_index = None
                self.class_info_key = None
                self.division_code = None
                self.employees = []
            else:
                self.period_code = item['period_code']
                try :
                    self.order_index = item['order_index']
                except Exception:
                    logger.debug('KeyError in Period - order_index not found')
                try:
                    self.employee_key = item['employee_key']
                except Exception:
                    logger.debug('KeyError in Period - employee_key not found')
                try:
                    self.subject_key = item['subject_key']
                except Exception:
                    logger.debug('KeyError in Period - subject_key not found')

                try:
                    self.class_info_key = item['class_info_key']
                except Exception:
                    logger.debug('KeyError in Period - class_info_key not found')

                try:
                    self.division_code = item['division_code']
                except Exception:
                    logger.debug('KeyError in Period - division_code not found')
                try:
                    employee_list = item['employees']
                    self.employees = []
                    for employee in employee_list:
                        self.employees.append(TimeTable.Employee(employee))
                except KeyError:
                    logger.debug('[WARN] - KeyError in Period - Employee not found')

    class Employee:
        def __init__(self, item):
            if item is None:
                self.employee_key = None
                self.subject_key = None
            else:
                self.employee_key = item['employee_key']
                self.subject_key = item['subject_key']


    class GenerationLog:

        def __init__(self, item):
            if item is None:
                self.code = None
                self.note = None
            else:
                self.code = item['code']
                self.note = item['note']
