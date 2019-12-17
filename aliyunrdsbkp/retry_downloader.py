import os
import pickle

from aliyunrdsbkp.postman import Postman
from aliyunrdsbkp.config import Config


class RetryDownloader:
    def __init__(self, config_file):
        self.config = Config(config_file)
        self.failed_dir = self.config.get_failed_dir()
        self.backup_dir = self.config.get_backup_dir()
        self.succeeded_files = list()
        self.failed_files = list()
        self.postman = Postman(self.config.get_mail_config())

    def run(self):
        files = os.listdir(self.failed_dir)
        for f in files:
            file_path = os.path.join(self.failed_dir, f)
            with open(file_path, 'rb') as fp:
                file = pickle.load(fp)
            if not file.backup(self.backup_dir):
                # Remove pickle file if succeeded
                os.remove(file_path)
                self.succeeded_files.append(f)
            else:
                self.failed_files.append(f)

        # Send backup report email
        self.postman.send_backup_report(
            self.succeeded_files,
            self.failed_files)
