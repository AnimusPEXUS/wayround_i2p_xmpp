
import wayround_org.utils.datetime_iso8601


def str_to_datetime(value):
    return wayround_org.utils.datetime_iso8601.str_to_datetime(value)[0]


def datetime_to_str(value):
    return wayround_org.utils.datetime_iso8601.datetime_to_str(
        value,
        {'Z', 'day', 'month', 'utc', 'min',
         'T', 'year', ':', '-', 'hour', 'sec'}
        )
