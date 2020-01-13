import logging
from logging import handlers
from datetime import datetime


class Logger:
    def __init__(self):
        self.logger = logging.getLogger()

    def set(self, log_path):
        file_rotating_file = handlers.RotatingFileHandler(
            log_path, maxBytes=1000000, backupCount=2,
            encoding='utf-8'
        )
        log_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")
        file_rotating_file.setFormatter(log_formatter)
        self.logger.addHandler(file_rotating_file)
        self.logger.setLevel(logging.INFO)

    def error(self, msg):
        self.logger.error(msg, exc_info=True)

    def warning(self, msg):
        self.logger.warning(msg)

    def info(self, msg):
        self.logger.info(msg)


logger = Logger()
