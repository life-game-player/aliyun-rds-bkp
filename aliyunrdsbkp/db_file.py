import os
import time
import pickle
import urllib.request
from urllib.parse import urlparse
import shutil
from datetime import timedelta

from aliyunrdsbkp.config import Config


class DBFile:
    def __init__(self, download_url, host_id,
            region_id, instance_id, start_time, end_time,
            file_type, file_status=0, file_size=0, checksum=0):
        self.file_type = file_type
        self.download_url = download_url
        self.host_id = host_id
        self.region_id = region_id
        self.instance_id = instance_id
        self.file_status = file_status
        self.file_size = file_size
        self.checksum = checksum
        self.start_time = start_time
        self.end_time = end_time
        self.parse_file_name()
        self.rds_instance = None

    def parse_file_name(self):
        self.file_name = urlparse(self.download_url).path.split('/')[-1]
        self.file_name = str(self.host_id) + '.' + self.file_name

    def get_end_time(self):
        return self.end_time

    def get_start_time(self):
        return self.start_time

    def get_file_name(self):
        return self.file_name

    def get_file_type(self):
        return self.file_type

    def get_file_size(self):
        return self.file_size

    def get_download_url(self):
        return self.download_url

    def set_rds_instance(self, instance):
        self.rds_instance = instance

    def download(self, dest_file, retry=5):
        rest = retry
        while rest > 0:
            try:
                "Start downloading..."
                with urllib.request.urlopen(self.download_url) as response, \
                        open(dest_file, 'wb') as f:
                    shutil.copyfileobj(response, f)
            except urllib.error.HTTPError as e:
                rest -= 1
                if e.code == 403:
                    if self.reset_download_url() == 0:
                        self.download(dest_file, rest)
                else:
                    print(e)
                    time.sleep(20)  # Retry after some seconds
            except Exception as e:
                print(e)
                rest -= 1
                time.sleep(20)  # Retry after some seconds
            else:
                return 0
        return 1

    def reset_download_url(self):
        print("Trying to refresh download url...")
        if self.rds_instance is None:
            print("RDS instance was not found")
            return 1  # RDS instance was not found
        start_time = self.start_time
        end_time = self.start_time
        if self.file_type == "binlog":
            start_time -= timedelta(seconds=2)
            end_time += timedelta(seconds=1)
        if self.file_type == "full":
            start_time -= timedelta(days=1)
            end_time += timedelta(days=1)
        backup_files = self.rds_instance.get_backup_files(
            self.file_type,
            start_time,
            end_time
        )
        if not backup_files:
            print("No backup file was found")
            return 2  # Get none backup file
        for backup_file in backup_files:
            if (
                backup_file.file_type == self.file_type and
                backup_file.start_time == self.start_time and
                backup_file.end_time == self.end_time
            ):
                self.download_url = backup_file.get_download_url()
                return 0

    def validate_file(self, dest_file):
        # Compare file size
        downloaded_size = os.path.getsize(dest_file)
        if downloaded_size >= self.file_size:
            return True
        else:
            return False

    def get_host_id(self):
        return self.host_id

    def backup(self, backup_dir):
        if self.file_status > 0:
            return 1  # Fail the backup if file status is abnormal
        else:
            dest_dir = os.path.join(backup_dir,
                                    self.region_id,
                                    self.instance_id,
                                    str(self.end_time.year),
                                    str(self.end_time.month),
                                    str(self.end_time.day))
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)  # Create derectory if not existing
            dest_file = os.path.join(dest_dir, self.file_name)
            if self.download(dest_file):  # Download failed
                if os.path.exists(dest_file):  # Clear semi-finished file if any
                    os.remove(dest_file)
                return 2
            if self.validate_file(dest_file):
                return 0
            else:
                # Downloaded file is invalid
                os.remove(dest_file)
                return 2

    def dump(self, failed_dir):
        failed_file_path = os.path.join(
            failed_dir, self.file_name
        )
        if not os.path.exists(failed_file_path):
            with open(failed_file_path, 'wb') as fp:
                pickle.dump(self, fp, pickle.HIGHEST_PROTOCOL)

    def __str__(self):
        return (
            "Region ID:{}, Instance ID:{}, File Type:{},\n"
            "File Status:{}, Start Time:{}, End Time:{},\n"
            "Download Link:{}, File Size:{}, Host ID:{}\n".format(
                self.region_id,
                self.instance_id,
                self.file_type,
                self.file_status,
                self.start_time,
                self.end_time,
                self.download_url,
                self.file_size,
                self.host_id
            )
        )
