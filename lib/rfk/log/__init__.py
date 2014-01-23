import logging

import rfk.database
from rfk.database.base import Log


def init_db_logging(name):
    logger = logging.getLogger(name)
    logger.addHandler(DBLogHandler())
    logger.setLevel(logging.INFO)
    return logger


class DBLogHandler(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self)

    def emit(self, record):
        log = Log(message=record.getMessage(), module=record.name, severity=record.levelno)
        rfk.database.session.add(log)
        rfk.database.session.flush()
