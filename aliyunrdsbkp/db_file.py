import os
import urllib.request
from urllib.parse import urlparse
import shutil


class DBFile:
    def __init__(self, download_url, host_id, start_time, end_time,
                 file_type, file_status=0, file_size=0, checksum=0):
        self.file_type = file_type
        self.download_url = download_url
        self.host_id = host_id
        self.file_status = file_status
        self.file_size = file_size
        self.checksum = checksum
        self.start_time = start_time
        self.end_time = end_time
        self.parse_file_name()

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

    def download(self, dest_file):
        with urllib.request.urlopen(self.download_url) as response, \
                open(dest_file, 'wb') as f:
            shutil.copyfileobj(response, f)

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
                                    str(self.end_time.year),
                                    str(self.end_time.month),
                                    str(self.end_time.day))
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)  # Create derectory if not existing
            dest_file = os.path.join(dest_dir, self.file_name)
            self.download(dest_file)
            if self.validate_file(dest_file):
                return 0
            else:
                # Downloaded file is invalid
                os.remove(dest_file)
                return 2
