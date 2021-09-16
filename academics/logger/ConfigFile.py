import configparser
import os


class _ConfigLoader:
    # Configuration File Loader Class Implementation
    def __init__(self):
        self.notificationConfig = readconfigfile(self)


def readconfigfile(self):
    parser = configparser.ConfigParser()
    parser.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'environ.ini'))
    return parser


config = _ConfigLoader()
