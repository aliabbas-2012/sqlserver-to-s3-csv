import math
import re

from progressbar import progressbar
import pandas as pd
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import  extras as e
from db import conn, data_types as d

def get_file_name(table_name):
    return f"{table_name}.csv"

def get_output_path(table_name, config, job_datetime):
    return str(
        os.path.join(config["PATH_TO_CSVS"], job_datetime, get_file_name(table_name))
    )

def upload_progress(up_progress, chunk):
    up_progress.update(up_progress.currval + chunk)


def get_export_csv_query(table_name):
    return (
        "SELECT *, Floor(ROW_NUMBER() OVER (ORDER BY ID)/200000) AS esIndex,"
        "(ROW_NUMBER() OVER (ORDER BY ID)) as tblOrder  "
        f"from {table_name}"
    )

def process_csv_writing(table_name, output_path, rows_count):
    columns_mapping = d.fields_mapping
    columns_keys = list(columns_mapping.keys())

    query = get_export_csv_query(table_name)
    chunk_size = 10000
    data_chunks = pd.read_sql_query(
        sql=query, con=conn.create_sqlalchemy_engine(), chunksize=chunk_size
    )
    chunk_count = math.ceil(rows_count / chunk_size)

    up_progress = progressbar.ProgressBar(maxval=chunk_count)
    print('chunk_count....', chunk_count)
    up_progress.start()
    header = True
    progress = 1
    for chunk in data_chunks:
        chunk = chunk.iloc[:, :len(columns_keys)]
        chunk.columns = columns_keys

        for col in chunk.columns:
            field_type = columns_mapping[col]
            chunk[col] = chunk[col].apply(e.format_column_value, args=(field_type, col))

        pd.DataFrame(data=chunk, index=None).to_csv(
            sep="\t",
            path_or_buf=output_path,
            header=header,
            mode="a",
            index=False,
        )
        header = False
        up_progress.update(progress)
        progress = progress + 1

    up_progress.finish()


def extract_keywords(text):
    # Include numbers in the pattern
    filtered_words = []
    if text is not None:
        pattern = r'\b(\d+|[A-Z]*\d*[A-Z]*|[A-Z\d]+/[A-Z\d]+)\b'

        # Split the text based on spaces and other delimiters
        words = re.findall(r'\b[\w/]+\b', text)

        # Filter words that match the pattern
        filtered_words = [word for word in words if re.fullmatch(pattern, word)]
        filtered_words = [x for x in filtered_words if 1 < len(x) < 5]
    return filtered_words


def get_rows_count_query(table_name):
    return f"SELECT COUNT(*) AS rows_count FROM {table_name}"


def get_tables_min_max_unique_id(table_name):
    return f"SELECT MIN(ID) AS MIN_ID, MAX(ID) AS MAX_ID FROM {table_name};"


def export_mssql_table(config, job_datetime):
    migration_log = {}
    mssql_connection = conn.get_mssql_connection()
    mssql_cursor = mssql_connection.cursor()
    table_name = config["TABLE_NAME"]

    mssql_cursor.execute(get_rows_count_query(table_name))
    rows_count = mssql_cursor.fetchone()["rows_count"]
    mssql_cursor.execute(get_tables_min_max_unique_id(table_name))
    min_max_id = mssql_cursor.fetchone()
    output_path = get_output_path(table_name, config, job_datetime)

    migration_log["total_rows"] = rows_count
    migration_log["min_id"] = min_max_id['MIN_ID']
    migration_log["max_id"] = min_max_id['MAX_ID']
    migration_log["file_name"] = f"""{table_name}.csv"""
    migration_log["file_path"] = output_path
    migration_log["job_datetime"] = job_datetime

    print(f"Processing {output_path}")
    process_csv_writing(table_name, output_path, rows_count)

    return migration_log

def generate_csvs(config, job_datetime):
    return export_mssql_table(config, job_datetime)
