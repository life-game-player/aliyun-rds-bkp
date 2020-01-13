import json
from datetime import datetime, timedelta

from aliyunsdkrds.request.v20140815 import DescribeBackupsRequest
from aliyunsdkrds.request.v20140815 import DescribeBinlogFilesRequest

from aliyunrdsbkp.db_file import DBFile
from aliyunrdsbkp.logger import logger


class RDSInstance:
    def __init__(self, client, region_id, instance_id):
        self.client = client
        self.region_id = region_id
        self.instance_id = instance_id

    def get_backup_files(self, backup_type, start_time, end_time=None):
        if backup_type == 'full':
            logger.info("get_fullbackup_files('{}', '{}')".format(start_time, end_time))
            return self.get_fullbackup_files(start_time, end_time)
        elif backup_type == 'binlog':
            logger.info("get_binlog_files('{}', '{}')".format(start_time, end_time))
            return self.get_binlog_files(start_time, end_time)
        else:
            return None

    def get_fullbackup_files(self, start_time, end_time=None, top=0, dummy=False):
        files = list()
        request = DescribeBackupsRequest.DescribeBackupsRequest()
        # Aliyun SDK works on this way: [Backup End Time]
        # BETWEEN [search start time] AND [search end time].
        # And full backup is taken once at most per day.
        # So it is safe to add 1 day on last backup end time as
        # current start time to avoid reundant downloading.
        start_time += timedelta(days=1)
        request.set_StartTime(start_time.strftime("%Y-%m-%dT00:00Z"))
        if end_time:
            search_end_time = end_time
        else:
            search_end_time = datetime.utcnow()
        # Add 1 day to end time because it is exclusive in SDK
        search_end_time += timedelta(days=1)
        request.set_EndTime(search_end_time.strftime("%Y-%m-%dT00:00Z"))
        request.set_DBInstanceId(self.instance_id)
        request.set_PageSize(100)
        read_record_cnt = 0
        page_num = 1
        while True:
            request.set_PageNumber(page_num)
            response = json.loads(
                self.client.do_action_with_exception(request))
            for bkp in response['Items']['Backup']:
                download_url = bkp["BackupDownloadURL"]
                host_id = bkp["HostInstanceID"]
                file_status = 0 if bkp["BackupStatus"] == "Success" else 1
                file_size = bkp["BackupSize"]
                file_start_time = datetime.strptime(bkp["BackupStartTime"],
                                                    "%Y-%m-%dT%H:%M:%SZ")
                file_end_time = datetime.strptime(bkp["BackupEndTime"],
                                                  "%Y-%m-%dT%H:%M:%SZ")
                file = DBFile(
                    download_url, host_id,
                    self.region_id, self.instance_id,
                    file_start_time, file_end_time,
                    file_type='full',
                    file_status=file_status,
                    file_size=file_size
                )
                if not dummy:
                    logger.info(file)
                files.append(file)
            read_record_cnt += response["PageRecordCount"]
            page_num += 1
            if (
                (top > 0 and read_record_cnt >= top) or
                read_record_cnt >= response["TotalRecordCount"]
            ):
                break
        return files

    def get_binlog_files(self, start_time, end_time=None):
        init_time = datetime(2001, 1, 1)
        recent_full_bkp_files = self.get_fullbackup_files(init_time, top=2, dummy=True)
        files = self.search_binlog_files(
            recent_full_bkp_files[0].get_host_id(),
            start_time
        )
        if (
            len(recent_full_bkp_files) == 2 and
            recent_full_bkp_files[0].get_host_id() != recent_full_bkp_files[1].get_host_id()
        ):  # Master and slave hosts were switched
            b_host_id = recent_full_bkp_files[0].get_host_id()
            b_start_time = recent_full_bkp_files[0].get_start_time()
            a_host_id = recent_full_bkp_files[1].get_host_id()
            if start_time < b_start_time:
                files += self.search_binlog_files(a_host_id, start_time, b_start_time)
        return files

    def search_binlog_files(self, host_id, start_time, end_time=None):
        files = list()
        # Aliyun SDK works on this way: [Backup End Time]
        # BETWEEN [search start time] AND [search end time].
        # So it is safe to add 1 sec on last backup end time as
        # current start time to avoid reundant downloading.
        start_time += timedelta(seconds=1)
        request = DescribeBinlogFilesRequest.DescribeBinlogFilesRequest()
        request.set_StartTime(start_time.strftime("%Y-%m-%dT%H:%M:%SZ"))
        if end_time:
            request.set_EndTime(end_time.strftime("%Y-%m-%dT%H:%M:%SZ"))
        else:
            request.set_EndTime(
                datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            )
        request.set_DBInstanceId(self.instance_id)
        request.set_PageSize(100)
        read_record_cnt = 0
        page_num = 1
        while True:
            request.set_PageNumber(page_num)
            response = json.loads(self.client.do_action_with_exception(
                request))
            for binlog in response['Items']['BinLogFile']:
                if binlog['HostInstanceID'] == host_id:
                    download_url = binlog['DownloadLink']
                    file_size = binlog['FileSize']
                    checksum = binlog['Checksum']
                    file_start_time = datetime.strptime(
                        binlog['LogBeginTime'],
                        "%Y-%m-%dT%H:%M:%SZ")
                    file_end_time = datetime.strptime(
                        binlog['LogEndTime'],
                        "%Y-%m-%dT%H:%M:%SZ")
                    file = DBFile(download_url, host_id,
                        self.region_id, self.instance_id,
                        file_start_time, file_end_time,
                        file_type='binlog',
                        file_size=file_size,
                        checksum=checksum
                    )
                    logger.info(file)
                    files.append(file)
            read_record_cnt += response["PageRecordCount"]
            logger.info("{} records has been read".format(response["PageRecordCount"]))
            logger.info("Total records:{}".format(response['TotalRecordCount']))
            page_num += 1
            if read_record_cnt >= response['TotalRecordCount']:
                break
        return files
