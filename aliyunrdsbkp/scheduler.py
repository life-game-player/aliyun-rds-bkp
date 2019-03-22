from datetime import datetime


class Scheduler:
    def __init__(self):
        self.base_time = datetime.now()

    def check_weekday(self, s_wkday):
        if s_wkday == '*' or \
                str(self.base_time.weekday() + 1) \
                in [x.strip() for x in s_wkday.split(',')]:
            return True
        else:
            return False

    def check_month(self, s_mon):
        if s_mon == '*' or \
                str(self.base_time.month) \
                in [x.strip() for x in s_mon.split(',')]:
            return True
        else:
            return False

    def check_day(self, s_day):
        if s_day == '*' or \
                str(self.base_time.day) \
                in [x.strip() for x in s_day.split(',')]:
            return True
        else:
            return False

    def check_hour(self, s_hr):
        if s_hr == '*' or \
                str(self.base_time.hour) \
                in [x.strip() for x in s_hr.split(',')]:
            return True
        else:
            return False

    def check_minute(self, s_min):
        if s_min == '*' or \
                str(self.base_time.minute) \
                in [x.strip() for x in s_min.split(',')]:
            return True
        else:
            return False

    def is_triggered_now(self, schedule):
        s_min, s_hr, s_day, s_mon, s_wkday \
            = [x.strip() for x in schedule.split(' ')]
        if self.check_weekday(s_wkday) and \
                self.check_month(s_mon) and \
                self.check_day(s_day) and \
                self.check_hour(s_hr) and \
                self.check_minute(s_min):
            return True
        else:
            return False
