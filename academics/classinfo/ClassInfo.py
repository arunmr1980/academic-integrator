from academics.logger import GCLogger as gclogger

class ClassInfo:

    def __init__(self, item):
        if(item is not None):
            self.class_info_key = item["class_info_key"]
            self.school_key = item["school_key"]
            try:
                self.class_code = item["class_code"]
            except KeyError as ke:
                gclogger.debug(' KeyError in ClassInfo - class_code not found'.format(str(ke)))
            self.name = item["name"]
            self.type = item["type"]
            self.divisions = []
            try:
                division_items = item['divisions']
                for division_item in division_items:
                    self.divisions.append(Division(division_item))
            except KeyError as ke:
                gclogger.debug(' KeyError in ClassInfo - divisions not found'.format(str(ke)))
            try:
                subject_items = item['subjects']
                self.subjects = []
                for subject_item in subject_items:
                    self.subjects.append(Subject(subject_item))
            except KeyError as ke:
                gclogger.debug(' KeyError in ClassInfo - subjects not found'.format(str(ke)))


class Subject:

    def __init__(self, item):
        if(item is not None):
            try:
                self.name = item["name"]
            except KeyError as ke:
                gclogger.debug(' KeyError in Subject - subject name not found'.format(str(ke)))
            self.code = item["code"]
            try:
                elective_subject_items = item['elective_subjects']
                self.elective_subjects = []
                for elective_subject_item in elective_subject_items:
                    self.elective_subjects.append(Subject(elective_subject_item))
            except KeyError as ke:
                gclogger.debug(' KeyError in Subject - elective_subjects not found'.format(str(ke)))




class Division:

    def __init__(self, item):
        if(item is not None):
            self.name = item["name"]
            self.code = item["code"]
            self.students = []
            self.subject_teachers =[]
            try:
                subject_teachers = item['subject_teachers']
                for subject_teacher in subject_teachers :
                    self.subject_teachers.append(SubjectTeacher(subject_teacher))
            except KeyError as ke:
                logger.debug ('[WARN] - KeyError in Calendar -events not present'.format (str (ke)))
            try:
                self.class_teacher_employee_key = item["class_teacher_employee_key"]
            except KeyError as ke:
                gclogger.debug(' KeyError in Division - class_teacher_employee_key not found'.format(str(ke)))

            try:
                subject_teachers_items = item['subject_teachers']
                self.subject_teachers = []
                for subject_teachers_item in subject_teachers_items:
                    self.subject_teachers.append(SubjectTeacher(subject_teachers_item))
            except KeyError as ke:
                gclogger.debug(' KeyError in Division - subject_teachers not found'.format(str(ke)))
            try:
                studentList = item["students"]
                for student in studentList:
                    self.students.append(Student(student))
            except KeyError as ke:
                gclogger.debug(' KeyError in ClassDivision - students not found'.format(str(ke)))

class Student:
    def __init__(self, item):
        if item is None:
            self.student_key = None
        else:
            try:
                self.student_key = item["student_key"]
            except KeyError as ke:
                gclogger.debug(' KeyError in Student - student_key not found'.format(str(ke)))


class SubjectTeacher:

    def __init__(self, item):
        if(item is not None):
            self.subject_code = item["subject_code"]
            try:
                self.teacher_employee_key = item["teacher_employee_key"]
                gclogger.debug("[ClassInfo] Teacher employee key " + self.teacher_employee_key)
            except KeyError as ke:
                gclogger.debug(' KeyError in SubjectTeacher - teacher_employee_key not found'.format(str(ke)))