from academics.logger import GCLogger as logger


class School:

    def __init__(self, item):
        self.school_id = item['school_id']
        self.name = item['name']
        try:
            self.transport = Transport(item['transport'])
        except KeyError as ke:
            gclogger.debug( '[WARN] - KeyError in School - transport not found'.format(str(ke)))

        academic_year_items = item['academic_years']
        self.academic_years = []
        for academic_year_item in academic_year_items:
            self.academic_years.append(AcademicYear(academic_year_item))

class Transport:

    def __init__(self, item):
        self.routes = item['routes']
        self.trips = item['trips']

class AcademicYear:

    def __init__(self, item):
        self.code = item['code']
        self.start_date = item['start_date']
        self.end_date = item['end_date']
        self.name = item['name']