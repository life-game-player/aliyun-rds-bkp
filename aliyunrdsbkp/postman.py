from smtplib import SMTP as SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class Postman:
    def __init__(self, mail_config):
        self.smtp_login = mail_config['SMTPLogin']
        self.smtp_passwd = mail_config['SMTPPassword']
        self.smtp_server = mail_config['SMTPServer']
        self.smtp_port = mail_config['SMTPPort']
        self.sender = mail_config['From']
        self.receivers = mail_config['To']
        self.cc = mail_config['Cc']
        self.subject = mail_config['Subject']
        self.ttls = mail_config['TTLS']

    def get_db_file_info_html(self, dbfile, succeeded):
        highlight = 'bgcolor="#FCDD59"'
        html_text = '<tr {}>'.format('' if succeeded else highlight)
        html_text += '<td style="border-left:1px solid black; \
            border-bottom: 1px solid black; \
            padding:10px 20px 10px 20px">{}</td>'\
            .format(dbfile.get_host_id())
        html_text += '<td style="border-left:1px solid black; \
            border-bottom: 1px solid black; \
            padding:10px 20px 10px 20px">{}</td>'\
            .format(dbfile.get_file_name())
        html_text += '<td style="border-left:1px solid black; \
            border-bottom: 1px solid black; \
            padding:10px 20px 10px 20px">{}</td>'\
            .format(dbfile.get_file_type())
        html_text += '<td style="border-left:1px solid black; \
            border-bottom: 1px solid black; \
            padding:10px 20px 10px 20px">{}</td>'\
            .format(dbfile.get_file_size())
        html_text += '<td style="border-left:1px solid black; \
            border-bottom: 1px solid black; \
            padding:10px 20px 10px 20px">{}</td>'\
            .format(dbfile.get_start_time())
        html_text += '<td style="border-left:1px solid black; \
            border-bottom: 1px solid black; \
            padding:10px 20px 10px 20px">{}</td>'\
            .format(dbfile.get_end_time())
        html_text += '<td style="border-left:1px solid black; \
            border-right:1px solid black;border-bottom: 1px solid black; \
            padding:10px 20px 10px 20px">{}</td>'\
            .format('' if succeeded else dbfile.get_download_url())
        html_text += '</tr>'
        return html_text

    def send_backup_report(self, succeeded, failed, free_in_gb):
        succeeded_cnt = len(succeeded)
        failed_cnt = len(failed)
        plain_text = "Sorry, HTML format only!"
        self.subject = "{} - {} succeeded, {} failed, {} GB space left".format(
            self.subject, succeeded_cnt, failed_cnt, free_in_gb
        )
        html_text = '<div style="margin-bottom:5px;color:{};font-size:12.0pt;\
        font-family:Calibri,Microsoft YaHei,黑体,宋体,sans-serif;">\
        {} succeeded, {} failed, {} GB space left</div>'.format(
            "red" if failed_cnt > 0 or free_in_gb < 30 else "green",
            succeeded_cnt,
            failed_cnt,
            free_in_gb
        )
        html_text += '<table cellpadding="10" cellspacing="0" \
        style="font-size:11.0pt; \
        font-family:Calibri,Microsoft YaHei,黑体,宋体,sans-serif;"> \
        <tr bgcolor="#63A8EB"> \
        <th style="border-left:1px solid black;\
        border-bottom: 1px solid black;border-top: 1px solid black; \
        padding:10px 20px 10px 20px"> \
        实例编号</th> \
        <th style="border-left:1px solid black; \
        border-bottom: 1px solid black;border-top: 1px solid black; \
        padding:10px 20px 10px 20px">文件名</th> \
        <th style="border-left:1px solid black; \
        border-bottom: 1px solid black;border-top: 1px solid black;\
        padding:10px 20px 10px 20px">类型</th> \
        <th style="border-left:1px solid black; \
        border-bottom: 1px solid black;border-top: 1px solid black; \
        padding:10px 20px 10px 20px">文件大小</th> \
        <th style="border-left:1px solid black; \
        border-bottom: 1px solid black; \
        border-top: 1px solid black;padding:10px 20px 10px 20px">\
        记录开始UTC时间</th> \
        <th style="border-left:1px solid black;border-bottom:1px solid black;\
        border-top: 1px solid black;padding:10px 20px 10px 20px">\
        记录结束UTC时间</th> \
        <th style="border: 1px solid black;padding:10px 20px 10px 20px">\
        下载链接</th> \
        </tr>'
        for f in failed:
            html_text += self.get_db_file_info_html(f, False)
        for f in succeeded:
            html_text += self.get_db_file_info_html(f, True)
        if succeeded_cnt == 0 and failed_cnt == 0:
            html_text += '<tr><td colspan="7" align="center" \
            style="border-left:1px solid black;border-right:1px solid black; \
            border-right:1px solid black; \
            border-bottom: 1px solid black;padding:10px 20px 10px 20px">无</tr>'
        html_text += "</table>"
        self.send_mail(plain_text, html_text)

    def send_mail(self, plain_text, html_text):
        message = MIMEMultipart("alternative")
        message["Subject"] = self.subject
        message["From"] = self.sender
        message["To"] = ", ".join(self.receivers)
        message["Cc"] = ", ".join(self.cc)
        part1 = MIMEText(plain_text, "plain")
        part2 = MIMEText(html_text, "html")
        message.attach(part1)
        message.attach(part2)
        with SMTP(self.smtp_server, self.smtp_port) as server:
            if self.ttls:
                server.ehlo()
                server.starttls()
                server.ehlo()
            server.login(self.smtp_login, self.smtp_passwd)
            server.send_message(message)
