import os
import datetime
import math
import logging
from logging.handlers import TimedRotatingFileHandler
import zipfile
import progressbar
from dateutil.parser import parse
from dateutil.parser import ParserError
from dotenv import dotenv_values

def load_config():
    return dotenv_values(".env")


CONFIG = load_config()

# Create a TimedRotatingFileHandler to rotate logs at midnight
log_handler = TimedRotatingFileHandler(
    "export-logs.log", when="midnight", interval=1, backupCount=15, encoding="utf-8"
)

# Format logs with timestamp
log_handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
))
logging.basicConfig(
    level=logging.INFO,
    handlers=[log_handler],
)

LOGGER = logging.getLogger(__name__)


def escape_string_quotes(value, is_date_time=False, date_format="%Y-%m-%d"):
    """This method escapes the single quote strings to insert them in SQL"""
    if isinstance(value, str):
        value = value.replace("'", "''").strip()

    if value is None or value == "":
        return "nan"
    elif is_date_time and isinstance(value, str):
        try:
            return datetime.datetime.strptime(value, date_format)
        except ValueError:
            try:
                return datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    return datetime.datetime.strptime(value, "%m/%d/%Y")
                except ValueError:
                    return datetime.datetime.strptime(value, "%Y-%m-%d")
    elif (isinstance(value, int) or isinstance(value, float)) and math.isnan(value):
        return "nan"
    elif isinstance(value, int) or isinstance(value, float):
        return str(value)
    else:
        return value


# This is an updated method will work for each format
def format_date(input, output_format="%Y-%m-%d"):
    try:
        if isinstance(input, datetime.datetime):
            return input.strftime(output_format)
        else:
            parsed_date = parse(input)
            return parsed_date.strftime(output_format)
    except (ValueError, ParserError):
        return "NULL"


def get_integer_val(value):
    """
    This method reads the integer value of the input string or float, return nan or the original value if not integer
    """
    if isinstance(value, str):
        value = value.strip()
        if value == "":
            return "NULL"
        try:
            return int(float(value))
        except ValueError:
            return value
    if isinstance(value, int) or isinstance(value, float):
        return "NULL" if math.isnan(value) else int(float(value))
    elif value is None:
        return "NULL"
    else:
        return value


def get_float_val(value):
    """
    This method reads the float value from the string instance and returns nan or the value if not float
    """
    if isinstance(value, str) and len(value) > 2:
        value = (
            value.replace("--", "-")
            .replace(",", "")
            .replace("-.", ".")
            .replace("..", ".")
        )
        value = value[0] + value[1:].replace("-", ".")
        value = "".join(value.split()).rstrip(".")
    if (
            (not isinstance(value, str) and (value is None or math.isnan(value)))
            or value == "`"
            or (isinstance(value, str) and value.isalpha())
    ):
        return "NULL"
    elif isinstance(value, str) or isinstance(value, float):
        try:
            return float(value)
        except ValueError:
            return "NULL"
    else:
        return value


def get_date_from_datetime(csv_row_value):
    if isinstance(csv_row_value, datetime.datetime):
        return csv_row_value.date()
    else:
        return csv_row_value


def get_boolean_val(value):
    if isinstance(value, str):
        try:
            return int(float(value))
        except ValueError:
            return bool(value)
    elif isinstance(value, int) or isinstance(value, float):
        # print("value here", value, type(value))
        return False if math.isnan(value) else bool(int(float(value)))
    elif value is None:
        return False
    elif isinstance(value, bool):
        return value
    else:
        return False


def calculate_decimal(value):
    # print("value to calculate decimal==", value)
    if value[0].endswith("'"):
        value.append(value[-1])
        value[2] = value[1]
        value[1] = value[0].split(".")[1]
        value[0] = value[0].split(".")[0]
    if len(value) == 3 and value[2].isalpha():
        value.append(value[2])

        if len(value[1].split(".")) == 2:
            [value[1], value[2]] = value[1].split(".")
        else:
            value[2] = "0"
    multiplier = 1
    degrees = float(value[0])
    minutes = float(value[1].replace("'", "")) / 60
    seconds = float(value[2].replace('"', "").replace("'", "")) / 3600
    if len(value) == 4 and value[3] in ["W", "S"]:
        multiplier = -1
    return round(multiplier * (degrees + minutes + seconds), 8)


def get_coordinate_val(value):
    if isinstance(value, str):
        value = value.lstrip("'")
    # print("coordinate value original", value, type(value))
    if isinstance(value, str) and (
            '"' in value or "'" in value or len(value.split()) > 2
    ):
        value = (
            "".join(
                char
                for char in value
                if char.isalnum() or char in [".", '"', "'", " ", "-"]
            )
            .replace("D", " ")
            .replace("--", "-")
            .replace("-", ".")
            .replace("'", "' ")
            .replace("\\", "")
        )
        if value[0].isalpha():
            value = f"{value[1:]} {value[0]}"
        elif value[-1].isalpha():
            value = f"{value[:-1]} {value[-1]}"
        # print("checking the result===", value, value[-1])

        return calculate_decimal(value.split())
    else:
        return get_float_val(value)


def create_zip_file(file_path, file_name):
    zip_file_path = "%s.zip" % file_path
    zipfile.ZipFile(
        zip_file_path, mode="w", compression=zipfile.ZIP_DEFLATED
    ).write(file_path, os.path.basename(file_path))
    return zip_file_path


def extract_zip_file(zip_file_path):
    try:
        zip_file = zipfile.ZipFile(zip_file_path)
        zip_file.extractall(os.path.dirname(zip_file_path))
        zip_file.close()
    except zipfile.BadZipFile as bz:
        logging.exception(f"Bad Zip File Error: {bz}")
    except Exception as e:
        logging.exception(f"Error extracting ZIP file: {e}")


def initialize_progress_bar(max_val):
    progress_bar = progressbar.ProgressBar(maxval=max_val)
    progress_bar.start()
    return progress_bar


def proceed_progress_bar(progress_bar, value):
    progress_bar.update(progress_bar.currval + value)


def get_unique_id_column(table_name):
    return "id"

def empty_directory_contents(directory_path, remove_self=False, export=False):
    try:
        if os.path.isdir(directory_path):
            for filename in os.listdir(directory_path):
                filepath = os.path.join(directory_path, filename)
                if export:
                    print(f"removing file==={filepath}")
                else:
                    logging.info(f"removing file==={filepath}")
                if os.path.isfile(filepath):
                    os.remove(filepath)
                    if export:
                        print(
                            f"File {filename} removed successfully in {directory_path}."
                        )
                    else:
                        logging.info(
                            f"File {filename} removed successfully in {directory_path}."
                        )
        else:
            logging.info(
                f"Directory {directory_path} not found."
            )
        if remove_self and os.path.isdir(directory_path):
            os.rmdir(directory_path)
    except (FileNotFoundError, PermissionError) as exception:
        if export:
            print(f"clear_export_requests_tables exception== {exception}")
        else:
            logging.info(f"clear_export_requests_tables exception== {exception}")
        raise exception