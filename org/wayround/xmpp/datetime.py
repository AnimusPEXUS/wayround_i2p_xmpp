
import datetime
import logging
import re

RE_DATE = \
    r'(?P<year>\-?\d{4})\-(?P<month>\d{2})\-(?P<day>\d{2})'

RE_TIME = \
    r'(?P<th>\d{2})\:(?P<tm>\d{2})\:(?P<ts>\d{2})(?P<tf>\.\d+)?' + \
    r'(?P<tz>(Z|(?P<tz_sign>[+-])(?P<tz_h>\d{2})\:(?P<tz_m>\d{2})))?'

RE = \
    r'^(?P<date>{})?(?P<time>T?{})?$'.format(RE_DATE, RE_TIME)


RE_COMPILED = re.compile(RE)


def str_to_datetime(value, _debug=False):

    ret = None

    if not isinstance(value, str):
        raise TypeError("parameter must be str")

    res = RE_COMPILED.match(value)

    if res == None:
        if _debug:
            logging.debug("Can't parse {}".format(value))
    else:

        # date operations
        date = res.group('date')

        year = res.group('year')
        if year != None:
            year = int(year)
        else:
            year = 0

        month = res.group('month')
        if month != None:
            month = int(month)
        else:
            month = 0

        day = res.group('day')
        if day != None:
            day = int(day)
        else:
            day = 0

        # time operations
        time = res.group('time')

        hour = res.group('th')
        if hour != None:
            hour = int(hour)
        else:
            hour = 0

        minute = res.group('tm')
        if minute != None:
            minute = int(minute)
        else:
            minute = 0

        sec = res.group('ts')
        if sec != None:
            sec = int(sec)
        else:
            sec = 0

        fract = res.group('tf')
        if fract != None:
            fract = int(fract)
        else:
            fract = 0

        # time zone operations
        tz = res.group('tz')
        tz_sign = res.group('tz_sign')
        tz_h = res.group('tz_h')
        if tz_h != None:
            tz_h = int(tz_h)
        else:
            tz_h = 0

        tz_m = res.group('tz_m')
        if tz_m != None:
            tz_m = int(tz_m)
        else:
            tz_m = 0

        if _debug:
            logging.debug(
"""{} parsed as:
date = {}
year = {}
month = {}
day = {}

time = {}
hour = {}
minute = {}
sec = {}
fract = {}

tz = {}
tz_sign = {}
tz_h = {}
tz_m = {}
""".format(
                    value,

                    date,
                    year, month, day,

                    time,
                    hour, minute, sec, fract,
                    tz, tz_sign, tz_h, tz_m
                    )
                )

        d = None

        if date != None and time != None:
            z = None
            if tz != 'Z':
                z = gen_tz(tz_h, tz_m, tz_sign == '+')
            d = datetime.datetime(
                year, month, day, hour, minute, sec, fract, z
                )

        elif date != None and time == None:
            d = datetime.date(year, month, day)

        elif date == None and time != None:
            z = None
            if tz != 'Z':
                z = gen_tz(tz_h, tz_m, tz_sign == '+')
            d = datetime.time(hour, minute, sec, fract, z)

        else:
            raise Exception("wrong time combination: '{}'".format(value))

        ret = d

    return ret


def datetime_to_str(value):

    t = type(value)

    if not t in [datetime.datetime, datetime.time, datetime.date]:
        raise TypeError(
"parameter type must be in [datetime.datetime, datetime.time, datetime.date]"
            )

    ret = None

    if t == datetime.datetime:
        tz = 'Z'
        if value.tzinfo != None:
            tz = format_tz(value.tzinfo)
        ms = ''
        if value.microsecond != 0:
            ms = '.{}'.format(value.microsecond)
        ret = '{:04}-{:02}-{:02}T{:02}:{:02}:{:02}{}{}'.format(
            value.year,
            value.month,
            value.day,
            value.hour,
            value.minute,
            value.second,
            ms,
            tz
            )

    elif t == datetime.time:
        tz = 'Z'
        if value.tzinfo != None:
            tz = format_tz(value.tzinfo)
        ms = ''
        if value.microsecond != 0:
            ms = '.{}'.format(value.microsecond)
        ret = '{:02}:{:02}:{:02}{}{}'.format(
            value.hour,
            value.minute,
            value.second,
            ms,
            tz
            )

    elif t == datetime.date:
        ret = '{:04}-{:02}-{:02}'.format(
            value.year,
            value.month,
            value.day
            )

    else:
        raise Exception("DNA error")

    return ret


def gen_tz(h, m, plus=True):

    td = datetime.timedelta(hours=h, minutes=m)
    if not plus:
        td = -td

    tz = datetime.timezone(td)

    return tz


def format_tz(value):

    ret = None

    if value == None:
        ret = 'Z'
    else:
        a = value.utcoffset(None)

        sign = '+'

        if a < datetime.timedelta():
            sign = '-'
            a = -a

        hours = int(a.seconds / 60 / 60)
        minutes = int((a.seconds - (hours * 60 * 60)) / 60 / 60)

        ret = '{}{:02}:{:02}'.format(sign, hours, minutes)

    return ret
