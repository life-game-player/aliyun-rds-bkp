import os
from datetime import datetime, timedelta
import shutil


class Cleaner:
    def clean_folder(self, dir, region_id, instance_id, retention_days):
        expire_date = datetime.utcnow() - timedelta(days=retention_days)
        backup_dir = os.path.join(
            dir, region_id, instance_id
        )
        for d_year in os.listdir(backup_dir):
            d_year_path = os.path.join(backup_dir, d_year)
            if int(d_year) < expire_date.year:
                shutil.rmtree(d_year_path)
            elif int(d_year) == expire_date.year:
                for d_month in os.listdir(d_year_path):
                    d_month_path = os.path.join(d_year_path, d_month)
                    if int(d_month) < expire_date.month:
                        shutil.rmtree(d_month_path)
                    elif int(d_month) == expire_date.month:
                        for d_day in os.listdir(d_month_path):
                            d_day_path = os.path.join(d_month_path, d_day)
                            if int(d_day) < expire_date.day:
                                shutil.rmtree(d_day_path)
