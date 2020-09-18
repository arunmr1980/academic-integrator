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


    def make_lessonplan_dict(self,lessonplan) :
        item ={
            'lesson_plan_key' : lessonplan.lesson_plan_key,
            'class_key' : lessonplan.class_key,
            'division' : lessonplan.division,
            'subject_code' : lessonplan.subject_code
        }
        if hasattr(lessonplan,'topics') and lessonplan.topics is not None :
            item['topics'] = self.get_topics_dict(lessonplan.topics)
        if hasattr(lessonplan,'resources') and lessonplan.resources is not None :
            item['resources'] = self.get_resources_dict(lessonplan.resources)
        if hasattr(lessonplan,'assignments') and lessonplan.assignments is not None :
            item['assignments'] = self.get_assignments_dict(lessonplan.assignments)
        return item

    def get_assignments_dict(self,assignments) :
        assignments_list = []
        for assignment in assignments :
            item = {
                'assignment_code' : assignment.assignment_code,
                'description' :assignment.description,
                'name' : assignment.name,
            }
            if hasattr(assignment,'topic_ref_code') and assignment.topic_ref_code is not None :
                item['topic_ref_code'] = assignment.topic_ref_code
            if hasattr(assignment,'session_ref_code') and assignment.session_ref_code is not None :
                item['session_ref_code'] = assignment.session_ref_code
            if hasattr(assignment,'resources') and assignment.resources is not None :
                item['resources'] = assignment.resources
            assignments_list.append(item)
        return assignments_list


    def get_resources_dict(self,resources) :
        resource_list =[]
        for resource in resources :
            item ={
                'code' : resource.code,
                'name' : resource.name,
                'publishable' : resource.publishable,
                'type' :resource.type
            }
            if hasattr(resource,'description') and resource.description is not None :
                item['description'] = resource.description
            if hasattr(resource,'description') and resource.description is not None :
                item['link'] = resource.link
            if hasattr(resource,'file_key') and resource.file_key is not None :
                item['file_key'] = resource.file_key
            resource_list.append(item)
        return resource_list

    def get_topics_dict(self,topics) :
        topics_list =[]
        for topic in topics :
            item ={
                'code' : topic.code,
                'name' : topic.name,
                'order_index': topic.order_index
            }
            if hasattr(topic,'topics') and topic.topics is not None :
                item['topics'] = self.get_topic(topic.topics)
            if hasattr(topic,'comments') and topic.topics is not None :
                item['comments'] = self.get_comments(topic.comments)
            topics_list.append(item)
        return topics_list


    def get_comments(self,comments) :
        comments_list =[]
        for comment in comments :
            item = {
                'comment' : comment.comment,
                'date_time' : comment.date_time,
                'employee_key' : comment.employee_key,
                'employee_name' : comment.employee_name,
                'type' : comment.type
            }
            comments_list.append(item)
        return comments_list


    def get_topic(self,topics) :
        topic_list = []
        for topic in topics :
            item = {
                'code' : topic.code ,
                'name' : topic.name,
                'order_index' : topic.order_index,
            }
            if hasattr(topic,'description') and topic.description is not None :
                item['description'] = topic.description

            if hasattr(topic,'resources') and topic.resources is not None :
                item['resources'] = self.get_resource(topic.resources)

            if hasattr(topic,'assignments') and topic.assignments is not None :
                item['assignments'] = self.get_assignment(topic.assignments)

            if hasattr(topic,'sessions') and topic.sessions is not None :
                item['sessions'] = self.get_sessions(topic.sessions)
            topic_list.append(item)
        return topic_list

    def get_assignment(self,assignments) :
        assignments_list = []
        for assignment in assignments :
            item = {
                'code' : assignment.code,
                'time_to_complete_mins' : assignment.time_to_complete_mins
            }
            if hasattr(assignment,'assigned_to') and assignment.assigned_to is not None :
                item['assigned_to'] = self.get_assigned_to(assignment.assigned_to)
            assignments_list.append(item)
        return assignments_list

    def get_assigned_to(self,assigned_to):
        item = {
            'status' : assigned_to.status,
            'type' :assigned_to.type
        }
        if hasattr(assigned_to,'assigned_date') and assigned_to.assigned_date is not None :
            item['assigned_date'] = assigned_to.assigned_date,
        if hasattr(assigned_to,'due_date') and assigned_to.due_date is not None :
            item['due_date'] = assigned_to.due_date
        return item

    def get_sessions(self,sessions) :
        sessions_list = []
        for session in sessions :
            item = {
                'code' :session.code,
                'name' :session.name,
                'order_index' :session.order_index
            }
            if hasattr(session,'completion_status') and session.completion_status is not None :
                item['completion_status'] = session.completion_status
            if hasattr(session,'completion_datetime') and session.completion_datetime is not None :
                item['completion_datetime'] = session.completion_datetime
            if hasattr(session,'description') and session.description is not None :
                item['description'] = session.description
            if hasattr(session,'resources') and session.resources is not None :
                item['resources'] = session.resources
            if hasattr(session,'comments') and session.comments is not None :
                item['comments'] = self.get_comments(session.comments)
            if hasattr(session,'schedule') and session.schedule is not None :
                item['schedule'] = self.get_schedule(session.schedule)
            sessions_list.append(item)
        return sessions_list

    def get_schedule(self,schedule) :
        item = {
            'calendar_key': schedule.calendar_key,
            'event_code' :schedule.event_code,
            'start_time' : schedule.start_time,
            'end_time' :schedule.end_time
        }
        return item

    def get_resource(self,resources) :
        resource_list =[]
        for resource in resources :
            item ={}
            if resource.code is not None :
                item['code'] = resource.code
            resource_list.append(item)
        return resource_list
