import json
from datetime import datetime


class Config:
    def __init__(self, config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            self.conf = json.load(f)
            self.config_file = config_file

    def get_accesskey_id(self):
        return self.conf['AccessKeyId']

    def get_accesskey_secret(self):
        return self.conf['AccessKeySecret']

    def get_regions(self):
        return self.conf['Regions']

    def get_region_id(self, region):
        return region['RegionID']

    def get_instances_by_region(self, region):
        return region['DBInstances']

    def get_backup_dir(self):
        return self.conf['BackupHome']

    def get_failed_dir(self):
        return self.conf['FailedDownloads']

    def get_mail_config(self):
        return self.conf['MailConfig']

    def get_instance_id(self, instance):
        return instance['DBInstanceId']

    def get_last_backup_time(self, instance, backup_type):
        last_backup_time = datetime(2001, 1, 1)
        if backup_type == 'full':
            last_backup_time = datetime.strptime(
                instance['LastFullBackup']['BackupEndTime'],
                '%Y-%m-%d %H:%M:%S')
        elif backup_type == 'binlog':
            last_backup_time = datetime.strptime(
                instance['LastBinlogBackup']['BackupEndTime'],
                '%Y-%m-%d %H:%M:%S')
        return last_backup_time

    def get_schedule(self, instance, backup_type):
        schedule = None
        if backup_type == 'full':
            schedule = instance['Schedule']['FullBackup']['Plan']
        elif backup_type == 'binlog':
            schedule = instance['Schedule']['BinlogBackup']['Plan']
        return schedule

    def get_retention_days(self, instance):
        return instance['BackupRetentionDays']

    def get_err_log(self):
        return self.conf['ErrorLog']

    def set_last_bkp_time(self, instance, backup_type, last_backup_time):
        if backup_type == 'full':
            instance['LastFullBackup']['BackupEndTime'] \
                = last_backup_time.strftime('%Y-%m-%d %H:%M:%S')
        elif backup_type == 'binlog':
            instance['LastBinlogBackup']['BackupEndTime'] \
                = last_backup_time.strftime('%Y-%m-%d %H:%M:%S')

    def update_config_file(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.conf, f, indent=4)
