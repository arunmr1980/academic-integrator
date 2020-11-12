from academics.logger import GCLogger as gclogger

class Exam:

    def __init__(self, item):
        if(item is not None):
            self.class_key = item["class_key"]
            self.division = item["division"]
            self.from_time = item["from_time"]
            self.to_time = item["to_time"]
            self.max_score = item["max_score"]
            self.subject_code = item["subject_code"]
            self.subject_name = item["subject_name"]
            self.series_code = item["series_code"]
            self.exam_key = item["exam_key"]
            try:
                self.academic_year = item["academic_year"]
            except KeyError as ke:
                gclogger.debug(' KeyError in Exam -  academic_year not found'.format(str(ke)))
            try:
                self.visibility = item["visibility"]
            except KeyError as ke:
                gclogger.debug(' KeyError in Exam -  visibility not found'.format(str(ke)))
            try:
                self.type = item["type"]
            except KeyError as ke:
                gclogger.debug(' KeyError in Exam -  type not found'.format(str(ke)))
            try:
                self.assessment_type = item["assessment_type"]
            except KeyError as ke:
                gclogger.debug(' KeyError in Exam -  assessment_type not found'.format(str(ke)))
            try:
                self.name = item["name"]
            except KeyError as ke:
                gclogger.debug(' KeyError in Exam -  name not found'.format(str(ke)))
            try:
                previous_schedule = item["previous_schedule"]
                self.previous_schedule = PreviousSchedule(previous_schedule)
            except KeyError as ke:
                gclogger.debug(' KeyError in Exam -  previous_schedule not found'.format(str(ke)))
            try:
                audit_logs = item['audit_logs']
                self.audit_logs = []
                for audit_log in audit_logs:
                    self.audit_logs.append(AuditLog(audit_log))
            except KeyError as ke:
                gclogger.debug(' KeyError in Exam - audit_logs not found'.format(str(ke)))
            
            try:
                self.institution_key = item["institution_key"]
            except KeyError as ke:
                gclogger.debug(' KeyError in Exam -  institution_key not found'.format(str(ke)))
            try:
                self.schedulable = item["schedulable"]
            except KeyError as ke:
                gclogger.debug(' KeyError in Exam -  schedulable not found'.format(str(ke)))
            
            try:
                self.schedule_flag = item["schedule_flag"]
            except KeyError as ke:
                gclogger.debug(' KeyError in Exam -  schedule_flag not found'.format(str(ke)))
            try:
                self.status = item["status"]
            except KeyError as ke:
                gclogger.debug(' KeyError in Exam -  status not found'.format(str(ke)))


            try:
                self.date_time = item["date_time"]
            except KeyError as ke:
                gclogger.debug(' KeyError in Exam -  date_time not found'.format(str(ke)))


           

    def make_exam_dict(item) :
        exam = {
            "class_key" : item.class_key,
            "division" : item.division,
            "from_time" : item.from_time,
            "to_time" :item.to_time
        }
        return exam
            

class AuditLog:
    def __init__(self, item):
        if(item is not None):
            try:
                self.datetime = item["datetime"]
            except KeyError as ke:
                gclogger.debug(' KeyError in AuditLog -  datetime not found'.format(str(ke)))
            try:
                self.message = item["message"]
            except KeyError as ke:
                gclogger.debug(' KeyError in AuditLog -  message not found'.format(str(ke)))


class PreviousSchedule :
    def __init__(self, item):
        if (item is not None):
            self.date_time = item['date_time']
            self.from_time = item['from_time']
            self.to_time = item['to_time']