class Assignments :
    def __init__(self, item):
        if item is None :
            self.assignment_code = None
            self.description = None
            self.name = None
            self.resources = []
            self.topic_ref_code = None
            self.session_ref_code = None
        else :
            self.assignment_code = item['assignment_code']
            self.description = item['description']
            self.name = item['name']
            try :
                resources = item['resources']
                self.resources = resources
            except KeyError as ke:
                logger.debug('[WARN] - KeyError in Assignments - resources not present'.format(str (ke)))
            try :
                topic_ref_code = item['topic_ref_code']
                self.topic_ref_code = topic_ref_code
            except KeyError as ke:
                logger.debug('[WARN] - KeyError in Assignments - topic_ref_code not present'.format(str (ke)))
            try :
                session_ref_code = item['session_ref_code']
                self.session_ref_code = session_ref_code
            except KeyError as ke:
                logger.debug('[WARN] - KeyError in Assignments - session_ref_code not present'.format(str (ke)))
class Resources :
    def __init__(self, item):
        if item is None:
            self.code = None
            self.link = None
            self.name = None
            self.publishable = None
            self.type = None
            self.file_key = None
        else :
            self.code = item['code']
            self.name = item['name']
            self.publishable = item['publishable']
            self.type = item['type']
            try :
                link = item['link']
                self.link = link
            except KeyError as ke:
                logger.debug('[WARN] - KeyError in Resources - link not present'.format(str (ke)))

            try :
                file_key = item['file_key']
                self.file_key = file_key
            except KeyError as ke:
                logger.debug('[WARN] - KeyError in Resources - file_key not present'.format(str (ke)))
class Topics :
    def __init__(self, item):
        if item is None:
            self.code = None
            self.name = None
            self.order_index = None
            self.topics = []
            self.comments = []
        else :
            self.code = item['code']
            self.name = item['name']
            self.order_index = item['order_index']
            self.topics = []
            self.comments = []
            try :
                topics =item['topics']
                for topic in topics :
                    self.topics.append(Topic(topic))
            except KeyError as ke:
                logger.debug('[WARN] - KeyError in Topics - topics not present'.format(str (ke)))
            try :
                comments = item['comments']
                for comment in comments :
                    self.comments.append(Comment(comment))
            except KeyError as ke:
                logger.debug('[WARN] - KeyError in Topics - comments not present'.format(str (ke)))
