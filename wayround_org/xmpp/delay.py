
import datetime

import lxml.etree
import wayround_org.utils.factory
import wayround_org.xmpp.datetime


class Delay:

    def __init__(self, stamp, from_=None, text=None):

        self.set_stamp(stamp)
        self.set_from_(from_)
        self.set_text(text)

    def check_text(self, value):
        if value is not None and not isinstance(value, str):
            raise TypeError("`text' must be None or str")

    def check_from_(self, value):
        if value is not None and not isinstance(value, str):
            raise TypeError("`from' must be None or str")

    def check_stamp(self, value):
        if value is not None and not isinstance(value, datetime.datetime):
            raise TypeError("`stamp' must be None or datetime.datetime")

    @classmethod
    def new_from_element(cls, element):

        tag = wayround_org.utils.lxml.parse_element_tag(
            element,
            'delay', ['urn:xmpp:delay']
            )[0]

        if tag is None:
            raise ValueError("invalid element tag or namespace")

        stamp = element.get('stamp')
        if stamp != None:
            stamp = wayround_org.xmpp.datetime.str_to_datetime(stamp)

        cl = cls(stamp)

        wayround_org.utils.lxml.elem_props_to_object_props(
            element, cl,
            [
             ('from', 'from_')
             ]
            )

        cl.set_text(element.text)

        cl.check()

        return cl

    def gen_element(self):

        self.check()

        element = lxml.etree.Element('delay')
        element.set('xmlns', 'urn:xmpp:delay')

        wayround_org.utils.lxml.object_props_to_elem_props(
            self, element,
            [
             ('from_', 'from')
             ]
            )

        stamp = self.get_stamp()
        if stamp != None:
            stamp = wayround_org.xmpp.datetime.datetime_to_str(stamp)
            element.set('stamp', stamp)

        element.text = self.get_text()

        return element

wayround_org.utils.factory.class_generate_attributes(
    Delay,
    ['from_', 'stamp', 'text']
    )
wayround_org.utils.factory.class_generate_check(
    Delay,
    ['from_', 'stamp', 'text']
    )
