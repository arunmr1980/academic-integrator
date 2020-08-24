import requests
import json
import logging
from academics.logger.ConfigFile import config


class NotificationStreamHandler(logging.Handler):

    def __init__(self):
        logging.Handler.__init__(self)

    def emit(self, record):
        url = config.notificationConfig.get('notification_msg', 'url')
        token = config.notificationConfig.get('notification_msg', 'token')
        partner_key = config.notificationConfig.get('notification_msg', 'partner_key')
        identifier = config.notificationConfig.get('notification_error', 'identifier')
        logmsg = self.format(record)
        data = {"partner_key": partner_key, "date_time": "1893291318", "message": {"text": logmsg},
            "delivery_channels": [
                {"type": "sms", "to_identifier": identifier, "status": "pending", "last_attempt_date_time": "43943333",
                    "no_of_attempts": "0"}]}
        headers = {'Authorization': 'Basic ' + token, "Content-Type": "application/json"}
        return requests.put(url, data=json.dumps(data), headers=headers).content
