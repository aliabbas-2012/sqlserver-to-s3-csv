import os, sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import helper as h
from s3 import shipper as s3_shipper
from notifications import manager as notification_manager
from db import exporter

def create_csvs_directory(config, job_datetime):
    path_to_csvs = ""
    path_to_csvs_directory = str(os.path.join(config["PATH_TO_CSVS"], job_datetime))
    try:
        for path in path_to_csvs_directory.split(os.sep):
            path_to_csvs = os.path.join(path_to_csvs, path)
            if not os.path.exists(path_to_csvs):
                os.mkdir(path_to_csvs)
    except OSError as e:
        notification_manager.export_error(config, e)

    return path_to_csvs_directory


def execute_data_export():
    config = h.load_config()
    try:

        job_datetime  = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        csvs_path = create_csvs_directory(config, job_datetime)
        print(
            "Processing requests - time start",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        migration_log = exporter.generate_csvs(config, job_datetime)
        print(
            "Processing requests - time end  ",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        migration_log = s3_shipper.export_csvs_to_s3(config, migration_log)
        h.empty_directory_contents(csvs_path, True, True)

    except Exception as e:
        notification_manager.export_error(config, e)
