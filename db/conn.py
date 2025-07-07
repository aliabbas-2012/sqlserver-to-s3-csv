import pymssql
from sqlalchemy import create_engine
from utils import helper as h

def get_mssql_connection(as_dict=True):
    """
    This method creates a connection with SQL server
    """
    config = h.load_config()
    return pymssql.connect(
        server=config["SQL_SERVER_HOST"],
        user=config["SQL_SERVER_UID"],
        password=config["SQL_SERVER_PWD"],
        database=config["SQL_SERVER_DB"],
        as_dict=as_dict,
    )


def create_sqlalchemy_engine():
    config = h.load_config()
    engine = create_engine(
        f"""mssql+pymssql://{config["SQL_SERVER_UID"]}:{config["SQL_SERVER_PWD"]}@{config["SQL_SERVER_HOST"]}:{config["SQL_SERVER_PORT"]}/{config["SQL_SERVER_DB"]}"""
    )
    return engine


def get_mssql_table_columns(table, mssql_connection):
    """
    This method is used to get column names from a table
    """
    cursor = mssql_connection.cursor()
    sql_query = (
        f"SELECT COLUMN_NAME,DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table}' ORDER BY "
        f"ORDINAL_POSITION"
    )
    cursor.execute(sql_query)
    columns_list = []
    columns = cursor.fetchall()
    for c in columns:
        columns_list.append(c[0])
    return columns_list
