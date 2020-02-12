import os
import pickle

from aliyunsdkcore.client import AcsClient

from aliyunrdsbkp.rds_instance import RDSInstance
from aliyunrdsbkp.postman import Postman
from aliyunrdsbkp.config import Config
from aliyunrdsbkp.logger import logger


class RetryDownloader:
    def __init__(self, config_file):
        self.config = Config(config_file)
        logger.set(self.config.get_err_log())
        self.failed_dir = self.config.get_failed_dir()
        self.backup_dir = self.config.get_backup_dir()
        self.succeeded_files = list()
        self.failed_files = list()
        self.postman = Postman(self.config.get_mail_config())

    def run(self):
        files = os.listdir(self.failed_dir)
        for f in files:
            logger.info("Retry to download {}...".format(f))
            file_path = os.path.join(self.failed_dir, f)
            with open(file_path, 'rb') as fp:
                file = pickle.load(fp)
                rds_instance = RDSInstance(
                    AcsClient(
                        self.config.get_accesskey_id(),
                        self.config.get_accesskey_secret(),
                        file.region_id
                    ),
                    file.region_id,
                    file.instance_id,
                )
                file.set_rds_instance(rds_instance)
            logger.info("File information has been extracted.")
            if not file.backup(self.backup_dir):
                # Remove pickle file if succeeded
                os.remove(file_path)
                self.succeeded_files.append(file)
            else:
                self.failed_files.append(file)

        # Send backup report email
        if (
            len(self.succeeded_files) > 0 or
            len(self.failed_files) > 0
        ):
            self.postman.send_backup_report(
                self.succeeded_files,
                self.failed_files
            )
