import logging
from logging import handlers
from datetime import datetime


class Logger:
    def __init__(self, log_path):
        self.logger = logging.getLogger()
        self.log_path = log_path

    def log_exception(self, expt_type, expt_value, tb):
        self.logger.setLevel(logging.DEBUG)
        file_rotating_file = handlers.RotatingFileHandler(
            self.log_path, maxBytes=1000000, backupCount=2,
            encoding='utf-8')
        file_rotating_file.setLevel(logging.DEBUG)
        self.logger.addHandler(file_rotating_file)
        self.logger.info(
            'Timestamp: %s' % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        self.logger.error(
            "Uncaught exception:",
            exc_info=(expt_type, expt_value, tb)
        )
        self.logger.info("")
