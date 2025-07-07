import re
from utils import helper as h


def format_column_value(value, field_type, col):
    if value is not None:
        return format_non_null_value(value, field_type, col)
    else:
        value = "NULL"
    return value


def format_non_null_value(value, field_type, col):
    if field_type == "string":
        value = (
            h.escape_string_quotes(value)
            .replace('"nan"', "NULL")
            .replace("nan", "NULL")
        )
    elif field_type == "double":
        if value is not None:
            value = h.get_float_val(value)
        else:
            value = "NULL"
    elif field_type == "boolean":
        value = h.get_boolean_val(value)
    elif field_type == "geo_point":
        value = re.sub(r"[^a-zA-Z0-9 \n\.\-]", "", value)
        if value is not None:
            value = h.get_coordinate_val(value)
        else:
            value = "NULL"
    elif field_type == "date":
        value = h.format_date(value)
    elif field_type == "timestamp":
        value = h.format_date(value, "%Y-%m-%d %H:%M:%S.%f")
    elif field_type == "int":
        value = "NULL" if value == "NULL" else h.get_integer_val(value)
    return value
