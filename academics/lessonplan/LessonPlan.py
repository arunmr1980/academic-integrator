from academics.logger import GCLogger as logger

class LessonPlan:

    def __init__(self, item):
        if item is None:
            self.lesson_plan_key = None
            self.class_key = None
            self.division = None
            self.subject_code = None
            self.topics = []
            self.resources = []
            self.assignments = []
        else:
            self.lesson_plan_key = item['lesson_plan_key']
            self.class_key = item['class_key']
            self.division = item['division']
            self.subject_code = item['subject_code']
            self.topics = []
            self.resources = []
            self.assignments = []
            try:
                topics = item["topics"]
                for topic in topics :
                     self.topics.append(Topics(topic))
            except KeyError as ke:
                logger.debug('[WARN] - KeyError in LessonPlan - topics not present'.format(str (ke)))
            try :
                resources = item['resources']
                for resource in resources :
                    self.resources.append(Resources(resource))
            except KeyError as ke:
                logger.debug('[WARN] - KeyError in LessonPlan - resources not present'.format(str (ke)))
            try :
                assignments = item['assignments']
                for assignment in assignments :
                    self.assignments.append(Assignments(assignment))
            except KeyError as ke:
                logger.debug('[WARN] - KeyError in LessonPlan - assignments not present'.format(str (ke)))



class Assignments :
    def __init__(self, item):
        if item is None :
            self.assignment_code = None
            self.description = None
            self.name = None
            self.resources = []
            self.topic_ref_code = None
        else :
            self.assignment_code = item['assignment_code']
            self.description = item['description']
            self.name = item['name']
            self.resources = item['resources']
            self.topic_ref_code = item['topic_ref_code']



class Resources :
    def __init__(self, item):
        if item is None:
            self.code = None
            self.link = None
            self.name = None
            self.publishable = None
            self.type = None
        else :
            self.code = item['code']
            self.link = item['link']
            self.name = item['name']
            self.publishable = item['publishable']
            self.type = item['type']




class Topics :
    def __init__(self, item):
        if item is None:
            self.code = None
            self.name = None
            self.order_index = None
            self.topics = []
        else :
            self.code = item['code']
            self.name = item['name']
            self.order_index = item['order_index']
            self.topics = []
            try :
                topics =item['topics']
                for topic in topics :
                    self.topics.append(Topic(topic))
            except KeyError as ke:
                logger.debug('[WARN] - KeyError in Topics - topics not present'.format(str (ke)))

class Topic :
    def __init__(self, item):
        if item is None:
            self.assignments = []
            self.code = None
            self.description = None
            self.name = None
            self.order_index = None
            self.resources = []
            self.sessions = []
        else :
            self.code = item['code']
            self.description =item['description']
            self.name = item['name']
            self.order_index = item['order_index']
            self.resources = []
            try :
                resources =item['resources']
                for resource in resources :
                    self.resources.append(Resource(resource))
            except KeyError as ke:
                logger.debug('[WARN] - KeyError in Topic - resources not present'.format(str (ke)))
            self.sessions = []
            try :
                sessions = item['sessions']
                for session in sessions :
                    self.sessions.append(Session(session))
            except KeyError as ke:
                logger.debug('[WARN] - KeyError in Topic - sessions not present'.format(str (ke)))
            self.assignments = []
            try :
                assignments = item['assignments']
                for assignment in assignments :
                    self.assignments.append(Assignment(assignment))
            except KeyError as ke:
                logger.debug('[WARN] - KeyError in Topic - assignments not present'.format(str (ke)))


class Assignment :
    def __init__(self, item):
        if item is None:
            self.code = None
            self.time_to_complete_mins = None
            self.description = None
            self.assigned_to = {}
        else :
            self.code = item['code']
            self.time_to_complete_mins = item['time_to_complete_mins']
            self.description = item['description']
            try :
                self.assigned_to = AssignedTo(item['assigned_to'])
            except KeyError as ke:
                logger.debug('[WARN] - KeyError in Assignment - assigned_to not present'.format(str (ke)))


class AssignedTo :
    def __init__(self, item):
        if item is None:
            self.due_date = None
            self.status = None
            self.type = None
        else :
            self.due_date = item['due_date']
            self.status = item['status']
            self.type = item['type']


class Resource :
    def __init__(self, item):
        if item is None:
            self.code = None
        else :
            self.code = item['code']


class Session :
    def __init__(self, item):
        if item is None:
            self.code = None
            self.completion_datetime = None
            self.completion_status = None
            self.name = None
            self.order_index = None
            self.resources = []
        else :
            self.code = item['code']
            self.completion_datetime = item['completion_datetime']
            self.completion_status = item['completion_status']
            self.name = item['name']
            self.order_index = item['order_index']
            self.resources = item['resources']

            






                