class Comment :
    def __init__(self, item):
        if item is None:
            self.comment = None
            self.date_time = None
            self.employee_key = None
            self.employee_name = None
            self.type = None
        else :
            try :
                comment =item['comment']
                self.comment = comment
            except KeyError as ke:
                logger.debug('[WARN] - KeyError in Comment - comment not present'.format(str (ke)))
            try :
                date_time =item['date_time']
                self.date_time = date_time
            except KeyError as ke:
                logger.debug('[WARN] - KeyError in Comment - date_time not present'.format(str (ke)))
            try :
                employee_key =item['employee_key']
                self.employee_key = employee_key
            except KeyError as ke:
                logger.debug('[WARN] - KeyError in Comment - employee_key not present'.format(str (ke)))
            try :
                employee_name =item['employee_name']
                self.employee_name = employee_name
            except KeyError as ke:
                logger.debug('[WARN] - KeyError in Comment - employee_name not present'.format(str (ke)))
            try :
                type =item['type']
                self.type = type
            except KeyError as ke:
                logger.debug('[WARN] - KeyError in Comment - type not present'.format(str (ke)))
class Topic :
    def __init__(self, item):
        if item is None:
            self.assignments = []
            self.code = None
            self.description = None
            self.comments = []
            self.name = None
            self.order_index = None
            self.resources = []
            self.sessions = []
        else :
            self.code = item['code']
            self.name = item['name']
            self.order_index = item['order_index']
            self.resources = []
            self.comments = []
            try :
                description =item['description']
                self.description = description
            except KeyError as ke:
                logger.debug('[WARN] - KeyError in Topic - description not present'.format(str (ke)))

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

            try :
                comments = item['comments']
                for comment in comments :
                    self.comments.append(Comment(comment))
            except KeyError as ke:
                logger.debug('[WARN] - KeyError in Topic - comments not present'.format(str (ke)))
class Assignment :
    def __init__(self, item):
        if item is None:
            self.code = None
            self.time_to_complete_mins = None
            # self.description = None
            self.assigned_to = {}
        else :
            self.code = item['code']
            self.time_to_complete_mins = item['time_to_complete_mins']
            # self.description = item['description']
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
            self.assigned_date = None
        else :
            self.status = item['status']
            try :
                self.type = item['type']
            except KeyError as ke:
                logger.debug('[WARN] - KeyError in AssignedTo - type not present'.format(str (ke)))
            try :
                self.assigned_date = item['assigned_date']
            except KeyError as ke:
                logger.debug('[WARN] - KeyError in AssignedTo - assigned_date not present'.format(str (ke)))
            try :
                self.due_date = item['due_date']
            except KeyError as ke:
                logger.debug('[WARN] - KeyError in AssignedTo - due_date not present'.format(str (ke)))
class Resource :
    def __init__(self, item):
        if item is None:
            self.code = None
        else :
            try :
                code = item['code']
                self.code = code
            except KeyError as ke:
                logger.debug ('[WARN] - KeyError in Resource - code not present'.format (str (ke)))
class Session :
    def __init__(self, item):
        if item is None:
            self.code = None
            self.description = None
            self.completion_datetime = None
            self.completion_status = None
            self.name = None
            self.order_index = None
            self.resources = []
            self.comments = []
            self.schedule = {}
        else :
            self.code = item['code']
            self.name = item['name']
            self.order_index = item['order_index']
            self.comments = []
            try :
                comments = item['comments']
                for comment in comments :
                    self.comments.append(Comment(comment))
            except KeyError as ke:
                logger.debug('[WARN] - KeyError in Session - comments not present'.format(str (ke)))

            try :
                description = item['description']
                self.description = description
            except KeyError as ke:
                logger.debug ('[WARN] - KeyError in Session - description not present'.format (str (ke)))
            try :
                completion_datetime = item['completion_datetime']
                self.completion_datetime = completion_datetime
            except KeyError as ke:
                logger.debug ('[WARN] - KeyError in Session - completion_datetime not present'.format (str (ke)))

            try :
                completion_status = item['completion_status']
                self.completion_status = completion_status
            except KeyError as ke:
                logger.debug ('[WARN] - KeyError in Session - completion_status not present'.format (str (ke)))
            try :
                resources = item['resources']
                self.resources = resources
            except KeyError as ke:
                logger.debug ('[WARN] - KeyError in Session - resources not present'.format (str (ke)))

            try :
                self.schedule = Schedule(item['schedule'])
            except KeyError as ke:
                logger.debug('[WARN] - KeyError in Session - schedule not present'.format(str (ke)))


class Schedule :
    def __init__(self, item):
        if item is None:
            self.calendar_key = None
            self.event_code = None
            self.start_time = None
            self.end_time = None
        else :
            self.calendar_key = item['calendar_key']
            self.event_code = item['event_code']
            self.start_time = item['start_time']
            self.end_time = item['end_time']
