from academics.logger import GCLogger as logger
import pprint
pp = pprint.PrettyPrinter(indent=4)

class Calendar:

    def __init__(self, item):
        if item is None:
            self.calendar_key = None
            self.subscriber_key = None
            self.subscriber_type = None
            self.events = []
            self.calendar_date = None
            self.institution_key = None
        else:

            self.calendar_key = item["calendar_key"]
            self.subscriber_key = item["subscriber_key"]
            self.subscriber_type = item["subscriber_type"]
            self.calendar_date = item["calendar_date"]
            self.events = []
            self.institution_key = None
            try:
                events = item['events']
                for event in events :
                    self.events.append(Event(event))
            except KeyError as ke:
                logger.debug ('[WARN] - KeyError in Calendar -events not present'.format (str (ke)))
            try:
                self.institution_key = item["institution_key"]
            except KeyError as ke:
                logger.debug ('[WARN] - KeyError in Calendar -institution_key not present'.format (str (ke)))

    def make_calendar_dict(self, calendar):
        if calendar is not None:
            item = {
                'calendar_key': calendar.calendar_key,
                'subscriber_type': calendar.subscriber_type,
                'calendar_date': str (calendar.calendar_date),
                'subscriber_key': calendar.subscriber_key
            }
        if calendar.institution_key is not None:
            item['institution_key'] = calendar.institution_key
        if calendar.events is not None:
            item['events'] = self.get_calendar_event_list(calendar.events)
        return item

    def get_calendar_event_list(self,event_list):
        collection_list = []
        for event in event_list:
            item = {
                'event_code': event.event_code
            }
            if hasattr(event,'event_type') and event.event_type is not None :
                item['event_type'] = event.event_type
            if hasattr(event,'from_time') and event.from_time is not None :
                item['from_time'] = event.from_time
            if hasattr(event,'to_time') and event.to_time is not None :
                item['to_time'] = event.to_time

            if hasattr(event,'ref_calendar_key') and event.ref_calendar_key is not None :
                item['ref_calendar_key'] = event.ref_calendar_key
            if hasattr(event, 'params') and event.params is not None and len(event.params) > 0  :
                item['params'] = self.get_event_params_list(event.params)
            collection_list.append(item)
        return collection_list

    def get_event_params_list(self,params) :
        collection_params = []
        for param in params :
            item = {
                'key' : param.key,
                'value' :param.value
            }
            collection_params.append(item)
        return collection_params





class Event :
    def __init__(self, item):
        if item is None:
            self.event_code = None
            self.event_type = None
            self.from_time = None
            self.to_time = None
            self.is_class = None
            self.ref_calendar_key = None
            self.params = []
        else :
            try :
                ref_calendar_key = item['ref_calendar_key']
                self.ref_calendar_key = ref_calendar_key
            except KeyError as ke:
                logger.debug ('[WARN] - KeyError in Event -ref_calendar_key not present'.format (str (ke)))
            try :
                is_class = item['is_class']
                self.is_class = is_class
            except KeyError as ke:
                logger.debug ('[WARN] - KeyError in Event -is_class not present'.format (str (ke)))

            try :
                event_code = item['event_code']
                self.event_code = event_code
            except KeyError as ke:
                logger.debug ('[WARN] - KeyError in Event -event_code not present'.format (str (ke)))
            try :
                event_type = item['event_type']
                self.event_type = item['event_type']
            except KeyError as ke:
                logger.debug ('[WARN] - KeyError in Event -event_type not present'.format (str (ke)))
            try :
                from_time = item['from_time']
                self.from_time = item['from_time']
            except KeyError as ke:
                logger.debug ('[WARN] - KeyError in Event -from_time not present'.format (str (ke)))
            try :
                to_time = item['to_time']
                self.to_time = item['to_time']
            except KeyError as ke:
                logger.debug ('[WARN] - KeyError in Event -to_time not present'.format (str (ke)))
            try :
                self.params = []
                params = item['params']
                for param in params:
                    self.params.append(Param(param))
            except KeyError as ke:
                logger.debug ('[WARN] - KeyError in Event -params not present'.format (str (ke)))

class Param:
    def __init__(self, item):
        if item is None:
            self.key = None
            self.value = None
        else :
            self.key = item['key']
            self.value = item['value']
