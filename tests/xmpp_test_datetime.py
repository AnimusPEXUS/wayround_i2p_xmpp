
import datetime

#datetime.MINYEAR = -9999
print('datetime.MINYEAR = {}'.format(datetime.MINYEAR))

import logging
import org.wayround.xmpp.datetime

logging.basicConfig(level='DEBUG')

for i in [
    '1776-07-04',
    '1969-07-21T02:56:15Z',
    '1969-07-20T21:56:15-05:00',
    '16:00:00'
    ]:
    res = org.wayround.xmpp.datetime.str_to_datetime(i, _debug=True)
    print("Result:         {}".format(res))
    print("Formatted back: {}".format(
            org.wayround.xmpp.datetime.datetime_to_str(res)
            )
          )
