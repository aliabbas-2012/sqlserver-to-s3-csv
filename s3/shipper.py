import os, sys
from botocore import exceptions as botocore_exceptions
import progressbar
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import helper as h
from s3 import  conn

def get_s3_path(config, file_path):
    return f"""{config.get("ENVIRONMENT", "")}/{file_path}.zip"""

def upload_csv(s3_client, config, file_path, filename):
    upload_file_path = os.path.join(file_path)
    zip_file_path = h.create_zip_file(upload_file_path, filename)
    s3_path = get_s3_path(config, file_path)

    file_info = os.stat(zip_file_path)
    up_progress = progressbar.progressbar.ProgressBar(maxval=file_info.st_size)
    up_progress.start()

    def upload_progress(chunk):
        up_progress.update(up_progress.currval + chunk)

    s3_client.upload_file(
        zip_file_path,
        config.get("S3_BUCKET", ""),
        s3_path,
        Callback=upload_progress,
    )
    return s3_path


def process_files_upload(s3_client, config, migration_log):
    print("\nprocessing csv upload")
    migration_log["s3_key"] = upload_csv(
        s3_client, config, migration_log.get("file_path", ""), migration_log["file_name"]
    )
    print("")
    return migration_log


def export_csvs_to_s3(config, migration_log):
    s3_client = conn.get_s3_client()
    try:
        migration_log = process_files_upload(s3_client, config, migration_log)
    except botocore_exceptions.ClientError as error:
        migration_log["error_text"] += f"{error}"

    return migration_log
