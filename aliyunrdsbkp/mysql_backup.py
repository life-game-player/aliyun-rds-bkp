import os
import sys

from aliyunsdkcore.client import AcsClient

from aliyunrdsbkp.rds_instance import RDSInstance
from aliyunrdsbkp.config import Config
from aliyunrdsbkp.scheduler import Scheduler
from aliyunrdsbkp.postman import Postman
from aliyunrdsbkp.cleaner import Cleaner
from aliyunrdsbkp.logger import Logger


class MySQLBackup:
    def __init__(self, config_file):
        self.config = Config(config_file)
        self.postman = Postman(self.config.get_mail_config())
        self.scheduler = Scheduler()
        self.cleaner = Cleaner()
        self.logger = Logger(self.config.get_err_log())
        self.succeeded_files = list()
        self.failed_files = list()
        sys.excepthook = self.logger.log_exception

    def download_db_files(self, instance, rds_instance,
                          backup_dir, backup_type):
        if self.scheduler.is_triggered_now(
                self.config.get_schedule(
                    instance,
                    backup_type
                )):
            last_bkp_time = self.config.get_last_backup_time(
                instance,
                backup_type)
            bkp_files = rds_instance.get_backup_files(
                backup_type, start_time=last_bkp_time)
            for f in bkp_files:
                curr_bkp_time = f.get_end_time()
                if curr_bkp_time > last_bkp_time:
                    last_bkp_time = curr_bkp_time
                if f.backup(backup_dir) == 0:
                    self.succeeded_files.append(f)
                else:
                    self.failed_files.append(f)
                self.config.set_last_bkp_time(
                    instance, backup_type,
                    last_bkp_time)
                # Update last backup time in config file
                self.config.update_config_file()

    def backup(self):
        for region in self.config.get_regions():
            client = AcsClient(
                self.config.get_accesskey_id(),
                self.config.get_accesskey_secret(),
                self.config.get_region_id(region)
            )
            for instance in self.config.get_instances_by_region(region):
                rds_instance = RDSInstance(
                    client,
                    self.config.get_instance_id(instance)
                )
                backup_dir = os.path.join(
                    self.config.get_backup_dir(),
                    self.config.get_region_id(region),
                    self.config.get_instance_id(instance)
                )

                # Download full backup files
                self.download_db_files(instance, rds_instance,
                                       backup_dir, 'full')

                # Download binlog files
                self.download_db_files(instance, rds_instance,
                                       backup_dir, 'binlog')

                # Clean up expired db files
                self.cleaner.clean_folder(
                    backup_dir,
                    self.config.get_retention_days(instance)
                )

        # Send backup report email
        self.postman.send_backup_report(
            self.succeeded_files,
            self.failed_files)