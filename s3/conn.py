import os, sys, boto3
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import helper as h

def get_s3_client():
    config = h.load_config()
    return boto3.client(
        "s3",
        aws_access_key_id=config["AWS_ACCESS_KEY"],
        aws_secret_access_key=config["AWS_SECRET_KEY"],
        region_name=config["AWS_REGION"],
    )