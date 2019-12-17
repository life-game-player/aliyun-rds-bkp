# Aliyun RDS Backup Tool

这是一个按照自定义配置，从阿里云RDS(***目前只支持MySQL***)下载数据库备份(包括全备和binlog备份)到本地的工具，并支持定时清理过期备份文件。

## 安装

```python
pip install aliyun-rds-bkp
```

## 配置

配置文件为json格式。

```json
{
    "AccessKeyId": "AccessKeyID Provided by Aliyun RDS",
    "AccessKeySecret": "AccessKeySecret Provided by Aliyun RDS",
    "Regions": [
        {
            "RegionID": "cn-hangzhou",
            "DBInstances": [
                {
                    "DBInstanceId": "rm-XXXXXXXXXXXXXXXXXX",
                    "LastFullBackup": {
                        "BackupEndTime": "2019-03-16 05:30:00"
                    },
                    "LastBinlogBackup": {
                        "BackupEndTime": "2019-03-16 05:30:00"
                    },
                    "BackupRetentionDays": 21,
                    "Schedule": {
                        "FullBackup": {
                            "Plan": "* * * * 2,4,6"
                        },
                        "BinlogBackup": {
                            "Plan": "* * * * *"
                        }
                    }
                }
            ]
        }
    ],
    "BackupHome": "Path/to/Backup/Directory",
    "FailedDownloads": "Path/to/Failed Downloads/Directory",
    "ErrorLog": "Path/to/Error/Log",
    "MailConfig": {
        "SMTPServer": "Your SMTP Server",
        "SMTPLogin": "Account to Login SMTP Server",
        "SMTPPassword": "Password to login SMTP Server",
        "SMTPPort": 25,
        "TTLS": false,
        "From": "email_from",
        "To": [
            "email_1",
            "email_2"
        ],
        "Cc": [
            "email_cc"
        ],
        "Subject": "E-Mail Subject"
    }
}
```

#### 参数说明

- AccessKeyId: 阿里云提供的AccessKeyId
- AccessKeySecret: 阿里云提供的AccessKeySecret
- RegionID: 参考https://help.aliyun.com/document_detail/40654.html
- DBInstanceId: RDS实例ID
- BackupEndTime: 上次备份的结束的UTC时间，用于增量，格式为YYYY-MM-DD HH:MI:SS
- BackupRetentionDays: 备份保留天数
- Plan: 备份计划(***本地时间***)。5个参数以空格分隔，分别代表触发备份的
  - 分钟
  - 小时
  - 一个月中的第几天
  - 月份
  - 一个星期中的第几天。1表示星期一，7表示星期日。
- BackupHome: 放置备份文件的总目录。在总目录下会自动按照RegionID->InstanceID->Year->Month->Day创建目录
- ErrorLog: 指定错误日志存放文件
- SMTPServer: 邮件服务器地址，用于发送备份成功或失败的通知邮件
- SMTPLogin: 邮件服务器登录账号
- SMTPPassword: 邮件服务器登录密码
- SMTPPort: 邮件服务器端口
- TTLS: 邮件服务器是否使用TTLS，true或false
- From: 邮件发送账户
- To: 邮件接收账户列表
- Cc: 邮件抄送账户列表
- Subject: 通知邮件的主题

## 使用

1. 编写调用脚本

```python
import os

from aliyunrdsbkp.mysql_backup import MySQLBackup

"""
日常备份
"""
if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config_file = os.path.join(
        dir_path,
        'config/settings.json'
    )  # 配置文件路径
    mysql_backup = MySQLBackup(config_file)
    mysql_backup.backup()

```

```python
import os

from aliyunrdsbkp.retry_downloader import RetryDownloader

"""
下载重试
"""
if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config_file = os.path.join(
        dir_path,
        'config/settings.json'
    )  # 配置文件路径
    retry_downloader = RetryDownloader(config_file)
    retry_downloader.run()
```

2. 在Linux下的crontab或Windows下的Task Scheduler配置定时执行以上调用脚本