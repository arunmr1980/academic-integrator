from academics.logger import GCLogger as gclogger

class Leave:

    def __init__(self, item):
        if item is None:
            self.leave_key = None
            self.institution_key = None
            self.subscriber_key = None
            self.subscriber_type = None
            self.from_date = None
            self.from_time = None
            self.to_date = None
            self.to_time = None
            self.reason = None
        else:
            self.leave_key = item["leave_key"]
            self.institution_key = item["institution_key"]
            self.subscriber_key = item["subscriber_key"]
            self.subscriber_type = item["subscriber_type"]
            self.from_date = item["from_date"]
            self.to_date = item["to_date"]
            try:
                self.from_time = item["from_time"]
            except KeyError as ke:
                gclogger.debug ('KeyError from_time '.format (str (ke)))
            try:
                self.status = item["status"]
            except KeyError as ke:
                gclogger.debug ('KeyError status '.format (str (ke)))
            try:
                self.to_time = item["to_time"]
            except KeyError as ke:
                gclogger.debug ('KeyError to_time '.format (str (ke)))
            try:
                self.reason = item["reason"]
            except KeyError as ke:
                gclogger.debug ('KeyError reason '.format (str (ke)))

    def get_as_dict(self):
        return vars(self)
